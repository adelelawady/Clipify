import os, json, tempfile
from pathlib import Path
import gradio as gr

def _normalize_highlights(res):
    # Accept dict({highlights:[...]}) or raw list
    if isinstance(res, dict):
        highs = res.get('highlights') or []
    elif isinstance(res, list):
        highs = res
    else:
        highs = []
    out=[]
    for h in (highs.get('highlights', highs) if isinstance(highs, dict) else highs):
        if isinstance(h, dict):
            title   = (h.get('title') or '').strip()
            excerpt = (h.get('excerpt') or h.get('text') or '').strip()
        else:
            title   = str(h)[:80]
            excerpt = str(h)
        if excerpt:
            out.append({'title': title or excerpt[:50], 'excerpt': excerpt})
    return {'highlights': out}

from dotenv import load_dotenv
import sys
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


load_dotenv()

ENV_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash-001')

from clipify.pipelines.gemini_pipeline import (
    read_timings, call_gemini, tokens_from_words,
    align_excerpt_exact_or_fuzzy, write_processed_segments, build_srts
)
from clipify.pipelines.ui_helpers import (
    ensure_transcripts, ffmpeg_cut, ffmpeg_burn_subs,
    css_hex_to_ass, safe_name
)

REPO = Path(__file__).resolve().parents[1]

# --- Logging: capture end-to-end UI/server activity into app_gradio.log ---
import logging
logger = logging.getLogger("clipify.ui.app_gradio")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    try:
        log_path = REPO / "app_gradio.log"
        fh = logging.FileHandler(str(log_path), mode='a')
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception:
        # fallback to basic config if file handler cannot be created
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')


def _gather_fonts(repo: Path):
    """Find fonts in repo/fonts, ui/fonts, system locations and bundled captacity assets."""
    try:
        import fontTools.ttLib as ttLib
    except ImportError:
        print("Warning: fontTools not installed. Font metadata will be limited.")
        ttLib = None

    fonts_list = []  # display names
    fonts_map = {}   # name -> path
    fonts_meta = {}  # name -> metadata

    # Locate fonts bundled with captacity_clipify
    try:
        import captacity_clipify
        captacity_fonts_dir = Path(captacity_clipify.__file__).resolve().parent / "assets" / "fonts"
    except Exception:
        captacity_fonts_dir = None

    # Look in standard locations
    search_paths = [
        repo / "fonts",
        repo / "ui" / "fonts",
        captacity_fonts_dir,
        Path("/Library/Fonts"),
        Path("/System/Library/Fonts"),
        Path("/System/Library/Fonts/Supplemental")
    ]

    # Common font extensions
    FONT_EXTENSIONS = {'.ttf', '.otf', '.ttc', '.dfont'}

    def get_font_info(font_path):
        """Extract font metadata if possible."""
        if not ttLib:
            return {'family': font_path.stem, 'style': 'Regular'}

        try:
            tt = ttLib.TTFont(font_path)
            family = style = ""

            for record in tt['name'].names:
                if record.nameID == 1 and not family:  # Font Family name
                    family = record.string.decode('utf-8', errors='ignore')
                elif record.nameID == 2 and not style:  # Font Subfamily name
                    style = record.string.decode('utf-8', errors='ignore')

            return {
                'family': family or font_path.stem,
                'style': style or 'Regular'
            }
        except Exception:
            return {'family': font_path.stem, 'style': 'Regular'}

    # Scan for fonts
    for path in search_paths:
        if not path or not path.exists():
            continue

        for font_file in path.glob('**/*'):
            if not font_file.is_file():
                continue

            if font_file.suffix.lower() in FONT_EXTENSIONS:
                try:
                    font_info = get_font_info(font_file)
                    display_name = f"{font_info['family']} ({font_info['style']})"
                    if display_name not in fonts_map:
                        fonts_list.append(display_name)
                        fonts_map[display_name] = str(font_file)
                        fonts_meta[display_name] = font_info
                except Exception as e:
                    print(f"Warning: Could not process font {font_file}: {e}")

    # Set default font: prefer Bangers-Regular.ttf, then any Regular, then first available
    default_font = None
    for name, path in fonts_map.items():
        if Path(path).name.lower() == "bangers-regular.ttf":
            default_font = name
            break
    if default_font is None:
        for name in fonts_list:
            if "Bangers" in name:
                default_font = name
                break
    if default_font is None:
        for name in fonts_list:
            if "Regular" in name or "regular" in name:
                default_font = name
                break
    if default_font is None and fonts_list:
        default_font = fonts_list[0]

    return fonts_list, fonts_map, default_font

# discover fonts once at module import
FONTS_LIST, FONTS_MAP, FONTS_DEFAULT = _gather_fonts(REPO)

def get_video_duration(path: Path) -> float:
    """Return video duration in seconds using ffprobe, or 0 on failure."""
    try:
        import subprocess
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        return float(out)
    except Exception:
        return 0.0


def _suggest_params(duration: float, total_words: int) -> dict:
    """Suggest clip parameters based on video duration and transcript word count."""
    if duration <= 0:
        duration = 60.0
    if total_words <= 0:
        total_words = int(duration * 2.5)  # assume ~150 wpm

    # Number of clips: roughly one per minute, capped between 1 and 8
    clips = max(1, min(8, round(duration / 60)))

    # Estimate speaking rate and target excerpt length
    words_per_second = total_words / max(1.0, duration)
    target_seconds = 7.0
    target_words = max(5, min(25, round(words_per_second * target_seconds)))

    min_words = max(4, target_words - 5)
    max_words = max(min_words + 5, target_words + 5)

    # Pads and minimum duration scale slightly with clip density
    pre_pad = 0.3
    post_pad = 0.8
    min_duration = max(5.0, min(20.0, target_seconds * 1.5))

    return {
        "clips": clips,
        "min_words": min_words,
        "max_words": max_words,
        "pre_pad": pre_pad,
        "post_pad": post_pad,
        "min_duration": min_duration,
    }


def _score_excerpt(excerpt: str, start: float, end: float, total_duration: float, min_words: int, max_words: int) -> int:
    """Heuristic virality score (0-100) for an excerpt.
    - prefers medium-long excerpts (within min/max words)
    - rewards hook words/questions and numbers
    - slight bonus for earlier placement
    """
    if not excerpt:
        return 0
    txt = excerpt.lower()
    words = txt.split()
    wc = len(words)

    # length score: ideal around max_words, scaled 0..1
    if wc <= min_words:
        length_score = wc / max(1, min_words)
    else:
        length_score = min(1.0, wc / max(1, max_words))

    # hook words
    hooks = ("how", "why", "what", "when", "who", "did", "can", "could", "would", "should", "i", "you", "we", "my", "our")
    hook_bonus = 1.0 if any(h in txt.split()[:4] for h in hooks) else 0.0
    # number bonus
    number_bonus = 1.0 if any(ch.isdigit() for ch in txt) else 0.0

    # position bonus: earlier in video slightly better
    pos_norm = 1.0 - min(1.0, (start / max(1.0, total_duration))) if total_duration > 0 else 0.5

    score = (0.5 * length_score + 0.25 * (0.6 * hook_bonus + 0.4 * number_bonus) + 0.25 * pos_norm)
    return int(max(0, min(100, round(score * 100))))


def _remux_audio(source_video: Path, target_video: Path) -> bool:
    """Copy audio stream from source_video into target_video and normalize loudness.

    Some captioning tools (e.g. captacity) drop the audio track. This helper
    re-injects the original audio into the captioned output using ffmpeg and
    applies a loudnorm filter for more consistent, broadcast-friendly levels.
    """
    import subprocess
    tmp = target_video.with_suffix(".tmp" + target_video.suffix)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(target_video),
        "-i", str(source_video),
        "-map", "0:v:0",
        "-map", "1:a:0?",
        "-c:v", "copy",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(tmp)
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        tmp.replace(target_video)
        return True
    except Exception as e:
        logger.warning("Audio remux failed for %s: %s", target_video, e)
        if tmp.exists():
            tmp.unlink()
        return False


def _srt_to_captacity_segments(srt_path: Path) -> list:
    """Convert an SRT file into the segment format expected by captacity_clipify.

    captacity expects segments=[{"words": [{"word": "...", "start": 0.0, "end": 0.5}, ...]}].
    SRT only has cue-level timings, so we split each cue's text into words and
    distribute the cue duration evenly across words.
    """
    import re
    if not srt_path.exists():
        return []

    def _parse_time(t: str) -> float:
        # SRT time: HH:MM:SS,mmm
        m = re.match(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", t)
        if not m:
            return 0.0
        h, mn, s, ms = map(int, m.groups())
        return h * 3600 + mn * 60 + s + ms / 1000.0

    content = srt_path.read_text(encoding="utf-8")
    # Split by double newlines to get cues
    cues = re.split(r"\n\s*\n", content.strip())
    segments = []
    for cue in cues:
        lines = [l.strip() for l in cue.splitlines() if l.strip()]
        if len(lines) < 2:
            continue
        # Find the timing line (contains -->)
        timing_line = None
        for line in lines:
            if "-->" in line:
                timing_line = line
                break
        if not timing_line:
            continue
        # Text is everything after the timing line
        idx = lines.index(timing_line)
        text = " ".join(lines[idx + 1:])
        if not text:
            continue
        start_str, end_str = timing_line.split("-->")
        start = _parse_time(start_str.strip())
        end = _parse_time(end_str.strip())
        words = text.split()
        if not words:
            continue
        cue_dur = max(0.001, end - start)
        word_dur = cue_dur / len(words)
        word_objs = []
        for i, w in enumerate(words):
            w_start = start + i * word_dur
            w_end = start + (i + 1) * word_dur
            # Add trailing space to all but the last word so concatenation matches the text
            word_text = w + (" " if i < len(words) - 1 else "")
            word_objs.append({"word": word_text, "start": w_start, "end": w_end})
        segments.append({"words": word_objs})
    return segments


def run_pipeline(video_file, clips, min_words, max_words, model, openai_model, fuzzy,
                 font_name, font_size, primary_hex, outline_w, outline_hex, subtitle_style, position, aspect,
                 ai_provider_name, gemini_api_key, openai_api_key,
                 pre_pad, post_pad, min_duration, auto_size=False,
                 words_per_caption=3, vertical_offset=85, horizontal_align="center"):

    logger.info("run_pipeline called: video=%s clips=%s model=%s provider=%s subtitle_style=%s",
                str(video_file), clips, model, ai_provider_name, subtitle_style)

    # Validate selected provider has a key available either via input or env
    if ai_provider_name == "gemini":
        if not (gemini_api_key or os.getenv("GOOGLE_API_KEY")):
            return "Missing GOOGLE_API_KEY in .env or input", None, []
    elif ai_provider_name == "openai":
        if not (openai_api_key or os.getenv("OPENAI_API_KEY")):
            return "Missing OPENAI_API_KEY in .env or input", None, []

    if video_file is None:
        return "Please upload a video.", None, []

    src = Path(video_file)
    try:
        tjson = ensure_transcripts(REPO, src)
        transcript, words = read_timings(tjson)
    except Exception as e:
        logger.exception("Transcription/read_timings failed for %s", src)
        return f"Transcription error: {e}", None, []

    # pick API key override if provided
    api_key = None
    if ai_provider_name == "gemini":
        api_key = gemini_api_key or os.getenv("GOOGLE_API_KEY")
    else:
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

    highs = call_gemini(
        transcript,
        clips=int(clips),
        min_words=int(min_words),
        max_words=int(max_words),
        model=model,
        api_key=api_key,
        ai_provider_name=ai_provider_name,
        openai_model=openai_model
    )

    logger.info("Received %s highlights from AI provider", (len(highs.get('highlights')) if isinstance(highs, dict) and highs.get('highlights') else (len(highs) if isinstance(highs, list) else 'unknown')))

    tokens = tokens_from_words(words)
    segments = []
    for h in (highs.get('highlights', highs) if isinstance(highs, dict) else highs):
        hit = align_excerpt_exact_or_fuzzy((h.get("excerpt") if isinstance(h, dict) else str(h)), tokens, use_fuzzy=bool(fuzzy))
        if not hit:
            continue
        # Support either legacy hits of shape (a,b,s,e) or current (s,e).
        # Be defensive: prefer to treat hit as a sequence and take the last two
        # items as (start, end). Avoid unpacking failures for odd iterable types.
        s = e = None
        seq = None
        try:
            if not isinstance(hit, (str, bytes)):
                seq = list(hit)
        except Exception:
            seq = None

        if seq and len(seq) >= 2:
            s, e = seq[-2], seq[-1]
        else:
            # Fallback: try a direct unpack (will raise if not possible)
            try:
                s, e = hit
            except Exception:
                # Can't interpret hit -> skip
                continue
        segments.append({"title": (h.get("title") if isinstance(h, dict) else str(h)[:80])[:80], "start": round(float(s),3), "end": round(float(e),3)})

    if not segments:
        return "No highlights could be aligned. Try enabling fuzzy or adjusting min/max words.", None, []

    proc_path = REPO / "processed_content" / "input_processed.json"
    # Persist segments (pass the list of dicts directly)
    write_processed_segments(segments, proc_path)

    srt_dir = REPO / "segmented_videos" / "input" / "srt"
    # We'll compute adjusted segments first (applying padding / min_duration / auto_size)
    seg_dir = REPO / "segmented_videos" / "input"
    seg_dir.mkdir(parents=True, exist_ok=True)

    outputs = []
    total_duration = get_video_duration(REPO / "input.mp4")
    adjusted_segments = []
    for idx, seg in enumerate(segments, start=1):
        # compute a heuristic score for each excerpt
        score = _score_excerpt(seg.get("title") or seg.get("excerpt", ""), seg.get("start"), seg.get("end"), total_duration, int(min_words), int(max_words))

        # If auto_size enabled, adjust padding and min_duration based on total video length
        pad_pre = float(pre_pad)
        pad_post = float(post_pad)
        min_dur = float(min_duration)
        try:
            if bool(auto_size):
                if total_duration <= 60:
                    pad_pre = max(0.2, pad_pre * 0.5)
                    pad_post = max(0.5, pad_post * 0.75)
                    min_dur = max(6.0, min_dur * 0.8)
                elif total_duration <= 300:
                    pad_pre = max(0.5, pad_pre)
                    pad_post = max(1.0, pad_post)
                    min_dur = max(8.0, min_dur)
                else:
                    pad_pre = max(1.0, pad_pre * 1.5)
                    pad_post = max(2.0, pad_post * 1.5)
                    min_dur = max(10.0, min_dur * 1.25)
        except Exception:
            pass

        # Expand segment by computed pre/post padding, clamp to video bounds, and
        # enforce a minimum duration so clips have context and aren't too short.
        start = max(0.0, float(seg["start"]) - pad_pre)
        end = float(seg["end"]) + pad_post
        if end - start < min_dur:
            mid = (float(seg["start"]) + float(seg["end"])) / 2.0
            half = min_dur / 2.0
            start = max(0.0, mid - half)
            end = mid + half

        adjusted_segments.append({"idx": idx, "title": seg.get("title"), "start": round(start, 3), "end": round(end, 3), "score": score})
    logger.info("Adjusted segment %s: start=%s end=%s score=%s", idx, start, end, score)

    # Persist adjusted segments so downstream tools see the final timings
    write_processed_segments([{"title": s["title"], "start": s["start"], "end": s["end"]} for s in adjusted_segments], proc_path)

    # Build SRTs for adjusted segments (build_srts uses start/end to produce relative SRT cue times)
    build_srts([{"title": s["title"], "start": s["start"], "end": s["end"]} for s in adjusted_segments], words, srt_dir)

    # Now run ffmpeg cut + captioning per adjusted segment
    scored_segments = []
    for s in adjusted_segments:
        idx = s["idx"]
        title = safe_name(s["title"])
        raw_out = seg_dir / f"segment_{idx}_{title}.mp4"
        sub_out = seg_dir / f"segment_{idx}_{title}_subtitled.mp4"
        srt = srt_dir / f"segment_{idx}.srt"

        # perform the cut
        logger.info("Cutting segment %s -> %s (%.3f-%.3f)", idx, raw_out, float(s['start']), float(s['end']))
        try:
            ffmpeg_cut(REPO / "input.mp4", float(s["start"]), float(s["end"]), raw_out)
        except Exception:
            logger.exception("ffmpeg_cut failed for segment %s", idx)
            raise

        # Try to apply captions through VideoProcessor so UI choices map directly
        try:
            # Resolve font path: prefer repo fonts/ and ui/fonts/ if present
            font_path = font_name or "Bangers-Regular.ttf"
            if isinstance(font_path, str) and font_path in FONTS_MAP:
                font_path = FONTS_MAP.get(font_path)
            else:
                maybe = REPO / "fonts" / font_path
                if maybe.exists():
                    font_path = str(maybe)
                else:
                    maybe2 = REPO / "ui" / "fonts" / font_path
                    if maybe2.exists():
                        font_path = str(maybe2)

            # Normalize numeric and color inputs
            try:
                f_size = int(font_size)
            except Exception:
                f_size = 60
            try:
                s_w = int(outline_w)
            except Exception:
                s_w = 3
            f_primary = primary_hex or "#FFFFFF"
            f_outline = outline_hex or "#000000"

            from clipify.video.processor import VideoProcessor

            # Map subtitle style to VideoProcessor options
            # For primary captioning we only have coarse positions; map precise % roughly.
            coarse_position = position
            if position == "bottom" and vertical_offset < 50:
                coarse_position = "center"
            elif position == "top" and vertical_offset > 50:
                coarse_position = "center"

            caption_opts = {
                "font": font_path,
                "font_size": f_size,
                "font_color": f_primary,
                "stroke_width": s_w if subtitle_style == "Outline" else 0,
                "stroke_color": f_outline,
                "position": coarse_position,
                "padding": 50,
                "words_per_caption": int(words_per_caption),
            }

            logger.info("Attempting primary captioning for segment %s via VideoProcessor", idx)
            vp = VideoProcessor(**caption_opts)
            # Convert the SRT we generated for this segment into captacity segments
            captacity_segments = _srt_to_captacity_segments(srt)
            ok = vp.process_video(str(raw_out), str(sub_out), custom_segments=captacity_segments)
            if not ok:
                logger.warning("VideoProcessor reported failure for %s, falling back to ffmpeg ASS burn", raw_out)
                raise RuntimeError("VideoProcessor failed to burn captions")
            logger.info("Primary captioning succeeded for segment %s -> %s", idx, sub_out)
            # Re-inject original audio because some captioning tools drop it
            if _remux_audio(raw_out, sub_out):
                logger.info("Audio remuxed into %s", sub_out)
            else:
                logger.warning("Could not remux audio into %s", sub_out)
        except Exception:
            # Fallback to ffmpeg burning (ASS style)
            logger.exception("Primary captioning failed for segment %s, using ffmpeg ASS fallback", idx)
            try:
                from pathlib import Path as _P
                if isinstance(font_path, str):
                    font_for_ass = _P(font_path).stem
                else:
                    font_for_ass = str(font_name)
            except Exception:
                font_for_ass = str(font_name)

            style = {
                "FontName": font_for_ass,
                "FontSize": int(f_size),
                "PrimaryColour": css_hex_to_ass(f_primary),
                "OutlineColour": css_hex_to_ass(f_outline),
                "Outline": int(s_w),
                "BorderStyle": 3,
            }
            alignment, margin_v = _position_to_ass_alignment(position, int(vertical_offset), horizontal_align)
            style["Alignment"] = alignment
            style["MarginV"] = margin_v
            logger.info("Calling ffmpeg_burn_subs for segment %s with style %s", idx, {k: style[k] for k in ('FontName','FontSize','Alignment','MarginV')})
            try:
                ffmpeg_burn_subs(raw_out, srt, sub_out, aspect=aspect, style=style)
            except Exception:
                logger.exception("ffmpeg_burn_subs failed for segment %s", idx)
                raise

        outputs.append(str(sub_out))
        scored_segments.append({"idx": s["idx"], "title": s["title"], "score": s["score"], "path": str(sub_out)})

    # Build a status summary with scores
    status_lines = [f"Done! Generated {len(outputs)} clips."]
    for s in scored_segments:
        status_lines.append(f"#{s['idx']}: {s['title'][:60]} — score {s['score']}")
    status = "\n".join(status_lines)
    logger.info("Generation complete: %s", status.replace('\n', ' | '))
    return status, (outputs[0] if outputs else None), outputs

def _position_to_ass_alignment(position: str, vertical_offset: int, horizontal_align: str) -> tuple:
    """Map UI position controls to ASS Alignment value and MarginV.

    ASS Alignment values:
      1=bottom-left, 2=bottom-center, 3=bottom-right
      4=middle-left, 5=middle-center, 6=middle-right
      7=top-left,    8=top-center,    9=top-right
    """
    # Vertical zone from position/offset
    if position == "top" or vertical_offset <= 33:
        row = 7  # top
    elif position == "bottom" or vertical_offset >= 66:
        row = 1  # bottom
    else:
        row = 4  # middle

    # Horizontal alignment
    if horizontal_align == "left":
        col = 0
    elif horizontal_align == "right":
        col = 2
    else:
        col = 1

    alignment = row + col
    # MarginV as percentage of 1080p height (common short-form canvas)
    margin_v = int((vertical_offset / 100.0) * 1080)
    return alignment, margin_v

with gr.Blocks(title="Clipify — AI Highlights") as demo:
    gr.Markdown("## Clipify — AI Highlights (Gemini)")

    with gr.Row():
        with gr.Column(scale=1):
            video_in = gr.File(label="Upload video", file_types=[".mp4", ".mov", ".m4v"])

            # AI Provider selection and keys
            ai_provider_name = gr.Radio(["gemini", "openai"], value=os.getenv("AI_PROVIDER", "gemini"), label="AI Provider")
            gemini_api_key = gr.Textbox(value=os.getenv("GOOGLE_API_KEY", ""), label="Gemini API Key (optional)", type="password")
            openai_api_key = gr.Textbox(value=os.getenv("OPENAI_API_KEY", ""), label="OpenAI API Key (optional)", type="password")
            openai_model = gr.Dropdown(["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"], value=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'), label="OpenAI Model")

            clips      = gr.Slider(3, 16, value=3, step=1, label="How many clips")
            min_words  = gr.Slider(5, 20, value=8, step=1, label="Min words per excerpt")
            max_words  = gr.Slider(12, 40, value=18, step=1, label="Max words per excerpt")
            pre_pad    = gr.Slider(0.0, 5.0, value=0.5, step=0.1, label="Pre-pad (seconds)")
            post_pad   = gr.Slider(0.0, 5.0, value=1.0, step=0.1, label="Post-pad (seconds)")
            min_duration = gr.Slider(2.0, 30.0, value=15.0, step=0.5, label="Min clip duration (s)")
            
            auto_suggest_btn = gr.Button("✨ Auto-suggest params", size="sm")
            
            model = gr.Dropdown(
                ["gemini-2.5-flash", "gemini-2.5-pro"],
                value=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
                label="Gemini Model"
            )
            fuzzy      = gr.Checkbox(value=True, label="Use fuzzy aligner")

            from ui.style_preview import StylePreview
            style_preview = StylePreview(FONTS_MAP, FONTS_DEFAULT)
            
            gr.Markdown("### Subtitle Style")
            with gr.Group():
                with gr.Row():
                    with gr.Column():
                        font_name = gr.Dropdown(
                            FONTS_LIST or [FONTS_DEFAULT],
                            value=FONTS_DEFAULT,
                            label="Font Family"
                        )
                        font_size = gr.Slider(6, 120, value=48, step=1, label="Font Size")
                        words_per_caption = gr.Slider(1, 10, value=3, step=1, label="Words per caption")
                        primary_hex = gr.ColorPicker(value="#FFFFFF", label="Font Color")
                    with gr.Column():
                        subtitle_style = gr.Radio(
                            ["Box", "Outline", "None"],
                            value="Box",
                            label="Subtitle Style"
                        )
                        outline_w = gr.Slider(0, 12, value=3, step=1, label="Outline/Box Width",
                                            visible=True)
                        outline_hex = gr.ColorPicker(value="#000000", label="Outline/Box Color",
                                               visible=True)
                
                with gr.Row():
                    position = gr.Radio(
                        ["bottom", "center", "top"],
                        value="bottom",
                        label="Position"
                    )
                    aspect = gr.Radio(
                        ["source", "9:16", "4:5", "1:1"],
                        value="source",
                        label="Aspect Ratio"
                    )
                
                with gr.Row():
                    vertical_offset = gr.Slider(
                        0, 100, value=85, step=1,
                        label="Vertical offset (% from top)"
                    )
                    horizontal_align = gr.Radio(
                        ["left", "center", "right"],
                        value="center",
                        label="Horizontal alignment"
                    )
                
                # Get fonts
                fonts_list, fonts_map, fonts_meta = _gather_fonts(REPO)
                default_font = next(iter(fonts_list))
                
                # Preview area
                preview_image = gr.Image(
                    label="Style Preview",
                    height=150
                )
                
                # Initialize StylePreview (avoid name collision with Gradio `preview` component)
                style_preview_instance = StylePreview(fonts_map=fonts_map, fonts_default=default_font)
                
                # Update preview when settings change
                style_inputs = [font_name, font_size, primary_hex, outline_w,
                              outline_hex, subtitle_style]
                
                preview = StylePreview(fonts_map=fonts_map, fonts_default=default_font)
                
                def update_preview(f, s, p, w, o, st):
                    try:
                        if not all([f, s, p]):
                            return None

                        # Normalize color inputs: accept '#RRGGBB', 'rgb(...)', 'rgba(...)' or tuples
                        def normalize_color(col):
                            if not col:
                                return "#FFFFFF"
                            if isinstance(col, (list, tuple)) and len(col) >= 3:
                                r, g, b = int(col[0]), int(col[1]), int(col[2])
                                return f"#{r:02X}{g:02X}{b:02X}"
                            if isinstance(col, str):
                                c = col.strip()
                                # hex already
                                if c.startswith('#') and (len(c) == 7 or len(c) == 4):
                                    # Expand short hex like #abc
                                    if len(c) == 4:
                                        r, g, b = c[1], c[2], c[3]
                                        return f"#{r}{r}{g}{g}{b}{b}".upper()
                                    return c.upper()
                                # rgb/rgba formats
                                if c.startswith('rgba') or c.startswith('rgb'):
                                    import re
                                    m = re.search(r"([\d\.]+)\s*,\s*([\d\.]+)\s*,\s*([\d\.]+)", c)
                                    if m:
                                        r = int(round(float(m.group(1))))
                                        g = int(round(float(m.group(2))))
                                        b = int(round(float(m.group(3))))
                                        return f"#{r:02X}{g:02X}{b:02X}"
                            # fallback
                            return "#FFFFFF"

                        primary = normalize_color(p)
                        outline = normalize_color(o) if o else "#000000"

                        return style_preview_instance.update_subtitle_preview(
                            font_name=f,
                            font_size=int(s) if s else 48,
                            primary_hex=primary,
                            outline_w=float(w) if w else 0,
                            outline_hex=outline,
                            subtitle_style=st
                        )
                    except Exception as e:
                        print(f"Error generating preview: {e}")
                        return None
                
                for input_elem in style_inputs:
                    input_elem.change(
                        fn=update_preview,
                        inputs=style_inputs,
                        outputs=[preview_image]
                    )

                
                # Update control visibility based on style
                subtitle_style.change(
                    fn=style_preview_instance.update_style_controls,
                    inputs=[subtitle_style],
                    outputs=[outline_w, outline_hex]
                )
                


            
            auto_size = gr.Checkbox(value=True, label="Auto-size clips by video length")

            run = gr.Button("Generate")

        with gr.Column(scale=2):
            status = gr.Textbox(label="Status")
            preview = gr.Video(label="Preview (first clip)")
            files = gr.Files(label="All output clips")
            preview_table = gr.JSON(label="Computed segments (start/end/score)")

            # Toggle visibility of API key fields based on selected provider
            def _provider_visibility(provider):
                if (provider or "").lower() == "gemini":
                    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
                else:
                    return gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)

            ai_provider_name.change(_provider_visibility, inputs=[ai_provider_name], outputs=[gemini_api_key, openai_api_key, openai_model])

            # Auto-suggest parameters based on uploaded video
            def auto_suggest(video_file):
                if not video_file:
                    return [gr.update()] * 6
                try:
                    src = Path(video_file)
                    tjson = ensure_transcripts(REPO, src)
                    _, words = read_timings(tjson)
                    duration = get_video_duration(REPO / "input.mp4")
                    p = _suggest_params(duration, len(words))
                    return [
                        gr.update(value=p["clips"]),
                        gr.update(value=p["min_words"]),
                        gr.update(value=p["max_words"]),
                        gr.update(value=p["pre_pad"]),
                        gr.update(value=p["post_pad"]),
                        gr.update(value=p["min_duration"]),
                    ]
                except Exception as e:
                    logger.warning("Auto-suggest failed: %s", e)
                    return [gr.update()] * 6

            auto_suggest_btn.click(
                auto_suggest,
                inputs=[video_in],
                outputs=[clips, min_words, max_words, pre_pad, post_pad, min_duration]
            )
            # Also trigger when a video is uploaded
            video_in.change(
                auto_suggest,
                inputs=[video_in],
                outputs=[clips, min_words, max_words, pre_pad, post_pad, min_duration]
            )

            # Two-step process: preview first, then generate
            def preview_clicked(video_file, clips, min_words, max_words, model, openai_model, fuzzy,
                           pre_pad, post_pad, min_duration, auto_size):
                preview_result = preview_segments(video_file, clips, min_words, max_words, model, openai_model, fuzzy,
                                               pre_pad, post_pad, min_duration, auto_size)

                # Error handling: return status text and keep Generate hidden
                if isinstance(preview_result, dict) and "error" in preview_result:
                    return f"Error: {preview_result['error']}", None, gr.update(visible=False)

                # If preview_result is a plain string, show it as status
                if isinstance(preview_result, str):
                    return preview_result, None, gr.update(visible=False)

                # If preview_result is a dict with computed values, show preview and enable Generate
                preview_clip = None
                preview_files = None
                preview_table_data = None
                if isinstance(preview_result, dict):
                    preview_clip = preview_result.get('preview_clip') if preview_result.get('preview_clip') and os.path.isfile(preview_result.get('preview_clip')) else None
                    preview_files = [f for f in preview_result.get('files', []) if os.path.isfile(f)]
                    preview_table_data = preview_result.get('segments')

                status_text = f"Preview ready — {len(preview_table_data) if preview_table_data else (len(preview_files) if preview_files else 0)} segments"
                return status_text, preview_clip, gr.update(visible=True)
                
            # Separate generate function that uses the last preview results
            def generate_clicked(video_file, clips, min_words, max_words, model, openai_model, fuzzy,
                            font_name, font_size, primary_hex, outline_w, outline_hex, subtitle_style, position, aspect,
                            ai_provider_name, gemini_api_key, openai_api_key,
                            pre_pad, post_pad, min_duration, auto_size,
                            words_per_caption, vertical_offset, horizontal_align):
                return run_pipeline(video_file, clips, min_words, max_words, model, openai_model, fuzzy,
                                font_name, font_size, primary_hex, outline_w, outline_hex, subtitle_style, position, aspect,
                                ai_provider_name, gemini_api_key, openai_api_key,
                                pre_pad, post_pad, min_duration, auto_size,
                                words_per_caption, vertical_offset, horizontal_align)
            
            preview_btn = gr.Button("Preview")
            generate_btn = gr.Button("Generate", visible=False)
            
            preview_btn.click(
                preview_clicked,
                inputs=[video_in, clips, min_words, max_words, model, openai_model, fuzzy,
                        pre_pad, post_pad, min_duration, auto_size],
                outputs=[status, preview, generate_btn]
            )
            
            generate_btn.click(
                generate_clicked,
                inputs=[video_in, clips, min_words, max_words, model, openai_model, fuzzy,
                    font_name, font_size, primary_hex, outline_w, outline_hex, subtitle_style, position, aspect,
                    ai_provider_name, gemini_api_key, openai_api_key,
                    pre_pad, post_pad, min_duration, auto_size,
                    words_per_caption, vertical_offset, horizontal_align],
                outputs=[status, preview, files]
            )

            # Preview button: compute segments and scores without running ffmpeg
            def preview_segments(video_file, clips, min_words, max_words, model, openai_model, fuzzy,
                                 pre_pad, post_pad, min_duration, auto_size):
                if not video_file:
                    return {"error": "No video provided"}
                # Reuse pipeline logic but avoid heavy processing: call into call_gemini and alignment
                try:
                    src = Path(video_file)
                    tjson = ensure_transcripts(REPO, src)
                    transcript, words = read_timings(tjson)
                except Exception as e:
                    return {"error": f"Transcription error: {e}"}

                highs = call_gemini(transcript, clips=int(clips), min_words=int(min_words), max_words=int(max_words), model=model)
                tokens = tokens_from_words(words)
                total_duration = get_video_duration(REPO / "input.mp4")
                out = []
                for idx, h in enumerate((highs.get('highlights', highs) if isinstance(highs, dict) else highs), start=1):
                    hit = align_excerpt_exact_or_fuzzy((h.get("excerpt") if isinstance(h, dict) else str(h)), tokens, use_fuzzy=bool(fuzzy))
                    if not hit:
                        continue
                    # interpret hit as seq or pair
                    s = e = None
                    try:
                        seq = list(hit) if not isinstance(hit, (str, bytes)) else None
                    except Exception:
                        seq = None
                    if seq and len(seq) >= 2:
                        s, e = seq[-2], seq[-1]
                    else:
                        try:
                            s, e = hit
                        except Exception:
                            continue

                    # apply auto_size/pad/min rules (same as pipeline)
                    pad_pre = float(pre_pad)
                    pad_post = float(post_pad)
                    min_dur = float(min_duration)
                    try:
                        if bool(auto_size):
                            if total_duration <= 60:
                                pad_pre = max(0.2, pad_pre * 0.5)
                                pad_post = max(0.5, pad_post * 0.75)
                                min_dur = max(6.0, min_dur * 0.8)
                            elif total_duration <= 300:
                                pad_pre = max(0.5, pad_pre)
                                pad_post = max(1.0, pad_post)
                                min_dur = max(8.0, min_dur)
                            else:
                                pad_pre = max(1.0, pad_pre * 1.5)
                                pad_post = max(2.0, pad_post * 1.5)
                                min_dur = max(10.0, min_dur * 1.25)
                    except Exception:
                        pass

                    start = max(0.0, float(s) - pad_pre)
                    end = float(e) + pad_post
                    if end - start < min_dur:
                        mid = (float(s) + float(e)) / 2.0
                        half = min_dur / 2.0
                        start = max(0.0, mid - half)
                        end = mid + half

                    score = _score_excerpt(h.get('title') if isinstance(h, dict) else str(h), s, e, total_duration, int(min_words), int(max_words))
                    out.append({"idx": idx, "title": (h.get('title') if isinstance(h, dict) else str(h))[:80], "start": round(start,3), "end": round(end,3), "score": score})

                return out

            preview_btn = gr.Button("Preview segments")
            preview_btn.click(preview_segments, inputs=[video_in, clips, min_words, max_words, model, openai_model, fuzzy,
                                                        pre_pad, post_pad, min_duration, auto_size], outputs=[preview_table])

if __name__ == "__main__":
    # Allow Gradio to serve files created in these output directories
    allowed = [
        str(REPO / "segmented_videos" / "input"),
        str(REPO / "segmented_videos" / "input" / "srt"),
        str(REPO / "processed_content")
    ]
    demo.launch(server_name="127.0.0.1", server_port=7860, allowed_paths=allowed)
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

def run_pipeline(video_file, clips, min_words, max_words, model, fuzzy,
                 font_name, font_size, primary_hex, outline_w, outline_hex, position, aspect):

    if not os.getenv("GOOGLE_API_KEY"):
        return "Missing GOOGLE_API_KEY in .env", None, []

    if video_file is None:
        return "Please upload a video.", None, []

    src = Path(video_file)
    try:
        tjson = ensure_transcripts(REPO, src)
        transcript, words = read_timings(tjson)
    except Exception as e:
        return f"Transcription error: {e}", None, []

    highs = call_gemini(
        transcript,
        clips=int(clips),
        min_words=int(min_words),
        max_words=int(max_words),
        model=model,
        api_key=os.getenv("GOOGLE_API_KEY")
    )

    tokens = tokens_from_words(words)
    segments = []
    for h in (highs.get('highlights', highs) if isinstance(highs, dict) else highs):
        hit = align_excerpt_exact_or_fuzzy((h.get("excerpt") if isinstance(h, dict) else str(h)), tokens, use_fuzzy=bool(fuzzy))
        if not hit:
            continue
        _, _, s, e = hit
        segments.append({"title": (h.get("title") if isinstance(h, dict) else str(h)[:80])[:80], "start": round(s,3), "end": round(e,3)})

    if not segments:
        return "No highlights could be aligned. Try enabling fuzzy or adjusting min/max words.", None, []

    proc_path = REPO / "processed_content" / "input_processed.json"
    write_processed_segments(proc_path, [
        type("S", (), seg) for seg in segments  # quick dataclass-like shim
    ])

    srt_dir = REPO / "segmented_videos" / "input" / "srt"
    build_srts(proc_path, tjson, srt_dir, words)

    seg_dir = REPO / "segmented_videos" / "input"
    seg_dir.mkdir(parents=True, exist_ok=True)

    outputs = []
    for idx, seg in enumerate(segments, start=1):
        title = safe_name(seg["title"])
        raw_out = seg_dir / f"segment_{idx}_{title}.mp4"
        sub_out = seg_dir / f"segment_{idx}_{title}_subtitled.mp4"
        srt = srt_dir / f"segment_{idx}.srt"
        ffmpeg_cut(REPO / "input.mp4", seg["start"], seg["end"], raw_out)

        style = {
            "FontName": font_name,
            "FontSize": font_size,
            "PrimaryColour": css_hex_to_ass(primary_hex),
            "OutlineColour": css_hex_to_ass(outline_hex),
            "Outline": outline_w,
            "BorderStyle": 3,
            "Alignment": 2 if position == "bottom" else 8
        }
        ffmpeg_burn_subs(raw_out, srt, sub_out, aspect=aspect, style=style)
        outputs.append(str(sub_out))

    return "Done!", (outputs[0] if outputs else None), outputs

with gr.Blocks(title="Clipify — AI Highlights") as demo:
    gr.Markdown("## Clipify — AI Highlights (Gemini)")

    with gr.Row():
        with gr.Column(scale=1):
            video_in = gr.File(label="Upload video", file_types=[".mp4", ".mov", ".m4v"])

            clips      = gr.Slider(3, 16, value=6, step=1, label="How many clips")
            min_words  = gr.Slider(5, 20, value=8, step=1, label="Min words per excerpt")
            max_words  = gr.Slider(12, 40, value=18, step=1, label="Max words per excerpt")
            model = gr.Dropdown(
                ["gemini-2.5-flash", "gemini-2.5-pro"],
                value=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
                label="Model"
            )
            fuzzy      = gr.Checkbox(value=True, label="Use fuzzy aligner")

            font_name  = gr.Textbox(value="Arial", label="Font name")
            font_size  = gr.Slider(24, 72, value=48, step=1, label="Font size")
            primary    = gr.ColorPicker(value="#FFFFFF", label="Font color")
            outline_w  = gr.Slider(0, 6, value=3, step=1, label="Outline width")
            outline_c  = gr.ColorPicker(value="#000000", label="Outline color")
            position   = gr.Dropdown(["bottom","top"], value="bottom", label="Position")
            aspect     = gr.Dropdown(["source","9:16","4:5","1:1"], value="source", label="Aspect (letterbox)")

            run = gr.Button("Generate clips")

        with gr.Column(scale=2):
            status = gr.Textbox(label="Status")
            preview = gr.Video(label="Preview (first clip)")
            files = gr.Files(label="All output clips")

    run.click(
        run_pipeline,
        inputs=[video_in, clips, min_words, max_words, model, fuzzy,
                font_name, font_size, primary, outline_w, outline_c, position, aspect],
        outputs=[status, preview, files]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
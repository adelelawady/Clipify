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

def run_pipeline(video_file, clips, min_words, max_words, model, openai_model, fuzzy,
                 font_name, font_size, primary_hex, outline_w, outline_hex, position, aspect,
                 ai_provider_name, gemini_api_key, openai_api_key):

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

    tokens = tokens_from_words(words)
    segments = []
    for h in (highs.get('highlights', highs) if isinstance(highs, dict) else highs):
        hit = align_excerpt_exact_or_fuzzy((h.get("excerpt") if isinstance(h, dict) else str(h)), tokens, use_fuzzy=bool(fuzzy))
        if not hit:
            continue
        # Support either legacy hits of shape (a,b,s,e) or current (s,e).
        try:
            # Most callers now return (s, e)
            s, e = hit
        except Exception:
            try:
                # Legacy shape: (_, _, s, e)
                _, _, s, e = hit
            except Exception:
                # Last resort: try to pull last two items
                try:
                    s, e = hit[-2], hit[-1]
                except Exception:
                    # Skip if we can't interpret hit
                    continue
        segments.append({"title": (h.get("title") if isinstance(h, dict) else str(h)[:80])[:80], "start": round(float(s),3), "end": round(float(e),3)})

    if not segments:
        return "No highlights could be aligned. Try enabling fuzzy or adjusting min/max words.", None, []

    proc_path = REPO / "processed_content" / "input_processed.json"
    # Persist segments (segments list first, out_path second)
    write_processed_segments([
        type("S", (), seg) for seg in segments  # quick dataclass-like shim
    ], proc_path)

    srt_dir = REPO / "segmented_videos" / "input" / "srt"
    # build_srts expects (segments, word_timings, out_dir)
    build_srts(segments, words, srt_dir)

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

            # AI Provider selection and keys
            ai_provider_name = gr.Radio(["gemini", "openai"], value=os.getenv("AI_PROVIDER", "gemini"), label="AI Provider")
            gemini_api_key = gr.Textbox(value=os.getenv("GOOGLE_API_KEY", ""), label="Gemini API Key (optional)", type="password")
            openai_api_key = gr.Textbox(value=os.getenv("OPENAI_API_KEY", ""), label="OpenAI API Key (optional)", type="password")
            openai_model = gr.Dropdown(["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"], value=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'), label="OpenAI Model")

            clips      = gr.Slider(3, 16, value=6, step=1, label="How many clips")
            min_words  = gr.Slider(5, 20, value=8, step=1, label="Min words per excerpt")
            max_words  = gr.Slider(12, 40, value=18, step=1, label="Max words per excerpt")
            model = gr.Dropdown(
                ["gemini-2.5-flash", "gemini-2.5-pro"],
                value=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
                label="Gemini Model"
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

            # Toggle visibility of API key fields based on selected provider
            def _provider_visibility(provider):
                if (provider or "").lower() == "gemini":
                    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
                else:
                    return gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)

            ai_provider_name.change(_provider_visibility, inputs=[ai_provider_name], outputs=[gemini_api_key, openai_api_key, openai_model])

            run.click(
        run_pipeline,
        inputs=[video_in, clips, min_words, max_words, model, openai_model, fuzzy,
                font_name, font_size, primary, outline_w, outline_c, position, aspect,
                ai_provider_name, gemini_api_key, openai_api_key],
        outputs=[status, preview, files]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
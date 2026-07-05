import os
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[1]

def test_preview_segments_returns_list():
    """Call the preview_segments helper and assert it returns a list of segments."""
    # Import inside test to avoid importing Gradio server
    from ui.app_gradio import preview_segments

    video = REPO / "input.mp4"
    assert video.exists(), "input.mp4 is required for this test"

    res = preview_segments(str(video), clips=4, min_words=5, max_words=20, model=None, openai_model=None, fuzzy=False,
                           pre_pad=0.5, post_pad=0.5, min_duration=6, auto_size=True)

    assert isinstance(res, list), f"Expected list from preview_segments, got {type(res)}"
    if res:
        first = res[0]
        assert "start" in first and "end" in first and "title" in first

def test_ffmpeg_burn_fallback_for_first_segment():
    """If preview produces segments and SRT exists, try burning the first segment's SRT into a copy of the mobile file."""
    from ui.app_gradio import preview_segments
    from clipify.pipelines.ui_helpers import ffmpeg_burn_subs

    video = REPO / "input.mp4"
    res = preview_segments(str(video), clips=4, min_words=5, max_words=20, model=None, openai_model=None, fuzzy=False,
                           pre_pad=0.5, post_pad=0.5, min_duration=6, auto_size=True)
    if not res:
        pytest.skip("No segments from preview; skipping burn-in test")

    first = res[0]
    seg_dir = REPO / "segmented_videos" / "input"
    srt = seg_dir / "srt" / "segment_1.srt"
    mobile = seg_dir / "segment_1_Quando nós vamos lendo essas cartas ao qual_mobile.mp4"
    out = REPO / "processed_videos" / "input" / "test_burn.mp4"

    if not srt.exists() or not mobile.exists():
        pytest.skip("SRT or mobile segment missing; skipping burn-in test")

    ffmpeg_burn_subs(mobile, srt, out, aspect="9:16", style={})
    assert out.exists(), "ffmpeg burn-in output not created"

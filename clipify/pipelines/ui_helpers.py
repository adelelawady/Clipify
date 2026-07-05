import json, subprocess, shlex, os, pathlib, shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any

def _extract_audio(input_video: Path, output_wav: Path):
    """Extract mono 16kHz WAV audio from a video file using ffmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_video),
        "-ar", "16000", "-ac", "1",
        "-c:a", "pcm_s16le",
        str(output_wav)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _transcribe_video(input_video: Path, tjson: Path):
    """Transcribe a video with OpenAI Whisper and save word timings as JSON."""
    import tempfile
    import whisper

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = Path(tmp.name)

    try:
        _extract_audio(input_video, wav_path)
        model = whisper.load_model("base")
        result = model.transcribe(str(wav_path), word_timestamps=True)

        word_timings = []
        for seg in result.get("segments", []):
            for w in seg.get("words", []):
                txt = str(w.get("word", "")).strip()
                if txt:
                    word_timings.append({
                        "text": txt,
                        "start": float(w.get("start", 0)),
                        "end": float(w.get("end", 0)),
                    })

        data = {
            "transcript": result.get("text", "").strip(),
            "word_timings": word_timings,
        }
        tjson.parent.mkdir(parents=True, exist_ok=True)
        tjson.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    finally:
        if wav_path.exists():
            wav_path.unlink()


def ensure_transcripts(repo_root: Path, input_video: Path) -> Path:
    tjson = repo_root / "transcripts" / "input_timings.json"
    if tjson.exists():
        return tjson
    # Make sure the video is available at the expected path
    target = repo_root / "input.mp4"
    if input_video.resolve() != target.resolve():
        shutil.copy2(str(input_video), str(target))
    # Run transcription directly via Whisper
    _transcribe_video(target, tjson)
    if not tjson.exists():
        raise RuntimeError("Transcription failed: transcripts/input_timings.json not created.")
    return tjson

def safe_name(s: str) -> str:
    bad = '\\/:*?"<>|'
    for c in bad:
        s = s.replace(c, "-")
    return s[:120].strip()

def ffmpeg_cut(input_video: Path, start: float, end: float, out_path: Path):
    dur = max(0.01, end - start)
    cmd = [
        "ffmpeg","-y",
        "-ss", str(start), "-t", str(dur),
        "-i", str(input_video),
        "-map","0:v:0","-map","0:a:0?",
        "-c:v","libx264","-crf","18","-preset","medium",
        "-c:a","aac","-b:a","192k","-movflags","+faststart",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)

from .ass_style import validate_subtitle_style, ass_force_style

def ffmpeg_burn_subs(raw_clip: Path, srt: Path, out_path: Path, aspect: str = "source", style: Dict[str,Any] = None):
    from .srt_validator import validate_srt_timings
    import subprocess
    
    # Get clip duration using ffprobe
    duration_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(raw_clip)
    ]
    try:
        duration = float(subprocess.check_output(duration_cmd).decode().strip())
        # Validate and adjust SRT timings if needed
        validate_srt_timings(srt, duration)
    except (subprocess.CalledProcessError, ValueError):
        print(f"Warning: Could not validate SRT timings for {srt}")
    
    vf = []
    if aspect in ("9:16","4:5","1:1"):
        targets = {"9:16": (1080,1920), "4:5": (1080,1350), "1:1": (1080,1080)}
        W,H = targets[aspect]
        vf.append(f"scale=w={W}:h={H}:force_original_aspect_ratio=decrease")
        vf.append(f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2")
    
    # Validate and apply subtitle style settings
    validated_style = validate_subtitle_style(style or {})
    sub = f"subtitles='{srt.as_posix()}':"
    sub += f"force_style='{ass_force_style(validated_style)}'"
    vf.append(sub)
    cmd = [
        "ffmpeg","-y","-i", str(raw_clip),
        "-vf", ",".join(vf),
        "-map","0:v:0","-map","0:a:0?",
        "-c:v","libx264","-crf","18","-preset","medium",
        "-c:a","aac","-b:a","160k","-movflags","+faststart","-shortest",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)

def css_hex_to_ass(h: str) -> str:
    """Convert CSS hex color to ASS format."""
    h = h.lstrip("#")
    if not h or len(h) != 6:
        return "&H00FFFFFF"  # Default to white if invalid
    try:
        r, g, b = h[0:2], h[2:4], h[4:6]
        # Validate hex values
        int(r, 16); int(g, 16); int(b, 16)
        return f"&H00{b.upper()}{g.upper()}{r.upper()}"
    except ValueError:
        return "&H00FFFFFF"  # Default to white if invalid hex

def validate_font_style(style: Dict[str, str]) -> Dict[str, str]:
    """Validate and normalize font style settings."""
    if not isinstance(style, dict):
        return {}
        
    validated = {}
    
    # Font size validation
    if "FontSize" in style:
        try:
            size = int(style["FontSize"])
            validated["FontSize"] = str(max(1, min(size, 100)))  # Clamp between 1-100
        except (ValueError, TypeError):
            validated["FontSize"] = "40"  # Default size
            
    # Color validation
    for color_key in ["PrimaryColour", "OutlineColour"]:
        if color_key in style:
            validated[color_key] = css_hex_to_ass(style[color_key])
            
    # Outline width validation
    if "Outline" in style:
        try:
            width = int(style["Outline"])
            validated["Outline"] = str(max(0, min(width, 4)))  # Clamp between 0-4
        except (ValueError, TypeError):
            validated["Outline"] = "2"  # Default outline width
            
    # Border style (3 = opaque box, 1 = outline)
    if "BorderStyle" in style:
        validated["BorderStyle"] = "3" if style["BorderStyle"] == 3 else "1"
        
    # Alignment (2 = bottom, 8 = top)
    if "Alignment" in style:
        validated["Alignment"] = style["Alignment"] if style["Alignment"] in [2, 8] else "2"
        
    return validated

import json, subprocess, shlex, os, pathlib, shutil
from pathlib import Path
from typing import Dict, List, Tuple

def ensure_transcripts(repo_root: Path, input_video: Path) -> Path:
    tjson = repo_root / "transcripts" / "input_timings.json"
    if tjson.exists():
        return tjson
    # Make example.py look at "input.mp4"
    target = repo_root / "input.mp4"
    if input_video.resolve() != target.resolve():
        shutil.copy2(str(input_video), str(target))
    # Run transcription via example.py (uses whisper+ffmpeg already wired)
    cmd = ["python", "example.py"]
    subprocess.run(cmd, cwd=str(repo_root), check=True)
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

def ass_force_style(style: Dict[str,str]) -> str:
    return ",".join(f"{k}={v}" for k,v in style.items())

def ffmpeg_burn_subs(raw_clip: Path, srt: Path, out_path: Path, aspect: str = "source", style: Dict[str,str] = None):
    vf = []
    if aspect in ("9:16","4:5","1:1"):
        targets = {"9:16": (1080,1920), "4:5": (1080,1350), "1:1": (1080,1080)}
        W,H = targets[aspect]
        vf.append(f"scale=w={W}:h={H}:force_original_aspect_ratio=decrease")
        vf.append(f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2")
    sub = f"subtitles='{srt.as_posix()}'"
    if style:
        sub += f":force_style='{ass_force_style(style)}'"
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
    h = h.lstrip("#")
    if len(h) != 6:
        return "&H00FFFFFF"
    r=g=b=None
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H00{b.upper()}{g.upper()}{r.upper()}"

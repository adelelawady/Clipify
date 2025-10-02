# (file content starts)
import os, json, re, unicodedata, argparse, pathlib, subprocess, shlex, sys
from dataclasses import dataclass
from pathlib import Path as _P
from dotenv import load_dotenv as _load
ENV_PATH = (_P(__file__).resolve().parents[2] / '.env')
_load(dotenv_path=ENV_PATH, override=False)

from typing import List, Optional, Tuple

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from rapidfuzz import process as rf_process, fuzz as rf_fuzz  # noqa: F401
    HAVE_RAPIDFUZZ = True
except Exception:
    import difflib  # noqa: F401
    HAVE_RAPIDFUZZ = False

@dataclass
class Word:
    text: str
    start: float
    end: float

@dataclass
class Segment:
    title: str
    start: float
    end: float

def norm(s: str) -> str:
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"[\s]+", " ", s)
    return s.strip()

def read_timings(tim_path: pathlib.Path):
    data = json.loads(tim_path.read_text())
    transcript = data.get("transcript", "").strip()
    wt = data.get("word_timings") or []
    words = [Word(text=str(w["text"]), start=float(w["start"]), end=float(w["end"])) for w in wt]
    if not transcript or not words:
        raise ValueError(f"Need both 'transcript' and 'word_timings' in {tim_path}")
    return transcript, words


def _resolve_model(requested, api_key):
    import google.generativeai as genai, os
    genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
    wanted = (requested or "").replace("models/", "")
    # list all models that support generateContent
    available = []
    for m in genai.list_models():
        if "generateContent" in getattr(m, "supported_generation_methods", []):
            name = m.name.replace("models/","")
            available.append(name)
    if not available:
        return requested  # fallback
    # exact match?
    if wanted in available:
        return wanted
    # prefix match (e.g., "gemini-1.5-flash" -> "gemini-1.5-flash-001")
    for a in available:
        if a.startswith(wanted):
            return a
    # last resort: first flash-like or first available
    for a in available:
        if "flash" in a:
            return a
    return available[0]


def _extract_text_from_resp(resp):
    """
    Return plain text from a Gemini response.
    Falls back to concatenating content parts if .text is empty.
    """
    try:
        txt = (resp.text or "").strip()
        if txt:
            return txt
    except Exception:
        pass
    # Try to collect parts text
    try:
        for cand in getattr(resp, "candidates", []) or []:
            parts = getattr(getattr(cand, "content", None), "parts", []) or []
            buf = []
            for part in parts:
                # part.text on modern SDKs; fallback to .inline_data / .function_call if present
                t = getattr(part, "text", None)
                if t:
                    buf.append(t)
            if buf:
                return "\n".join(buf).strip()
    except Exception:
        pass
    return ""

def _raise_if_blocked(resp):
    # If the model blocked output, raise a readable error for the UI.
    try:
        for cand in getattr(resp, "candidates", []) or []:
            fr = getattr(cand, "finish_reason", None)
            # finish_reason enums: STOP=1, SAFETY=2 (varies by SDK), LENGTH=3, ...
            if fr is not None and int(fr) != 1:
                # collect safety labels if available
                ratings = getattr(cand, "safety_ratings", []) or []
                labels = [getattr(r, "category", "unknown") for r in ratings]
                raise ValueError(f"Gemini did not return usable text (finish_reason={fr}). Safety labels: {labels}")
    except Exception:
        # ignore introspection issues
        pass



def _extract_text_from_resp(resp):
    # Try quick accessor
    try:
        txt = (resp.text or "").strip()
        if txt:
            return txt
    except Exception:
        pass
    # Scan parts
    try:
        for cand in getattr(resp, "candidates", []) or []:
            content = getattr(cand, "content", None)
            parts = getattr(content, "parts", []) if content else []
            buf=[]
            for part in parts or []:
                t = getattr(part, "text", None)
                if t:
                    buf.append(t)
            if buf:
                return "\n".join(buf).strip()
    except Exception:
        pass
    return ""

def _is_blocked(resp):
    try:
        for cand in getattr(resp, "candidates", []) or []:
            fr = getattr(cand, "finish_reason", None)
            # STOP=1 on most SDKs
            if fr is None:
                continue
            if int(fr) != 1:
                return True
    except Exception:
        pass
    return False

def _summarize_resp_for_log(resp, limit=600):
    try:
        import json
        compact = {
            "candidates": [
                {
                    "finish_reason": getattr(c, "finish_reason", None),
                    "has_parts": bool(getattr(getattr(c, "content", None), "parts", []) or []),
                    "safety_ratings": [getattr(r, "category", "unknown") for r in getattr(c, "safety_ratings", []) or []],
                } for c in getattr(resp, "candidates", []) or []
            ]
        }
        s = json.dumps(compact)[:limit]
        return s
    except Exception:
        return "<unprintable response>"

def _fallback_highlights_from_text(full_text, k=6, min_words=8, max_words=24):
    import re
    # crude sentence split
    sents = re.split(r"(?<=[.!?])\s+", full_text.strip())
    hs=[]
    for s in sents:
        w = re.findall(r"\S+", s)
        if len(w) < min_words:
            continue
        if len(w) > max_words:
            s = " ".join(w[:max_words])
        title = (s[:60] + "…") if len(s) > 60 else s
        hs.append({"title": title or "Highlight", "excerpt": s})
        if len(hs) >= k:
            break
    # if nothing matched, take head of transcript
    if not hs and full_text:
        w = re.findall(r"\S+", full_text)
        chunk = " ".join(w[:max_words]) if len(w)>max_words else full_text
        hs = [{"title":"Highlight 1","excerpt":chunk}]
    return hs


SAFETY_NONE = [
    {"category":"HARM_CATEGORY_DANGEROUS","threshold":"BLOCK_NONE"},
    {"category":"HARM_CATEGORY_HARASSMENT","threshold":"BLOCK_NONE"},
    {"category":"HARM_CATEGORY_HATE_SPEECH","threshold":"BLOCK_NONE"},
    {"category":"HARM_CATEGORY_SEXUAL_CONTENT","threshold":"BLOCK_NONE"},
    {"category":"HARM_CATEGORY_VIOLENCE","threshold":"BLOCK_NONE"},
]



def call_gemini(full_text: str, *, clips: int, min_words: int, max_words: int, model: str, api_key: str):
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    gmodel = genai.GenerativeModel(model)
    prompt = f"""
You are a video editor assistant. Given a speech transcript, choose the {clips} most compelling, self-contained highlights that would make engaging short clips for social media.

Return ONLY valid JSON (no prose) with a list under key "highlights". Each highlight MUST have:
- "title": a short, catchy title (max 70 chars)
- "excerpt": a short exact excerpt (between {min_words} and {max_words} words) copied verbatim from the transcript that best represents the highlight.

JSON schema example:
{{"highlights":[{{"title":"...", "excerpt":"..."}}]}}

Transcript:
\"\"\"{full_text[:16000]}\"\"\"
""".strip()
    resp = gmodel.generate_content(
        prompt,
        generation_config={"temperature":0.4, "max_output_tokens": 1200},
        safety_settings=SAFETY_NONE
    )
    if _is_blocked(resp):
        # fallback instead of error
        return _fallback_highlights_from_text(full_text, k=clips, min_words=min_words, max_words=max_words)
    txt = _extract_text_from_resp(resp)
    if not txt:
        return _fallback_highlights_from_text(full_text, k=clips, min_words=min_words, max_words=max_words)
    try:
        obj = json.loads(txt)
    except Exception:
        m = re.search(r'\{.*\}', txt, flags=re.S)
        if not m:
            raise ValueError("Gemini did not return JSON.\nRaw:\n" + txt)
        obj = json.loads(m.group(0))
    highs = obj.get("highlights") or []
    cleaned = []
    for h in highs:
        title = (h.get("title") or "").strip()
        excerpt = (h.get("excerpt") or "").strip()
        if title and excerpt:
            cleaned.append({"title": title[:80], "excerpt": excerpt})
    return cleaned

def tokens_from_words(words: List[Word]):
    return [{"txt": w.text, "n": norm(w.text), "start": w.start, "end": w.end} for w in words]

def align_excerpt_exact_or_fuzzy(excerpt: str, tokens, *, use_fuzzy: bool):
    tgt = norm(excerpt)
    tgt_words = [p for p in tgt.split() if p]
    if len(tgt_words) < 3:
        return None
    norms = [t["n"] for t in tokens]
    min_len = min(5, len(tgt_words))
    max_len = min(12, len(tgt_words))
    for L in range(max_len, min_len-1, -1):
        for i in range(0, len(tgt_words) - L + 1):
            phrase = " ".join(tgt_words[i:i+L])
            buf = []
            for idx, w in enumerate(norms):
                buf.append(w)
                if len(buf) > L: buf.pop(0)
                if len(buf) == L and " ".join(buf) == phrase:
                    start_idx = idx - L + 1
                    end_idx = min(len(tokens)-1, idx + (len(tgt_words)-L) + 1)
                    s_time = tokens[start_idx]["start"]
                    e_time = tokens[end_idx]["end"]
                    if e_time > s_time:
                        return (start_idx, end_idx, s_time, e_time)
    if not use_fuzzy:
        return None
    # simple difflib-based rescue (best-effort)
    full_norm = " ".join(norms)
    import difflib
    m = difflib.SequenceMatcher(None, full_norm, tgt)
    block = max(m.get_matching_blocks(), key=lambda b: b.size)
    if block.size < max(10, len(tgt)//6):
        return None
    left_tokens = len(full_norm[:block.a].split())
    span_tokens = len(full_norm[block.a:block.a+block.size].split())
    start_idx = max(0, left_tokens)
    end_idx = min(len(tokens)-1, start_idx + span_tokens)
    s_time = tokens[start_idx]["start"]
    e_time = tokens[end_idx]["end"]
    if e_time > s_time:
        return (start_idx, end_idx, s_time, e_time)
    return None

def write_processed_segments(out_path: pathlib.Path, segments: List[Segment]):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"segments": [dict(title=s.title, start=round(s.start,3), end=round(s.end,3)) for s in segments]}
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

def build_srts(proc_path: pathlib.Path, tim_path: pathlib.Path, out_dir: pathlib.Path, words: List[Word]):
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = json.loads(proc_path.read_text())
    def to_srt_time(t):
        if t < 0: t = 0.0
        h = int(t//3600); t-=h*3600
        m = int(t//60);   t-=m*60
        s = int(t);       ms = int(round((t-s)*1000))
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    for idx, seg in enumerate(proc.get("segments", []), start=1):
        start = float(seg["start"]); end = float(seg["end"])
        ws = [w for w in words if start <= w.start <= end]
        cues=[]; line=[]; lstart=None; lend=0.0
        for w in ws:
            s = w.start - start; e = w.end - start
            if not line: lstart = max(0.0, s)
            line.append(w.text); lend = max(0.0, e)
            if len(line) >= 8:
                cues.append((lstart, lend, " ".join(line))); line=[]; lstart=None
        if line: cues.append((lstart, lend, " ".join(line)))
        if not cues: cues=[(0.0, max(0.5, end-start), seg.get('title') or f"segment_{idx}")]
        lines=[]
        for i,(a,b,txt) in enumerate(cues, start=1):
            lines += [str(i), f"{to_srt_time(a)} --> {to_srt_time(b)}", txt, ""]
        (out_dir / f"segment_{idx}.srt").write_text("\n".join(lines), encoding="utf-8")

def cut_and_burn(input_video: pathlib.Path, proc_path: pathlib.Path, srt_dir: pathlib.Path, out_dir: pathlib.Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = json.loads(proc_path.read_text())
    for idx, seg in enumerate(proc.get("segments", []), start=1):
        start = float(seg["start"]); end = float(seg["end"]); dur = max(0.01, end - start)
        title = (seg.get("title") or f"segment_{idx}").replace("/", "-")
        raw_out = out_dir / f"segment_{idx}_{title}.mp4"
        sub_out = out_dir / f"segment_{idx}_{title}_subtitled.mp4"
        srt = srt_dir / f"segment_{idx}.srt"
        cut = ["ffmpeg","-y","-ss",str(start),"-t",str(dur),"-i",str(input_video),
               "-map","0:v:0","-map","0:a:0?","-c:v","libx264","-c:a","aac","-b:a","192k",
               "-movflags","+faststart",str(raw_out)]
        print("Cut:", " ".join(shlex.quote(c) for c in cut))
        subprocess.run(cut, check=False)
        if srt.exists():
            vf = f"subtitles=filename='{srt.as_posix()}'"
            sub = ["ffmpeg","-y","-i",str(raw_out),"-vf",vf,
                   "-map","0:v:0","-map","0:a:0?","-c:v","libx264","-c:a","aac","-b:a","192k",
                   "-movflags","+faststart","-shortest",str(sub_out)]
            print("Subs:", " ".join(shlex.quote(c) for c in sub))
            subprocess.run(sub, check=False)

def main():
    ap = argparse.ArgumentParser(description="Gemini → Align → Cut → Burn pipeline")
    ap.add_argument("--input-video", default="input.mp4")
    ap.add_argument("--timings", default="transcripts/input_timings.json")
    ap.add_argument("--processed-out", default="processed_content/input_processed.json")
    ap.add_argument("--segments-dir", default="segmented_videos/input")
    ap.add_argument("--clips", type=int, default=8)
    ap.add_argument("--min-words", type=int, default=10)
    ap.add_argument("--max-words", type=int, default=25)
    ap.add_argument("--model", default=os.getenv("GEMINI_MODEL","gemini-1.5-flash"))
    ap.add_argument("--fuzzy", action="store_true")
    ap.add_argument("--google-api-key", default=os.getenv("GOOGLE_API_KEY"))
    args = ap.parse_args()

    if not args.google_api_key:
        print("ERROR: set GOOGLE_API_KEY or pass --google-api-key", file=sys.stderr)
        sys.exit(2)

    transcript, words = read_timings(pathlib.Path(args.timings))
    highs = call_gemini(
        transcript,
        clips=args.clips, min_words=args.min_words, max_words=args.max_words,
        model=args.model, api_key=args.google_api_key,
    )
    tokens = tokens_from_words(words)
    aligned: List[Segment] = []
    skipped = 0
    for h in highs:
        hit = align_excerpt_exact_or_fuzzy(h["excerpt"], tokens, use_fuzzy=args.fuzzy)
        if not hit:
            skipped += 1; continue
        si, ei, s, e = hit
        aligned.append(Segment(title=h["title"], start=s, end=e))

    if not aligned:
        print("No highlights could be aligned. Try --fuzzy and/or adjust --min-words/--max-words.", file=sys.stderr)
        sys.exit(1)

    proc_path = pathlib.Path(args.processed_out)
    write_processed_segments(proc_path, aligned)
    print(f"Wrote {proc_path} with {len(aligned)} segments (skipped {skipped}).")

    srt_dir = pathlib.Path(args.segments_dir) / "srt"
    build_srts(proc_path, pathlib.Path(args.timings), srt_dir, words)
    print(f"Wrote SRTs to {srt_dir}")

    cut_and_burn(pathlib.Path(args.input_video), proc_path, srt_dir, pathlib.Path(args.segments_dir))
    print("Done.")

if __name__ == "__main__":
    main()
# (file content ends)

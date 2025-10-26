# -*- coding: utf-8 -*-
"""
Clean Gemini → Align → SRT helpers.
One stable entrypoint: call_gemini(...)
"""

import os
import json
import re
import unicodedata
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path as _P

# Optional fuzzy
try:
    from rapidfuzz import fuzz as rf_fuzz
    HAVE_RAPIDFUZZ = True
except Exception:
    import difflib
    HAVE_RAPIDFUZZ = False

# -------------------------
# Utils
# -------------------------

def _normalize(s: str) -> str:
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"[\s]+", " ", s)
    return s.strip()

def _get_env_key() -> Optional[str]:
    return os.getenv("GOOGLE_API_KEY")

def _get_env_model(default="gemini-2.5-flash") -> str:
    m = (os.getenv("GEMINI_MODEL") or "").strip()
    return m or default

def _json_from_text(txt: str) -> Optional[dict]:
    txt = (txt or "").strip()
    if not txt:
        return None
    try:
        return json.loads(txt)
    except Exception:
        m = re.search(r'\{.*\}', txt, flags=re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
    return None

# -------------------------
# Timings & tokens
# -------------------------

def read_timings(timings_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Returns (transcript:str, word_timings:[{'text','start','end'}])
    Supports shapes:
      {"transcript": "...", "word_timings":[...]}
      {"words":[...]}
      {"segments":[{"words":[...]}, ...]}
      or direct list of words
    """
    tpath = _P(timings_path)
    if not tpath.exists():
        raise FileNotFoundError(f"Timings JSON not found: {tpath}")
    try:
        data = json.loads(tpath.read_text())
    except Exception as e:
        raise ValueError(f"Invalid JSON at {tpath}: {e}")

    transcript = ""
    words_raw: List[dict] = []

    if isinstance(data, dict):
        transcript = (data.get("transcript") or "").strip()
        if isinstance(data.get("word_timings"), list):
            words_raw = data["word_timings"]
        elif isinstance(data.get("words"), list):
            words_raw = data["words"]
        elif isinstance(data.get("segments"), list):
            for seg in data["segments"]:
                if isinstance(seg, dict) and isinstance(seg.get("words"), list):
                    words_raw.extend(seg["words"])
    elif isinstance(data, list):
        if data and isinstance(data[0], dict):
            if {"text","start","end"}.issubset(set(data[0].keys())):
                words_raw = data
            else:
                for item in data:
                    if isinstance(item, dict) and isinstance(item.get("words"), list):
                        words_raw.extend(item["words"])

    word_timings: List[Dict[str, Any]] = []
    for w in words_raw:
        txt = str(w.get("text") or w.get("word") or "")
        s = w.get("start"); e = w.get("end")
        if s is None or e is None:
            continue
        try:
            word_timings.append({"text": txt, "start": float(s), "end": float(e)})
        except Exception:
            continue

    if not transcript:
        alt_txt = tpath.parent / "input_transcript.txt"
        if alt_txt.exists():
            transcript = alt_txt.read_text().strip()
        elif word_timings:
            transcript = " ".join(w["text"] for w in word_timings)

    return transcript, word_timings

def tokens_from_words(words: List[dict]) -> List[dict]:
    tokens=[]
    for w in words:
        txt = str(w.get("text") or "")
        s   = w.get("start"); e = w.get("end")
        if s is None or e is None:
            continue
        tokens.append({"txt": txt, "n": _normalize(txt), "start": float(s), "end": float(e)})
    return tokens

# -------------------------
# Align excerpt
# -------------------------

def align_excerpt_exact_or_fuzzy(excerpt: str,
                                 tokens: List[dict],
                                 use_fuzzy: bool = False) -> Optional[Tuple[float,float]]:
    """
    Try exact normalized token matching first (phrase windows 5..12).
    If not found and use_fuzzy=True, pick best fuzzy window.
    Returns (start_time, end_time) in seconds or None.
    """
    if not excerpt or not tokens:
        return None

    tgt = _normalize(excerpt)
    if not tgt:
        return None

    norms = [t["n"] for t in tokens]
    tgt_words = tgt.split()
    if len(tgt_words) < 3:
        return None

    # Exact sliding window
    for L in range(min(12, len(tgt_words)), 4, -1):
        for i in range(0, len(tgt_words)-L+1):
            phrase = " ".join(tgt_words[i:i+L])
            buf=[]
            for idx, w in enumerate(norms):
                buf.append(w)
                if len(buf)>L: buf.pop(0)
                if len(buf)==L and " ".join(buf)==phrase:
                    s_idx = idx-L+1
                    e_idx = min(len(tokens)-1, idx + (len(tgt_words)-L) + 1)
                    return (tokens[s_idx]["start"], tokens[e_idx]["end"])

    if not use_fuzzy:
        return None

    # Fuzzy window search
    best = (0.0, None)  # (score, (s_time, e_time))
    tgt_join = " ".join(tgt_words[:50])
    N = len(norms)
    window = min(20, max(8, len(tgt_words)))
    step = max(1, window // 2)
    def score(a, b):
        if HAVE_RAPIDFUZZ:
            return rf_fuzz.token_set_ratio(a, b)
        else:
            return int(difflib.SequenceMatcher(None, a, b).ratio()*100)

    for i in range(0, max(1, N-window+1), step):
        candidate = " ".join(norms[i:i+window])
        sc = score(tgt_join, candidate)
        if sc > best[0]:
            s_time = tokens[i]["start"]
            e_time = tokens[min(N-1, i+window-1)]["end"]
            best = (sc, (s_time, e_time))

    if best[1] and best[0] >= 70:
        return best[1]
    return None

# -------------------------
# Build SRTs
# -------------------------

def _to_srt_time(t: float) -> str:
    if t < 0: t = 0.0
    h = int(t//3600); t-=h*3600
    m = int(t//60);   t-=m*60
    s = int(t);       ms = int(round((t-s)*1000))
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def build_srts(segments: List[dict],
               word_timings: List[dict],
               out_dir: str) -> List[_P]:
    """
    Creates segment_i.srt files based on word timings or titles fallback.
    """
    outp = _P(out_dir)
    outp.mkdir(parents=True, exist_ok=True)

    tokens = tokens_from_words(word_timings) if word_timings else []
    srts=[]
    for idx, seg in enumerate(segments, start=1):
        start = seg.get("start"); end = seg.get("end")
        title = seg.get("title") or f"segment_{idx}"
        p = outp / f"segment_{idx}.srt"
        cues=[]

        if start is None or end is None:
            # one-line fallback
            cues=[(0.0, 2.0, title)]
        else:
            if tokens:
                ws = [t for t in tokens if start <= t["start"] <= end]
                if ws:
                    line, lstart = [], None
                    lend=0.0
                    for w in ws:
                        if not line: lstart = max(0.0, w["start"]-start)
                        line.append(w["txt"]); lend = max(0.0, w["end"]-start)
                        if len(line) >= 8:
                            cues.append((lstart,lend," ".join(line)))
                            line, lstart = [], None
                    if line:
                        cues.append((lstart,lend," ".join(line)))
            if not cues:
                dur = max(0.5, float(end)-float(start))
                cues=[(0.0, dur, title)]

        lines=[]
        for i,(a,b,txt) in enumerate(cues, start=1):
            lines.append(str(i))
            lines.append(f"{_to_srt_time(a)} --> {_to_srt_time(b)}")
            lines.append(txt or title); lines.append("")
        p.write_text("\n".join(lines), encoding="utf-8")
        srts.append(p)
    return srts

# -------------------------
# Fallback Highlights (strong)
# -------------------------

def _fallback_highlights_from_text(full_text: str,
                                   k=6,
                                   min_words=8,
                                   max_words=18) -> List[dict]:
    """
    Deterministic fallback when Gemini returns nothing/blocked:
    - Try sentence-based picks with min_words..max_words
    - If not enough, chunk the transcript by words evenly to produce k items.
    Always returns <= k items (may return fewer if not enough words).
    """
    if not full_text:
        return []
    words_all = re.findall(r"\S+", full_text)
    if len(words_all) < min_words:
        return []

    highlights=[]

    # Sentence pass
    parts = re.split(r'(?<=[\.!?])\s+', full_text.strip())
    parts = [s.strip() for s in parts if s.strip()]
    for s in parts:
        w = re.findall(r"\S+", s)
        if len(w) < min_words:
            continue
        excerpt = " ".join(w[:max_words])
        title   = " ".join(w[:8])
        highlights.append({"title": title[:80], "excerpt": excerpt})
        if len(highlights) >= k:
            break

    # Chunk pass if needed
    if len(highlights) < k and words_all:
        step = max(min_words, len(words_all)//max(1, k))
        i = 0
        while len(highlights) < k and i < len(words_all):
            chunk = words_all[i:i+max_words]
            if len(chunk) >= min_words:
                seg = " ".join(chunk)
                t   = " ".join(chunk[:8])
                highlights.append({"title": t[:80], "excerpt": seg})
            i += step

    return highlights[:k]

# -------------------------
# Gemini core and wrapper
# -------------------------

def _call_gemini_core(full_text: str,
                      clips=6,
                      min_words=8,
                      max_words=18,
                      model=None,
                      api_key=None,
                      ai_provider_name: str = "gemini",
                      provider_api_key: str = None,
                      **_unused) -> dict:
    """
    Calls Gemini and returns dict: {"highlights":[{"title","excerpt"}, ...]}
    Raises on block/invalid/empty.
    """
    if not full_text:
        return {"highlights":[]}
    # Build prompt
    prompt = (
        f"You are a video shorts editor.\n"
        f"Given a speech transcript, pick the {clips} most compelling highlights for social media.\n\n"
        f"Return ONLY valid JSON with a single key \"highlights\": a list where each item has:\n"
        f"- \"title\": a catchy title (<= 70 chars)\n"
        f"- \"excerpt\": exact words copied from the transcript, between {min_words} and {max_words} words.\n\n"
        f"Example:\n"
        f"{{\"highlights\":[{{\"title\":\"...\",\"excerpt\":\"...\"}}]}}\n\n"
        f"Transcript:\n"
        f"{full_text[:20000]}"
    )

    # Use factory to obtain provider (keeps support for multiple providers)
    try:
        from clipify.core.ai_providers import get_ai_provider
    except Exception:
        # Fallback: try to import provider directly
        get_ai_provider = None

    provider_name = (ai_provider_name or "gemini").lower()
    # Prefer explicit provider_api_key, then api_key param, then env
    prov_key = provider_api_key or api_key

    try:
        if get_ai_provider:
            prov = get_ai_provider(provider_name, prov_key, model)
            resp = prov.get_response(prompt)
        else:
            # Last-resort: assume Gemini and call google.generativeai directly
            import google.generativeai as genai
            key = prov_key or _get_env_key()
            if not key:
                raise RuntimeError("Missing GOOGLE_API_KEY in env/.env")
            genai.configure(api_key=key)
            mdl = model or _get_env_model()
            gmodel = genai.GenerativeModel(mdl)
            resp = gmodel.generate_content(prompt, generation_config={"temperature":0.4, "max_output_tokens":1400})

    except Exception as e:
        raise

    # Extract textual content from provider response
    try:
        # Many providers return a structure like {"choices": [{"message": {"content": "..."}}]}
        txt = ""
        if isinstance(resp, dict):
            # openai-like
            ch = resp.get("choices") or []
            if ch and isinstance(ch, list):
                first = ch[0]
                if isinstance(first, dict):
                    msg = first.get("message") or first
                    if isinstance(msg, dict):
                        txt = msg.get("content") or ""
                    else:
                        txt = msg
        # Some clients return objects with .text
        if not txt:
            txt = getattr(resp, "text", "") or ""

        obj = _json_from_text(txt)
        if not obj or not isinstance(obj, dict) or "highlights" not in obj:
            # Could be blocked — try to inspect candidates
            try:
                cands = getattr(resp, "candidates", []) or []
                blocked = any(getattr(c, "finish_reason", None) == 2 for c in cands)
            except Exception:
                blocked = False
            if blocked:
                raise ValueError("AI provider blocked the output.")
            raise ValueError("AI provider did not return valid JSON.")

        highs_raw = obj.get("highlights") or []
        cleaned=[]
        for h in highs_raw:
            if isinstance(h, dict):
                title   = (h.get("title") or "").strip()
                excerpt = (h.get("excerpt") or h.get("text") or "").strip()
            else:
                title   = str(h)[:80]
                excerpt = str(h)
            if excerpt:
                cleaned.append({"title": title[:80] or excerpt[:50], "excerpt": excerpt})
        return {"highlights": cleaned[:clips]}
    except Exception:
        raise

def call_gemini(*args,
                full_text=None,
                transcript=None,
                word_timings=None,
                clips=6,
                min_words=8,
                max_words=18,
                model=None,
                api_key=None,
                **kwargs) -> dict:
    """
    Public entrypoint used by CLI/UI.
    Accepts full_text OR transcript; also accepts a positional str/dict for back-compat.
    If core fails or returns empty, falls back to local highlights.
    """
    # Back-compat positional mapping
    if args and full_text is None and transcript is None:
        a0 = args[0]
        if isinstance(a0, str):
            full_text = a0
        elif isinstance(a0, dict):
            if a0.get("transcript"):
                full_text = str(a0["transcript"])
            elif a0.get("full_text"):
                full_text = str(a0["full_text"])
            elif a0.get("text"):
                full_text = str(a0["text"])

    text = (full_text or transcript or "").strip()
    if not text:
        return {"highlights":[]}

    # Try Gemini
    try:
        res = _call_gemini_core(full_text=text,
                                clips=clips,
                                min_words=min_words,
                                max_words=max_words,
                                model=model,
                                api_key=api_key)
        highs = res.get("highlights") or []
        if highs:
            return {"highlights": highs[:clips]}
        # Empty → fallback
        raise ValueError("Gemini returned empty highlights.")
    except Exception:
        highs = _fallback_highlights_from_text(text, k=clips,
                                               min_words=min_words,
                                               max_words=max_words)
        return {"highlights": highs}

# -------------------------
# Write processed segments (for UI)
# -------------------------

def write_processed_segments(segments, out_path: str = "processed_content/input_processed.json"):
    """
    Persist segments to a JSON file the rest of the pipeline expects:
    {
      "segments": [
        {"title": "...", "start": float|None, "end": float|None},
        ...
      ]
    }
    """
    p = _P(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    norm = []
    for i, s in enumerate(segments, 1):
        if not isinstance(s, dict):
            s = {"title": str(s), "start": None, "end": None}
        title = (s.get("title") or f"segment_{i}").strip()
        start = s.get("start")
        end   = s.get("end")

        try:
            start = float(start) if start is not None else None
        except Exception:
            start = None
        try:
            end = float(end) if end is not None else None
        except Exception:
            end = None

        norm.append({"title": title, "start": start, "end": end})

    out = {"segments": norm}
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return p

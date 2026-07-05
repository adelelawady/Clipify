"""Validates and adjusts SRT timings to match clip boundaries."""

import re
from pathlib import Path
from typing import List, Tuple

def parse_srt_time(time_str: str) -> float:
    """Convert SRT timestamp to seconds."""
    pattern = r"(\d{2}):(\d{2}):(\d{2}),(\d{3})"
    match = re.match(pattern, time_str)
    if not match:
        return 0.0
    h, m, s, ms = map(int, match.groups())
    return h * 3600 + m * 60 + s + ms/1000

def format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format."""
    if seconds < 0:
        seconds = 0.0
    h = int(seconds//3600); seconds -= h*3600
    m = int(seconds//60); seconds -= m*60
    s = int(seconds); ms = int(round((seconds-s)*1000))
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def validate_srt_timings(srt_path: Path, clip_duration: float) -> bool:
    """
    Validates and fixes SRT timings to ensure they fall within clip boundaries.
    Returns True if file was modified, False otherwise.
    """
    if not srt_path.exists():
        return False
        
    content = srt_path.read_text(encoding='utf-8')
    lines = content.strip().split('\n')
    modified = False
    new_lines = []
    
    i = 0
    while i < len(lines):
        # Skip empty lines and subtitle numbers
        if not lines[i].strip():
            new_lines.append(lines[i])
            i += 1
            continue
            
        if lines[i].isdigit():
            new_lines.append(lines[i])
            i += 1
            if i >= len(lines):
                break
                
        # Handle timestamp line
        if '-->' in lines[i]:
            timestamp_line = lines[i]
            start_time, end_time = timestamp_line.split(' --> ')
            
            # Convert to seconds
            start_sec = parse_srt_time(start_time)
            end_sec = parse_srt_time(end_time)
            
            # Validate and adjust timings
            if end_sec > clip_duration:
                end_sec = clip_duration
                modified = True
            if start_sec >= end_sec:
                start_sec = max(0, end_sec - 2.0)  # Default to 2 second duration
                modified = True
                
            # Write back adjusted timestamps
            new_timestamp = f"{format_srt_time(start_sec)} --> {format_srt_time(end_sec)}"
            new_lines.append(new_timestamp)
            
        else:
            new_lines.append(lines[i])
        i += 1
    
    if modified:
        srt_path.write_text('\n'.join(new_lines), encoding='utf-8')
    
    return modified
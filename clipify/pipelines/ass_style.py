"""Helper module for ASS subtitle style validation and formatting."""

from typing import Dict, Any

def validate_color(color: str) -> str:
    """Validate and convert color to ASS format."""
    if not color or not isinstance(color, str):
        return "&H00FFFFFF"  # Default white
        
    # Strip # if present
    color = color.lstrip("#")
    
    if len(color) != 6:
        return "&H00FFFFFF"
        
    try:
        # Validate hex values
        int(color, 16)
        # Convert RGB to ASS BGR
        r, g, b = color[0:2], color[2:4], color[4:6]
        return f"&H00{b.upper()}{g.upper()}{r.upper()}"
    except ValueError:
        return "&H00FFFFFF"

def validate_style_value(key: str, value: Any) -> str:
    """Validate individual style values."""
    if key in ["FontSize", "Outline", "Shadow", "MarginV"]:
        try:
            val = int(value)
            if key == "FontSize":
                return str(max(1, min(val, 100)))
            elif key == "Outline":
                return str(max(0, min(val, 4)))
            elif key == "Shadow":
                return str(max(0, min(val, 4)))
            elif key == "MarginV":
                return str(max(0, min(val, 100)))
        except (ValueError, TypeError):
            return "40" if key == "FontSize" else "2"
            
    elif key in ["BorderStyle"]:
        try:
            val = int(value)
            if val in [0, 1, 3, 4]:
                return str(val)
        except (ValueError, TypeError):
            pass
        return "3"  # Default to opaque box
        
    elif key in ["Alignment"]:
        try:
            val = int(value)
            if val in range(1, 12):  # ASS alignments 1-11
                return str(val)
        except (ValueError, TypeError):
            pass
        return "2"  # Default to bottom-center
        
    elif key in ["PrimaryColour", "OutlineColour", "BackColour"]:
        return validate_color(value)
        
    return str(value)

def validate_subtitle_style(style: Dict[str, Any]) -> Dict[str, str]:
    """Validate and normalize subtitle style settings."""
    if not isinstance(style, dict):
        return {}
        
    validated = {}
    
    # Process each style attribute
    for key, value in style.items():
        if key in [
            "FontSize", "PrimaryColour", "OutlineColour", "BackColour",
            "Outline", "BorderStyle", "Shadow", "Alignment", "MarginV"
        ]:
            validated[key] = validate_style_value(key, value)
            
    # Ensure required attributes have defaults
    if "FontSize" not in validated:
        validated["FontSize"] = "40"
    if "PrimaryColour" not in validated:
        validated["PrimaryColour"] = "&H00FFFFFF"
    if "OutlineColour" not in validated:
        validated["OutlineColour"] = "&H000F0F0F"
    if "BorderStyle" not in validated:
        validated["BorderStyle"] = "3"
    if "Alignment" not in validated:
        validated["Alignment"] = "2"
        
    return validated

def ass_force_style(style: Dict[str, str]) -> str:
    """Convert style dictionary to ASS force_style format."""
    return ",".join(f"{k}={v}" for k, v in style.items())
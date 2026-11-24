"""Starting points for common jobs. A preset is just a partial parameter set."""
from __future__ import annotations

SKETCH_PRESETS: dict[str, dict] = {
    "Realistic pencil portrait": {
        "style": "pencil", "detail": 72, "contrast": 55, "shadow": 55, "grain": 35, "outline": 12,
    },
    "Soft pencil (pets, landscapes)": {
        "style": "pencil", "detail": 55, "contrast": 45, "shadow": 40, "grain": 40, "outline": 0,
    },
    "Clean outline to trace": {
        "style": "lineart", "detail": 55, "line_threshold": 30, "line_weight": 1.5,
    },
    "Fine outline (more detail)": {
        "style": "lineart", "detail": 80, "line_threshold": 22, "line_weight": 1.0,
    },
    "Hatched drawing": {
        "style": "hatch", "detail": 60, "levels": 4, "hatch_spacing": 9, "outline": 25, "jitter": 35,
    },
    "Value study (4 tones)": {
        "style": "value", "levels": 4, "detail": 60, "outline": 0,
    },
    "Value study (6 tones)": {
        "style": "value", "levels": 6, "detail": 65, "outline": 0,
    },
}

PBN_PRESETS: dict[str, dict] = {
    "Beginner (6 colours, big shapes)": {"colors": 6, "min_shape_mm": 9, "pre_smooth": 6, "edge_smooth": 7},
    "Standard (12 colours)": {"colors": 12, "min_shape_mm": 5, "pre_smooth": 4, "edge_smooth": 5},
    "Detailed (24 colours)": {"colors": 24, "min_shape_mm": 3.5, "pre_smooth": 3, "edge_smooth": 4},
    "Portrait (28 colours, fine detail)": {"colors": 28, "min_shape_mm": 3, "pre_smooth": 2, "edge_smooth": 3},
}


def all_presets() -> dict:
    return {
        "sketch": [{"name": k, "params": v} for k, v in SKETCH_PRESETS.items()],
        "pbn": [{"name": k, "params": v} for k, v in PBN_PRESETS.items()],
    }

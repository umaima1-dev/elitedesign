"""Glue between raw bytes + JSON params and the engine. Used by the API and the CLI."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass

import numpy as np

from .engine import ENGINE_VERSION, PBNParams, SketchParams, render_pbn, render_sketch
from .engine.common import decode_image, dpi_for, encode_png, sha256_bytes

PREVIEW_SIDE = 720
FULL_SIDE = {"sketch": 3000, "pbn": 1800}
MAX_SIDE_LIMIT = 4000


@dataclass
class Output:
    mode: str
    width: int
    height: int
    png: bytes | None
    svg: str | None
    palette: list[dict] | None
    stats: dict
    recipe: dict
    ms: int


def parse_params(mode: str, raw: str | dict | None):
    data = json.loads(raw) if isinstance(raw, str) and raw.strip() else (raw or {})
    if isinstance(data, dict) and "params" in data and "engine_version" in data:
        data = data["params"]  # a full recipe file was supplied
    if mode == "sketch":
        return SketchParams(**data)
    if mode == "pbn":
        return PBNParams(**data)
    raise ValueError("mode must be 'sketch' or 'pbn'")


def run(data: bytes, mode: str, params_raw, quality: str = "preview", max_side: int | None = None) -> Output:
    t0 = time.perf_counter()
    params = parse_params(mode, params_raw)
    side = PREVIEW_SIDE if quality == "preview" else (max_side or FULL_SIDE[mode])
    side = min(side, MAX_SIDE_LIMIT)
    rgb = decode_image(data, side)
    h, w = rgb.shape[:2]

    recipe = {
        "engine_version": ENGINE_VERSION,
        "mode": mode,
        "params": params.model_dump(mode="json"),
        "input_sha256": sha256_bytes(data),
        "max_side": side,
    }

    if mode == "sketch":
        img = render_sketch(rgb, params)
        png = encode_png(img, dpi_for(w, params.print_width_cm))
        recipe["output_sha256"] = sha256_bytes(np.ascontiguousarray(img).tobytes())
        return Output(mode, w, h, png, None, None, {"width": w, "height": h}, recipe,
                      int((time.perf_counter() - t0) * 1000))

    # The on-screen preview omits the colour key (the UI lists the palette itself) so the
    # picture keeps the photo's proportions. The recipe still records the user's setting.
    render_params = params.model_copy(update={"legend": False}) if quality == "preview" else params
    res = render_pbn(rgb, render_params)
    svg = res.svg()
    recipe["output_sha256"] = sha256_bytes(svg.encode("utf-8"))
    stats = {**res.stats, "width": w, "height": h}
    return Output(mode, w, h, None, svg, res.palette, stats, recipe, int((time.perf_counter() - t0) * 1000))

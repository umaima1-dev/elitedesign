"""Shared helpers: image decoding, PNG encoding, hashing.

Everything in the engine is a pure function of (pixels, params). There is no
random sampling anywhere that is not driven by an explicit integer seed.
"""
from __future__ import annotations

import hashlib
import io
import os

import cv2
import numpy as np
from PIL import Image, ImageOps

ENGINE_VERSION = "0.1.0"
MAX_INPUT_PIXELS = int(os.environ.get("MAX_INPUT_PIXELS", 120_000_000))
MIN_SIDE = 32


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_image(data: bytes, max_side: int | None = None) -> np.ndarray:
    """Decode bytes to an RGB uint8 array, honouring EXIF rotation.

    Transparent images are composited over white. If ``max_side`` is given the
    image is shrunk (never enlarged) with area interpolation so the longest side
    is at most ``max_side``.
    """
    Image.MAX_IMAGE_PIXELS = MAX_INPUT_PIXELS
    try:
        im = Image.open(io.BytesIO(data))
        if max_side and im.format == "JPEG":
            # Let libjpeg decode at a reduced size: a 48 MP photo never has to sit in memory in full.
            im.draft("RGB", (max_side * 2, max_side * 2))
        im.load()
    except Exception as exc:  # noqa: BLE001 - any decoder failure is a bad upload
        raise ValueError("Could not read this file as an image.") from exc

    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        rgba = im.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, rgba)
    im = im.convert("RGB")

    arr = np.asarray(im, dtype=np.uint8)
    h, w = arr.shape[:2]
    if min(h, w) < MIN_SIDE:
        raise ValueError(f"Image is too small ({w}x{h}px). Use at least {MIN_SIDE}px per side.")
    if max_side and max(h, w) > max_side:
        f = max_side / max(h, w)
        arr = cv2.resize(
            arr,
            (max(1, round(w * f)), max(1, round(h * f))),
            interpolation=cv2.INTER_AREA,
        )
    return np.ascontiguousarray(arr)


def encode_png(arr: np.ndarray, dpi: float | None = None) -> bytes:
    """Encode an RGB/gray uint8 array as PNG, optionally embedding DPI."""
    buf = io.BytesIO()
    kwargs = {}
    if dpi:
        kwargs["dpi"] = (dpi, dpi)
    Image.fromarray(arr).save(buf, format="PNG", compress_level=6, **kwargs)
    return buf.getvalue()


def dpi_for(width_px: int, print_width_cm: float | None) -> float | None:
    if not print_width_cm:
        return None
    return round(width_px / (print_width_cm / 2.54), 2)


def scale_of(shape: tuple[int, ...]) -> float:
    """Size factor relative to a 1000px image. Keeps parameters resolution independent."""
    return max(shape[0], shape[1]) / 1000.0

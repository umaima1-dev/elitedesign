"""Deterministic photo -> sketch rendering.

Classical image processing only: Gaussian / bilateral filters, CLAHE, colour dodge,
extended difference-of-Gaussians (XDoG), structure-tensor flow fields, quantile
tone mapping. Noise (paper grain, hand wobble) is drawn from a generator seeded
with ``params.seed`` so a render is reproducible bit for bit.
"""
from __future__ import annotations

import cv2
import numpy as np

from .common import scale_of
from .schemas import SketchParams

PAPER_RGB = {"white": (1.0, 1.0, 1.0), "cream": (1.0, 0.972, 0.925)}


# --------------------------------------------------------------------------- utils
def _smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _prep_gray(rgb: np.ndarray, contrast: int) -> np.ndarray:
    """Luminance in 0..1 with local contrast (CLAHE) and a percentile stretch."""
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clip = 1.0 + 3.0 * contrast / 100.0
    g = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8)).apply(g)
    g = g.astype(np.float32) / 255.0
    lo, hi = np.percentile(g, [1.0, 99.0])
    if hi - lo > 1e-3:
        g = np.clip((g - np.float32(lo)) / np.float32(hi - lo), 0.0, 1.0)
    return g.astype(np.float32)


def _noise(shape: tuple[int, int], seed: int, sigma: float, coarse: int = 1) -> np.ndarray:
    """Unit-variance Gaussian noise, optionally generated on a coarse grid and upsampled."""
    h, w = shape
    rng = np.random.default_rng(seed)
    if coarse > 1:
        n = rng.standard_normal((h // coarse + 2, w // coarse + 2)).astype(np.float32)
        n = cv2.GaussianBlur(n, (0, 0), max(sigma / coarse, 0.3))
        n = cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
    else:
        n = rng.standard_normal((h, w)).astype(np.float32)
        if sigma > 0:
            n = cv2.GaussianBlur(n, (0, 0), sigma)
    std = float(n.std())
    return n / (std if std > 1e-6 else 1.0)


# ------------------------------------------------------------------- line extraction
def _xdog_lines(rgb: np.ndarray, p: SketchParams) -> np.ndarray:
    """Ink coverage in 0..1 (1 = black line) using extended difference of Gaussians."""
    s = scale_of(rgb.shape)
    g = _prep_gray(rgb, p.contrast)
    # Edge-preserving smoothing removes skin / fabric texture but keeps contours.
    g = cv2.bilateralFilter(g, d=0, sigmaColor=0.12, sigmaSpace=max(2.0, 2.5 * s))

    sigma = (0.6 + (100 - p.detail) / 100.0 * 2.6) * s
    k = 1.6
    sharp = 25.0
    g1 = cv2.GaussianBlur(g, (0, 0), sigma)
    g2 = cv2.GaussianBlur(g, (0, 0), k * sigma)
    d = (1.0 + sharp) * g1 - sharp * g2

    # Higher sensitivity -> larger epsilon -> more pixels fall below it -> more ink.
    eps = 0.02 + (p.line_threshold / 100.0) * 0.30
    phi = 12.0
    t = np.where(d >= eps, 1.0, 1.0 + np.tanh(phi * (d - eps))).astype(np.float32)
    lines = 1.0 - t

    # Remove isolated specks (they are noise, not drawing).
    binary = (lines > 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    min_area = max(4.0, 5.0 * s * s)
    small = np.flatnonzero(stats[:, cv2.CC_STAT_AREA] < min_area)
    small = small[small != 0]
    if small.size:
        lines[np.isin(lab, small)] = 0.0

    # Line weight (radius in px, scaled with resolution).
    r = p.line_weight * s * 0.5
    if r >= 0.75:
        ks = int(2 * round(r) + 1)
        kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ks, ks))
        lines = cv2.dilate(lines, kern)
        lines = cv2.GaussianBlur(lines, (0, 0), 0.5 + 0.1 * s)
    return np.clip(lines, 0.0, 1.0)


# ----------------------------------------------------------------------------- styles
def _pencil(rgb: np.ndarray, p: SketchParams) -> np.ndarray:
    h, w = rgb.shape[:2]
    g = _prep_gray(rgb, p.contrast)
    sigma = (0.003 + (100 - p.detail) / 100.0 * 0.02) * max(h, w)
    blur = cv2.GaussianBlur(1.0 - g, (0, 0), sigma)
    dodge = np.clip(g / np.maximum(1.0 - blur, 1e-3), 0.0, 1.0)

    # Mix some of the true tone back in: gives soft graphite shading, not just edges.
    t = p.shadow / 100.0 * 0.65
    tone = cv2.GaussianBlur(g, (0, 0), max(0.8, sigma * 0.25))
    out = (1.0 - t) * dodge + t * tone
    out = out ** (1.0 + p.shadow / 100.0 * 0.6)

    lo = float(np.percentile(out, 0.5))
    if lo < 0.95:
        out = np.clip((out - lo) / (1.0 - lo), 0.0, 1.0)

    if p.grain:
        s = scale_of(rgb.shape)
        n = _noise((h, w), p.seed, 0.5 + 0.35 * s)
        cover = 1.0 - out
        cover = np.clip(cover * (1.0 + p.grain / 100.0 * 0.35 * n), 0.0, 1.0)
        out = 1.0 - cover
    return out.astype(np.float32)


def _lineart(rgb: np.ndarray, p: SketchParams) -> np.ndarray:
    return (1.0 - _xdog_lines(rgb, p)).astype(np.float32)


_NB = 12  # number of quantised hatch directions


def _flow_bins(g: np.ndarray, p: SketchParams, s: float) -> np.ndarray:
    """Hatch direction per pixel, following contours via the structure tensor."""
    default = np.deg2rad(p.hatch_angle)
    if not p.hatch_flow:
        theta = np.full(g.shape, default, np.float32)
    else:
        gs = cv2.GaussianBlur(g, (0, 0), 1.5 * s + 0.5)
        gx = cv2.Sobel(gs, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gs, cv2.CV_32F, 0, 1, ksize=3)
        sig = 20.0 * s + 3.0
        jxx = cv2.GaussianBlur(gx * gx, (0, 0), sig)
        jyy = cv2.GaussianBlur(gy * gy, (0, 0), sig)
        jxy = cv2.GaussianBlur(gx * gy, (0, 0), sig)
        grad_dir = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)
        coherence = np.sqrt((jxx - jyy) ** 2 + 4.0 * jxy**2) / (jxx + jyy + 1e-6)
        # Hatch along contours (perpendicular to the gradient); fall back where flow is unclear.
        # Only trust the flow where there is real structure; flat areas keep one clean angle.
        energy = jxx + jyy
        trusted = (coherence > 0.3) & (energy > np.float32(np.percentile(energy, 55)))
        theta = np.where(trusted, grad_dir + np.pi / 2, default)
    bins = np.round(np.mod(theta, np.pi) / np.pi * _NB).astype(np.int32) % _NB
    return bins


def _hatch(rgb: np.ndarray, p: SketchParams) -> np.ndarray:
    h, w = rgb.shape[:2]
    s = scale_of(rgb.shape)
    g = _prep_gray(rgb, p.contrast)
    smooth = cv2.GaussianBlur(g, (0, 0), (0.5 + (100 - p.detail) / 100.0 * 3.0) * s)
    gamma = 1.6 - p.shadow / 100.0
    tone = np.clip(1.0 - smooth, 0.0, 1.0) ** gamma  # 0 paper white .. 1 black

    spacing = max(2.5, p.hatch_spacing * s)
    levels = p.levels
    bins = _flow_bins(g, p, s).ravel()

    warp = np.zeros(h * w, np.float32)
    if p.jitter:
        warp = (_noise((h, w), p.seed + 1, 12.0 * s, coarse=8) * (p.jitter / 100.0) * spacing * 0.6).ravel()

    tone_f = tone.ravel()
    flat_idx = np.arange(h * w, dtype=np.int64)
    xs = (flat_idx % w).astype(np.float32)
    ys = (flat_idx // w).astype(np.float32)

    paper_left = np.ones(h * w, np.float32)  # product of (1 - ink) over layers
    for k in range(levels):
        start = 0.28 + 0.60 * k / levels
        cover = _smoothstep(start, start + 0.30, tone_f) * 0.42
        active = cover > 0.01
        layer = np.zeros(h * w, np.float32)
        for b in range(_NB):
            idx = np.flatnonzero((bins == b) & active)
            if idx.size == 0:
                continue
            ang = b * np.pi / _NB + k * (np.pi / 3.0)
            u = xs[idx] * np.cos(ang) + ys[idx] * np.sin(ang) + warp[idx] + k * spacing * 0.37
            phase = u / spacing
            tri = 1.0 - 2.0 * np.abs(phase - np.floor(phase) - 0.5)  # 1 on the line centre
            # 1px-wide antialiased edge: d(tri)/d(px) = 2/spacing
            ink = np.clip((tri - (1.0 - cover[idx])) / (2.0 / spacing) + 0.5, 0.0, 1.0)
            layer[idx] = ink
        paper_left *= 1.0 - layer
    ink = (1.0 - paper_left).reshape(h, w)

    if p.grain:
        n = _noise((h, w), p.seed, 0.5 + 0.3 * s)
        ink = np.clip(ink * (1.0 + p.grain / 100.0 * 0.3 * n), 0.0, 1.0)
    return (1.0 - 0.95 * ink).astype(np.float32)


def _value(rgb: np.ndarray, p: SketchParams) -> np.ndarray:
    s = scale_of(rgb.shape)
    g = _prep_gray(rgb, p.contrast)
    g = cv2.bilateralFilter(g, d=0, sigmaColor=0.15, sigmaSpace=max(2.0, 3.0 * s))
    n = p.levels
    # Quantile cut points: every tone is used, so the study reads well on any photo.
    cuts = np.quantile(g, np.linspace(0.0, 1.0, n + 1)[1:-1])
    idx = np.digitize(g, cuts).astype(np.uint8)
    k = int(2 * round(3.0 * s * (1.0 - p.detail / 100.0) + 1) + 1)
    k = min(k, 51)
    idx = cv2.medianBlur(idx, k) if k >= 3 else idx
    levels = np.linspace(0.07, 0.96, n).astype(np.float32)
    return levels[np.clip(idx, 0, n - 1)]


STYLES = {"pencil": _pencil, "lineart": _lineart, "hatch": _hatch, "value": _value}


# -------------------------------------------------------------------------- finishing
def _focus_mask(shape: tuple[int, int], p: SketchParams) -> np.ndarray | None:
    if p.focus is None or p.focus_boost == 0:
        return None
    h, w = shape
    f = p.focus
    x0, y0 = int(round(f.x * w)), int(round(f.y * h))
    x1, y1 = int(round(min(1.0, f.x + f.w) * w)), int(round(min(1.0, f.y + f.h) * h))
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None
    m = np.zeros((h, w), np.float32)
    m[y0:y1, x0:x1] = 1.0
    return np.clip(cv2.GaussianBlur(m, (0, 0), 0.03 * max(h, w)) * 1.15, 0.0, 1.0)


def _draw_grid(rgb: np.ndarray, cols: int) -> np.ndarray:
    h, w = rgb.shape[:2]
    cell = w / cols
    thick = max(1, int(round(0.8 * scale_of(rgb.shape))))
    overlay = rgb.copy()
    k = 1
    while k * cell < w - 1:
        x = int(round(k * cell))
        overlay[:, max(0, x - thick // 2) : x - thick // 2 + thick] = (96, 140, 215)
        k += 1
    k = 1
    while k * cell < h - 1:
        y = int(round(k * cell))
        overlay[max(0, y - thick // 2) : y - thick // 2 + thick, :] = (96, 140, 215)
        k += 1
    return cv2.addWeighted(overlay, 0.55, rgb, 0.45, 0)


def render_sketch(rgb: np.ndarray, p: SketchParams) -> np.ndarray:
    """Return an RGB uint8 sketch with the same size as ``rgb``."""
    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8:
        raise ValueError("render_sketch expects an RGB uint8 image")
    h, w = rgb.shape[:2]

    out = STYLES[p.style](rgb, p)

    mask = _focus_mask((h, w), p)
    if mask is not None:
        boosted = STYLES[p.style](rgb, p.model_copy(update={"detail": min(100, p.detail + p.focus_boost)}))
        out = out * (1.0 - mask) + boosted * mask

    if p.style != "lineart" and p.outline > 0:
        lines = _xdog_lines(rgb, p)
        out = out * (1.0 - 0.85 * (p.outline / 100.0) * lines)

    out = np.clip(out, 0.0, 1.0)
    paper = np.array(PAPER_RGB[p.paper], np.float32)
    img = out[..., None] * paper[None, None, :]
    img8 = np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8)
    if p.grid_cols:
        img8 = _draw_grid(img8, p.grid_cols)
    return img8

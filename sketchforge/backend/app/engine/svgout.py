"""SVG assembly for the paint-by-numbers result.

Layers (each is a <g> with a stable id so they can be toggled in Inkscape / Illustrator):
  fills    - one compound path per palette colour
  outlines - every boundary chain drawn exactly once
  numbers  - one <text> per shape, at the deepest point of the shape
  legend   - colour key below the picture
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

from .vectorize import reverse_bezier

if TYPE_CHECKING:  # pragma: no cover
    from .pbn import PBNResult

FONT = "Helvetica, Arial, sans-serif"


def _f(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def _pt(p) -> str:
    return f"{_f(p[0])},{_f(p[1])}"


def _bez_run(segments) -> str:
    return "".join(f"C{_pt(c1)} {_pt(c2)} {_pt(e)}" for c1, c2, e in segments)


def ring_path(res: PBNResult, ring) -> str:
    parts: list[str] = []
    for i, (ci, rev) in enumerate(ring):
        ch = res.chains[ci]
        start, seg = (reverse_bezier(ch.pts[0], ch.bezier) if rev else (ch.pts[0], ch.bezier))
        if i == 0:
            parts.append(f"M{_pt(start)}")
        parts.append(_bez_run(seg))
    parts.append("Z")
    return "".join(parts)


def outline_path(res: PBNResult) -> str:
    parts: list[str] = []
    for ch in res.chains:
        if ch.left < 0 or ch.right < 0:
            continue  # image border: drawn as a frame instead
        if len(ch.bezier) == 0:
            continue
        parts.append(f"M{_pt(ch.pts[0])}{_bez_run(ch.bezier)}")
        if ch.closed:
            parts.append("Z")
    return "".join(parts)


def _luma(rgb) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _legend(res: PBNResult, y0: float, show_swatch_colour: bool) -> tuple[str, float]:
    W = res.width
    ppm = res.px_per_mm
    cell_w = 36 * ppm
    cell_h = 12 * ppm
    cols = max(1, int(W // cell_w))
    cell_w = W / cols
    sw = 8 * ppm
    fs = 3.6 * ppm
    out = [f'<g id="legend" font-family="{FONT}" font-size="{_f(fs)}" fill="#222">']
    for i, c in enumerate(res.palette):
        r, k = divmod(i, cols)
        x = k * cell_w + 2 * ppm
        y = y0 + r * cell_h
        fill = c["hex"] if show_swatch_colour else "#ffffff"
        out.append(
            f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(sw)}" height="{_f(sw)}" fill="{fill}" '
            f'stroke="#333" stroke-width="{_f(0.2 * ppm)}"/>'
        )
        out.append(
            f'<text x="{_f(x + sw / 2)}" y="{_f(y + sw / 2 + fs * 0.35)}" text-anchor="middle" '
            f'font-weight="700" fill="{"#fff" if (show_swatch_colour and _luma(c["rgb"]) < 140) else "#222"}">{c["number"]}</text>'
        )
        out.append(
            f'<text x="{_f(x + sw + 2 * ppm)}" y="{_f(y + sw / 2 - 0.2 * ppm)}">{c["hex"]}</text>'
        )
        out.append(
            f'<text x="{_f(x + sw + 2 * ppm)}" y="{_f(y + sw / 2 + 3.4 * ppm)}" fill="#777" '
            f'font-size="{_f(fs * 0.85)}">{c["coverage"]}%</text>'
        )
    out.append("</g>")
    rows = math.ceil(len(res.palette) / cols)
    return "\n".join(out), rows * cell_h + 4 * ppm


def build_svg(res: PBNResult, view: str) -> str:
    p = res.params
    W, H, ppm = res.width, res.height, res.px_per_mm
    show_fills = view in ("guide", "painted")
    show_lines = view in ("canvas", "guide")
    show_numbers = p.numbers and view in ("canvas", "guide")
    show_legend = p.legend and view in ("canvas", "guide")

    body: list[str] = [f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    if show_fills:
        by_number: dict[int, list[str]] = {}
        for region in sorted(res.rings):
            n = int(res.region_number[region])
            by_number.setdefault(n, []).append("".join(ring_path(res, r) for r in res.rings[region]))
        body.append('<g id="fills" stroke-linejoin="round">')
        for c in res.palette:
            d = "".join(by_number.get(c["number"], []))
            if d:
                body.append(
                    f'<path id="color-{c["number"]}" fill="{c["hex"]}" stroke="{c["hex"]}" '
                    f'stroke-width="0.6" fill-rule="evenodd" d="{d}"/>'
                )
        body.append("</g>")

    if show_lines:
        sw = max(0.6, 0.22 * p.line_weight * ppm)
        body.append(
            f'<g id="outlines" fill="none" stroke="#2b2b2b" stroke-width="{_f(sw)}" '
            f'stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="{outline_path(res)}"/>'
            f'<rect x="{_f(sw / 2)}" y="{_f(sw / 2)}" width="{_f(W - sw)}" height="{_f(H - sw)}"/></g>'
        )

    if show_numbers:
        max_fs = 4.5 * ppm
        body.append(
            f'<g id="numbers" font-family="{FONT}" text-anchor="middle" fill="#4a4a4a">'
        )
        for region in range(len(res.region_number)):
            x, y, r = res.label_points[region]
            num = int(res.region_number[region])
            nd = len(str(num))
            fs = min(max_fs, r / math.hypot(0.3 * nd, 0.35))
            attr = ""
            if show_fills and _luma(res.palette[num - 1]["rgb"]) < 140:
                attr = ' fill="#ffffff"'
            body.append(f'<text x="{_f(x)}" y="{_f(y + fs * 0.35)}" font-size="{_f(fs)}"{attr}>{num}</text>')
        body.append("</g>")

    total_h = float(H)
    if show_legend:
        legend, legend_h = _legend(res, H + 6 * ppm, show_swatch_colour=True)
        body.append(legend)
        total_h = H + 6 * ppm + legend_h

    width_cm = p.print_width_cm
    height_cm = width_cm * total_h / W
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {_f(total_h)}" '
        f'width="{_f(width_cm)}cm" height="{_f(height_cm)}cm">'
    )
    return head + "\n" + "\n".join(body) + "\n</svg>\n"

"""Deterministic paint-by-numbers generation.

Pipeline
  1. edge-preserving smoothing (bilateral) so skin / sky stop producing noise
  2. k-means in CIELAB (seeded k-means++, own implementation, fixed iteration order)
  3. majority filter + merge of every shape that is too small to paint
  4. shared-edge vectorisation (see vectorize.py)
  5. number placement at the pole of inaccessibility of each shape
  6. SVG assembly (see svgout.py)

Palette numbers are assigned dark -> light, so number 1 is always the darkest colour.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import cv2
import numpy as np
from scipy import ndimage as ndi

from .schemas import PBNParams
from .svgout import build_svg
from .vectorize import Chain, build_rings, trace_chains


@dataclass
class PBNResult:
    width: int
    height: int
    params: PBNParams
    palette: list[dict]  # [{number, hex, rgb, coverage, regions}]
    stats: dict
    chains: list[Chain] = field(repr=False, default_factory=list)
    rings: dict = field(repr=False, default_factory=dict)
    region_number: np.ndarray = field(repr=False, default=None)  # region id -> palette number (1-based)
    label_points: np.ndarray = field(repr=False, default=None)  # (n, 3): x, y, inscribed radius
    px_per_mm: float = 1.0

    def svg(self, view: str | None = None) -> str:
        return build_svg(self, view or self.params.view)


# --------------------------------------------------------------------------- colour
def _smooth(rgb: np.ndarray, iterations: int, scale: float) -> np.ndarray:
    out = rgb
    for _ in range(iterations):
        out = cv2.bilateralFilter(out, d=7, sigmaColor=28, sigmaSpace=max(3.0, 3.5 * scale))
    return out


def _sqdist(points: np.ndarray, centers: np.ndarray) -> np.ndarray:
    diff = points[:, None, :] - centers[None, :, :]
    return np.einsum("nkc,nkc->nk", diff, diff)


def _kpp_init(pts: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    n = len(pts)
    centers = np.empty((k, pts.shape[1]), dtype=np.float64)
    centers[0] = pts[rng.integers(n)]
    d2 = ((pts - centers[0]) ** 2).sum(1)
    for i in range(1, k):
        total = d2.sum()
        if total <= 1e-12:
            centers[i:] = centers[0]
            break
        centers[i] = pts[rng.choice(n, p=d2 / total)]
        d2 = np.minimum(d2, ((pts - centers[i]) ** 2).sum(1))
    return centers


def kmeans_lab(lab: np.ndarray, k: int, seed: int, max_samples: int = 25_000, iters: int = 40):
    """Seeded k-means on Lab pixels. Returns (centers[k,3], labels[h,w])."""
    h, w = lab.shape[:2]
    X = lab.reshape(-1, 3).astype(np.float64)
    rng = np.random.default_rng(seed)
    n = len(X)
    sample = X[rng.choice(n, min(n, max_samples), replace=False)]

    best_c, best_inertia = None, math.inf
    for _attempt in range(3):
        c = _kpp_init(sample, k, rng)
        for _ in range(iters):
            a = _sqdist(sample, c).argmin(1)
            cnt = np.bincount(a, minlength=k).astype(np.float64)
            new = c.copy()
            for ch in range(3):
                sums = np.bincount(a, weights=sample[:, ch], minlength=k)
                nz = cnt > 0
                new[nz, ch] = sums[nz] / cnt[nz]
            if np.allclose(new, c, atol=1e-3):
                c = new
                break
            c = new
        inertia = _sqdist(sample, c).min(1).sum()
        if inertia < best_inertia:
            best_inertia, best_c = inertia, c

    centers = best_c
    labels = np.empty(n, dtype=np.int32)
    step = 40_000
    for i in range(0, n, step):
        labels[i : i + step] = _sqdist(X[i : i + step], centers).argmin(1)
    return centers, labels.reshape(h, w)


def _majority(labels: np.ndarray, k: int, radius: int, passes: int) -> np.ndarray:
    ks = 2 * radius + 1
    for _ in range(passes):
        best = np.full(labels.shape, -1.0, np.float32)
        out = labels.copy()
        for j in range(k):
            m = (labels == j).astype(np.float32)
            if not m.any():
                continue
            f = cv2.boxFilter(m, -1, (ks, ks), normalize=False, borderType=cv2.BORDER_REPLICATE)
            upd = f > best
            out[upd] = j
            best[upd] = f[upd]
        labels = out
    return labels


# --------------------------------------------------------------------------- regions
def _build_regions(labels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """4-connected components of every colour label -> (region id map, label per region)."""
    rid = np.zeros(labels.shape, np.int32)
    region_label: list[int] = []
    offset = 0
    for j in np.unique(labels):
        comp, n = ndi.label(labels == j)  # default structure = 4-connectivity
        mask = comp > 0
        rid[mask] = comp[mask] + offset - 1
        region_label.extend([int(j)] * n)
        offset += n
    return rid, np.asarray(region_label, dtype=np.int32)


def _geometry(rid: np.ndarray, n: int):
    """Inscribed radius (px) of every region from one global distance transform."""
    pad = np.pad(rid, 1, constant_values=-1)
    c = pad[1:-1, 1:-1]
    boundary = (c != pad[:-2, 1:-1]) | (c != pad[2:, 1:-1]) | (c != pad[1:-1, :-2]) | (c != pad[1:-1, 2:])
    edt = ndi.distance_transform_edt(~boundary)
    idx = np.arange(n)
    max_edt = np.asarray(ndi.maximum(edt, rid, idx), dtype=np.float64)
    return edt, max_edt + 0.5  # +0.5: pixel centre -> crack between pixels


def _adjacency(rid: np.ndarray, n: int) -> list[dict[int, int]]:
    nbr: list[dict[int, int]] = [dict() for _ in range(n)]
    a = np.concatenate([rid[:, :-1].ravel(), rid[:-1, :].ravel()])
    b = np.concatenate([rid[:, 1:].ravel(), rid[1:, :].ravel()])
    m = a != b
    a, b = a[m].astype(np.int64), b[m].astype(np.int64)
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    keys, counts = np.unique(lo * n + hi, return_counts=True)
    for key, cnt in zip(keys.tolist(), counts.tolist()):
        i, j = divmod(key, n)
        nbr[i][j] = cnt
        nbr[j][i] = cnt
    return nbr


def _merge_small(
    rid: np.ndarray,
    region_label: np.ndarray,
    centers: np.ndarray,
    r_min: float,
    max_passes: int = 8,
) -> tuple[np.ndarray, np.ndarray]:
    """Absorb every region whose inscribed circle is smaller than ``r_min`` pixels.

    A small region joins the neighbour with the closest colour; neighbours that end up
    sharing a colour are fused. Geometry is re-measured between passes.
    """
    for _ in range(max_passes):
        n = len(region_label)
        _, inr = _geometry(rid, n)
        small = np.flatnonzero(inr < r_min)
        if small.size == 0 or n == 1:
            break
        areas = np.bincount(rid.ravel(), minlength=n)
        order = small[np.lexsort((areas[small], inr[small]))]
        nbr = _adjacency(rid, n)
        parent = list(range(n))
        label = region_label.tolist()
        grown = [False] * n
        cen = centers

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def merge(r: int, t: int) -> None:
            """Fold region r into region t (both are roots)."""
            stack = [(r, t)]
            while stack:
                r, t = stack.pop()
                parent[r] = t
                grown[t] = True
                for m, cnt in nbr[r].items():
                    if m == t:
                        continue
                    nm = nbr[m]
                    nm.pop(r, None)
                    nm[t] = nm.get(t, 0) + cnt
                    nbr[t][m] = nbr[t].get(m, 0) + cnt
                nbr[t].pop(r, None)
                nbr[r] = {}
                # neighbours that now share t's colour become one shape
                for m in [m for m in nbr[t] if label[m] == label[t]]:
                    if parent[m] == m and m != t:
                        stack.append((m, t))

        changed = False
        for r in order.tolist():
            if parent[r] != r or grown[r] or not nbr[r]:
                continue
            lr = cen[label[r]]
            best = None
            for m, cnt in nbr[r].items():
                d = float(((cen[label[m]] - lr) ** 2).sum())
                key = (d, -cnt, m)
                if best is None or key < best[0]:
                    best = (key, m)
            merge(r, best[1])
            changed = True
        if not changed:
            break

        roots = np.array([find(i) for i in range(n)], dtype=np.int64)
        uniq, inverse = np.unique(roots, return_inverse=True)
        rid = inverse.astype(np.int32)[rid]
        region_label = np.asarray([label[u] for u in uniq.tolist()], dtype=np.int32)
    return rid, region_label


def _label_points(rid: np.ndarray, n: int) -> np.ndarray:
    """(x, y, inscribed radius) per region; the point is the deepest pixel of the shape."""
    edt, inr = _geometry(rid, n)
    pos = ndi.maximum_position(edt, rid, np.arange(n))
    pts = np.empty((n, 3), dtype=np.float64)
    for i, (y, x) in enumerate(pos):
        pts[i] = (x + 0.5, y + 0.5, inr[i])
    return pts


# ------------------------------------------------------------------------------ main
def render_pbn(rgb: np.ndarray, p: PBNParams) -> PBNResult:
    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8:
        raise ValueError("render_pbn expects an RGB uint8 image")
    h, w = rgb.shape[:2]
    scale = max(h, w) / 1000.0
    px_per_mm = w / (p.print_width_cm * 10.0)

    smooth = _smooth(rgb, p.pre_smooth, scale)
    lab = cv2.cvtColor(smooth.astype(np.float32) / 255.0, cv2.COLOR_RGB2Lab)

    centers, labels = kmeans_lab(lab, p.colors, p.seed)
    if p.cleanup:
        labels = _majority(labels, len(centers), max(1, int(round(scale))), p.cleanup)

    rid, region_label = _build_regions(labels)
    r_min_px = max(1.0, p.min_shape_mm * px_per_mm / 2.0)
    rid, region_label = _merge_small(rid, region_label, centers, r_min_px)
    n_regions = len(region_label)

    # Final palette: mean Lab of the pixels that kept each label, ordered dark -> light.
    used = np.unique(region_label)
    lab_flat = lab.reshape(-1, 3)
    label_per_px = region_label[rid].ravel()
    mean_lab = np.empty((len(used), 3), np.float64)
    coverage = np.empty(len(used))
    for i, lbl in enumerate(used):
        sel = label_per_px == lbl
        mean_lab[i] = lab_flat[sel].mean(0)
        coverage[i] = sel.mean()
    order = np.argsort(mean_lab[:, 0], kind="stable")
    used, mean_lab, coverage = used[order], mean_lab[order], coverage[order]
    rgb_pal = cv2.cvtColor(mean_lab.astype(np.float32).reshape(-1, 1, 3), cv2.COLOR_Lab2RGB).reshape(-1, 3)
    rgb_pal = np.clip(np.rint(rgb_pal * 255.0), 0, 255).astype(np.uint8)

    number_of_label = {int(lbl): i + 1 for i, lbl in enumerate(used)}
    region_number = np.asarray([number_of_label[int(l)] for l in region_label], dtype=np.int32)

    regions_per_colour = np.bincount(region_number, minlength=len(used) + 1)[1:]
    palette = [
        {
            "number": i + 1,
            "hex": "#{:02x}{:02x}{:02x}".format(*[int(v) for v in rgb_pal[i]]),
            "rgb": [int(v) for v in rgb_pal[i]],
            "coverage": round(float(coverage[i]) * 100.0, 2),
            "regions": int(regions_per_colour[i]),
        }
        for i in range(len(used))
    ]

    smooth_iters = int(round(p.edge_smooth * 1.6))
    eps = 0.25 + 0.11 * p.edge_smooth
    chains = trace_chains(rid, smooth_iters, eps)
    rings = build_rings(chains, n_regions)
    points = _label_points(rid, n_regions)

    diam_mm = points[:, 2] * 2.0 / px_per_mm
    stats = {
        "colors": len(used),
        "regions": int(n_regions),
        "smallest_shape_mm": round(float(diam_mm.min()), 2),
        "median_shape_mm": round(float(np.median(diam_mm)), 2),
        "print_size_cm": [round(p.print_width_cm, 1), round(p.print_width_cm * h / w, 1)],
    }
    return PBNResult(
        width=w,
        height=h,
        params=p,
        palette=palette,
        stats=stats,
        chains=chains,
        rings=rings,
        region_number=region_number,
        label_points=points,
        px_per_mm=px_per_mm,
    )

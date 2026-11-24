"""Topologically consistent vectorisation of a region-id map.

Instead of tracing every region on its own (which leaves gaps and overlaps between
neighbours), we trace the *crack edges* between pixels once. Each boundary chain
between two junctions is smoothed and simplified a single time and then shared by
the two regions on either side, so neighbouring shapes meet exactly.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np


@dataclass
class Chain:
    pts: np.ndarray  # (m, 2) float64, x/y in pixel-corner coordinates
    closed: bool
    left: int  # region id on the left of the travel direction (screen coords), -1 = outside
    right: int
    start: int = 0  # node ids (junction / loop anchor)
    end: int = 0
    _bez: np.ndarray | None = field(default=None, repr=False)

    @property
    def bezier(self) -> np.ndarray:
        """(n_seg, 3, 2): control1, control2, end point for each segment, forward direction."""
        if self._bez is None:
            self._bez = catmull_rom_bezier(self.pts, self.closed)
        return self._bez


def catmull_rom_bezier(pts: np.ndarray, closed: bool) -> np.ndarray:
    """Convert a polyline to cubic Beziers through its vertices (Catmull-Rom).

    Uniform Catmull-Rom is symmetric under reversal, which is what lets two regions
    reuse one chain in opposite directions and still meet exactly.
    """
    n = len(pts)
    if closed:
        # ``pts`` repeats the first point at the end for closed chains; drop the duplicate.
        p = pts[:-1] if n > 1 and np.allclose(pts[0], pts[-1]) else pts
        m = len(p)
        if m < 3:
            return np.empty((0, 3, 2))
        p0 = np.roll(p, 1, axis=0)
        p1 = p
        p2 = np.roll(p, -1, axis=0)
        p3 = np.roll(p, -2, axis=0)
    else:
        if n < 2:
            return np.empty((0, 3, 2))
        p1 = pts[:-1]
        p2 = pts[1:]
        p0 = np.vstack([pts[:1], pts[:-2]]) if n > 2 else pts[:1]
        p3 = np.vstack([pts[2:], pts[-1:]]) if n > 2 else pts[-1:]
    c1 = p1 + (p2 - p0) / 6.0
    c2 = p2 - (p3 - p1) / 6.0
    return np.stack([c1, c2, p2], axis=1)


def reverse_bezier(start_pt: np.ndarray, bez: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Reverse a forward Bezier run. Returns (new_start_point, segments)."""
    if len(bez) == 0:
        return start_pt, bez
    ends = bez[:, 2]
    new_start = ends[-1]
    prev_pts = np.vstack([start_pt[None, :], ends[:-1]])  # start point of each forward segment
    rev = np.stack([bez[::-1, 1], bez[::-1, 0], prev_pts[::-1]], axis=1)
    return new_start, rev


# ----------------------------------------------------------------------------- tracing
def _smooth_open(pts: np.ndarray, iters: int) -> np.ndarray:
    if iters <= 0 or len(pts) < 3:
        return pts
    p = pts.copy()
    for _ in range(iters):
        p[1:-1] = 0.25 * p[:-2] + 0.5 * p[1:-1] + 0.25 * p[2:]
    return p


def _smooth_closed(pts: np.ndarray, iters: int) -> np.ndarray:
    if iters <= 0 or len(pts) < 4:
        return pts
    p = pts[:-1].copy()
    for _ in range(iters):
        p = 0.25 * np.roll(p, 1, axis=0) + 0.5 * p + 0.25 * np.roll(p, -1, axis=0)
    return np.vstack([p, p[:1]])


def _simplify(pts: np.ndarray, eps: float, closed: bool) -> np.ndarray:
    if eps <= 0 or len(pts) < 4:
        return pts
    src = pts.astype(np.float32).reshape(-1, 1, 2)
    if closed:
        out = cv2.approxPolyDP(src[:-1], eps, True).reshape(-1, 2).astype(np.float64)
        if len(out) < 3:
            return pts[:: max(1, len(pts) // 4)]
        return np.vstack([out, out[:1]])
    if np.allclose(pts[0], pts[-1]):
        # An open curve that leaves a junction and returns to it: OpenCV would collapse it
        # (zero-length baseline), so split at the farthest point and simplify each half.
        far = int(np.argmax(np.linalg.norm(pts - pts[0], axis=1)))
        a = _simplify(pts[: far + 1], eps, False)
        b = _simplify(pts[far:], eps, False)
        return np.vstack([a, b[1:]])
    out = cv2.approxPolyDP(src, eps, False).reshape(-1, 2).astype(np.float64)
    # approxPolyDP keeps the exact first/last vertices of an open curve.
    return out


def trace_chains(rid: np.ndarray, smooth_iters: int, eps: float) -> list[Chain]:
    """Trace every boundary between regions (and the image border) into chains."""
    h, w = rid.shape
    pad = np.pad(rid, 1, constant_values=-1)
    W1 = w + 1

    # Vertical unit edges: corner (cy, cx) -> (cy + 1, cx), between pixels (cy, cx-1) and (cy, cx).
    vmask = pad[1:-1, :-1] != pad[1:-1, 1:]  # shape (h, w+1)
    vy, vx = np.nonzero(vmask)
    vu = vy * W1 + vx
    vv = (vy + 1) * W1 + vx
    # Horizontal unit edges: corner (cy, cx) -> (cy, cx + 1), between pixels (cy-1, cx) and (cy, cx).
    hmask = pad[:-1, 1:-1] != pad[1:, 1:-1]  # shape (h+1, w)
    hy, hx = np.nonzero(hmask)
    hu = hy * W1 + hx
    hv = hy * W1 + hx + 1

    eu = np.concatenate([vu, hu]).astype(np.int64)
    ev = np.concatenate([vv, hv]).astype(np.int64)
    n_edges = len(eu)
    if n_edges == 0:
        return []

    # Adjacency in CSR form: for each node the (neighbour, edge id) pairs.
    nodes = np.concatenate([eu, ev])
    nbrs = np.concatenate([ev, eu])
    eids = np.concatenate([np.arange(n_edges), np.arange(n_edges)])
    order = np.argsort(nodes, kind="stable")
    nodes, nbrs, eids = nodes[order], nbrs[order], eids[order]
    uniq, first, counts = np.unique(nodes, return_index=True, return_counts=True)
    start_of = dict(zip(uniq.tolist(), first.tolist()))
    deg = dict(zip(uniq.tolist(), counts.tolist()))
    nbrs_l = nbrs.tolist()
    eids_l = eids.tolist()
    used = bytearray(n_edges)
    # The four image corners are pinned: smoothing must never round off the artwork's frame.
    anchors = {0, w, h * W1, h * W1 + w}

    def coords(node: int) -> tuple[int, int]:
        return node % W1, node // W1  # x, y

    def side_regions(a: int, b: int) -> tuple[int, int]:
        ax, ay = coords(a)
        bx, by = coords(b)
        dx, dy = bx - ax, by - ay
        mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
        lx, ly = mx + 0.5 * dy, my - 0.5 * dx  # left of travel on screen
        rx, ry = mx - 0.5 * dy, my + 0.5 * dx

        def at(x: float, y: float) -> int:
            xi, yi = int(np.floor(x)), int(np.floor(y))
            if 0 <= xi < w and 0 <= yi < h:
                return int(rid[yi, xi])
            return -1

        return at(lx, ly), at(rx, ry)

    chains: list[Chain] = []

    def walk(s: int, first_edge_pos: int, closed_loop: bool) -> None:
        node_list = [s]
        pos = first_edge_pos
        while True:
            nxt = nbrs_l[pos]
            e = eids_l[pos]
            used[e] = 1
            node_list.append(nxt)
            if closed_loop:
                if nxt == s:
                    break
            elif deg[nxt] != 2 or nxt in anchors:
                break
            # degree-2 node: continue along the other unused edge
            base = start_of[nxt]
            p0, p1 = base, base + 1
            pos = p1 if eids_l[p0] == e else p0
            if used[eids_l[pos]]:
                break
        arr = np.array([coords(n) for n in node_list], dtype=np.float64)
        left, right = side_regions(node_list[0], node_list[1])
        # Only junction-free loops are periodic. A chain that leaves a junction and comes
        # back to it stays "open" so the junction point itself is never moved.
        closed = closed_loop
        if closed:
            arr = _smooth_closed(arr, smooth_iters)
            arr = _simplify(arr, eps, True)
        else:
            arr = _smooth_open(arr, smooth_iters)
            arr = _simplify(arr, eps, False)
        chains.append(
            Chain(pts=arr, closed=closed, left=left, right=right, start=node_list[0], end=node_list[-1])
        )

    # 1) chains that begin at junctions (degree != 2)
    for node in uniq.tolist():
        if deg[node] == 2 and node not in anchors:
            continue
        base = start_of[node]
        for pos in range(base, base + deg[node]):
            if not used[eids_l[pos]]:
                walk(node, pos, False)

    # 2) leftover edges form closed loops with no junction
    for pos in range(len(eids_l)):
        if not used[eids_l[pos]]:
            s = nodes[pos].item()
            walk(s, pos, True)

    return chains


def build_rings(chains: list[Chain], n_regions: int) -> dict[int, list[list[tuple[int, bool]]]]:
    """Group chains into closed rings per region, each oriented with the region on its left.

    Returns ``{region: [ring, ...]}`` where a ring is a list of ``(chain_index, reversed)``.
    """
    outgoing: dict[int, dict[int, list[tuple[int, bool]]]] = {}
    for ci, ch in enumerate(chains):
        if ch.left >= 0:
            outgoing.setdefault(ch.left, {}).setdefault(ch.start, []).append((ci, False))
        if ch.right >= 0:
            outgoing.setdefault(ch.right, {}).setdefault(ch.end, []).append((ci, True))

    rings: dict[int, list[list[tuple[int, bool]]]] = {}
    for region, by_node in outgoing.items():
        region_rings: list[list[tuple[int, bool]]] = []
        for node in sorted(by_node):
            while by_node[node]:
                ci, rev = by_node[node].pop(0)
                ring = [(ci, rev)]
                ring_start = node
                cur_end = chains[ci].start if rev else chains[ci].end
                guard = 0
                while cur_end != ring_start:
                    options = by_node.get(cur_end)
                    if not options:
                        break  # should not happen for a valid partition
                    ci2, rev2 = options.pop(0)
                    ring.append((ci2, rev2))
                    cur_end = chains[ci2].start if rev2 else chains[ci2].end
                    guard += 1
                    if guard > len(chains) + 5:
                        break
                region_rings.append(ring)
        rings[region] = region_rings
    return rings

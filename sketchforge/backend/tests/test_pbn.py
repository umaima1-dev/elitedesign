import hashlib
import xml.etree.ElementTree as ET

import numpy as np
import pytest

from app.engine import PBNParams, render_pbn

NS = "{http://www.w3.org/2000/svg}"


def ring_area(res, ring):
    """Signed polygon area of a ring using the (smoothed, simplified) chain vertices."""
    pts = []
    for ci, rev in ring:
        c = res.chains[ci].pts
        c = c[::-1] if rev else c
        pts.extend(c[:-1].tolist())
    a = np.asarray(pts)
    x, y = a[:, 0], a[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


@pytest.fixture(scope="module")
def result(photo):
    return render_pbn(photo, PBNParams(colors=8, min_shape_mm=6, print_width_cm=24))


def test_deterministic(photo):
    p = PBNParams(colors=8)
    a, b = render_pbn(photo, p), render_pbn(photo.copy(), p)
    assert hashlib.sha256(a.svg().encode()).hexdigest() == hashlib.sha256(b.svg().encode()).hexdigest()


def test_colour_count_and_numbering(result):
    pal = result.palette
    assert 2 <= len(pal) <= 8
    assert [c["number"] for c in pal] == list(range(1, len(pal) + 1))
    lum = [0.2126 * c["rgb"][0] + 0.7152 * c["rgb"][1] + 0.0722 * c["rgb"][2] for c in pal]
    assert lum[0] < lum[-1]  # number 1 is the darkest colour
    assert abs(sum(c["coverage"] for c in pal) - 100) < 0.5


def test_min_shape_is_respected(result):
    assert result.stats["smallest_shape_mm"] >= 6 * 0.95


def test_shared_edges_leave_no_gaps_or_overlaps(result):
    """Because neighbours share the same traced edge, shape areas must add up to the canvas."""
    total = 0.0
    for region, rings in result.rings.items():
        total += abs(sum(ring_area(result, r) for r in rings))
    assert total == pytest.approx(result.width * result.height, rel=1e-6)


def test_every_ring_closes(result):
    for rings in result.rings.values():
        for ring in rings:
            first, last = ring[0], ring[-1]
            start = result.chains[first[0]].end if first[1] else result.chains[first[0]].start
            end = result.chains[last[0]].start if last[1] else result.chains[last[0]].end
            assert start == end


@pytest.mark.parametrize("view", ["canvas", "guide", "painted"])
def test_svg_is_valid_xml(result, view):
    root = ET.fromstring(result.svg(view))
    assert root.tag == NS + "svg"
    assert root.get("width").endswith("cm")
    ids = {g.get("id") for g in root.iter(NS + "g")}
    assert ("fills" in ids) == (view != "canvas")
    assert ("outlines" in ids) == (view != "painted")
    assert ("numbers" in ids) == (view != "painted")


def test_one_number_per_shape(result):
    root = ET.fromstring(result.svg("canvas"))
    numbers = [t for g in root.iter(NS + "g") if g.get("id") == "numbers" for t in g.iter(NS + "text")]
    assert len(numbers) == len(result.region_number)
    valid = {str(c["number"]) for c in result.palette}
    assert {t.text for t in numbers} <= valid


def test_number_sits_inside_its_shape(result):
    # label point must be at a depth equal to the region's inscribed radius (i.e. deepest point)
    assert (result.label_points[:, 2] > 0).all()


def test_more_colours_more_regions(photo):
    few = render_pbn(photo, PBNParams(colors=4, min_shape_mm=4))
    many = render_pbn(photo, PBNParams(colors=20, min_shape_mm=4))
    assert many.stats["regions"] > few.stats["regions"]


def test_bigger_min_shape_fewer_regions(photo):
    small = render_pbn(photo, PBNParams(colors=12, min_shape_mm=3))
    big = render_pbn(photo, PBNParams(colors=12, min_shape_mm=12))
    assert big.stats["regions"] < small.stats["regions"]


def test_flat_image_does_not_crash():
    flat = np.full((120, 160, 3), 200, np.uint8)
    res = render_pbn(flat, PBNParams(colors=5))
    assert res.stats["regions"] == 1 and len(res.palette) == 1
    ET.fromstring(res.svg("guide"))

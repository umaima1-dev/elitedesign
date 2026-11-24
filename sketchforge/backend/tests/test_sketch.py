import hashlib

import cv2
import numpy as np
import pytest

from app.engine import Focus, SketchParams, render_sketch


def h(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


@pytest.mark.parametrize("style", ["pencil", "lineart", "hatch", "value"])
def test_same_input_same_output(photo, style):
    p = SketchParams(style=style)
    a, b = render_sketch(photo, p), render_sketch(photo.copy(), p)
    assert a.shape == photo.shape and a.dtype == np.uint8
    assert h(a) == h(b)


@pytest.mark.parametrize("style", ["pencil", "hatch"])
def test_seed_changes_texture_only(photo, style):
    a = render_sketch(photo, SketchParams(style=style, seed=1))
    b = render_sketch(photo, SketchParams(style=style, seed=2))
    assert h(a) != h(b)
    # Same drawing, different grain / wobble: the overall tones must agree once blurred.
    blur = lambda x: cv2.blur(x, (15, 15)).astype(int)  # noqa: E731
    assert np.abs(blur(a) - blur(b)).mean() < 6


def test_detail_slider_adds_line_features(photo):
    def features(detail):
        out = render_sketch(photo, SketchParams(style="lineart", detail=detail))[..., 0]
        return cv2.connectedComponents((out < 128).astype(np.uint8))[0]

    assert features(60) > features(10)


def test_paper_white_stays_light(photo):
    out = render_sketch(photo, SketchParams(style="pencil"))
    assert np.percentile(out, 95) > 200


def test_focus_region_gets_more_detail(photo):
    base = SketchParams(style="lineart", detail=30, focus_boost=0)
    boosted = base.model_copy(update={"focus": Focus(x=0.3, y=0.3, w=0.4, h=0.4), "focus_boost": 70})
    a, b = render_sketch(photo, base), render_sketch(photo, boosted)
    h_, w_ = photo.shape[:2]
    inside = (slice(int(h_ * 0.35), int(h_ * 0.65)), slice(int(w_ * 0.35), int(w_ * 0.65)))
    assert (b[inside] < 128).mean() != (a[inside] < 128).mean()
    outside = (slice(0, int(h_ * 0.15)), slice(None))
    assert np.array_equal(a[outside], b[outside])  # far from the box nothing changes


def test_grid_and_paper(photo):
    out = render_sketch(photo, SketchParams(style="lineart", grid_cols=6, paper="cream"))
    assert out.shape == photo.shape
    assert out[..., 2].mean() < out[..., 0].mean()  # cream tint: blue channel lower


def test_unknown_param_rejected():
    with pytest.raises(Exception):
        SketchParams(styel="pencil")

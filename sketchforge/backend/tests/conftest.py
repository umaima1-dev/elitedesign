import io
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def make_photo(size: int = 360) -> np.ndarray:
    """Synthetic 'photo': soft gradient background, a face-like disc, shapes and mild noise.
    Fully deterministic so tests never depend on downloaded sample images."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / size
    img = np.stack([0.35 + 0.4 * xx, 0.45 + 0.3 * yy, 0.7 - 0.3 * xx], axis=-1)
    img = (img * 255).astype(np.uint8)
    c = size // 2
    cv2.circle(img, (c, c), size // 4, (224, 172, 140), -1)
    cv2.circle(img, (c - size // 12, c - size // 16), size // 40, (40, 30, 30), -1)
    cv2.circle(img, (c + size // 12, c - size // 16), size // 40, (40, 30, 30), -1)
    cv2.ellipse(img, (c, c + size // 10), (size // 12, size // 24), 0, 0, 180, (150, 50, 60), -1)
    cv2.rectangle(img, (size // 14, int(size * 0.72)), (int(size * 0.45), int(size * 0.93)), (30, 90, 40), -1)
    cv2.circle(img, (int(size * 0.8), int(size * 0.2)), size // 10, (250, 230, 120), -1)
    rng = np.random.default_rng(1)
    img = np.clip(img.astype(np.int16) + rng.normal(0, 4, img.shape), 0, 255).astype(np.uint8)
    return img


@pytest.fixture(scope="session")
def photo() -> np.ndarray:
    return make_photo()


@pytest.fixture(scope="session")
def photo_bytes(photo) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(photo).save(buf, format="JPEG", quality=92)
    return buf.getvalue()

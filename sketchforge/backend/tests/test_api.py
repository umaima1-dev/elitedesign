import json

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def post(path, photo_bytes, **data):
    return client.post(path, files={"file": ("my photo.jpg", photo_bytes, "image/jpeg")}, data=data)


def test_health_and_presets():
    assert client.get("/api/health").json()["status"] == "ok"
    p = client.get("/api/presets").json()
    assert p["sketch"] and p["pbn"]


def test_schema_drives_the_ui():
    sc = client.get("/api/schema").json()
    assert sc["sketch"]["detail"]["maximum"] == 100 and sc["sketch"]["detail"]["default"] == 60
    assert sc["pbn"]["colors"]["minimum"] == 2 and sc["pbn"]["view"]["enum"] == ["canvas", "guide", "painted"]
    assert sc["sketch"]["style"]["enum"] == ["pencil", "lineart", "hatch", "value"]


def test_process_sketch(photo_bytes):
    r = post("/api/process", photo_bytes, mode="sketch", params=json.dumps({"style": "lineart"}))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["image"].startswith("data:image/png;base64,")
    assert body["recipe"]["params"]["style"] == "lineart"
    assert len(body["recipe"]["output_sha256"]) == 64


def test_process_pbn(photo_bytes):
    r = post("/api/process", photo_bytes, mode="pbn", params=json.dumps({"colors": 6}))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["svg"].lstrip().startswith("<svg")
    assert 'id="legend"' not in body["svg"]  # previews keep the photo's proportions
    assert body["recipe"]["params"]["legend"] is True  # ...but the recipe keeps the user's choice
    assert len(body["palette"]) <= 6
    assert body["stats"]["regions"] >= 1


def test_same_request_same_hash(photo_bytes):
    args = dict(mode="pbn", params=json.dumps({"colors": 6}))
    a = post("/api/process", photo_bytes, **args).json()["recipe"]["output_sha256"]
    b = post("/api/process", photo_bytes, **args).json()["recipe"]["output_sha256"]
    assert a == b


def test_recipe_can_be_replayed(photo_bytes):
    first = post("/api/process", photo_bytes, mode="sketch", params=json.dumps({"style": "pencil", "detail": 80})).json()
    again = post("/api/process", photo_bytes, mode="sketch", params=json.dumps(first["recipe"])).json()
    assert again["recipe"]["output_sha256"] == first["recipe"]["output_sha256"]


def test_export_formats(photo_bytes):
    r = post("/api/export", photo_bytes, mode="sketch", params="{}", format="png")
    assert r.status_code == 200 and r.content[:8] == b"\x89PNG\r\n\x1a\n"
    assert 'filename="my-photo-pencil.png"' in r.headers["content-disposition"]
    r = post("/api/export", photo_bytes, mode="pbn", params=json.dumps({"colors": 6}), format="svg_painted")
    assert r.status_code == 200 and b'id="fills"' in r.content and b'id="numbers"' not in r.content
    r = post("/api/export", photo_bytes, mode="pbn", params=json.dumps({"colors": 6}), format="svg_canvas")
    assert r.status_code == 200 and b'id="legend"' in r.content and b'id="fills"' not in r.content
    r = post("/api/export", photo_bytes, mode="pbn", params=json.dumps({"colors": 6}), format="recipe")
    assert json.loads(r.content)["mode"] == "pbn"


def test_errors(photo_bytes):
    assert post("/api/process", b"not an image", mode="sketch").status_code == 400
    assert post("/api/process", photo_bytes, mode="sketch", params='{"detail": 999}').status_code == 422
    assert post("/api/process", photo_bytes, mode="sketch", params="{oops").status_code == 422
    assert post("/api/process", photo_bytes, mode="banana").status_code == 400
    assert post("/api/export", photo_bytes, mode="sketch", params="{}", format="svg").status_code == 400

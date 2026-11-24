"""HTTP API. Everything heavy runs in a worker thread so the server stays responsive."""
from __future__ import annotations

import base64
import json
import os
import re

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, Response
from pydantic import ValidationError

from . import service
from .engine import ENGINE_VERSION, PBNParams, SketchParams
from .presets import all_presets

MAX_UPLOAD_BYTES = 30 * 1024 * 1024

app = FastAPI(title="SketchForge", version=ENGINE_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.environ.get(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


async def _read(file: UploadFile) -> bytes:
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"File is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.")
    if not data:
        raise HTTPException(400, "Empty file.")
    return data


def _execute(data: bytes, mode: str, params: str, quality: str, max_side: int | None):
    try:
        return service.run(data, mode, params, quality, max_side)
    except ValidationError as exc:
        raise HTTPException(422, detail=json.loads(exc.json())) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(422, "params is not valid JSON.") from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/api/health")
def health():
    return {"status": "ok", "engine_version": ENGINE_VERSION}


def _flat_schema(model) -> dict:
    """Flatten a pydantic model into {field: {type, minimum, maximum, default, ...}} for the UI."""
    out = {}
    for name, prop in model.model_json_schema()["properties"].items():
        spec = dict(prop)
        if "anyOf" in prop:
            branches = [b for b in prop["anyOf"] if b.get("type") != "null"]
            spec = {**prop, **(branches[0] if branches else {})}
        out[name] = {
            "type": spec.get("type"),
            "minimum": spec.get("minimum", spec.get("exclusiveMinimum")),
            "maximum": spec.get("maximum"),
            "default": prop.get("default"),
            "description": prop.get("description"),
            "enum": spec.get("enum"),
        }
    return out


@app.get("/api/schema")
def schema():
    return {"sketch": _flat_schema(SketchParams), "pbn": _flat_schema(PBNParams)}


@app.get("/api/presets")
def presets():
    return all_presets()


@app.post("/api/process")
async def process(
    file: UploadFile = File(...),
    mode: str = Form(...),
    params: str = Form("{}"),
    quality: str = Form("preview"),
    max_side: int | None = Form(None),
):
    if quality not in ("preview", "full"):
        raise HTTPException(422, "quality must be 'preview' or 'full'.")
    data = await _read(file)
    out = await run_in_threadpool(_execute, data, mode, params, quality, max_side)
    body = {
        "mode": out.mode,
        "quality": quality,
        "width": out.width,
        "height": out.height,
        "stats": out.stats,
        "recipe": out.recipe,
        "ms": out.ms,
    }
    if out.png is not None:
        body["image"] = "data:image/png;base64," + base64.b64encode(out.png).decode("ascii")
    if out.svg is not None:
        body["svg"] = out.svg
        body["palette"] = out.palette
    return JSONResponse(body)


@app.post("/api/export")
async def export(
    file: UploadFile = File(...),
    mode: str = Form(...),
    params: str = Form("{}"),
    format: str = Form(...),
    max_side: int | None = Form(None),
):
    """Full-resolution download. format: png | svg | svg_canvas | svg_guide | svg_painted | recipe"""
    data = await _read(file)
    stem = re.sub(r"[^A-Za-z0-9_-]+", "-", os.path.splitext(file.filename or "photo")[0]).strip("-") or "photo"

    def _go():
        if format.startswith("svg") and mode == "pbn" and format != "svg":
            view = format.split("_", 1)[1]
            if view not in ("canvas", "guide", "painted"):
                raise ValueError("Unknown SVG view.")
            parsed = json.loads(params) if params.strip() else {}
            parsed = {**(parsed.get("params", parsed) if isinstance(parsed, dict) else {}), "view": view}
            return service.run(data, mode, parsed, "full", max_side)
        return service.run(data, mode, params, "full", max_side)

    try:
        out = await run_in_threadpool(_go)
    except ValidationError as exc:
        raise HTTPException(422, detail=json.loads(exc.json())) from exc
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(400, str(exc)) from exc

    label = out.recipe["params"].get("style") if mode == "sketch" else out.recipe["params"].get("view")
    if format == "recipe":
        body = json.dumps(out.recipe, indent=2).encode()
        return Response(body, media_type="application/json",
                        headers={"Content-Disposition": f'attachment; filename="{stem}-{mode}-recipe.json"'})
    if format == "png" and out.png is not None:
        return Response(out.png, media_type="image/png",
                        headers={"Content-Disposition": f'attachment; filename="{stem}-{label}.png"'})
    if format.startswith("svg") and out.svg is not None:
        return Response(out.svg.encode(), media_type="image/svg+xml",
                        headers={"Content-Disposition": f'attachment; filename="{stem}-pbn-{label}.svg"'})
    raise HTTPException(400, f"Format '{format}' is not available for mode '{mode}'.")

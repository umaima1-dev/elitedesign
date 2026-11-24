"""Command line access, handy for batch jobs:

  python -m app.cli sketch photo.jpg -o out.png --preset "Realistic pencil portrait"
  python -m app.cli pbn photo.jpg -o out.svg --set colors=18 --set min_shape_mm=4
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .presets import PBN_PRESETS, SKETCH_PRESETS
from . import service


def _coerce(v: str):
    try:
        return json.loads(v)
    except json.JSONDecodeError:
        return v


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sketchforge")
    ap.add_argument("mode", choices=["sketch", "pbn"])
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--preset", help="Preset name (see presets.py)")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--recipe", help="Re-run from a recipe JSON file")
    ap.add_argument("--max-side", type=int)
    ap.add_argument("--preview", action="store_true", help="Fast low-resolution render")
    a = ap.parse_args(argv)

    params: dict = {}
    if a.recipe:
        params = json.loads(Path(a.recipe).read_text())
    elif a.preset:
        table = SKETCH_PRESETS if a.mode == "sketch" else PBN_PRESETS
        if a.preset not in table:
            ap.error(f"unknown preset. choose from: {', '.join(table)}")
        params = dict(table[a.preset])
    for kv in a.set:
        k, _, v = kv.partition("=")
        if isinstance(params, dict) and "params" in params:
            params = params["params"]
        params[k] = _coerce(v)

    out = service.run(Path(a.input).read_bytes(), a.mode, params,
                      "preview" if a.preview else "full", a.max_side)
    dest = Path(a.output)
    if out.png is not None:
        dest.write_bytes(out.png)
    else:
        dest.write_text(out.svg)
    dest.with_suffix(".recipe.json").write_text(json.dumps(out.recipe, indent=2))
    print(f"{dest}  ({out.width}x{out.height}, {out.ms} ms, sha256 {out.recipe['output_sha256'][:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Turn a saved-posts export into saved.json.

Accepts: Instagram's official export (.zip or unzipped folder), a .json file, a .csv file,
an .html file, or a plain .txt with one URL per line. Anything else is scanned for
Instagram links with a regex, so a pasted list of URLs works too.

Usage:  parse_saved.py <file-or-folder-or-url> [more...] [-o saved.json]
A bare reel URL works too. If the output file already exists, new links are merged into it
(nothing is lost, duplicates are ignored), so you can keep adding reels over time.
"""
import argparse
import csv
import io
import json
import re
import sys
import zipfile
from pathlib import Path

URL_RE = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?:([A-Za-z0-9_.]+)/)?(reel|reels|p|tv)/([A-Za-z0-9_-]+)",
    re.I,
)
TEXT_SUFFIXES = {".json", ".csv", ".html", ".htm", ".txt", ".md", ".tsv"}
CREATOR_KEYS = ("creator", "username", "owner", "author", "account", "uploader", "title", "name")
TIME_KEYS = ("saved", "date", "time", "timestamp")
SKIP_CODES = {"audio", "explore"}


def fix_mojibake(s):
    """Meta exports double-encode UTF-8 as latin-1; undo that for names and captions."""
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


class Collector:
    def __init__(self):
        self.items = {}  # shortcode -> entry (insertion ordered)

    def add(self, text, creator=None, ts=None):
        for m in URL_RE.finditer(text):
            user, kind, code = m.group(1), m.group(2).lower(), m.group(3)
            if code.lower() in SKIP_CODES:
                continue
            path = "reel" if kind in ("reel", "reels") else kind
            entry = self.items.setdefault(
                code,
                {
                    "shortcode": code,
                    "url": f"https://www.instagram.com/{path}/{code}/",
                    "kind": path,
                    "creator": None,
                    "saved_at": None,
                },
            )
            who = creator or (user if user and user.lower() not in ("reel", "p", "tv") else None)
            if who and not entry["creator"]:
                entry["creator"] = fix_mojibake(str(who)).lstrip("@")
            if ts and not entry["saved_at"]:
                entry["saved_at"] = ts


def walk_json(node, ctx, out):
    if isinstance(node, dict):
        ctx = dict(ctx)
        title = node.get("title")
        if isinstance(title, str) and title.strip():
            ctx["creator"] = title.strip()
        label = str(node.get("label", "")).lower()
        if label in ("username", "owner", "creator") and isinstance(node.get("value"), str):
            ctx["creator"] = node["value"]
        if isinstance(node.get("timestamp"), (int, float)) and node["timestamp"] > 0:
            ctx["ts"] = int(node["timestamp"])
        for v in node.values():
            walk_json(v, ctx, out)
    elif isinstance(node, list):
        for v in node:
            walk_json(v, ctx, out)
    elif isinstance(node, str):
        out.add(node, ctx.get("creator"), ctx.get("ts"))


def read_csv(text, out):
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.DictReader(io.StringIO(text), dialect=dialect))
    if not rows or not rows[0] or not any(URL_RE.search(str(v or "")) for r in rows[:20] for v in r.values()):
        out.add(text)  # headerless csv or one url per line
        return
    for row in rows:
        lowered = {str(k).lower().strip(): (v or "").strip() for k, v in row.items() if k}
        url_cell = next((v for v in lowered.values() if URL_RE.search(v)), None)
        if not url_cell:
            continue
        creator = next(
            (lowered[k] for c in CREATOR_KEYS for k in lowered if c in k and lowered[k] and not URL_RE.search(lowered[k])),
            None,
        )
        ts = next((lowered[k] for c in TIME_KEYS for k in lowered if c in k and lowered[k]), None)
        out.add(url_cell, creator, ts)


def read_text(name, raw, out):
    text = raw.decode("utf-8", errors="replace")
    suffix = Path(name).suffix.lower()
    if suffix == ".json":
        try:
            walk_json(json.loads(text), {}, out)
            return
        except json.JSONDecodeError:
            pass
    elif suffix in (".csv", ".tsv"):
        read_csv(text, out)
        return
    out.add(text)


def load(path, out):
    if re.match(r"https?://", str(path)):
        out.add(str(path))
        return
    p = Path(path)
    members = []  # (name, bytes)
    if p.is_dir():
        for f in sorted(p.rglob("*")):
            if f.is_file() and f.suffix.lower() in TEXT_SUFFIXES:
                members.append((str(f), f.read_bytes()))
    elif p.suffix.lower() == ".zip":
        with zipfile.ZipFile(p) as z:  # read in memory: nothing is extracted to disk
            for n in z.namelist():
                if Path(n).suffix.lower() in TEXT_SUFFIXES:
                    members.append((n, z.read(n)))
    elif p.is_file():
        members.append((str(p), p.read_bytes()))
    else:
        sys.exit(f"Not found: {path}")
    # A full Instagram export also holds likes, comments, etc. Prefer files about saves.
    saved_only = [m for m in members if "saved" in m[0].lower()]
    for name, raw in saved_only or members:
        read_text(name, raw, out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", nargs="+", help="export zip/folder, .json, .csv, .html, .txt, or a reel URL")
    ap.add_argument("-o", "--out", default="saved.json")
    args = ap.parse_args()

    out = Collector()
    existing = Path(args.out)
    before = 0
    if existing.exists():
        for e in json.loads(existing.read_text()):
            out.items[e["shortcode"]] = e
        before = len(out.items)
    for s in args.source:
        load(s, out)
    items = list(out.items.values())
    if not items:
        sys.exit("No Instagram post or reel links found in that file.")
    Path(args.out).write_text(json.dumps(items, indent=2, ensure_ascii=False))
    reels = sum(1 for i in items if i["kind"] == "reel")
    new = f", {len(items) - before} new" if before else ""
    print(f"{len(items)} saved items ({reels} reels, {len(items) - reels} posts/IGTV{new}) -> {args.out}")


if __name__ == "__main__":
    main()

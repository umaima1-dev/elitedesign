#!/usr/bin/env python3
"""Outlier scoring for Outlier Scout and Analyst. Standard library only.

Input: JSON list of posts. Fields: creator, url, views, likes, comments,
saves (optional), shares (optional), format (optional), posted (optional).

Baseline = median views of the creator's OTHER posts (leave-one-out), so one
viral post cannot inflate its own baseline.
"""
import argparse, json, os, statistics, sys
from collections import defaultdict

def score(posts, multiplier=5.0, min_posts=8):
    by = defaultdict(list)
    for p in posts:
        by[p["creator"]].append(p)
    out, skipped = [], {}
    for creator, ps in by.items():
        if len(ps) < min_posts:
            skipped[creator] = len(ps)
            continue
        for i, p in enumerate(ps):
            others = [q["views"] for j, q in enumerate(ps) if j != i]
            base = statistics.median(others)
            if base <= 0:
                continue
            mult = p["views"] / base
            inter = p.get("likes", 0) + p.get("comments", 0) + p.get("saves", 0) + p.get("shares", 0)
            row = dict(p, baseline=base, multiplier=round(mult, 2),
                       engagement_ratio=round(inter / p["views"], 4) if p["views"] else 0.0,
                       is_outlier=mult >= multiplier)
            out.append(row)
    out.sort(key=lambda r: (r["multiplier"], r["engagement_ratio"]), reverse=True)
    return out, skipped

def cfg():
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    try:
        return json.load(open(p))
    except (OSError, ValueError):
        return {}

def main(argv=None):
    c = cfg()
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--multiplier", type=float, default=c.get("outlier_multiplier", 5.0), help="outlier threshold (default from config.json)")
    ap.add_argument("--min-posts", type=int, default=c.get("min_posts_for_baseline", 8), help="posts needed for a reliable baseline")
    ap.add_argument("--all", action="store_true", help="show non-outliers too")
    a = ap.parse_args(argv)
    posts = json.load(open(a.data))
    rows, skipped = score(posts, a.multiplier, a.min_posts)
    if not a.all:
        rows = [r for r in rows if r["is_outlier"]]
    print(f"| Creator | Multiplier | Views | Baseline | Eng/views | Format | Link |\n|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['creator']} | {r['multiplier']}x | {r['views']} | {int(r['baseline'])} | {r['engagement_ratio']} | {r.get('format','')} | {r['url']} |")
    for c, n in skipped.items():
        print(f"\nSkipped {c}: only {n} posts, need {a.min_posts} for a baseline.", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())

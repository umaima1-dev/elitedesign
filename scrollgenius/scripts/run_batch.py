#!/usr/bin/env python3
"""Process every reel in saved.json one by one. Safe to stop and rerun: finished reels are skipped.

Usage:
  run_batch.py ~/ScrollGenius/saved.json              # everything (work folder defaults to ~/ScrollGenius)
  run_batch.py ~/ScrollGenius/saved.json --limit 5    # trial run first
  run_batch.py saved.json --cookies-from-browser chrome         # if Instagram blocks anonymous downloads
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

from process_reel import Transcriber, process


def read_status(work, code):
    f = Path(work) / "reels" / code / "status.json"
    return json.loads(f.read_text()) if f.exists() else None


def write_index(items, work):
    index = []
    for it in items:
        st = read_status(work, it["shortcode"]) or {"state": "pending"}
        row = {"shortcode": it["shortcode"], "url": it["url"], "creator": it.get("creator"), "state": st["state"]}
        meta_f = Path(work) / "reels" / it["shortcode"] / "meta.json"
        if meta_f.exists():
            meta = json.loads(meta_f.read_text())
            row.update(creator=meta.get("creator") or row["creator"], caption=meta.get("caption", "")[:160])
        row.update({k: st[k] for k in ("transcript_words", "frames", "error") if st.get(k) is not None})
        index.append(row)
    (Path(work) / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False))
    return index


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("saved", help="saved.json from parse_saved.py")
    ap.add_argument("--work", default=str(Path.home() / "ScrollGenius"))
    ap.add_argument("--model", default="base", help="whisper model: tiny (fastest), base (default), small")
    ap.add_argument("--language", default=None)
    ap.add_argument("--limit", type=int, default=0, help="only process this many pending reels")
    ap.add_argument("--max-frames", type=int, default=8)
    ap.add_argument("--keep-video", action="store_true")
    ap.add_argument("--retry-failed", action="store_true")
    ap.add_argument("--sleep", type=float, default=4.0, help="average pause between downloads (be polite to Instagram)")
    ap.add_argument("--cookies-from-browser", metavar="BROWSER", help="chrome, firefox, safari, edge...")
    ap.add_argument("--cookies", metavar="FILE", help="cookies.txt in Netscape format")
    a = ap.parse_args()

    items = json.loads(Path(a.saved).read_text())
    Path(a.work).mkdir(parents=True, exist_ok=True)
    todo = []
    for it in items:
        st = read_status(a.work, it["shortcode"])
        if st is None or (st["state"] == "failed" and a.retry_failed):
            todo.append(it)
    if a.limit:
        todo = todo[: a.limit]
    done_before = sum(1 for it in items if (read_status(a.work, it["shortcode"]) or {}).get("state") == "done")
    print(f"{len(items)} saved | {done_before} already done | {len(todo)} to process now", flush=True)
    if not todo:
        write_index(items, a.work)
        return

    transcriber = Transcriber(a.model, a.language)
    print(f"Whisper: {transcriber.backend} ({a.model})", flush=True)
    ok = failed = blocked_streak = 0
    try:
        for n, it in enumerate(todo, 1):
            t0 = time.time()
            try:
                st = process(it, a.work, transcriber, a.max_frames, a.keep_video, a.cookies_from_browser, a.cookies)
            except Exception as e:  # one bad reel must never stop the batch
                st = {"state": "failed", "error": f"{type(e).__name__}: {e}"}
                (Path(a.work) / "reels" / it["shortcode"]).mkdir(parents=True, exist_ok=True)
                (Path(a.work) / "reels" / it["shortcode"] / "status.json").write_text(json.dumps(st))
            if st["state"] == "done":
                ok += 1
                blocked_streak = 0
                detail = f"{st.get('transcript_words', 0)} words, {st.get('frames', 0)} frames"
            else:
                failed += 1
                blocked_streak = blocked_streak + 1 if st.get("needs_login") else 0
                detail = f"FAILED: {st.get('error')}"
            print(f"[{n}/{len(todo)}] {it['shortcode']} {time.time() - t0:.0f}s  {detail}", flush=True)
            if blocked_streak >= 3 and not (a.cookies_from_browser or a.cookies):
                print("\nInstagram is blocking anonymous downloads. Stop here and rerun with "
                      "--cookies-from-browser chrome (use the browser you are logged in to).", flush=True)
                break
            if n < len(todo):
                time.sleep(random.uniform(a.sleep * 0.5, a.sleep * 1.5))
    except KeyboardInterrupt:
        print("\nStopped. Rerun the same command to continue where you left off.")
    index = write_index(items, a.work)
    states = [r["state"] for r in index]
    print(f"\nDone this run: {ok} ok, {failed} failed. Overall: {states.count('done')} done, "
          f"{states.count('failed')} failed, {states.count('pending')} pending. Index: {a.work}/index.json")


if __name__ == "__main__":
    sys.exit(main())

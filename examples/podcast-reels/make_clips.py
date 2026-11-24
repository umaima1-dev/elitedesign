#!/usr/bin/env python3
"""
make_clips.py - download a YouTube podcast ONCE and cut it into short vertical clips
for index.html (the "one podcast, many clips" animation).

    pip install yt-dlp          # plus ffmpeg on your PATH
    python make_clips.py "https://youtu.be/Kl-I7sUcAOY"

Output (next to index.html):
    clips/clip_01.mp4 ...       9:16, 360x640, silent, small
    clips/main.mp4              short 16:9 preview of the full episode (the centre video)
    clips/main.jpg              poster frame
    clips.js                    config the page reads (works from file://, no server needed)

Which moments? YouTube's "Most replayed" graph if the video has one, otherwise evenly spaced.
Captions come from the video's subtitles if available, else chapter titles, else "Clip N".

Already have the file?   python make_clips.py --input episode.mp4
If YouTube asks you to sign in:  add  --cookies-from-browser chrome
"""
import argparse, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def need(tool):
    if not shutil.which(tool):
        sys.exit(f"'{tool}' not found on PATH. Install it first (yt-dlp: pip install yt-dlp, ffmpeg: https://ffmpeg.org).")


def probe_duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], text=True)
    return float(out.strip())


def download(url, work, cookies_browser):
    need("yt-dlp")
    cmd = ["yt-dlp", "--no-playlist", "-f", "bv*[height<=720]+ba/b[height<=720]", "--merge-output-format", "mp4",
           "--write-info-json", "--write-subs", "--write-auto-subs", "--sub-langs", "en.*,en", "--sub-format", "vtt",
           "-o", str(work / "source.%(ext)s"), url]
    if cookies_browser:
        cmd[1:1] = ["--cookies-from-browser", cookies_browser]
    run(cmd)
    video = work / "source.mp4"
    info_path = work / "source.info.json"
    info = json.loads(info_path.read_text()) if info_path.exists() else {}
    vtts = sorted(work.glob("source*.vtt"))
    return video, info, (vtts[0] if vtts else None)


# ---------- subtitles ----------
def ts(s):
    parts = s.replace(",", ".").split(":")
    parts = [float(p) for p in parts]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def parse_vtt(path):
    cues = []
    if not path:
        return cues
    blocks = re.split(r"\n\s*\n", Path(path).read_text(encoding="utf-8", errors="ignore"))
    for b in blocks:
        lines = [l for l in b.strip().splitlines() if l.strip()]
        for k, l in enumerate(lines):
            m = re.match(r"(\S+)\s+-->\s+(\S+)", l)
            if m:
                text = " ".join(lines[k + 1:])
                text = re.sub(r"<[^>]+>", "", text)
                text = re.sub(r"\s+", " ", text).strip()
                if text:
                    cues.append((ts(m.group(1)), ts(m.group(2)), text))
                break
    return cues


def caption_for(cues, start, end, words=6):
    seen, out = set(), []
    for a, b, t in cues:
        if b < start or a > end:
            continue
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    txt = " ".join(out)
    # auto-captions roll: drop immediate word repeats
    toks = []
    for w in txt.split():
        if not toks or toks[-1].lower() != w.lower():
            toks.append(w)
    toks = toks[:words]
    cap = " ".join(toks).strip(" ,.;:-")
    return cap.upper()


# ---------- picking moments ----------
def pick_starts(duration, count, length, heatmap):
    lo, hi = duration * 0.03, max(duration * 0.97 - length, duration * 0.03)
    chosen = []
    if heatmap:
        peaks = sorted(heatmap, key=lambda h: h.get("value", 0), reverse=True)
        for h in peaks:
            s = max(0.0, h["start_time"] - 1.0)
            if s < lo or s > hi:
                continue
            if all(abs(s - c) >= length * 1.5 for c in chosen):
                chosen.append(s)
            if len(chosen) == count:
                break
    if len(chosen) < count:  # top up with evenly spaced moments
        step = (hi - lo) / max(count, 1)
        for k in range(count):
            s = lo + step * (k + 0.5)
            if all(abs(s - c) >= 2.0 for c in chosen):
                chosen.append(s)
            if len(chosen) == count:
                break
    return sorted(chosen)[:count]


def chapter_at(chapters, t):
    for c in chapters or []:
        if c["start_time"] <= t < c["end_time"]:
            return c["title"]
    return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", nargs="?", help="YouTube URL")
    ap.add_argument("--input", help="use a local video instead of downloading")
    ap.add_argument("--subs", help="optional .vtt subtitle file to use for captions")
    ap.add_argument("--out", default=str(HERE), help="folder that holds index.html (default: next to this script)")
    ap.add_argument("--count", type=int, default=12, help="number of clips (default 12)")
    ap.add_argument("--len", type=float, default=8, help="seconds per clip (default 8)")
    ap.add_argument("--main-len", type=float, default=40, help="seconds in the centre preview (default 40)")
    ap.add_argument("--title", help="title shown on the centre video")
    ap.add_argument("--cookies-from-browser", help="e.g. chrome, firefox, safari")
    ap.add_argument("--keep", action="store_true", help="keep the downloaded source in ./source/")
    a = ap.parse_args()

    if not a.url and not a.input:
        ap.error("give a YouTube URL or --input file")
    need("ffmpeg"); need("ffprobe")

    out = Path(a.out); clips_dir = out / "clips"; clips_dir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="podcast_"))
    info, vtt = {}, a.subs

    try:
        if a.input:
            video = Path(a.input).resolve()
        else:
            print("Downloading the episode once...")
            video, info, auto_vtt = download(a.url, work, a.cookies_from_browser)
            vtt = vtt or auto_vtt

        dur = float(info.get("duration") or probe_duration(video))
        cues = parse_vtt(vtt)
        starts = pick_starts(dur, a.count, a.len, info.get("heatmap"))
        print(f"Cutting {len(starts)} clips of {a.len:g}s from a {dur/60:.1f} min episode...")

        # clear old clips so stale files don't linger
        for f in clips_dir.glob("clip_*.mp4"):
            f.unlink()

        vf = "crop='min(iw,ih*9/16)':'min(ih,iw*16/9)',scale=360:640,fps=30"
        meta = []
        for n, s in enumerate(starts, 1):
            name = f"clip_{n:02d}.mp4"
            run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{s:.2f}", "-t", f"{a.len:.2f}", "-i", str(video),
                 "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "27", "-pix_fmt", "yuv420p",
                 "-movflags", "+faststart", str(clips_dir / name)])
            cap = caption_for(cues, s, s + a.len) or chapter_at(info.get("chapters"), s).upper() or f"CLIP {n}"
            tag = chapter_at(info.get("chapters"), s)[:18]
            meta.append({"src": f"clips/{name}", "caption": cap, "tag": tag, "start": round(s), "end": round(s + a.len)})
            print(f"  {name}  {int(s//60)}:{int(s%60):02d}  {cap}")

        # centre preview: short, light 16:9 stand-in for the full episode
        ms = min(30.0, dur * 0.05)
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ms:.2f}", "-t", f"{a.main_len:.2f}", "-i", str(video),
             "-vf", "scale=960:-2,fps=24", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(clips_dir / "main.mp4")])
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ms + 2:.2f}", "-i", str(video), "-frames:v", "1",
             "-vf", "scale=1280:-2", "-q:v", "3", str(clips_dir / "main.jpg")])

        mins = int(dur // 60); secs = int(dur % 60)
        podcast = {
            "title": a.title or info.get("title") or "Full episode",
            "youtubeId": info.get("id") or "",
            "main": "clips/main.mp4", "poster": "clips/main.jpg",
            "duration": f"{mins}:{secs:02d}", "durationSec": round(dur),
        }
        (out / "clips.js").write_text(
            "// generated by make_clips.py\nwindow.PODCAST = " + json.dumps(podcast, indent=2) +
            ";\nwindow.CLIPS = " + json.dumps(meta, indent=2) + ";\n", encoding="utf-8")
        print(f"\nDone. Open {out / 'index.html'} in your browser.")

        if a.keep and not a.input:
            keep = out / "source"; keep.mkdir(exist_ok=True); shutil.copy(video, keep / "source.mp4")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

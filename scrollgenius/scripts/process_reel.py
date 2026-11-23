#!/usr/bin/env python3
"""Download one reel, transcribe it, grab keyframes, and write a digest Claude can read.

Per reel it creates  <work>/reels/<shortcode>/
    digest.md       caption + transcript + on-screen text + frame list (the file Claude reads)
    transcript.txt  spoken words
    ocr.txt         on-screen text (only if tesseract is installed)
    frames/*.jpg    evenly spaced keyframes (Claude can look at these)
    meta.json       creator, caption, duration, url
    status.json     done | failed (+ reason), so reruns skip finished reels

Usage (one reel):  process_reel.py <url> [--work scrollgenius_work]
Use run_batch.py for a whole saved.json.
"""
import argparse
import functools
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

LOGIN_HINTS = ("login required", "rate-limit", "rate limit", "empty media response", "cookies", "sign in", "log in")


def run(cmd, timeout=600):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def ytdlp_cmd():
    exe = shutil.which("yt-dlp")
    return [exe] if exe else [sys.executable, "-m", "yt_dlp"]


class Transcriber:
    """Loads a small Whisper model once and reuses it for every reel."""

    def __init__(self, model="base", language=None):
        self.language = language
        try:
            from faster_whisper import WhisperModel

            self.backend = "faster-whisper"
            self.model = self._load(lambda: WhisperModel(model, device="cpu", compute_type="int8"), model)
        except ImportError:
            try:
                import whisper

                self.backend = "openai-whisper"
                self.model = self._load(lambda: whisper.load_model(model), model)
            except ImportError:
                sys.exit("No Whisper found. Run: pip install faster-whisper")

    @staticmethod
    def _load(loader, model):
        try:
            return loader()
        except Exception as e:  # first run downloads the model (about 150 MB for base)
            sys.exit(f"Could not load Whisper model '{model}': {type(e).__name__}: {e}\n"
                     "The first run downloads the model, so it needs internet access. Check your connection and retry.")

    def transcribe(self, wav):
        if self.backend == "faster-whisper":
            segments, info = self.model.transcribe(wav, language=self.language, beam_size=1, vad_filter=True)
            return " ".join(s.text.strip() for s in segments).strip(), info.language
        res = self.model.transcribe(wav, language=self.language, fp16=False)
        return res["text"].strip(), res.get("language")


@functools.lru_cache(maxsize=1)
def ffmpeg_exe():
    """System ffmpeg if present, else the copy bundled by imageio-ffmpeg (installs without admin rights)."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found. Run: python scripts/bootstrap.py")


def media_info(path):
    """(duration_seconds, has_audio) read from `ffmpeg -i`, so ffprobe is not needed."""
    err = run([ffmpeg_exe(), "-hide_banner", "-i", str(path)], 60).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", err)
    duration = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0
    return duration, bool(re.search(r"Stream #.*Audio:", err))


def download(url, folder, cookies_from_browser=None, cookies_file=None):
    """Returns (video_path, error_text)."""
    cmd = ytdlp_cmd() + [
        "--no-playlist", "--write-info-json", "--no-progress", "--no-warnings",
        "-S", "res:480", "-f", "bv*+ba/b",           # small file: transcript + frames do not need HD
        "--retries", "3", "--socket-timeout", "30", "--ffmpeg-location", ffmpeg_exe(),
        "-o", str(folder / "video.%(ext)s"),
    ]
    if cookies_from_browser:
        cmd += ["--cookies-from-browser", cookies_from_browser]
    if cookies_file:
        cmd += ["--cookies", cookies_file]
    res = run(cmd + [url], timeout=600)
    videos = [p for p in folder.glob("video.*") if p.suffix not in (".json", ".part", ".ytdl")]
    if res.returncode != 0 or not videos:
        err = (res.stderr.strip().splitlines() or ["download failed"])[-1]
        return None, err
    return videos[0], None


def extract_audio(video, wav, has_audio):
    if not has_audio:
        return False  # silent reel (music-only edits or screen recordings with no audio track)
    res = run([ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    return res.returncode == 0 and wav.exists()


def extract_frames(video, frames_dir, duration, max_frames):
    frames_dir.mkdir(exist_ok=True)
    interval = max(1.5, (duration or 30) / max_frames)
    run([
        ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(video),
        "-vf", f"fps=1/{interval:.2f},scale='min(720,iw)':-2",
        "-frames:v", str(max_frames), "-q:v", "4", str(frames_dir / "f_%02d.jpg"),
    ])
    return sorted(frames_dir.glob("f_*.jpg"))


def ocr_frames(frames):
    """On-screen text via tesseract if available. Returns '' otherwise (Claude reads frames itself)."""
    if not shutil.which("tesseract"):
        return ""
    seen, lines = set(), []
    for f in frames:
        res = run(["tesseract", str(f), "stdout", "-l", "eng", "--psm", "11"], 60)
        for ln in res.stdout.splitlines():
            ln = re.sub(r"\s+", " ", ln).strip()
            if len(ln) > 3 and re.search(r"[A-Za-z]{3}", ln) and ln.lower() not in seen:
                seen.add(ln.lower())
                lines.append(ln)
    return "\n".join(lines)


def write_digest(folder, meta, transcript, ocr, frames):
    parts = [
        f"# {meta.get('title') or meta['shortcode']}",
        f"Creator: @{meta.get('creator') or 'unknown'}  |  URL: {meta['url']}  |  Length: {meta.get('duration') or '?'}s",
        "", "## Caption", meta.get("caption") or "(none)",
        "", "## Spoken (transcript)", transcript or "(no speech detected)",
        "", "## On-screen text (OCR)", ocr or "(not extracted: look at the frames)",
        "", "## Frames (view these when the transcript is thin or says 'look at this')",
        *[f"- {f.relative_to(folder)}" for f in frames],
    ]
    (folder / "digest.md").write_text("\n".join(parts), encoding="utf-8")


def process(entry, work, transcriber, max_frames=8, keep_video=False,
            cookies_from_browser=None, cookies_file=None):
    code, url = entry["shortcode"], entry["url"]
    folder = Path(work) / "reels" / code
    folder.mkdir(parents=True, exist_ok=True)
    status = {"shortcode": code, "state": "failed", "error": None}

    video, err = download(url, folder, cookies_from_browser, cookies_file)
    if not video:
        status["error"] = err
        status["needs_login"] = any(h in err.lower() for h in LOGIN_HINTS)
        (folder / "status.json").write_text(json.dumps(status, indent=2))
        return status

    info = {}
    info_file = next(folder.glob("video.info.json"), None)
    if info_file:
        info = json.loads(info_file.read_text(encoding="utf-8"))
        info_file.unlink()
    duration, has_audio = media_info(video)
    duration = duration or float(info.get("duration") or 0)
    meta = {
        "shortcode": code, "url": url,
        "creator": info.get("uploader") or info.get("channel") or info.get("uploader_id") or entry.get("creator"),
        "caption": (info.get("description") or info.get("title") or "").strip(),
        "title": (info.get("title") or "")[:100],
        "duration": round(duration, 1), "upload_date": info.get("upload_date"),
    }
    (folder / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    transcript, lang = "", None
    wav = folder / "audio.wav"
    if extract_audio(video, wav, has_audio):
        transcript, lang = transcriber.transcribe(str(wav))
        wav.unlink(missing_ok=True)
    (folder / "transcript.txt").write_text(transcript, encoding="utf-8")

    frames = extract_frames(video, folder / "frames", duration, max_frames)
    ocr = ocr_frames(frames)
    if ocr:
        (folder / "ocr.txt").write_text(ocr, encoding="utf-8")
    write_digest(folder, meta, transcript, ocr, frames)

    if not keep_video:
        video.unlink(missing_ok=True)
    status.update(state="done", error=None, language=lang, transcript_words=len(transcript.split()),
                  frames=len(frames), has_ocr=bool(ocr))
    (folder / "status.json").write_text(json.dumps(status, indent=2))
    return status


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--work", default="scrollgenius_work")
    ap.add_argument("--model", default="base", help="whisper model: tiny, base (default), small")
    ap.add_argument("--language", default=None, help="force a language code, e.g. en. Default: auto-detect")
    ap.add_argument("--max-frames", type=int, default=8)
    ap.add_argument("--keep-video", action="store_true")
    ap.add_argument("--cookies-from-browser", metavar="BROWSER")
    ap.add_argument("--cookies", metavar="FILE")
    a = ap.parse_args()
    m = re.search(r"/(?:reel|reels|p|tv)/([A-Za-z0-9_-]+)", a.url)
    entry = {"shortcode": m.group(1) if m else "reel", "url": a.url}
    st = process(entry, a.work, Transcriber(a.model, a.language), a.max_frames, a.keep_video,
                 a.cookies_from_browser, a.cookies)
    print(json.dumps(st, indent=2))
    sys.exit(0 if st["state"] == "done" else 1)


if __name__ == "__main__":
    main()

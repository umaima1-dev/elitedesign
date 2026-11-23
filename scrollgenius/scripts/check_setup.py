#!/usr/bin/env python3
"""Check that everything ScrollGenius needs is installed, and say how to fix what is not."""
import importlib.util
import platform
import shutil
import sys

ok = True


def line(good, name, detail=""):
    global ok
    print(f"[{'ok' if good else 'MISSING'}] {name} {detail}")


def need(good, name, fix):
    global ok
    ok = ok and good
    line(good, name, "" if good else f"-> {fix}")


system = platform.system()
ff_fix = {"Darwin": "brew install ffmpeg", "Windows": "winget install ffmpeg", "Linux": "sudo apt install ffmpeg"}.get(
    system, "install ffmpeg from ffmpeg.org"
)

need(sys.version_info >= (3, 9), f"python {sys.version.split()[0]}", "use Python 3.9 or newer")
need(bool(shutil.which("ffmpeg")), "ffmpeg", ff_fix)
need(bool(shutil.which("ffprobe")), "ffprobe (ships with ffmpeg)", ff_fix)
need(
    bool(shutil.which("yt-dlp")) or importlib.util.find_spec("yt_dlp") is not None,
    "yt-dlp",
    "pip install -U yt-dlp",
)
has_fw = importlib.util.find_spec("faster_whisper") is not None
has_ow = importlib.util.find_spec("whisper") is not None
need(has_fw or has_ow, "whisper (faster-whisper or openai-whisper)", "pip install faster-whisper")
line(bool(shutil.which("tesseract")), "tesseract (optional OCR for on-screen text)",
     "" if shutil.which("tesseract") else "-> optional. Without it Claude reads the frames visually instead.")

print("\nAll required tools found." if ok else "\nInstall the MISSING items above, then run this again.")
sys.exit(0 if ok else 1)

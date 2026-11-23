#!/usr/bin/env python3
"""One command that sets up everything ScrollGenius needs, and says exactly what is wrong if it cannot.

Safe to run again and again. Works in Claude Code in the browser (cloud container) and in the desktop app.

  bootstrap.py              install anything missing, pre-download the Whisper model, test the network
  bootstrap.py --check      only report, install nothing
  bootstrap.py --update     also upgrade yt-dlp (Instagram changes often; do this if downloads start failing)
  bootstrap.py --model tiny pick a different Whisper model to pre-download
"""
import argparse
import importlib.util
import os
import platform
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REQ = HERE.parent / "requirements.txt"
MODULES = {"yt_dlp": "yt-dlp", "faster_whisper": "faster-whisper", "imageio_ffmpeg": "imageio-ffmpeg"}


def say(ok, text):
    print(f"[{'ok' if ok else '!!'}] {text}", flush=True)


def is_cloud():
    return any(os.environ.get(k) for k in ("CLAUDE_CODE_REMOTE", "CCR_AGENT_PROXY_ENABLED"))


def missing_modules():
    return [pkg for mod, pkg in MODULES.items() if importlib.util.find_spec(mod) is None]


def pip_install(args):
    cmd = [sys.executable, "-m", "pip", "install", "-q", *args]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 and "externally-managed" in res.stderr:  # Debian/Ubuntu/Homebrew Python
        res = subprocess.run(cmd + ["--user", "--break-system-packages"], capture_output=True, text=True)
    return res.returncode == 0, (res.stderr.strip().splitlines() or [""])[-1]


def reachable(url):
    """True if the host answered at all (any HTTP status). False + reason if the network blocked it."""
    try:
        urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"}), timeout=15)
        return True, ""
    except urllib.error.HTTPError:
        return True, ""
    except Exception as e:
        return False, str(e)[:160]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--model", default="base")
    ap.add_argument("--no-model", action="store_true", help="skip the Whisper model download")
    a = ap.parse_args()

    cloud = is_cloud()
    problems = []
    say(sys.version_info >= (3, 9), f"Python {platform.python_version()} on {platform.system()} "
        f"({'cloud session' if cloud else 'your computer'})")
    if sys.version_info < (3, 9):
        sys.exit("Python 3.9 or newer is required.")

    # 1. Python packages
    todo = missing_modules()
    if a.update and not a.check:
        todo = sorted(set(todo) | {"yt-dlp"})
    if todo and not a.check:
        print(f"Installing: {', '.join(todo)} ...", flush=True)
        ok, err = pip_install(["-U", *todo] if a.update else ["-r", str(REQ)])
        if not ok:
            problems.append(f"pip install failed: {err}")
    still = missing_modules()
    say(not still, "Python packages (yt-dlp, faster-whisper, imageio-ffmpeg)" + (f" missing: {', '.join(still)}" if still else ""))
    if still:
        problems.append(f"missing packages: {', '.join(still)}")

    # 2. ffmpeg (system copy, or the bundled one)
    if not still or importlib.util.find_spec("imageio_ffmpeg") or __import__("shutil").which("ffmpeg"):
        sys.path.insert(0, str(HERE))
        try:
            from process_reel import ffmpeg_exe

            exe = ffmpeg_exe()
            ver = subprocess.run([exe, "-version"], capture_output=True, text=True).stdout.split("\n")[0]
            say(True, f"ffmpeg ready ({ver[:40]})")
        except SystemExit as e:
            say(False, "ffmpeg not available")
            problems.append(str(e))

    # 3. Network
    ig_ok, ig_err = reachable("https://www.instagram.com/")
    say(ig_ok, "Can reach instagram.com" + ("" if ig_ok else f" -> blocked: {ig_err}"))
    hf_ok, hf_err = reachable("https://huggingface.co/")
    say(hf_ok, "Can reach huggingface.co (Whisper model download)" + ("" if hf_ok else f" -> blocked: {hf_err}"))
    if not ig_ok or not hf_ok:
        problems.append("NETWORK: " + ("instagram.com " if not ig_ok else "") + ("huggingface.co " if not hf_ok else "") +
                        "blocked. In a cloud session set the environment's Network access to Full (or add these hosts "
                        "plus cdninstagram.com and fbcdn.net under Allowed domains), then start a new session.")

    # 4. Whisper model (cached after the first download)
    if not a.check and not a.no_model and not still and hf_ok:
        try:
            from process_reel import Transcriber

            Transcriber(a.model)
            say(True, f"Whisper '{a.model}' model ready")
        except SystemExit as e:
            say(False, "Whisper model could not be loaded")
            problems.append(str(e).splitlines()[0])

    print()
    if problems:
        print("NOT READY:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print("READY.")
    if cloud:
        print("Note: this is a cloud container, so it is wiped when the session goes idle. "
              "If Instagram blocks downloads, a cookies.txt export is the only login option here.")
    else:
        print("If Instagram blocks downloads, rerun with --cookies-from-browser <your browser>.")


if __name__ == "__main__":
    main()

# ScrollGenius

Turns your saved tutorial reels into workflows Claude can run.

Give it your saved-posts list. It downloads each reel (yt-dlp), listens to it (Whisper, small model), looks at it (ffmpeg keyframes), keeps only the real tutorials, groups them by topic and writes one Claude skill per topic, with every creator credited.

## 1. Install

You need Python 3.9+, then:

```bash
pip install -U yt-dlp faster-whisper
```

ffmpeg:

| System | Command |
|---|---|
| Mac | `brew install ffmpeg` |
| Windows | `winget install ffmpeg` |
| Linux | `sudo apt install ffmpeg` |

Optional, for reading on-screen text automatically: install `tesseract`. Without it, Claude looks at the frames directly.

Copy this whole folder to:

- Mac / Linux: `~/.claude/skills/scrollgenius`
- Windows: `%USERPROFILE%\.claude\skills\scrollgenius`

Then restart Claude Code.

## 2. Export your saved reels

Instagram > Settings > Accounts Centre > Your information and permissions > Download your information > Some of your information > tick **Saved** > Format **JSON** > Date range **All time**. Instagram emails you a zip when it is ready.

JSON is best, but a CSV, an HTML file or a plain list of reel URLs works too.

## 3. Run it

Open Claude Code in any folder and say:

> Run ScrollGenius on my saved reels. The export is at ~/Downloads/instagram-export.zip

Claude does a 5-reel trial first, then the full run. You can stop and restart any time; finished reels are skipped.

## What you get

- `scrollgenius_work/skills/<topic>-workflow/` one skill per topic, ready to install
- `scrollgenius_work/dist/*.zip` the same skills zipped to share
- A list of reels that could not be downloaded (private or removed)

## Good to know

- The export file only holds links, so each reel is downloaded from Instagram. Public reels usually work without logging in. If Instagram blocks it, rerun with `--cookies-from-browser chrome` (your own logged-in browser; cookies never leave your computer).
- Whisper `base` is the default. Use `--model tiny` for speed or `--model small` for accuracy.
- Videos are deleted after processing; only transcripts and a few frames are kept.
- Expect roughly 15 to 40 seconds per reel on a normal laptop, so 200 reels is a long lunch.

## Scripts (Claude runs these for you)

| Script | Job |
|---|---|
| `check_setup.py` | Checks ffmpeg, yt-dlp, Whisper |
| `parse_saved.py` | Export (json, csv, html, zip, txt) to `saved.json` |
| `process_reel.py` | One reel: download, transcribe, frames, digest |
| `run_batch.py` | All reels, resumable |
| `package_skills.py` | Validates and zips the generated skills |

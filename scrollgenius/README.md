# ScrollGenius

Turns your saved tutorial reels into workflows Claude can run. Built for the Claude desktop app (Mac and Windows).

You do two things: set it up once, then drop reels whenever you want.

## 1. First time only

Open the Claude desktop app, start a Claude Code session, attach `scrollgenius.zip` and send this exact prompt:

```text
Set up ScrollGenius from the attached zip. Unzip it into ~/.claude/skills/ so that ~/.claude/skills/scrollgenius/SKILL.md exists, install Python if I do not have it, run its scripts/bootstrap.py, fix anything that fails, then read the SKILL.md so you can run it for me in this session. Tell me when it is ready.
```

Claude installs everything itself (Python if needed, yt-dlp, a small Whisper model, ffmpeg). Nothing for you to install by hand.

## 2. Get your saved reels

Instagram > Settings > Accounts Centre > Your information and permissions > Download your information > Some of your information > tick **Saved** > Format **JSON** > Date range **All time**. Instagram emails you a zip. You do not need to unzip it.

## 3. Every time after that

Attach the zip, or a list (JSON, CSV, HTML, or a text file with one reel URL per line), or just paste one reel URL, and send:

```text
Run ScrollGenius on this.
```

You get back finished skills, a summary of what was learned, and a list of reels that could not be read. New reels get merged into skills you already have, so you can keep dropping more over time.

## Good to know

- **Instagram may block downloads.** Your export only holds links, so each reel is downloaded from Instagram. Public reels often work as is. If Instagram blocks it, Claude asks which browser you are logged in to Instagram with and uses that login on your own computer. Nothing is uploaded or stored. If it errors, fully close that browser and retry, or try Firefox.
- Speed is roughly 15 to 40 seconds per reel. You can stop and rerun; finished reels are skipped.
- Everything lives on your computer: skills in `~/.claude/skills/`, working files in `~/ScrollGenius/`. Videos are deleted after reading; only transcripts and a few frames are kept.
- Whisper `base` is the default. Ask for `tiny` (faster) or `small` (more accurate).

## What is inside

| File | Job |
|---|---|
| `SOP.md` | Step-by-step setup guide for end users |
| `SKILL.md` | The instructions Claude follows |
| `requirements.txt` | Python packages (yt-dlp, faster-whisper, imageio-ffmpeg) |
| `scripts/bootstrap.py` | One-command setup and self-repair |
| `scripts/parse_saved.py` | Export (json, csv, html, zip, txt) or URL to `saved.json`, merging new links |
| `scripts/process_reel.py` | One reel: download, transcribe, frames, digest |
| `scripts/run_batch.py` | All reels, resumable |
| `scripts/package_skills.py` | Validates and zips the generated skills |
| `references/skill-template.md` | The shape of every generated skill |

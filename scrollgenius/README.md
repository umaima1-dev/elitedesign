# ScrollGenius

Turns your saved tutorial reels into workflows Claude can run. Works in Claude Code in the browser and in the desktop app.

You do two things: set it up once, then drop reels whenever you want.

## 1. First time only

Open Claude Code, attach `scrollgenius.zip` and send this exact prompt:

```text
Set up ScrollGenius from the attached zip. Unzip it into .claude/skills/ so that .claude/skills/scrollgenius/SKILL.md exists, run .claude/skills/scrollgenius/scripts/bootstrap.py, fix anything that fails, then read the SKILL.md so you can run it for me in this session. Tell me when it is ready.
```

Claude installs everything itself (yt-dlp, a small Whisper model, ffmpeg). Nothing for you to install by hand.

**Browser users:** your session runs in a cloud container with a network allowlist. If setup says `NETWORK ... blocked`, open the cloud environment menu in the session title bar, choose Edit, and set Network access to **Full**. Then send the prompt again in a new session.

## 2. Get your saved reels

Instagram > Settings > Accounts Centre > Your information and permissions > Download your information > Some of your information > tick **Saved** > Format **JSON** > Date range **All time**. Instagram emails you a zip. You do not need to unzip it.

## 3. Every time after that

Attach the zip, or a list (JSON, CSV, HTML, or a text file with one reel URL per line), or just paste one reel URL, and send:

```text
Run ScrollGenius on this.
```

You get back finished skills in `.claude/skills/`, a summary of what was learned, and a list of reels that could not be read. New reels get merged into skills you already have, so you can keep dropping more over time.

## Good to know

- **Instagram may block downloads.** The export only holds links, so each reel is downloaded from Instagram. Public reels often work without logging in, but Instagram blocks anonymous downloads often, and cloud servers get blocked more than home computers.
  - **Desktop app:** Claude asks which browser you use and borrows its login on your own machine. Nothing leaves your computer.
  - **Browser version:** there is no browser to borrow from. The only option is uploading a `cookies.txt` export of your Instagram session, which works like your login. Only do that if you are comfortable with it. If not, use the desktop app.
- **Browser sessions are wiped when idle.** After setup, Claude offers to make it permanent (saves the skill in your repo and the install as your environment's setup script). Say yes once and you never repeat step 1.
- Speed is roughly 15 to 40 seconds per reel. You can stop and rerun; finished reels are skipped.
- Videos are deleted after reading. Only transcripts and a few frames are kept in `scrollgenius_work/`.
- Whisper `base` is the default. Ask for `tiny` (faster) or `small` (more accurate).

## What is inside

| File | Job |
|---|---|
| `SKILL.md` | The instructions Claude follows |
| `requirements.txt` | Python packages (yt-dlp, faster-whisper, imageio-ffmpeg) |
| `scripts/bootstrap.py` | One-command setup and self-repair |
| `scripts/parse_saved.py` | Export (json, csv, html, zip, txt) or URL to `saved.json`, merging new links |
| `scripts/process_reel.py` | One reel: download, transcribe, frames, digest |
| `scripts/run_batch.py` | All reels, resumable |
| `scripts/package_skills.py` | Validates and zips the generated skills |
| `references/skill-template.md` | The shape of every generated skill |

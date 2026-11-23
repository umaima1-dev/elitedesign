---
name: scrollgenius
description: Turns a user's saved Instagram reels (or any list of tutorial video links) into Claude skills. Use when the user hands over a saved-posts export (JSON, CSV, HTML, zip, or a list of URLs), says "run ScrollGenius", "turn my saved reels into skills", "go through my saved folder", or wants tutorial videos converted into reusable workflows. Downloads each reel with yt-dlp, transcribes with a small Whisper model, pulls keyframes with ffmpeg, keeps only the real tutorials, groups them by topic and writes one skill per topic with every creator credited.
---

# ScrollGenius

Saved reels in, working Claude skills out. The scripts do the heavy lifting (download, transcribe, frames).
You do the thinking (is it a tutorial, what are the steps, which topic, write the skill).

Scripts live in `scripts/` next to this file. Work happens in `./scrollgenius_work/` in the user's current folder.

## Rules

- Only process the user's own saved list. Never ask for their Instagram password.
- Instagram sometimes blocks anonymous downloads. If that happens, use `--cookies-from-browser <browser>` (the user's own logged-in browser). Cookies stay on their machine; never copy, print or store them.
- Credit every creator. Synthesize steps in your own words; never paste a transcript wholesale into a skill.
- Tell the user the truth about failures: private, removed or image-only posts are skipped and listed at the end.

## Workflow

### 1. Check setup
```bash
python scripts/check_setup.py
```
If anything is MISSING, give the user the printed install command and wait. ffmpeg, yt-dlp and a Whisper package are required; tesseract is optional.

### 2. Parse the export
Ask for the path if the user has not given one. It can be Instagram's zip, the unzipped folder, a `.json`, `.csv`, `.html`, or a `.txt` of URLs.
```bash
python scripts/parse_saved.py <path> -o scrollgenius_work/saved.json
```
Report the count. If 0, the export probably did not include "Saved"; tell them how to re-export (Settings > Accounts Centre > Your information and permissions > Download your information > Some of your information > Saved > JSON > All time).

### 3. Trial run first
```bash
python scripts/run_batch.py scrollgenius_work/saved.json --work scrollgenius_work --limit 5
```
Show what happened (words transcribed, failures). If 3+ fail with login/rate-limit errors, ask the user which browser they use and add `--cookies-from-browser chrome` (or firefox, safari, edge). Whisper `base` is the default; `--model tiny` is faster on slow laptops, `--model small` is more accurate.

### 4. Full run
Run the same command without `--limit`. For 100+ reels run it in the background and check `scrollgenius_work/index.json` as it grows. It is resumable: stopping and rerunning continues where it stopped. Add `--retry-failed` to retry failures.

### 5. Analyse each reel
For each `done` reel in `scrollgenius_work/index.json`, read `scrollgenius_work/reels/<code>/digest.md` (caption + transcript + on-screen text).
- If the transcript has under ~30 words or the caption says things like "look at this", view 3-4 of the listed frame images.
- Write `scrollgenius_work/analysis/<code>.json`:
```json
{"shortcode": "", "creator": "", "url": "", "is_tutorial": true,
 "topic": "short-kebab-topic", "title": "", "summary": "one sentence",
 "tools": [{"name": "", "use": "what it is used for"}],
 "steps": ["imperative step", "..."], "tips": ["..."], "confidence": "high|medium|low"}
```
- `is_tutorial` is true only when the reel teaches a repeatable process with steps. Memes, opinions, news, ads, motivation and pure promo are false (keep the file, set false, no steps).
- With many reels, split them into batches of ~20 and hand each batch to a subagent, then collect the JSON files.

### 6. Group by topic
Read all analysis files where `is_tutorial` is true. Merge near-duplicate topics (`video-editing`, `edit-videos` become one). Target 2 or more reels per skill; a strong lone reel can stand alone, weak singletons go into a `misc-quick-wins` skill. Show the user the proposed grouping (topic, reel count) and let them adjust before writing.

### 7. Write one skill per topic
Create `scrollgenius_work/skills/<topic>-workflow/SKILL.md` using `references/skill-template.md`. Combine the steps from every reel in the topic into one coherent workflow, resolve conflicts (note when creators disagree), and list the tools with what each is for. The `description` must contain the phrases a user would actually say ("edit my video", "cut my reel"). End every skill with a Credits section: one line per source reel, `@creator - URL`.

### 8. Package and hand over
```bash
python scripts/package_skills.py scrollgenius_work/skills -o scrollgenius_work/dist
```
Fix anything it flags. Then tell the user: how many reels were read, how many were tutorials, how many failed (with the list), the skills created, and the install line (copy each folder into `~/.claude/skills/`, Windows: `%USERPROFILE%\.claude\skills\`, then restart Claude Code).

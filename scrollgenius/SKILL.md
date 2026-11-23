---
name: scrollgenius
description: Turns saved Instagram reels (or any tutorial video links) into Claude skills. Use when the user sets up ScrollGenius, says "run ScrollGenius", drops a saved-posts export (JSON, CSV, HTML, zip, a list of URLs) or a single reel URL, or asks to turn saved tutorial videos into reusable workflows. Downloads each reel with yt-dlp, transcribes it with a small Whisper model, pulls keyframes with ffmpeg, keeps only real tutorials, groups them by topic and installs one credited skill per topic.
---

# ScrollGenius

Saved reels in, working Claude skills out. Scripts in `scripts/` (next to this file) do the download, transcription and frames.
You do the judgment: is it a tutorial, what are the steps, which topic, write the skill.

Runs in the Claude desktop app on the user's own computer (Mac or Windows).

Paths (use the user's home folder; `~` is `%USERPROFILE%` on Windows):
- `SKILL_DIR` = the folder containing this file, normally `~/.claude/skills/scrollgenius/`
- Work folder = `~/ScrollGenius/` (saved list, per-reel digests, analysis, zips). Scripts use it by default.
- Generated skills go in `~/.claude/skills/<topic>-workflow/`, so they work from any folder.
- Python command: `python3` on Mac, `python` on Windows.

## Rules
- Do the whole job without stopping to ask for approval. Ask only when genuinely blocked (below).
- Only the user's own saved list. Never ask for an Instagram password.
- Credit every creator. Write steps in your own words; never paste a transcript wholesale.
- Be straight about failures: private, removed or image-only posts are skipped and listed at the end.

## Mode A: First-time setup
Triggered by "set up ScrollGenius" or the zip being dropped with the setup prompt.

1. Unzip the dropped zip into `~/.claude/skills/` so `~/.claude/skills/scrollgenius/SKILL.md` exists (skip this if it is already there and the user is just rerunning setup).
2. Check Python is installed (`python3 --version` / `python --version`, needs 3.9+). If missing, install it (Mac: `brew install python`, or python.org; Windows: `winget install Python.Python.3.12`) and carry on.
3. Run `scripts/bootstrap.py`. It installs yt-dlp, faster-whisper and a bundled ffmpeg, downloads the Whisper model, and tests that Instagram and the model host are reachable.
4. If it prints `NOT READY`, fix what it names and rerun. A failed package install: read the error, fix (older pip, permissions), retry. Blocked network: ask the user to check their internet, VPN or firewall.
5. When READY, tell the user in two lines: it is set up, and from now on they only drop a list or a reel URL.

## Mode B: Run (every time after)
Input is any of: an export zip/folder, `.json`, `.csv`, `.html`, `.txt`, or one or more reel URLs pasted in the message. Use the attached file's path from the message; never search the user's whole disk.

1. **Quick check.** `scripts/bootstrap.py --check`. If NOT READY, rerun without `--check` (it repairs itself).
2. **Parse and merge.** `scripts/parse_saved.py <file-or-url> [more urls] -o ~/ScrollGenius/saved.json`
   New links are merged into earlier ones. If 0 found for an Instagram export, the export lacked "Saved": tell them to re-export (Settings > Accounts Centre > Your information and permissions > Download your information > Some of your information > Saved > JSON > All time).
3. **Process.** `scripts/run_batch.py ~/ScrollGenius/saved.json`
   - Skips reels already done, so reruns only handle new ones. Safe to stop and restart.
   - For lists over 20 reels run it in the background and watch `~/ScrollGenius/index.json`.
   - **Blocked by Instagram** (it prints "login required" / "rate-limit" and stops after 3 in a row): this is the one time you ask. Ask which browser they are logged in to Instagram with, then rerun with `--cookies-from-browser <chrome|firefox|safari|edge>`. It reads that browser's login on their own computer; nothing is uploaded or stored. If it errors, have them fully close that browser and retry; if it still fails, try Firefox, which is the most reliable. On Mac, Safari may need Full Disk Access for the terminal.
   - Slow computer: `--model tiny`. Want accuracy: `--model small`.
   - Many reels failing with extractor or HTTP errors (not login errors), or the user asks to "update the downloader": run `scripts/bootstrap.py --update`, then rerun with `--retry-failed`.
4. **Analyse.** For each `done` reel, read `~/ScrollGenius/reels/<code>/digest.md`. If the transcript is under ~30 words or the caption says "look at this", view 3-4 of the listed frames. Skip reels that already have `~/ScrollGenius/analysis/<code>.json`. Write:
```json
{"shortcode": "", "creator": "", "url": "", "is_tutorial": true,
 "topic": "short-kebab-topic", "title": "", "summary": "one sentence",
 "tools": [{"name": "", "use": ""}], "steps": ["imperative step"], "tips": ["..."],
 "confidence": "high|medium|low"}
```
   `is_tutorial` is true only for a repeatable process with steps. Memes, opinions, news, ads and pure promo are false. For 40+ new reels, hand batches of ~20 to subagents.
5. **Place each tutorial in a skill.** Look at `~/.claude/skills/*/SKILL.md` for files containing `<!-- generated by ScrollGenius -->`.
   - Same topic exists: merge the new steps, tools, tips and credits into it. Keep it coherent; do not append blindly. Only edit skills with that marker, never the user's own.
   - New topic: create `~/.claude/skills/<topic>-workflow/SKILL.md` from `references/skill-template.md`. Aim for 2+ reels per skill; one strong lone reel can stand alone; weak singletons go in `misc-quick-wins-workflow`.
   - The `description` must hold the phrases a user would say ("edit my video"). End with a Credits section, one line per reel: `@creator - URL`.
   - Merge near-duplicate topics (`video-editing` and `edit-videos`). Where creators disagree, say so inside the skill.
6. **Validate and package.** `scripts/package_skills.py ~/.claude/skills -o ~/ScrollGenius/dist` (checks only the marked ScrollGenius-made skills; fix anything it flags).
7. **Final result.** Short summary: reels read, tutorials found, skipped and why, failed (list), skills created or updated with their trigger phrases, and the zips in `~/ScrollGenius/dist/` for sharing. Say the new skills are ready (restart the app if they do not show up) and that you can regroup or rename topics on request. For a single URL the answer is just: the steps found and which skill got them (or "this one is not a tutorial, nothing added").

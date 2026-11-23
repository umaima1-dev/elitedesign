---
name: scrollgenius
description: Turns saved Instagram reels (or any tutorial video links) into Claude skills. Use when the user sets up ScrollGenius, says "run ScrollGenius", drops a saved-posts export (JSON, CSV, HTML, zip, a list of URLs) or a single reel URL, or asks to turn saved tutorial videos into reusable workflows. Downloads each reel with yt-dlp, transcribes it with a small Whisper model, pulls keyframes with ffmpeg, keeps only real tutorials, groups them by topic and installs one credited skill per topic.
---

# ScrollGenius

Saved reels in, working Claude skills out. Scripts in `scripts/` (next to this file) do the download, transcription and frames.
You do the judgment: is it a tutorial, what are the steps, which topic, write the skill.

`SKILL_DIR` = the folder containing this file. Work folder = `./scrollgenius_work/` in the current project. Generated skills are installed into `./.claude/skills/` in the current project.

## Rules
- Do the whole job without stopping to ask for approval. Ask only when you are genuinely blocked (below).
- Only the user's own saved list. Never ask for an Instagram password.
- Credit every creator. Write steps in your own words; never paste a transcript wholesale.
- Be straight about failures: private, removed or image-only posts are skipped and listed at the end.

## Mode A: First-time setup
Triggered by "set up ScrollGenius" or the zip being dropped with the setup prompt.

1. If the skill is not yet at `.claude/skills/scrollgenius/`, unzip the dropped zip into `.claude/skills/` so that `.claude/skills/scrollgenius/SKILL.md` exists.
2. Run `python .claude/skills/scrollgenius/scripts/bootstrap.py`. It installs everything (yt-dlp, faster-whisper, bundled ffmpeg), downloads the Whisper model and tests the network.
3. If it prints `NOT READY`, fix what it names and rerun:
   - Package install failed: read the error and fix it (older pip, permissions), rerun.
   - `NETWORK ... blocked` (cloud session): use your environment tools to add the hosts if you have them (`www.instagram.com`, `huggingface.co`, `cdninstagram.com`, `fbcdn.net`); otherwise tell the user to set the cloud environment's Network access to Full (environment menu in the session title bar, Edit, Network access), then start a new session and send the setup prompt again.
4. When READY, tell the user it is set up and that next time they only need to drop a list or a reel URL.
5. Cloud sessions only (the bootstrap says "cloud session"): the container is wiped when idle. Offer once, in one short message, to make the setup permanent: commit `.claude/skills/scrollgenius` to their repo, and save the environment setup script `python .claude/skills/scrollgenius/scripts/bootstrap.py || true` (the `|| true` matters: a failing setup script blocks every session). Do it only if they say yes.

## Mode B: Run (every time after)
Input is any of: an export zip/folder, `.json`, `.csv`, `.html`, `.txt`, or one or more reel URLs pasted in the message. Use the attached file's path from the message; never search the user's whole disk.

1. **Quick check.** `python <SKILL_DIR>/scripts/bootstrap.py --check`. If NOT READY, run it without `--check` (it repairs itself), and handle failures as in Mode A step 3.
2. **Parse and merge.**
   `python <SKILL_DIR>/scripts/parse_saved.py <file-or-url> [more urls] -o scrollgenius_work/saved.json`
   New links are merged into earlier ones. If 0 found for an Instagram export, the export lacked "Saved": tell them to re-export (Settings > Accounts Centre > Your information and permissions > Download your information > Some of your information > Saved > JSON > All time).
3. **Process.** `python <SKILL_DIR>/scripts/run_batch.py scrollgenius_work/saved.json --work scrollgenius_work`
   - It skips reels already done, so reruns only handle new ones.
   - For lists over 20 reels run it in the background and watch `scrollgenius_work/index.json`.
   - **Blocked by Instagram** (it prints "login required"/"rate-limit" and stops after 3): this is the one time you ask.
     - Local/desktop session: ask which browser they are logged in to, rerun with `--cookies-from-browser <browser>`.
     - Cloud session: there is no browser to borrow from. Tell them plainly that a `cookies.txt` export of their Instagram session is the only option, that it works like their login (only upload it if they are comfortable), and that running ScrollGenius in the desktop app avoids this. Rerun with `--cookies <file>`.
   - Slow machine: `--model tiny`. Want accuracy: `--model small`.
4. **Analyse.** For each `done` reel, read `scrollgenius_work/reels/<code>/digest.md`. If the transcript is under ~30 words or the caption says "look at this", view 3-4 of the listed frames. Skip reels that already have `scrollgenius_work/analysis/<code>.json`. Write:
```json
{"shortcode": "", "creator": "", "url": "", "is_tutorial": true,
 "topic": "short-kebab-topic", "title": "", "summary": "one sentence",
 "tools": [{"name": "", "use": ""}], "steps": ["imperative step"], "tips": ["..."],
 "confidence": "high|medium|low"}
```
   `is_tutorial` is true only for a repeatable process with steps. Memes, opinions, news, ads and pure promo are false. For 40+ new reels, hand batches of ~20 to subagents.
5. **Place each tutorial in a skill.** Look at `.claude/skills/*/SKILL.md` for files containing `<!-- generated by ScrollGenius -->`.
   - Same topic exists: merge the new steps, tools, tips and credits into it. Keep it coherent; do not append blindly. Only edit skills that carry that marker, never the user's own.
   - New topic: create `.claude/skills/<topic>-workflow/SKILL.md` from `references/skill-template.md`. Aim for 2+ reels per skill; one strong lone reel can stand alone; weak singletons go in `misc-quick-wins-workflow`.
   - The `description` must hold the phrases a user would say ("edit my video"). End with a Credits section, one line per reel: `@creator - URL`.
   - Merge near-duplicate topics (`video-editing` and `edit-videos`). Where creators disagree, say so inside the skill.
6. **Validate and package.** `python <SKILL_DIR>/scripts/package_skills.py .claude/skills -o scrollgenius_work/dist` (it checks only the marked ScrollGenius-made skills; fix anything it flags).
7. **Final result.** Give a short summary: reels read, tutorials found, skipped and why, failed (list), skills created or updated with their trigger phrases, and the zips in `scrollgenius_work/dist/` for sharing. Say new skills are live (restart the session if they do not show up) and that you can regroup or rename topics on request. For a single URL, the answer is just: the steps found and which skill got them (or "this one is not a tutorial, nothing added").

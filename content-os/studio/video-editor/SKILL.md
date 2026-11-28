---
name: video-editor
description: Video Editor for the AI Savvy Founders Content OS. Edits raw talking-head footage into a finished short: cuts, captions, reframing, B-roll.
---

# Video Editor

**Department:** studio
**Build status:** Modify: start from upstream patterns, adapt to Business Brain and approval gate
**Approval:** No external action. Output is files for human review.

## Job

Edits raw talking-head footage into a finished short: cuts, captions, reframing, B-roll.

## Inputs

- Raw footage path
- Approved script
- Caption style from visual-identity

## Outputs

- `studio/videos/<slug>/` edited MP4, captions file, edit notes

## Process

1. Transcribe footage and align with the script.
2. Remove pauses and bad takes, keep best take per line.
3. Reframe to 9:16 with face tracking where needed.
4. Burn in captions in brand style. Add B-roll and sound only where it helps.
5. Export, then write edit notes listing every cut decision.
6. Hold for founder approval.

## Rules

- Requires FFmpeg and a transcription tool installed locally. See `integrations/README.md`.
- Never overwrite raw footage.
- Read `business-brain/` before producing anything. If a Brain file is empty, ask Brain Keeper to build it first.
- Handoff format: see `shared/workflows/handoffs.md`.

## Upstream references (study, do not blindly install)

- [jdjf39/video-creator-skills](https://github.com/jdjf39/video-creator-skills): pause removal, retakes, reframing, captions, B-roll
- [Melvynx/video-agent-skills](https://github.com/Melvynx/video-agent-skills): short-form editing
- [sunithvs/video-agent-skill](https://github.com/sunithvs/video-agent-skill): captions, B-roll, motion graphics

These links come from discovery research and have not been audited. Record findings in `docs/repository-audit.md` before copying anything.

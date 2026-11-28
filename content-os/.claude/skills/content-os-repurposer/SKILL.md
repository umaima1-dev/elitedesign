---
name: content-os-repurposer
description: Repurposer in the Content OS. Turns one approved piece into platform-specific versions.
---

# Repurposer

**Department:** distribution
**Build status:** Reuse: adopt an existing skill largely as is
**Approval:** No external action. Output is files for human review.

## Job

Turns one approved piece into platform-specific versions.

## Inputs

- Approved asset
- Target platforms

## Outputs

- `distribution/repurposed/<slug>/` one file per platform

## Process

1. Use the Brand Brain `how-i-sound.md` for voice. If you have your own voice or repurposing skills installed, use them too.
2. Adapt, do not paste: change hook shape, length, formatting and CTA per platform.
3. Brain Keeper check on each version.
4. Queue for Scheduler.

## Rules

- LinkedIn is text-first. Instagram is visual-first. Do not reuse the same hook unchanged.
- Read `config.json` and `business-brain/` before producing anything. If a Brain file is empty, ask Brain Keeper to build it first.
- Handoff format: see `shared/workflows/handoffs.md`.
- Outputs go to `distribution/` (folders are created by the repo).

## Upstream references (study, do not blindly install)

- [social-media-skills/skills](https://github.com/social-media-skills/skills): cross-platform repurposing
- [Ootto-AI/claude-content-skills](https://github.com/Ootto-AI/claude-content-skills): reels, captions
- [jsath/claude-skills](https://github.com/jsath/claude-skills): LinkedIn, X, newsletters
- [Schmedu/social-post-skill](https://github.com/Schmedu/social-post-skill): platform formatting

These links come from discovery research and have not been audited. Record findings in `docs/repository-audit.md` before copying anything.

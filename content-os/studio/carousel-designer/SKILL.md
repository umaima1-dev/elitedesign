---
name: carousel-designer
description: Carousel Designer for the AI Savvy Founders Content OS. Plans, writes and renders carousels as 1080x1350 slides using the brand design system.
---

# Carousel Designer

**Department:** studio
**Build status:** Reuse: adopt an existing skill largely as is
**Approval:** No external action. Output is files for human review.

## Job

Plans, writes and renders carousels as 1080x1350 slides using the brand design system.

## Inputs

- Slot brief
- Chosen hook
- `business-brain/visual-identity.md`

## Outputs

- `studio/carousels/<slug>/` copy file, slide PNGs or PDF

## Process

1. Draft the copy deck: hook slide, 5 to 8 body slides, CTA slide.
2. Get Brain Keeper PASS on the copy before any design work.
3. Render using the installed `ai-savvy-carousel-pdf` or `carousel-builder` skill, or the upstream carousel skill if adopted.
4. Run a cold-reader check: could a stranger follow it in 20 seconds.
5. Hold for founder approval.

## Rules

- Approve copy before rendering, approve render before handoff.
- Read `business-brain/` before producing anything. If a Brain file is empty, ask Brain Keeper to build it first.
- Handoff format: see `shared/workflows/handoffs.md`.

## Upstream references (study, do not blindly install)

- [social-media-skills/instagram-carousel-skill](https://github.com/social-media-skills/instagram-carousel-skill): plan, write, render, approval
- [tenfoldmarc/carousel-suite-skill](https://github.com/tenfoldmarc/carousel-suite-skill): idea, copy, design, production
- [cth9191/carousel-engine](https://github.com/cth9191/carousel-engine): ranked hooks, cold-reader review

These links come from discovery research and have not been audited. Record findings in `docs/repository-audit.md` before copying anything.

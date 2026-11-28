---
name: content-os
description: Main entry point for the Content OS. Use for any content request (research, planning, hooks, scripts, carousels, video, scheduling, engagement, funnels, analytics). Routes to the right content-os agent and enforces the Brand Brain check and approval gate.
---

# Content OS

1. Read `config.json` and `business-brain/`. If `brand_name` is still `YOUR BRAND NAME` or Brain files contain TODO, run `/setup-content-os` first.
2. Route the request:

| Request | Skill |
|---|---|
| Build or check brand knowledge | content-os-brain-keeper |
| Find what is working in my niche | content-os-outlier-scout, then content-os-hook-analyst |
| Competitor teardown | content-os-competitor-research |
| Plan the week | content-os-content-strategist |
| Hooks | content-os-hook-writer |
| Short-form video script | content-os-scriptwriter |
| Carousel | content-os-carousel-designer |
| Edit video | content-os-video-editor |
| Adapt to other platforms | content-os-repurposer |
| Queue posts | content-os-scheduler (gated) |
| Stories | content-os-stories-writer |
| Comments and DMs | content-os-engagement-assistant (draft only) |
| Freebie and DM funnel | content-os-conversion-builder (gated) |
| Pull metrics | content-os-performance-tracker |
| What to do next | content-os-analyst |

3. Every final asset passes `content-os-brain-keeper` before human review.
4. Nothing is published, emailed or sent without `python scripts/approve.py check <asset> --action <publish|message>` returning OK. See `shared/workflows/approval-gate.md`.
5. If the user is unsure where to start, run the weekly loop in `shared/workflows/handoffs.md` one step at a time and ask before each step.

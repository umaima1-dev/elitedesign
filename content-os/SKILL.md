---
name: content-os
description: Orchestrator for the AI Savvy Founders Content OS. Routes any content request (research, planning, writing, carousels, video, scheduling, engagement, funnels, analytics) to the right department agent, enforces the Business Brain check and the approval gate.
---

# Content OS orchestrator

1. Read `business-brain/`. If files still contain TODO, route to `brain-keeper` first.
2. Route the request:

| Request | Agent |
|---|---|
| Build or check brand knowledge | brain-keeper |
| Find what is working | outlier-scout, then hook-analyst |
| Competitor teardown | competitor-research |
| Plan the week | content-strategist |
| Hooks | hook-writer |
| Reel script | scriptwriter |
| Carousel | carousel-designer |
| Edit video | video-editor |
| Other platforms | repurposer |
| Queue in Buffer | scheduler (gated) |
| Stories | stories-writer |
| Comments and DMs | engagement-assistant (draft only) |
| Freebie and ManyChat funnel | conversion-builder (gated) |
| Pull metrics | performance-tracker |
| What to do next | analyst |

3. Every final asset passes `brain-keeper` before founder review.
4. Nothing leaves the system without `python scripts/approve.py check`. See `shared/workflows/approval-gate.md`.
5. Brand name is always AI Savvy Founders.

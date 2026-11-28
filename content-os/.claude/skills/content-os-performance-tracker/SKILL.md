---
name: content-os-performance-tracker
description: Performance Tracker in the Content OS. Collects post metrics on a schedule and stores them in one tidy table.
---

# Performance Tracker

**Department:** analytics
**Build status:** Modify: start from upstream patterns, adapt to Business Brain and approval gate
**Approval:** No external action. Output is files for human review.

## Job

Collects post metrics on a schedule and stores them in one tidy table.

## Inputs

- Platform analytics, Buffer stats, ManyChat tags

## Outputs

- `analytics/data/performance.csv` appended rows

## Process

1. Pull metrics at 24h, 72h and 7d after publish.
2. Record views, reach, likes, comments, saves, shares, follows, link clicks, keyword leads.
3. Join each row to its hook type, format, pillar, CTA keyword from the plan.
4. Flag collection gaps instead of filling them with guesses.

## Rules

- Data only, no interpretation. Interpretation is the Analyst's job.
- Read `config.json` and `business-brain/` before producing anything. If a Brain file is empty, ask Brain Keeper to build it first.
- Handoff format: see `shared/workflows/handoffs.md`.
- Outputs go to `analytics/` (folders are created by the repo).

## Upstream references (study, do not blindly install)

- [michaellady/claude-social-media-skills](https://github.com/michaellady/claude-social-media-skills): Buffer and LinkedIn stats
- [Bynor-S-R-L/bynor-mcp](https://github.com/Bynor-S-R-L/bynor-mcp): analytics
- [shika-stuck/viral-analyzer](https://github.com/shika-stuck/viral-analyzer): outlier scoring

These links come from discovery research and have not been audited. Record findings in `docs/repository-audit.md` before copying anything.

---
name: competitor-research
description: Competitor Research for the AI Savvy Founders Content OS. Runs a periodic teardown of competitor offers, angles, formats and gaps.
---

# Competitor Research

**Department:** research
**Build status:** Reuse: adopt an existing skill largely as is
**Approval:** No external action. Output is files for human review.

## Job

Runs a periodic teardown of competitor offers, angles, formats and gaps.

## Inputs

- `research/watchlist.md`
- Scrape data

## Outputs

- `research/competitors/YYYY-MM.md` teardown with gaps we can own

## Process

1. Use the existing `competitor-intel` skill if installed, otherwise scrape via Apify.
2. Summarise each competitor: offer, audience claim, top angles, formats, posting cadence, CTA style.
3. List gaps: topics, formats or audiences nobody covers well.
4. Hand the gaps to Content Strategist.

## Rules

- Observation only. No contact with competitors.
- Read `business-brain/` before producing anything. If a Brain file is empty, ask Brain Keeper to build it first.
- Handoff format: see `shared/workflows/handoffs.md`.

## Upstream references (study, do not blindly install)

- [zayd28061-hub/viral-content-skill](https://github.com/zayd28061-hub/viral-content-skill): account audit
- [Bynor-S-R-L/bynor-mcp](https://github.com/Bynor-S-R-L/bynor-mcp): competitor research tools

These links come from discovery research and have not been audited. Record findings in `docs/repository-audit.md` before copying anything.

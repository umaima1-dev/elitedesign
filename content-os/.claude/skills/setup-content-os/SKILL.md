---
name: setup-content-os
description: One-time guided setup for the Content OS. Interviews the user, fills config.json and the business-brain files, sets banned phrases and checks the repo works. Use when the user says set up, get started, configure, or when config.json still says YOUR BRAND NAME.
---

# Setup

Run this as a friendly conversation. Ask 2 to 3 questions at a time, never a wall of questions. Never invent facts. If the user does not know, write `TODO` and move on.

## Steps

1. **Basics** (writes `config.json`): brand name, platforms they post on, how they publish (Buffer, native, other), posts per week. Keep the existing defaults for `outlier_multiplier` (5) and `min_posts_for_baseline` (8) unless asked.
2. **Who they are and what they sell**: fill `business-brain/who-i-am.md`, `what-i-sell.md`, `offers.md`.
3. **Audience**: fill `who-i-serve.md`. Ask for words customers actually use.
4. **Voice**: ask for 3 samples of their writing or a link to content they like. Fill `how-i-sound.md`. Ask for words and phrases they never want used, then write them one per line into `business-brain/banned-phrases.txt`.
5. **Pillars and visuals**: fill `content-pillars.md` (3 to 5 pillars) and `visual-identity.md` (colours, fonts, name of any brand design skill).
6. **Boundaries**: fill `boundaries.md` (claims never to make, topics to avoid).
7. **Watchlist**: ask for 3 to 10 competitor or inspiration handles, write to `research/watchlist.md`.
8. **Check**: run `python scripts/validate.py`. Report problems plainly.
9. **Next step**: offer to run the first loop: `content-os-outlier-scout`, then `content-os-content-strategist`.

## Rules

- Show the user each file's contents before saving and ask for corrections.
- Tell the user which integrations are optional: scraping (Apify), publishing (Buffer or other), DM funnels (ManyChat or other). Setup works without any of them. See `integrations/README.md`.
- Do not publish or message anyone during setup.

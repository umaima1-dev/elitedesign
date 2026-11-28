---
name: setup-content-os
description: Guided one-time setup of the Content OS for any brand. Reads the user's website, drafts their brand profile from it, then asks step-by-step questions to confirm and fill gaps, and configures everything. Use when the user says set up, get started, configure, install, or when config.json still says YOUR BRAND NAME.
---

# Setup

You are onboarding a new user. Goal: by the end, `config.json` and every file in `business-brain/` describe THEIR brand, in their words, and they know what to type next.

## Ground rules

- Ask 2 to 3 questions at a time. Wait for answers. Never dump a long form.
- Never invent facts. Anything unknown stays `TODO` and you move on.
- Show each drafted file and ask "Does this sound like you? What should change?" before saving.
- Nothing is published, emailed or messaged during setup.
- Keep a short running checklist visible: `[x] Basics  [ ] Website  [ ] Offer ...`
- Use plain language. The user may not be technical.

## Phase 0: Environment (silent, only speak if something is wrong)

1. Confirm you are inside the Content OS folder (`config.json` and `.claude/skills/` exist). If the user just cloned it in an existing session, say so, work inside the cloned folder, and at the end tell them to open that folder as a project so slash commands load.
2. Check Python 3.8+: `python --version` (try `python3` too). If missing, setup still works but the helper scripts will not. Tell the user how to install Python.
3. Privacy: this repo is a public template. Ask the user whether to disconnect it from the template remote so their brand files are never pushed to the public repo: offer `git remote remove origin` and recommend they create a **private** repo if they want a backup. Only run it if they agree.

## Phase 1: Basics (writes `config.json`)

Ask: brand name (exact spelling and capitalisation), website URL, which platforms they post on, how they publish today (Buffer, native apps, other tool, by hand), how many posts a week they can realistically make. Write `brand_name`, `platforms`, `publishing_tool`, `posts_per_week`. Keep `outlier_multiplier` 5 and `min_posts_for_baseline` 8.

## Phase 2: Website analysis

Goal: learn the brand from their site first, so you ask fewer questions.

1. Run `python scripts/site_snapshot.py <url>`. It writes `business-brain/site-snapshot.md` (headings, copy, buttons, colours, fonts, social links).
2. If it exits 2 or returns thin content (JavaScript-only site), try, in order: a web fetch tool if you have one, an Apify website crawler connector if connected, then ask the user to paste their homepage, about page and offer page text.
3. Read the snapshot. Draft a **Findings summary** in chat: what they sell, who it seems to be for, tone, key claims, colours and fonts, social handles found. Mark each line `from site` and flag anything you are guessing.
4. Ask them to correct it. Corrections beat the site, because sites are often out of date.

## Phase 3: Fill the Brand Brain (one file at a time, confirm each)

Start from the findings so questions are "I read X, is that right?" not blank-page questions.

| File | Cover |
|---|---|
| `who-i-am.md` | Founder name, origin story, real proof (numbers, results, years), what they believe that others in their space do not |
| `what-i-sell.md` | One-sentence promise, flagship offer, who it is for and not for, transformation, price and how people buy, real testimonials |
| `who-i-serve.md` | Ideal client, top problems in their own words, what they tried before, objections, where they hang out online |
| `how-i-sound.md` | Tone in 3 words, rhythm, favourite words, signature moves. Ask for 3 real writing samples or links, and analyse them |
| `content-pillars.md` | 3 to 5 pillars with purpose and weekly share. Propose pillars from the site and offer, then let them edit |
| `visual-identity.md` | Colours and fonts from the snapshot (confirm), carousel and reel sizes, caption style, name of a brand design skill if they have one |
| `offers.md` | Each freebie or offer with a CTA keyword. Suggest keywords, ask them to pick |
| `boundaries.md` | Claims never to make, topics to avoid, legal or compliance limits |

Also ask: "Any words or phrases you never want in your content?" Write them one per line into `business-brain/banned-phrases.txt`, uncommented. Offer a few common cliches as suggestions, user decides.

## Phase 4: Research setup

1. Ask for 3 to 10 competitor or inspiration accounts (handle and platform). Write `research/watchlist.md`.
2. Explain the outlier idea in one sentence: "We look for posts that did far better than that creator's normal, and learn why."

## Phase 5: Integrations (all optional)

Explain briefly, then ask which they want now. Skipping is fine, everything still works with files.

- **Scraping (Apify)** for the Research agents. If an Apify connector is available in this session, confirm it works.
- **Publishing (Buffer or other)** for the scheduler. Needs their own account and credentials. Never ask them to paste keys in chat. Point to `integrations/README.md`.
- **DM funnels (ManyChat or other)** for conversion-builder. Same rule.
- **FFmpeg** for video editing.

## Phase 6: Verify and hand over

1. Run `python scripts/validate.py` and `python tests/test_content_os.py`. Report plainly.
2. Run `python scripts/lint_voice.py business-brain` to catch banned phrases in the brain files.
3. Give a short summary: what was configured, what is still TODO, what is not connected.
4. Tell them how to use it: `/content-os` then say what they want, for example "find what is working in my niche" or "plan my week". If slash commands are not showing, open this folder as a project in the Claude Code desktop app.
5. Offer to run the first loop right now: `content-os-outlier-scout`, then `content-os-content-strategist`.

## Re-running

If setup was done before, ask what to change instead of starting over. Update only those files.

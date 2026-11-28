# Content OS

A free, brand-agnostic content operating system for Claude Code. 16 agents in 7 departments take you from research to planning, creation, publishing, lead capture and performance review, with a human approval step before anything goes out.

```
Research -> Planning -> Studio -> Brand check -> Distribution -> Conversion -> Analytics
   ^                                                                              |
   +------------------------ recommendations loop ---------------------------------+
```

## One-step install

Open Claude Code (desktop app or web) and paste this:

```text
Clone https://github.com/YOUR-USERNAME/content-os and set it up for me.
Follow the setup instructions in the repo. Ask me the questions step by step,
starting with my website, and customise everything to my brand.
```

Claude will clone the repo, read your website, draft your brand profile from it, then ask short questions to confirm and fill the gaps. When it finishes you have a working Content OS configured for your brand.

**Desktop app:** after setup, open the cloned folder (`content-os`) as a project so the slash commands load. Then type `/content-os` and say what you want, for example "find what is working in my niche" or "plan my week".

**Web app:** start a session on your copy of the repo (see "Your own private copy" below). Skills load automatically and outputs are saved as files you commit.

**Manual route:** `git clone` it, open the folder as a project, type `/setup-content-os`.

Requires Python 3.8+ for the helper scripts. No third-party packages. Everything else is optional: scraping, publishing and funnel tools can be connected later.

## What setup does

1. Checks your environment and asks if you want to disconnect from this public template so your brand files stay private.
2. Asks your brand name, website, platforms and publishing tool.
3. Reads your website (`scripts/site_snapshot.py`): copy, offers, buttons, colours, fonts, social links.
4. Shows you what it found and asks for corrections.
5. Walks through eight brand files one at a time: you, what you sell, who you serve, your voice, pillars, visuals, offers and CTA keywords, boundaries.
6. Takes your banned phrases and your competitor list.
7. Offers optional integrations, never asks for keys in chat.
8. Runs the checks and offers to run your first research and planning loop.

## Your own private copy

This repo is a public template. Your brand files are personal, so keep your working copy private:

```bash
git clone https://github.com/YOUR-USERNAME/content-os my-content-os
cd my-content-os
git remote remove origin
```

Then create a private repo on GitHub and push to it if you want a backup or want to use the web app.

## Departments and agents

| Department | Agent | Build | Gate |
|---|---|---|---|
| business-brain | brain-keeper | modify | none |
| research | outlier-scout, hook-analyst | modify | none |
| research | competitor-research | reuse | none |
| planning | content-strategist | modify | none |
| studio | hook-writer, scriptwriter, video-editor | modify | none |
| studio | carousel-designer | reuse | none |
| distribution | repurposer | reuse | none |
| distribution | scheduler | modify | **publish** |
| distribution | stories-writer | build | none |
| distribution | engagement-assistant | modify | **outbound message** (draft only) |
| conversion | conversion-builder | build | **outbound message** |
| analytics | performance-tracker, analyst | modify | none |

Source of truth: [`agents.json`](agents.json). Each agent is a skill at `.claude/skills/content-os-<agent>/SKILL.md`. Department folders hold the outputs.

## Making it yours

| What | Where |
|---|---|
| Brand name, platforms, publishing tool, outlier threshold | `config.json` |
| Who you are, offer, audience, voice, pillars, boundaries | `business-brain/*.md` (filled by setup from your website and answers) |
| Re-run or change setup | `/setup-content-os` (it asks what to change, not everything again) |
| Phrases you never want written | `business-brain/banned-phrases.txt` |
| Competitors and inspiration accounts | `research/watchlist.md` |
| Swap a tool (Buffer, ManyChat) | Edit the matching agent's `SKILL.md` and `integrations/` |

## What is real code today

| Piece | File |
|---|---|
| Outlier scoring with a configurable multiplier and leave-one-out median baseline | `scripts/outlier.py` |
| Approval gate with asset hash, so edits after approval void it | `scripts/approve.py` |
| Banned-phrase lint driven by your `business-brain/banned-phrases.txt` | `scripts/lint_voice.py` |
| Website reader for brand analysis | `scripts/site_snapshot.py` |
| Repo self-check | `scripts/validate.py` |

Everything else is skill instructions. Skills do not provide API access. See [`integrations/README.md`](integrations/README.md).

## Approval boundary

No agent publishes, emails or messages anyone without an approval record. Details: [`shared/workflows/approval-gate.md`](shared/workflows/approval-gate.md).

## Status and limits

- The upstream repositories listed in each SKILL.md came from discovery research. **None have been cloned, read or tested here.** Descriptions are from public summaries.
- Treat the "reuse / modify" labels as plans. [`docs/repository-audit.md`](docs/repository-audit.md) holds the audit checklist and the per-repo tracker to complete before copying code.
- Trending audio discovery is not solved.
- Buffer and ManyChat integrations are untested until credentials are connected.

## License

MIT. See `LICENSE`.

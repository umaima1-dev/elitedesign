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
```

Claude clones the repo and starts setup by itself. It reads your website, draft your brand profile from it, then ask short questions to confirm and fill the gaps. When it finishes you have a working Content OS configured for your brand.

**Desktop app:** after setup, open the cloned folder (`content-os`) as a project so the slash commands load. Then type `/content-os` and say what you want, for example "find what is working in my niche" or "plan my week".

**Web app:** the same prompt works. Skills load automatically and outputs are saved as files in the repo.

**Manual route:** `git clone` it, open the folder as a project, type `/setup-content-os`.

Requires Python 3.8+ for the helper scripts. No third-party packages. Everything else is optional: scraping, publishing and funnel tools can be connected later.

## What setup does

1. Asks your brand name, website, platforms and publishing tool.
2. Reads your website (`scripts/site_snapshot.py`): copy, offers, buttons, colours, fonts, social links.
3. Shows you what it found and asks for corrections.
4. Walks through eight brand files one at a time: you, what you sell, who you serve, your voice, pillars, visuals, offers and CTA keywords, boundaries.
5. Takes your banned phrases and your competitor list.
6. Offers optional integrations, never asks for keys in chat.
7. Runs the checks.
8. Shows you every command, how each agent works and a normal week, as a table ([`shared/cheatsheet.md`](shared/cheatsheet.md)), then offers to run your first research and planning loop.

## Commands at a glance

Type `/content-os` and ask in plain words, or call an agent directly. Full table with examples: [`shared/cheatsheet.md`](shared/cheatsheet.md).

| Command | Does |
|---|---|
| `/setup-content-os` | Set up or change your brand profile |
| `/content-os` | Routes any request to the right agent |
| `/content-os-outlier-scout`, `-hook-analyst`, `-competitor-research` | Research what works |
| `/content-os-content-strategist` | Weekly plan |
| `/content-os-hook-writer`, `-scriptwriter`, `-carousel-designer`, `-video-editor` | Create |
| `/content-os-repurposer`, `-scheduler`, `-stories-writer`, `-engagement-assistant` | Distribute |
| `/content-os-conversion-builder` | Freebie and DM funnel |
| `/content-os-performance-tracker`, `-analyst` | Measure and feed back |
| `/content-os-brain-keeper` | Check anything against your brand |

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

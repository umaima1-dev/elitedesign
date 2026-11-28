# Content OS

A free, brand-agnostic content operating system for Claude Code. 16 agents in 7 departments take you from research to planning, creation, publishing, lead capture and performance review, with a human approval step before anything goes out.

```
Research -> Planning -> Studio -> Brand check -> Distribution -> Conversion -> Analytics
   ^                                                                              |
   +------------------------ recommendations loop ---------------------------------+
```

## Set up in 3 steps (Claude Code desktop app)

1. **Get the folder.** Download this repo as a ZIP and unzip it (or `git clone` it).
2. **Open the folder as a project** in the Claude Code desktop app. The skills in `.claude/skills/` load automatically. No install step.
3. **Type `/setup-content-os`.** Claude interviews you, fills `config.json` and the `business-brain/` files, and checks everything works. Then use `/content-os` for any request, for example "find what is working in my niche" or "plan my week".

**Claude Code on the web:** push the folder to your own GitHub repo and start a session on it. Skills load the same way. Outputs are files in the repo, so commit them.

**Use it in every project instead:** run `python scripts/install.py` to copy the skills into `~/.claude/skills`. Optional.

Requires Python 3.8+ for the helper scripts. No third-party packages.

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
| Who you are, offer, audience, voice, pillars, boundaries | `business-brain/*.md` (filled by `/setup-content-os`) |
| Phrases you never want written | `business-brain/banned-phrases.txt` |
| Competitors and inspiration accounts | `research/watchlist.md` |
| Swap a tool (Buffer, ManyChat) | Edit the matching agent's `SKILL.md` and `integrations/` |

## What is real code today

| Piece | File |
|---|---|
| Outlier scoring with a configurable multiplier and leave-one-out median baseline | `scripts/outlier.py` |
| Approval gate with asset hash, so edits after approval void it | `scripts/approve.py` |
| Banned-phrase lint driven by your `business-brain/banned-phrases.txt` | `scripts/lint_voice.py` |
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

# Content OS for AI Savvy Founders

A repo-based content operating system: 16 agents in 7 departments, each a Claude Code skill with defined inputs, outputs, process and approval rules. It reuses ideas from the best open-source skills instead of installing 30 repos as 30 competing agents.

```
Research -> Planning -> Studio -> Brain check -> Distribution -> Conversion -> Analytics
   ^                                                                              |
   +------------------------ recommendations loop ---------------------------------+
```

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

Source of truth: [`agents.json`](agents.json). Each agent lives at `<department>/<agent>/SKILL.md`.

## Quick start

```bash
cd content-os
python scripts/validate.py          # 16 agents valid, no banned phrases
python tests/test_content_os.py     # unit tests
python scripts/install.py           # installs skills as content-os-<agent> into ~/.claude/skills
```

Then fill `business-brain/` (ask `content-os-brain-keeper` to interview you), add handles to `research/watchlist.md`, and start with the orchestrator in `SKILL.md`.

Requires Python 3.8+. No third-party packages.

## What is real code today

| Piece | File |
|---|---|
| Outlier scoring with a configurable multiplier and leave-one-out median baseline | `scripts/outlier.py` |
| Approval gate with asset hash, so edits after approval void it | `scripts/approve.py` |
| Banned-phrase lint driven by `business-brain/banned-phrases.txt` | `scripts/lint_voice.py` |
| Repo self-check | `scripts/validate.py` |

Everything else is skill instructions. Skills do not provide API access. See [`integrations/README.md`](integrations/README.md).

## Approval boundary

No agent publishes, emails, or messages a lead without an approval record. Details: [`shared/workflows/approval-gate.md`](shared/workflows/approval-gate.md).

## Honest status

- The upstream repositories listed in each SKILL.md came from discovery research. **None have been cloned, read or tested here.** Descriptions are from public summaries.
- Treat the "reuse / modify" labels as plans. [`docs/repository-audit.md`](docs/repository-audit.md) holds the audit checklist and the per-repo tracker to complete before copying code.
- Trending audio discovery is not solved.
- Buffer and ManyChat integrations are untested until credentials are connected.

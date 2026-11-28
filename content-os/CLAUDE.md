# Content OS

This folder is a content operating system made of Claude Code skills. Start with `/setup-content-os` the first time, then use `/content-os` for everything.

- Config: `config.json`. Brand knowledge: `business-brain/`.
- Skills live in `.claude/skills/` and are discovered automatically when this folder is opened as a project.
- Outputs are written to the department folders: `research/`, `planning/`, `studio/`, `distribution/`, `conversion/`, `analytics/`.
- Hard rule: never publish, email or message anyone without an approval record (`scripts/approve.py`, see `shared/workflows/approval-gate.md`).
- Use the brand name exactly as in `config.json`. Never use phrases in `business-brain/banned-phrases.txt`.
- Scripts need only Python 3.8+. Run `python scripts/validate.py` after editing skills.

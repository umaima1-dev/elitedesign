# Content OS

A content operating system made of Claude Code skills: research, planning, creation, distribution, conversion and analytics, with human approval before anything goes out.

## First thing to check

Read `config.json`. If `brand_name` is `YOUR BRAND NAME`, this copy is **not set up yet**. Follow `.claude/skills/setup-content-os/SKILL.md` now, even if the user did not type `/setup-content-os`. Ask the questions step by step, starting with their website.

## After setup

- Use `/content-os` for every request. It routes to the 16 agents in `.claude/skills/`.
- Brand knowledge lives in `business-brain/`. Config lives in `config.json`.
- Outputs go to `research/`, `planning/`, `studio/`, `distribution/`, `conversion/`, `analytics/`.

## Hard rules

- Never publish, email or message anyone without an approval record. `python scripts/approve.py check <asset> --action <publish|message>` must return OK. See `shared/workflows/approval-gate.md`.
- Use the brand name exactly as in `config.json`. Never use phrases in `business-brain/banned-phrases.txt`.
- Never ask the user to paste API keys into chat. Credentials go in connector settings or environment variables.
- Never invent facts about the user's business. Unknown means `TODO`.

## Tooling

Python 3.8+, standard library only. After editing skills run `python scripts/validate.py`.

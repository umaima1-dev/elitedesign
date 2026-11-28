#!/usr/bin/env python3
"""Repo self-check: every registered agent has a valid SKILL.md, gated agents
declare their gate, and no banned phrases appear. Exit 1 on failure."""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errs = []
reg = json.load(open(os.path.join(ROOT, "agents.json")))
if len(reg) != 16:
    errs.append(f"expected 16 agents, found {len(reg)}")
for a in reg:
    p = os.path.join(ROOT, ".claude", "skills", "content-os-" + a["name"], "SKILL.md")
    if not os.path.isfile(p):
        errs.append(f"missing {p}"); continue
    t = open(p, encoding="utf-8").read()
    m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", t)
    if not m or m.group(1) != "content-os-" + a["name"]:
        errs.append(f"bad frontmatter: {p}")
    for sec in ("## Job", "## Inputs", "## Outputs", "## Process", "## Rules"):
        if sec not in t:
            errs.append(f"{p} missing {sec}")
    label = a["gate"].upper().replace("-", " ")
    if a["gate"] != "none" and "Gate: " + label not in t:
        errs.append(f"{p} does not declare its gate")
for extra in ("content-os", "setup-content-os"):
    if not os.path.isfile(os.path.join(ROOT, ".claude", "skills", extra, "SKILL.md")):
        errs.append("missing skill " + extra)
cs = os.path.join(ROOT, "shared", "cheatsheet.md")
cst = open(cs, encoding="utf-8").read() if os.path.isfile(cs) else ""
for a in reg:
    if "/content-os-" + a["name"] not in cst:
        errs.append("cheatsheet missing /content-os-" + a["name"])
rc = subprocess.call([sys.executable, os.path.join(ROOT, "scripts", "lint_voice.py"), ROOT])
if rc:
    errs.append("banned phrases found")
for e in errs:
    print("FAIL:", e)
print("OK" if not errs else f"{len(errs)} problem(s)")
sys.exit(1 if errs else 0)

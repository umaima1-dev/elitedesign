#!/usr/bin/env python3
"""Copy every agent SKILL.md into a Claude Code skills folder.
Usage: install.py [--target ~/.claude/skills | <project>/.claude/skills]
Copies (not symlinks) so it works on Windows. Re-run after edits."""
import argparse, json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--target", default=os.path.join(os.path.expanduser("~"), ".claude", "skills"))
a = ap.parse_args()
for ag in json.load(open(os.path.join(ROOT, "agents.json"))):
    src = os.path.join(ROOT, ag["department"], ag["name"], "SKILL.md")
    dst = os.path.join(a.target, "content-os-" + ag["name"])
    os.makedirs(dst, exist_ok=True)
    text = open(src, encoding="utf-8").read().replace(f"name: {ag['name']}\n", f"name: content-os-{ag['name']}\n", 1)
    open(os.path.join(dst, "SKILL.md"), "w", encoding="utf-8").write(text)
    print("installed", dst)

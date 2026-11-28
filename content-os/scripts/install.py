#!/usr/bin/env python3
"""OPTIONAL. Copy the Content OS skills into your global Claude Code skills folder
so they work in every project. Not needed if you open this folder as a project.
Usage: install.py [--target ~/.claude/skills]"""
import argparse, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".claude", "skills")
ap = argparse.ArgumentParser()
ap.add_argument("--target", default=os.path.join(os.path.expanduser("~"), ".claude", "skills"))
a = ap.parse_args()
for name in sorted(os.listdir(SRC)):
    if os.path.isfile(os.path.join(SRC, name, "SKILL.md")):
        shutil.copytree(os.path.join(SRC, name), os.path.join(a.target, name), dirs_exist_ok=True)
        print("installed", name)
print("Note: global copies still read config.json and business-brain/ from the folder you run Claude in.")

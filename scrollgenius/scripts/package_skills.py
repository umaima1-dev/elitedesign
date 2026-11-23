#!/usr/bin/env python3
"""Validate the generated skills and zip each one so it can be shared or installed.

Usage: package_skills.py <folder-with-generated-skills> [-o dist]
Each subfolder must contain SKILL.md with name + description frontmatter.
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path


def check(skill_dir):
    problems = []
    md = skill_dir / "SKILL.md"
    if not md.exists():
        return ["missing SKILL.md"]
    text = md.read_text(encoding="utf-8")
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not fm:
        return ["missing --- frontmatter ---"]
    name = re.search(r"^name:\s*(.+)$", fm.group(1), re.M)
    desc = re.search(r"^description:\s*(.+)$", fm.group(1), re.M)
    if not name or name.group(1).strip() != skill_dir.name:
        problems.append(f"frontmatter name must equal folder name '{skill_dir.name}'")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", skill_dir.name):
        problems.append("folder name must be lowercase-hyphen")
    if not desc or len(desc.group(1)) < 40:
        problems.append("description is missing or too short to trigger reliably")
    if not re.search(r"credit", text, re.I):
        problems.append("no creator credits section")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skills_dir")
    ap.add_argument("-o", "--out", default="dist")
    a = ap.parse_args()
    root, out = Path(a.skills_dir), Path(a.out)
    dirs = sorted(d for d in root.iterdir() if d.is_dir())
    if not dirs:
        sys.exit("No skill folders found.")
    out.mkdir(exist_ok=True)
    bad = 0
    for d in dirs:
        problems = check(d)
        if problems:
            bad += 1
            print(f"[fix] {d.name}: " + "; ".join(problems))
            continue
        zpath = out / f"{d.name}.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(d.rglob("*")):
                if f.is_file():
                    z.write(f, Path(d.name) / f.relative_to(d))
        print(f"[ok]  {zpath}")
    print("\nInstall one: unzip it into ~/.claude/skills/  (Windows: %USERPROFILE%\\.claude\\skills\\)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

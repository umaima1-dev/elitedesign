#!/usr/bin/env python3
"""Banned-phrase lint. Usage: lint_voice.py <file-or-dir> [...]
Phrases come from business-brain/banned-phrases.txt. Exit 1 on any hit."""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PHRASES = os.environ.get("CONTENT_OS_BANNED", os.path.join(ROOT, "business-brain", "banned-phrases.txt"))
EXTS = {".md", ".txt", ".json", ".py", ".yaml", ".yml"}

def load():
    with open(PHRASES, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]

def files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
        else:
            for d, _, fs in os.walk(p):
                if ".git" in d.split(os.sep):
                    continue
                for n in fs:
                    if os.path.splitext(n)[1] in EXTS:
                        yield os.path.join(d, n)

def main(paths):
    pats = [(p, re.compile(re.escape(p), re.I)) for p in load()]
    hits = 0
    for f in files(paths or [ROOT]):
        if os.path.abspath(f) in (os.path.abspath(PHRASES), os.path.abspath(__file__)):
            continue
        for n, line in enumerate(open(f, encoding="utf-8", errors="ignore"), 1):
            for phrase, rx in pats:
                if rx.search(line):
                    hits += 1
                    print(f"{f}:{n}: banned phrase '{phrase}'")
    print(f"{hits} hit(s)")
    return 1 if hits else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

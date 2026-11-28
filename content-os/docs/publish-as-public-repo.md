# Publishing this as a public one-click repo

For maintainers. Users never need this page.

## 1. Create the repo

On GitHub, create a new **public** repo named `content-os` with no README, licence or .gitignore.

## 2. Push this folder as the repo root

If this folder lives inside another repo (as it does in `elitedesign`), split it out so `.claude/skills/` ends up at the root:

```bash
git subtree split --prefix=content-os -b content-os-release
git push git@github.com:YOUR-USERNAME/content-os.git content-os-release:main
```

Or copy the folder somewhere clean, then `git init`, commit and push.

## 3. Replace the placeholder

`README.md` uses `YOUR-USERNAME` in the install prompt. Replace it with your GitHub username or org, commit, push.

## 4. Pre-publish checks

```bash
python scripts/validate.py
python tests/test_content_os.py
```

Also confirm that `config.json` still says `YOUR BRAND NAME`, `business-brain/*.md` still contain `TODO`, and `business-brain/site-snapshot.md` does not exist. If any of those is filled in, you are about to publish your own brand data.

## 5. Try it as a stranger

In a fresh Claude Code session, paste the install prompt from the README and walk through setup on a test website. Fix anything confusing.

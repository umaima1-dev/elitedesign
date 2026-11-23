# ScrollGenius: Setup SOP

**What this does:** turns the tutorial reels you saved on Instagram into skills that Claude can run for you. You set it up once. After that you just drop in reels.

**Time needed:** about 10 minutes for setup. About 15 to 40 seconds per reel after that.

---

## Before you start

You need:

- [ ] A computer running **Mac or Windows**
- [ ] The **Claude desktop app** with **Claude Code**, signed in to your Claude account
- [ ] An **Instagram account** with saved reels
- [ ] An internet connection and about **1 GB** of free disk space
- [ ] This file: `scrollgenius.zip`

Do **not** unzip `scrollgenius.zip`. Claude does that for you.

---

## Part 1: One-time setup

### Step 1. Open Claude Code
1. Open the **Claude desktop app**.
2. Switch to **Claude Code** (the Code tab).
3. Start a **new session**. When it asks for a folder, pick any folder (for example Documents). The folder does not matter.

### Step 2. Attach the zip
Drag `scrollgenius.zip` into the message box. You will see it appear as an attachment.

### Step 3. Paste this prompt and send it
Copy it exactly:

```text
Set up ScrollGenius from the attached zip. Unzip it into ~/.claude/skills/ so that ~/.claude/skills/scrollgenius/SKILL.md exists, install Python if I do not have it, run its scripts/bootstrap.py, fix anything that fails, then read the SKILL.md so you can run it for me in this session. Tell me when it is ready.
```

### Step 4. Approve the permission prompts
Claude will ask permission before it runs commands or installs things. Read each prompt and approve it. This is normal. It is installing:

| What | Why |
|---|---|
| Python (only if you do not have it) | runs the ScrollGenius scripts |
| yt-dlp | downloads your saved reels |
| Whisper (small model) | listens to each reel and writes out what is said |
| ffmpeg | pulls still frames from each reel |

The first run also downloads the Whisper model (about 150 MB), so it can take a few minutes.

### Step 5. Wait for "READY"
Claude finishes with a message that ScrollGenius is ready. **Setup is done. You never repeat Part 1.**

If it says `NOT READY`, go to the Troubleshooting section at the bottom.

---

## Part 2: Export your saved reels from Instagram

You do this once now, and again whenever you want to add more.

1. Open Instagram (app or website) and go to **Settings**.
2. Tap **Accounts Centre**.
3. Tap **Your information and permissions**.
4. Tap **Download your information**.
5. Tap **Some of your information**.
6. Tick **Saved** (only Saved).
7. Choose **Download to device** (or the email option).
8. Set **Format** to **JSON** and **Date range** to **All time**.
9. Tap **Submit**.

Instagram prepares the file. This can take a few minutes up to a few hours. You get an email with a download link. Download the **zip file**. **Do not unzip it.**

> Instagram sometimes renames these menus. If a step looks different, look for "Download your information" and make sure Saved, JSON and All time are selected.

---

## Part 3: Turn your reels into skills

### Step 1. Open Claude Code
Start a new session in the Claude desktop app (any folder).

### Step 2. Attach your Instagram export
Drag the Instagram zip into the message box.

### Step 3. Send this prompt
```text
Run ScrollGenius on this.
```

### Step 4. Let it work
Claude does the whole job without more questions:

1. Reads your saved list
2. Downloads each reel, listens to it and looks at it
3. Keeps only the real tutorials (memes, opinions and ads are skipped)
4. Groups them by topic
5. Writes one skill per topic and credits every creator

You can leave it running. If you stop it, send the same prompt later and it continues where it left off.

### Step 5. If Instagram blocks the downloads
Instagram sometimes refuses to let a program download reels. If so, Claude stops and asks **which browser you use to log in to Instagram**. Reply with its name (Chrome, Firefox, Safari or Edge).

Claude then uses your browser's login **on your own computer** to download the reels. Nothing is uploaded or stored anywhere.

- You must be logged in to Instagram in that browser.
- If it errors, **fully close that browser** and try again.
- If it still fails, log in to Instagram in **Firefox** and choose Firefox. This is the most reliable.
- On Mac, Safari may need Full Disk Access for the Terminal. Claude tells you if so.

### Step 6. Read your results
At the end Claude tells you:

- How many reels it read
- How many were real tutorials
- Which reels failed, and why (private accounts and deleted reels cannot be downloaded)
- Which skills it created, and the phrase to say to use each one

---

## Part 4: Use your new skills

Skills are ready to use. If Claude does not seem to know a new skill, **quit and reopen the Claude desktop app** once.

Then just ask in plain words. For example, if a skill was built from video editing reels:

```text
Edit my video
```

Claude follows the workflow built from the tutorials you saved, using the steps and tools the creators showed.

---

## Part 5: Add more reels later

Whenever you save new reels, or want to add one:

- **One reel:** paste the reel link into a new Claude Code session and send: `Run ScrollGenius on this.`
- **Many reels:** attach a new Instagram export (or a text file with one link per line) and send the same prompt.

New tutorials are added to the skills you already have, or become a new skill. Reels you already processed are skipped.

---

## Where everything is saved

| What | Where |
|---|---|
| Your finished skills | `~/.claude/skills/` (one folder per topic) |
| Zip copies of your skills, to share | `~/ScrollGenius/dist/` |
| Working files (transcripts, frames) | `~/ScrollGenius/` |

`~` means your home folder. On Windows that is `C:\Users\<your name>`.

Everything stays on your computer. Videos are deleted as soon as each one is read. Only the written transcript and a few still frames are kept.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| `NOT READY` after setup | Read the line starting with a dash. If it says it cannot reach instagram.com or huggingface.co, check your internet, turn off any VPN, then send: `Run ScrollGenius setup again.` |
| Claude says Python is missing | Approve the install when asked. On Windows it uses `winget`. If that is not available, it will point you to python.org. Install from there, then try again. |
| "login required" or "rate limit" errors | Follow Part 3, Step 5 (use your browser login). |
| It found 0 reels | Your export did not include Saved. Redo Part 2 and make sure **Saved** is ticked, format is **JSON**. |
| Some reels failed | Normal. Private accounts and deleted reels cannot be downloaded. Claude lists them. |
| Reels that are not tutorials were skipped | Working as designed. Only step-by-step tutorials become skills. |
| New skill does not show up | Quit and reopen the Claude desktop app. |
| It is very slow | Say: `Use the tiny model for ScrollGenius.` It is faster and a little less accurate. |
| Downloads suddenly start failing everywhere | Instagram changed something. Say: `Update ScrollGenius's downloader and retry the failed reels.` |
| You want to start over | Delete the folder `~/ScrollGenius/` and the topic skills in `~/.claude/skills/`, then run Part 3 again. |

Still stuck? Copy the error message and paste it into Claude Code. Say "Fix this ScrollGenius error." It can read the setup scripts and repair them.

---

## Quick reference

**First time:** attach `scrollgenius.zip` + send the setup prompt (Part 1, Step 3).
**Every time:** attach your list, or paste a reel link, then send `Run ScrollGenius on this.`

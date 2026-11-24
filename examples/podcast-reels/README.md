# Podcast to Reels animation

One podcast in the centre, short vertical clips flowing out of it, each with its own caption.

- `index.html` is the whole animation (no build step). Open it in a browser.
- With no `clips.js` next to it, it runs in **demo mode** (placeholder cards + the episode's YouTube thumbnail).
- `make_clips.py` downloads the episode once and cuts the clips for the page.

```bash
pip install yt-dlp          # ffmpeg must be on your PATH
python make_clips.py "https://youtu.be/Kl-I7sUcAOY"
```

Then open `index.html`. Useful flags: `--count 12`, `--len 8` (seconds per clip), `--title "Episode name"`,
`--input episode.mp4` (skip the download), `--cookies-from-browser chrome` (if YouTube asks you to sign in).

Clips are picked from YouTube's "Most replayed" graph when the video has one, otherwise evenly spaced.
Captions come from the video's subtitles, falling back to chapter titles, then "CLIP N".
Edit `clips.js` by hand to change any caption, tag or timestamp.

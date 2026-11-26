# Clip It sales page: GoHighLevel build guide

Every section is **self-contained**: its own unique wrapper class (`clone-...`), its own CSS scoped to that wrapper, no shared stylesheet, so nothing leaks into GHL or into the other sections. Same pattern as your `clone-you-recorded-a-great-episode` block.

## One-time setup (Page > Settings > Custom Code > Header Code)
Paste `00-fonts-header-code.html` (Inter, Open Sans, Manrope). Set the page background colour to `#1C1412`.

## Media
1. Upload everything in `media-to-upload/` to the GHL Media Library.
2. Replace each `{{file-name}}` token with that file's URL. Either find-and-replace by hand, or fill `media-urls.txt` and run `python3 fill_urls.py` (ready files appear in `ready/`).
3. The tokens are: `logo.png`, `site-bg.png`, `clip_05.mp4/.jpg`, `clip_08.mp4/.jpg`, `clip_10.mp4/.jpg`, `hero-loop.mp4`, `motion.jpg`, `main.jpg`.

## Build order (one Custom Code element per section)
| File | Section | Needs |
|---|---|---|
| 01-nav.html | Fixed top bar (skip if you use the GHL header) | logo.png |
| 02-hero.html | Hero with 3 playing reels | clip_05, clip_08, hero-loop, motion.jpg |
| 03-problem.html | You recorded a great episode | none |
| 04-what-it-does.html | Press the button: 6 numbered steps | main.jpg, clip_10, clip_08.jpg |
| 05-how-it-works.html | Three steps, one coffee | none |
| 06-why-local.html | Why it runs on your computer | site-bg.png |
| 07-pricing.html | Pricing and comparison | none |
| 08-honest-bit.html | The honest bit | none |
| 09-who-its-for.html | Who it is for | none |
| 10-faq.html | FAQ | none |
| 11-final-cta.html | Final call to action | site-bg.png |
| 12-footer.html | Footer | logo.png |

For each: add a **full-width section**, set section and row padding/margin to **0**, one column, add a **Custom JS/HTML** element, paste the file.

## Notes
- All "Get Clip It free" buttons point to `/thanks`. Change it if your thank-you page URL is different.
- The eyebrow "What Clip It does" now lives in `04-what-it-does.html` (it used to sit at the bottom of the problem section, which put it on the wrong background).
- Each section already pauses its videos for visitors who prefer reduced motion. There is no shared JavaScript to install.
- The scroll-reveal fade-ins were left out so each block works on its own.

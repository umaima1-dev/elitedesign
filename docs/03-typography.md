# 03 · Typography

Type carries ~70% of the "elite" feeling. The formula: **one characterful display face + one neutral workhorse** (+ an optional mono for labels). All faces below are free on Google Fonts.

## The pairings used in this kit

| Design | Display | Body / UI | Labels | Personality |
|---|---|---|---|---|
| Maison Aurél | **Cormorant Garamond** (light italic) | Jost | — | High-contrast couture serif |
| Amara Reed | **Fustat** (200–300 wt) | Fustat | — | Warm, modern, premium |
| Prisma | **Bricolage Grotesque** (800) | Roboto Condensed | — | Bold, quirky, playful |
| Vessel | **Bodoni Moda** (display) | Syne | — | Dramatic Didone editorial |
| FabChain | **Anton** | DM Sans | DM Mono | Loud, condensed, web3 |

## Substituting paid fonts
Reference sites often use paid display faces. Closest free swaps:

| Paid (seen in the wild) | Free Google Fonts substitute |
|---|---|
| Manuka (ApeChain) | **Anton** (tall condensed bold) |
| PP Eiko (Occupied) | **Bodoni Moda** (high-contrast serif) |
| PP Otherside | **Space Grotesk** / Bricolage Grotesque |
| GT Sectra / editorial serifs | **Fraunces**, Cormorant Garamond |
| Söhne / Aeonik (neutral grotesk) | **Inter**, Hanken Grotesk, Space Grotesk |

> If a client licenses the real font, drop the `@font-face` in and you get a pixel-true match. Anton/Bodoni get you 90% there for free.

## Rules that make type look designed

1. **Tighten display letter-spacing.** Big headings want negative tracking: `letter-spacing: -0.02em` to `-0.04em`. Tiny labels want *positive*, wide tracking: `0.2em–0.4em`, uppercase.
2. **Go bigger than feels safe.** Hero headings here use `clamp(44px, 8–13vw, 100–170px)`. Confidence reads as quality.
3. **Line-height tightens as size grows.** Display: `0.9–1.0`. Body: `1.5–1.75`.
4. **Mix weights, not faces.** A 200-weight Fustat next to a 600 looks richer than adding a third font.
5. **Italic accent words.** One italic word in a serif headline (`<em>` in Cormorant/Bodoni) adds editorial flourish — e.g. *"worn for life."*
6. **Gradient or accent on one word.** `background-clip:text` a single keyword in the brand gradient to draw the eye.

## A reliable loading pattern
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300..500;1,300..400&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
```

## Label / eyebrow style (used everywhere)
```css
.eyebrow{ font-size:12px; letter-spacing:0.3em; text-transform:uppercase; color:var(--accent); }
```
Small, wide, uppercase, accent-colored. It's the connective tissue of an editorial layout.

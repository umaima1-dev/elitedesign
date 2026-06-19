# Design Craft — a playbook for building elite, modern websites

A complete, opinionated playbook for designing and shipping **studio-grade websites** — the kind that win on Awwwards, not the kind that "scream AI."

It was built by reverse-engineering real, beautiful sites, extracting their *actual* design tokens, and rebuilding them as five distinct, production-ready landing pages — each with real AI-generated imagery and signature scroll interactions. This repo documents **every technique** so you can do the same.

> **Live gallery of all 5 designs:** open [`examples/index.html`](examples/index.html), or see them deployed.

---

## What's inside

| | |
|---|---|
| 🎨 **5 complete designs** | Five distinct visual languages, fully coded ([`examples/`](examples/)) |
| 📐 **Design principles** | How to make work feel *intentional*, not generated → [`docs/01-principles.md`](docs/01-principles.md) |
| 🔍 **Token extraction** | Pull a real site's exact colors/fonts from its CSS → [`docs/02-extracting-real-sites.md`](docs/02-extracting-real-sites.md) |
| 🔠 **Typography** | The font pairings that work, and why → [`docs/03-typography.md`](docs/03-typography.md) |
| 🌈 **Color & themes** | Real palettes + how to theme → [`docs/04-color-and-themes.md`](docs/04-color-and-themes.md) |
| ✨ **Animations** | Copy-paste recipes for every scroll effect → [`docs/05-animations.md`](docs/05-animations.md) |
| 🔘 **Buttons & UI** | Buttons, cursors, grain, marquees → [`docs/06-buttons-and-ui.md`](docs/06-buttons-and-ui.md) |
| 🖼️ **Image generation** | The AI-imagery workflow that doesn't look like slop → [`docs/07-image-generation.md`](docs/07-image-generation.md) |
| 🚀 **Deployment** | Ship it to the web → [`docs/08-deployment.md`](docs/08-deployment.md) |
| 🧩 **Snippets** | Drop-in JS/CSS → [`snippets/`](snippets/) |

---

## The stack (no build step)

Every design is a **single HTML file**. No framework, no bundler, no `npm install`. Just open it.

- **[GSAP](https://gsap.com) + ScrollTrigger** — the animation engine behind most award-winning sites (now 100% free)
- **[Lenis](https://github.com/darkroom-engineering/lenis)** — buttery smooth-scroll; the single biggest "this feels premium" upgrade
- **[Three.js](https://threejs.org)** — only where a WebGL shader background earns its place
- **Google Fonts** — for type
- **AI image generation** (Magnific / Flux / Midjourney / DALL·E) — for real photography & 3D art

That's the whole toolkit. The magic is in *how* you combine them — that's what the docs cover.

---

## The five designs (case studies)

Each was built from a real reference, using its **actual extracted tokens**.

### 01 · Maison Aurél — *Quiet luxury*
Dark fashion-maison. Champagne gold on near-black, **Cormorant Garamond** + Jost, a WebGL gold-silk shader, a preloader counter, a **curved-path heritage timeline** that draws on scroll, and a pinned horizontal collection.
`--bg:#0a0908 · --gold:#c5a572`

### 02 · Amara Reed — *Personal brand*
Warm, premium mentor brand (tokens lifted from a real Saudi luxury site). Dark teal + gold, **Fustat**, and a **scatter gallery** — images stacked in the centre that fly apart on scroll, all the *same AI-generated person* (via a reference image).
`--bg:#081614 · --gold:#e8c583`

### 03 · Prisma — *Creative studio*
Bright, playful, rainbow. **Bricolage Grotesque**, the exact 15-hue spectrum + warm-paper base from the reference, an **interactive image-trail**, hover-reveal previews, a sticky-stack, and a colour-cycling accent.
`--cream:#f7f6f3 · --orange:hsl(20 100% 50%)`

### 04 · Vessel — *Dark editorial*
High-contrast art/design studio. **Bodoni Moda** + Syne, oxblood red `#8C1209` on `#080808`, AI fine-art imagery, and a **pinned horizontal-scroll gallery** where works glide sideways.

### 05 · FabChain — *Web3 / crypto*
Energetic blockchain brand. **Anton** + DM Sans/Mono, deep navy `#020315` with the signature rainbow gradient, two-row opposing word-marquees, **3D-tilt dApp cards**, and AI 3D objects.

→ Full breakdown of each in [`docs/04-color-and-themes.md`](docs/04-color-and-themes.md).

---

## The core philosophy

1. **Steal the *system*, not the pixels.** Extract a real site's tokens, then build something new with them. (See [`docs/02`](docs/02-extracting-real-sites.md).)
2. **Restraint reads as expensive.** One accent. Generous whitespace. Slow, confident easing. The fastest way to look "AI" is too many bright colours and snappy motion.
3. **Motion is the product.** Smooth scroll + a few signature scroll moments separate "template" from "studio."
4. **Real imagery or none.** Random stock clashes. Generate cohesive, on-brand images — and unify them (grayscale, duotone, consistent grading) so a set feels intentional.
5. **Ship it.** A design isn't done until it's on a URL someone can open.

---

## Quick start

```bash
# clone, then just open any design — no install needed
open examples/index.html        # macOS
start examples/index.html       # Windows
```

To develop with live-reload + smooth scroll working correctly, serve the folder:

```bash
cd examples
python -m http.server 3000      # then visit http://localhost:3000
```

Then read [`docs/05-animations.md`](docs/05-animations.md) and start remixing.

---

## License

MIT — use it, learn from it, build beautiful things. Fonts and any licensed assets retain their own licenses; the AI-generated images here are illustrative — generate your own for production.

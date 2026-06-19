# 04 · Color & themes

Every design is driven by a small `:root` token block. Copy any of these to start in that world. Each was extracted from a real reference (see [`02`](docs/02-extracting-real-sites.md)).

## 01 · Maison Aurél — dark quiet luxury
```css
:root{
  --bg:#0a0908; --ink:#f3ece1; --muted:#9c948a;
  --gold:#c5a572; --gold-soft:#d8c4a0;
}
```
Near-black + champagne gold. WebGL gold-silk shader, vignette, 6% grain. Cormorant Garamond.

## 02 · Amara Reed — dark teal + gold (lifted from a luxury gifting site)
```css
:root{
  --bg:#081614; --bg2:#0c201d; --teal:#1c3431; --ink:#f9f8f8;
  --gold:#e8c583; --gold-soft:#ffd8a2; --gold-deep:#937241;
  --line:rgba(255,216,162,0.16);
}
```
Warm gold accents on deep teal-black. Gold-shimmer dividers (`linear-gradient(90deg,#ffd8a200,#ffd8a2,#ffd8a200)`). Fustat.

## 03 · Prisma — bright rainbow studio (exact tokens from duyvenvoorde.nl)
```css
:root{
  --cream:#f7f6f3; --ink:#141414; --muted:#6f6a60;
  --orange:hsl(20 100% 50%);  --yellow:hsl(47 95% 52%);
  --green:hsl(155 85% 29%);   --purple:hsl(254 79% 66%); --pink:hsl(331 94% 81%);
}
/* signature: cycle 15 hues, 24° apart */
const HUES = Array.from({length:15}, (_,i)=> i*24);  // hsl(h 90% 55%)
```
Warm-paper base, near-black ink, a *spectrum* of accents used playfully.

## 04 · Vessel — dark editorial (tokens from an experimental WP/Bricks site)
```css
:root{
  --black:#080808; --white:#f0f0f0; --muted:#6c6c6c;
  --red:#8C1209; --red-deep:#670b0b;
  --line:rgba(240,240,240,0.16);
}
```
Oxblood red on near-black. Bodoni Moda + Syne. High drama, museum lighting.

## 05 · FabChain — web3 (exact tokens from apechain.com)
```css
:root{
  --navy:#08193b; --navy2:#020315; --ink:#eaf1ff; --muted:#7d9ab2;
  --blue:#0086ff;
  --rainbow:linear-gradient(275deg,#a281ff 10%,#eb8280 30%,#ebbf9a 57%,#89d0ff 78%);
}
```
Deep navy + electric blue + the rainbow gradient as the hero of the brand. Anton + DM Sans/Mono.

---

## Theming patterns that recur

**Gradient text** (one accent word or whole headline):
```css
.grad-text{ background:var(--rainbow); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
```

**Film grain** (drop on any dark theme):
```css
.grain{ position:fixed; inset:0; z-index:1; pointer-events:none; opacity:0.05; mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }
```

**Vignette** (depth on dark):
```css
.vignette{ position:fixed; inset:0; z-index:1; pointer-events:none;
  background:radial-gradient(130% 130% at 50% 40%, transparent 0%, var(--bg) 100%); }
```

**Animated gradient blobs** (alive background, kept behind text):
```css
.blob{ position:absolute; width:40vw; height:40vw; border-radius:50%; mix-blend-mode:multiply; filter:blur(90px); }
/* drift each with a slow @keyframes translate+scale; put content on z-index:1 above */
```

**Light vs dark guidance**
- Dark themes feel premium/dramatic (luxury, editorial, web3). Add grain + vignette + a glow.
- Light themes feel trustworthy/clean (SaaS, beauty, studio). Use warm off-whites (`#f7f6f3`, `#f7f7f4`) not pure `#fff`, and one confident accent.

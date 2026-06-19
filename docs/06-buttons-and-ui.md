# 06 · Buttons & UI details

The small components that recur across the designs. Full CSS in [`snippets/ui.css`](../snippets/ui.css).

## Buttons

**Pill, solid + ghost** (the default pair):
```css
.btn{ display:inline-block; padding:15px 30px; border-radius:999px; font-size:14px; letter-spacing:0.02em;
  transition:transform .3s, background .3s, color .3s, box-shadow .3s; will-change:transform; }
.btn.solid{ background:var(--accent); color:#fff; }
.btn.solid:hover{ filter:brightness(1.08); }
.btn.ghost{ border:1px solid var(--line); color:var(--ink); background:transparent; }
.btn.ghost:hover{ border-color:var(--accent); }
```

**Gradient pill** (Prisma / FabChain):
```css
.btn.grad{ background:var(--rainbow); color:#08193b; font-weight:700; }
.btn.grad:hover{ transform:translateY(-2px); box-shadow:0 12px 30px rgba(162,129,255,0.4); }
```

**Glow pill** (Aether / tech):
```css
.btn.glow{ background:var(--grad); color:#fff; box-shadow:0 0 30px rgba(59,109,255,0.45); }
.btn.glow:hover{ box-shadow:0 0 46px rgba(59,109,255,0.7); }
```

**Outline luxury button** (Maison): 1px border in the accent, wide uppercase tracking, fills on hover.
```css
.btn-lux{ padding:20px 52px; border:1px solid var(--gold); border-radius:999px; color:var(--ink);
  text-transform:uppercase; letter-spacing:0.2em; font-size:13px; transition:background .5s, color .5s; }
.btn-lux:hover{ background:var(--gold); color:var(--bg); }
```

Tip: make the primary CTA **magnetic** (recipe #7 in [`05-animations.md`](05-animations.md)).

## Animated underline nav link
```css
.nav a{ position:relative; }
.nav a::after{ content:''; position:absolute; left:0; bottom:-6px; width:100%; height:1px; background:var(--accent);
  transform:scaleX(0); transform-origin:right; transition:transform .5s cubic-bezier(.16,1,.3,1); }
.nav a:hover::after{ transform:scaleX(1); transform-origin:left; }
```

## Custom cursor (dot + trailing ring)
Use only on editorial/showcase pages — never on commerce/SaaS.
```css
body{ cursor:none; }
.cur{ position:fixed; width:8px; height:8px; border-radius:50%; background:var(--accent); transform:translate(-50%,-50%); pointer-events:none; z-index:90; }
.ring{ position:fixed; width:40px; height:40px; border:1px solid var(--accent); border-radius:50%; transform:translate(-50%,-50%); pointer-events:none; z-index:90; transition:width .4s, height .4s; }
.ring.grow{ width:84px; height:84px; }
```
```js
let mx=innerWidth/2,my=innerHeight/2,rx=mx,ry=my;
addEventListener('mousemove',e=>{ mx=e.clientX; my=e.clientY; cur.style.left=mx+'px'; cur.style.top=my+'px'; });
(function loop(){ rx+=(mx-rx)*0.15; ry+=(my-ry)*0.15; ring.style.left=rx+'px'; ring.style.top=ry+'px'; requestAnimationFrame(loop); })();
```
**To revert to native cursor:** remove `cursor:none`, delete the `.cur`/`.ring` elements and this JS. (Keep any `mousemove` that feeds a shader's `uMouse`.)

## Nav with mix-blend
A nav that flips color over any background:
```css
nav{ mix-blend-mode:difference; color:#fff; }
```

## Sticky glass nav
```css
nav{ position:sticky; top:0; background:rgba(8,9,12,0.5); backdrop-filter:blur(12px); border-bottom:1px solid var(--line); }
```

## Cards
- **Glass:** `background:rgba(255,255,255,0.04); backdrop-filter:blur(10px); border:1px solid var(--line);` + spotlight (#15).
- **Lift on hover:** `transform:translateY(-6px); box-shadow:0 24px 50px rgba(0,0,0,.14);`
- **Image frame:** wrap in `overflow:hidden`, image `grayscale(1)` default → color + `scale(1.05)` on hover for the editorial reveal.

## Image tile / badge details
- Rounded image tiles with `border:3px solid #fff` read as polished "app icons."
- Discount/"new" badges: small accent pill, top-left, `font-weight:600`.

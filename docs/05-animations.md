# 05 · Animations — the recipe book

Every effect used across the five designs, as copy-paste recipes. They all build on **GSAP + ScrollTrigger + Lenis**. See [`snippets/setup.js`](../snippets/setup.js) and [`snippets/animations.js`](../snippets/animations.js) for ready-to-drop versions.

## 0 · The setup (always first)
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://unpkg.com/lenis@1.1.14/dist/lenis.min.js"></script>
```
```js
gsap.registerPlugin(ScrollTrigger);
const lenis = new Lenis({ duration: 1.2, smoothWheel: true, easing: t => Math.min(1, 1.001 - Math.pow(2, -10*t)) });
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add(t => lenis.raf(t * 1000));
gsap.ticker.lagSmoothing(0);
// smooth anchor links
document.querySelectorAll('a[href^="#"]').forEach(a => a.addEventListener('click', e => {
  const t = document.querySelector(a.getAttribute('href')); if (t){ e.preventDefault(); lenis.scrollTo(t, { offset:-40 }); }
}));
```

> ⚠️ **Load-timing gotcha (learned the hard way):** if a page occasionally renders with *no* animations, the inline script ran before the CDN libs were ready. Wrap your whole init in `window.addEventListener('load', () => { ... })`. It cost an hour once — just do it.

---

## 1 · Masked line reveal (hero headlines)
Each line rises out of a clipped mask.
```html
<h1><span class="line"><span>Crafted in</span></span><span class="line"><span><em>silence.</em></span></span></h1>
```
```css
.line{ overflow:hidden; display:block; } .line>span{ display:block; }
```
```js
gsap.set('.line>span', { yPercent: 110 });
gsap.to('.line>span', { yPercent: 0, duration: 1.4, ease: 'expo.out', stagger: 0.12 });
```

## 2 · Word-by-word statement reveal (scrubbed)
Words light up from dim → bright as you scroll through a quote.
```js
const el = document.getElementById('stmt');
el.innerHTML = el.textContent.split(' ').map(w => `<span class="w">${w}&nbsp;</span>`).join('');
gsap.to('#stmt .w', { opacity:1, ease:'none', stagger:0.3,
  scrollTrigger:{ trigger:'#stmt', start:'top 80%', end:'top 35%', scrub:true } });
/* .w { opacity:0.16; } */
```

## 3 · Scroll-progress bar
```css
.progress{ position:fixed; top:0; left:0; height:2px; width:100%; background:var(--accent); transform:scaleX(0); transform-origin:left; z-index:60; }
```
```js
gsap.to('#progress', { scaleX:1, ease:'none', scrollTrigger:{ start:0, end:'max', scrub:0.3 } });
```

## 4 · Count-up stats
```js
gsap.utils.toArray('[data-count]').forEach(el => {
  const end = +el.dataset.count, suf = el.dataset.suffix || '';
  ScrollTrigger.create({ trigger: el, start:'top 90%', once:true, onEnter: () =>
    gsap.to({v:0}, { v:end, duration:1.8, ease:'power2.out',
      onUpdate(){ el.textContent = Math.round(this.targets()[0].v) + suf; } }) });
});
```

## 5 · Marquee — two ways
**Continuous (CSS):** duplicate the content, translate −50%.
```css
.run{ display:inline-block; animation:slide 28s linear infinite; }
@keyframes slide{ to{ transform:translateX(-50%); } }
```
**Scroll-velocity (GSAP scrub):**
```js
gsap.to('#marquee', { xPercent:-50, ease:'none', scrollTrigger:{ trigger:'.marquee', start:'top bottom', end:'bottom top', scrub:1 } });
```
**Two-row opposing** (FabChain): one row `mqL`, one `mqR` reversed — see `animations.js`.

## 6 · Parallax (image drifts inside its frame)
Give the image extra height so there's slack; never reveals edges.
```css
.frame{ overflow:hidden; } .frame img{ height:120%; }
```
```js
gsap.fromTo('[data-par]', { yPercent:-8 }, { yPercent:8, ease:'none',
  scrollTrigger:{ trigger:'[data-par]', start:'top bottom', end:'bottom top', scrub:true } });
```

## 7 · Magnetic button
```js
const mag = document.getElementById('mag'), btn = mag.querySelector('.btn');
mag.addEventListener('mousemove', e => { const r = mag.getBoundingClientRect();
  gsap.to(btn, { x:(e.clientX-r.left-r.width/2)*0.4, y:(e.clientY-r.top-r.height/2)*0.4, duration:0.4 }); });
mag.addEventListener('mouseleave', () => gsap.to(btn, { x:0, y:0, duration:0.6, ease:'elastic.out(1,0.4)' }));
```

## 8 · Hover-reveal floating image (work lists)
Hovering a list row shows an image that trails the cursor.
```js
const preview = document.getElementById('preview'), img = preview.querySelector('img');
gsap.set(preview, { xPercent:-50, yPercent:-50, scale:0.85 });
const X = gsap.quickTo(preview,'x',{duration:0.5,ease:'power3.out'}), Y = gsap.quickTo(preview,'y',{duration:0.5,ease:'power3.out'});
addEventListener('mousemove', e => { X(e.clientX); Y(e.clientY); });
document.querySelectorAll('.item').forEach(it => {
  it.addEventListener('mouseenter', () => { img.src = it.dataset.img; gsap.to(preview,{opacity:1,scale:1,duration:0.4}); });
  it.addEventListener('mouseleave', () => gsap.to(preview,{opacity:0,scale:0.85,duration:0.3}));
});
```

## 9 · Image trail (Prisma hero)
Move the mouse → images spawn along the path and fade.
```js
const pool = ['a.jpg','b.jpg',/*…*/]; let lx=null, ly=null, i=0;
hero.addEventListener('mousemove', e => {
  if (lx===null){ lx=e.clientX; ly=e.clientY; return; }
  if (Math.hypot(e.clientX-lx, e.clientY-ly) < 120) return;
  lx=e.clientX; ly=e.clientY;
  const im = document.createElement('img'); im.className='trail-img'; im.src = pool[i++ % pool.length];
  im.style.left=e.clientX+'px'; im.style.top=e.clientY+'px'; trail.appendChild(im);
  gsap.fromTo(im, {scale:0.5,opacity:0,rotation:gsap.utils.random(-18,18)}, {scale:1,opacity:1,duration:0.4,ease:'power3.out'});
  gsap.to(im, {opacity:0,scale:0.85,duration:0.6,delay:0.5,onComplete:()=>im.remove()});
});
```

## 10 · Scatter-on-scroll (Amara) ⭐
Images stacked dead-centre that fly apart (and rotate) on scroll, revealing a caption behind. Sticky stage + scrubbed timeline.
```css
.scatter{ height:280vh; } /* scroll room */
.scatter-stage{ position:sticky; top:0; height:100vh; overflow:hidden; display:grid; place-items:center; }
.sc-img{ position:absolute; left:50%; top:50%; width:clamp(150px,17vw,248px); aspect-ratio:4/5; object-fit:cover; }
```
```js
const T = [[-0.30,-0.16,-13],[0.31,-0.12,11],[-0.26,0.21,9],[0.27,0.23,-8],[-0.44,0.04,-5],[0.44,0.07,7]];
const imgs = gsap.utils.toArray('.sc-img');
imgs.forEach((im,i)=> gsap.set(im,{ xPercent:-50, yPercent:-50, rotate:(i-2.5)*4, zIndex:10+i }));
const tl = gsap.timeline({ scrollTrigger:{ trigger:'.scatter', start:'top top', end:'bottom bottom', scrub:1 } });
imgs.forEach((im,i)=> tl.to(im,{ x:()=>innerWidth*T[i][0], y:()=>innerHeight*T[i][1], rotate:T[i][2], ease:'power1.inOut' }, 0));
```
> Use the CSS `position:sticky` stage **instead of** GSAP `pin` — combining both fights. Sticky + a `start:'top top' / end:'bottom bottom'` scrub is clean.

## 11 · Pinned horizontal scroll (Maison, Vessel) ⭐
Scroll down → a row of images glides sideways. Here GSAP `pin` IS used.
```js
const track = document.getElementById('track');
gsap.to(track, { x: () => -(track.scrollWidth - innerWidth), ease:'none',
  scrollTrigger:{ trigger:'.h-scroll', start:'top top',
    end: () => '+=' + (track.scrollWidth - innerWidth), scrub:1, pin:true, invalidateOnRefresh:true } });
```

## 12 · Sticky stack (Prisma "case studies")
Cards pile up; lower ones recede as the next covers them.
```css
.scard{ position:sticky; height:80vh; transform-origin:center top; } /* increasing top: 64,82,100,118px */
```
```js
const cards = gsap.utils.toArray('.scard');
cards.forEach((c,i)=>{ if(i===cards.length-1) return;
  gsap.to(c, { scale:0.9, filter:'brightness(0.7)', ease:'none',
    scrollTrigger:{ trigger: cards[i+1], start:'top bottom', end:'top top', scrub:true } }); });
```

## 13 · Curved-path draw + side reveals (Maison heritage) ⭐
A gold SVG line draws itself on scroll; images appear alternately left/right.
```html
<svg viewBox="0 0 1000 2000" preserveAspectRatio="none">
  <path id="curvePath" d="M500 20 C 880 280, 120 560, 500 840 C 880 1120, 120 1400, 500 1680 ..."/>
</svg>
<!-- path { stroke:var(--gold); vector-effect:non-scaling-stroke; fill:none; } -->
```
```js
const p = document.getElementById('curvePath'), len = p.getTotalLength();
p.style.strokeDasharray = len; p.style.strokeDashoffset = len;
gsap.to(p, { strokeDashoffset:0, ease:'none', scrollTrigger:{ trigger:'.path-sec', start:'top 72%', end:'bottom bottom', scrub:true } });
gsap.utils.toArray('.path-item').forEach(it =>
  gsap.from(it, { opacity:0, x: it.classList.contains('left')?-80:80, y:40, duration:1.1, ease:'power3.out',
    scrollTrigger:{ trigger:it, start:'top 84%' } }));
```
`vector-effect:non-scaling-stroke` keeps the line thin even when the SVG is stretched with `preserveAspectRatio="none"`. The single full-length dash makes the draw work regardless of scaling.

## 14 · 3D tilt cards (FabChain dApps)
Cards rotate toward the cursor in perspective.
```css
.dapp-grid{ perspective:1200px; } .dapp{ transform-style:preserve-3d; transition:transform .18s ease-out; }
.dapp .info{ transform:translateZ(45px); } /* depth pop */
```
```js
document.querySelectorAll('[data-tilt]').forEach(card => {
  card.addEventListener('mousemove', e => { const r = card.getBoundingClientRect();
    const px=(e.clientX-r.left)/r.width-0.5, py=(e.clientY-r.top)/r.height-0.5;
    card.style.transform = `rotateY(${px*12}deg) rotateX(${-py*12}deg) translateZ(12px)`; });
  card.addEventListener('mouseleave', () => card.style.transform = 'rotateY(0) rotateX(0)');
});
```

## 15 · Spotlight cards (glassmorphic)
A glow follows the cursor inside a card.
```css
.card::before{ content:''; position:absolute; inset:0; opacity:0; transition:opacity .4s;
  background:radial-gradient(340px circle at var(--mx) var(--my), rgba(255,255,255,0.14), transparent 45%); }
.card:hover::before{ opacity:1; }
```
```js
card.addEventListener('mousemove', e => { const r = card.getBoundingClientRect();
  card.style.setProperty('--mx', (e.clientX-r.left)+'px'); card.style.setProperty('--my', (e.clientY-r.top)+'px'); });
```

## 16 · WebGL shader background (Maison gold-silk, Aether plasma)
A full-screen `ShaderMaterial` plane with a domain-warped fbm-noise fragment shader, animated by `uTime`, nudged by `uMouse`. Tune the `mix()` color stops to your palette (gold-on-black, or neon-on-navy). Full shader in [`examples/luxury.html`](../examples/luxury.html). Keep it dark (`col * 0.5`) so text stays readable; confine it to the hero with `position:absolute; height:100vh` so it doesn't bleed down the page.

## 17 · Preloader counter
```js
const tl = gsap.timeline();
tl.to({v:0}, { v:100, duration:2.2, ease:'power2.inOut', onUpdate(){ count.textContent = Math.round(this.targets()[0].v); } })
  .to('#loader', { yPercent:-100, duration:1.1, ease:'expo.inOut' })
  .add(/* then run the hero reveal */);
```

---

### Pin vs sticky — the rule
- **Sticky stage + scrub** for in-place transforms (scatter, sticky-stack). Don't also `pin`.
- **GSAP `pin:true`** for horizontal-scroll galleries (you're translating a track wider than the viewport).
- Always `invalidateOnRefresh:true` on responsive pinned/scrubbed triggers.

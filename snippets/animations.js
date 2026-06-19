/* animations.js — reusable scroll/interaction recipes.
   Requires GSAP + ScrollTrigger (+ Lenis from setup.js). Call the inits you need
   inside the window-load handler in setup.js. See docs/05-animations.md for details. */

/* 1. Masked line reveal — <h1><span class="line"><span>...</span></span></h1> */
export function initLineReveal(sel = '.line>span') {
  gsap.set(sel, { yPercent: 110 });
  gsap.to(sel, { yPercent: 0, duration: 1.4, ease: 'expo.out', stagger: 0.12 });
}

/* 2. Word-by-word scrubbed reveal — element with id, .w { opacity:.16 } */
export function initWordReveal(id) {
  const el = document.getElementById(id);
  el.innerHTML = el.textContent.split(' ').map(w => `<span class="w">${w}&nbsp;</span>`).join('');
  gsap.to(`#${id} .w`, { opacity: 1, ease: 'none', stagger: 0.3,
    scrollTrigger: { trigger: `#${id}`, start: 'top 80%', end: 'top 35%', scrub: true } });
}

/* 3. Scroll-progress bar — <div class="progress"> with transform-origin:left */
export function initProgress(sel = '.progress') {
  gsap.to(sel, { scaleX: 1, ease: 'none', scrollTrigger: { start: 0, end: 'max', scrub: 0.3 } });
}

/* 4. Count-up — <span data-count="400" data-suffix="+"> */
export function initCountUp(sel = '[data-count]') {
  gsap.utils.toArray(sel).forEach(el => {
    const end = +el.dataset.count, suf = el.dataset.suffix || '';
    ScrollTrigger.create({ trigger: el, start: 'top 90%', once: true, onEnter: () =>
      gsap.to({ v: 0 }, { v: end, duration: 1.8, ease: 'power2.out',
        onUpdate() { el.textContent = Math.round(this.targets()[0].v) + suf; } }) });
  });
}

/* 5. Scrubbed marquee — duplicate content inside the track */
export function initMarquee(sel) {
  gsap.to(sel, { xPercent: -50, ease: 'none',
    scrollTrigger: { trigger: sel, start: 'top bottom', end: 'bottom top', scrub: 1 } });
}

/* 6. Parallax — <img data-par> inside an overflow-hidden frame, img height >100% */
export function initParallax(sel = '[data-par]') {
  gsap.utils.toArray(sel).forEach(img =>
    gsap.fromTo(img, { yPercent: -8 }, { yPercent: 8, ease: 'none',
      scrollTrigger: { trigger: img, start: 'top bottom', end: 'bottom top', scrub: true } }));
}

/* 7. Magnetic button — wrapper #mag containing .btn */
export function initMagnetic(wrapSel = '#mag') {
  const mag = document.querySelector(wrapSel); if (!mag) return;
  const btn = mag.querySelector('.btn');
  mag.addEventListener('mousemove', e => { const r = mag.getBoundingClientRect();
    gsap.to(btn, { x: (e.clientX - r.left - r.width / 2) * 0.4, y: (e.clientY - r.top - r.height / 2) * 0.4, duration: 0.4 }); });
  mag.addEventListener('mouseleave', () => gsap.to(btn, { x: 0, y: 0, duration: 0.6, ease: 'elastic.out(1,0.4)' }));
}

/* 8. Hover-reveal floating image — rows .item[data-img], a #preview>img */
export function initHoverPreview() {
  const preview = document.getElementById('preview'); if (!preview) return;
  const img = preview.querySelector('img');
  gsap.set(preview, { xPercent: -50, yPercent: -50, scale: 0.85 });
  const X = gsap.quickTo(preview, 'x', { duration: 0.5, ease: 'power3.out' });
  const Y = gsap.quickTo(preview, 'y', { duration: 0.5, ease: 'power3.out' });
  addEventListener('mousemove', e => { X(e.clientX); Y(e.clientY); });
  document.querySelectorAll('.item').forEach(it => {
    it.addEventListener('mouseenter', () => { img.src = it.dataset.img; gsap.to(preview, { opacity: 1, scale: 1, duration: 0.4 }); });
    it.addEventListener('mouseleave', () => gsap.to(preview, { opacity: 0, scale: 0.85, duration: 0.3 }));
  });
}

/* 9. Image trail — pass a hero element + array of image URLs */
export function initImageTrail(hero, pool) {
  const trail = document.getElementById('trail'); if (!hero || !trail) return;
  pool.forEach(s => { const i = new Image(); i.src = s; });
  let lx = null, ly = null, i = 0;
  hero.addEventListener('mousemove', e => {
    if (lx === null) { lx = e.clientX; ly = e.clientY; return; }
    if (Math.hypot(e.clientX - lx, e.clientY - ly) < 120) return;
    lx = e.clientX; ly = e.clientY;
    const im = document.createElement('img'); im.className = 'trail-img'; im.src = pool[i++ % pool.length];
    im.style.left = e.clientX + 'px'; im.style.top = e.clientY + 'px'; trail.appendChild(im);
    gsap.fromTo(im, { scale: 0.5, opacity: 0, rotation: gsap.utils.random(-18, 18) }, { scale: 1, opacity: 1, duration: 0.4, ease: 'power3.out' });
    gsap.to(im, { opacity: 0, scale: 0.85, duration: 0.6, delay: 0.5, onComplete: () => im.remove() });
  });
}

/* 10. Scatter on scroll — sticky stage .scatter-stage, items .sc-img, section .scatter */
export function initScatter() {
  const T = [[-.30, -.16, -13], [.31, -.12, 11], [-.26, .21, 9], [.27, .23, -8], [-.44, .04, -5], [.44, .07, 7]];
  const imgs = gsap.utils.toArray('.sc-img'); if (!imgs.length) return;
  imgs.forEach((im, i) => gsap.set(im, { xPercent: -50, yPercent: -50, rotate: (i - 2.5) * 4, zIndex: 10 + i }));
  const tl = gsap.timeline({ scrollTrigger: { trigger: '.scatter', start: 'top top', end: 'bottom bottom', scrub: 1, invalidateOnRefresh: true } });
  imgs.forEach((im, i) => tl.to(im, { x: () => innerWidth * T[i % T.length][0], y: () => innerHeight * T[i % T.length][1], rotate: T[i % T.length][2], ease: 'power1.inOut' }, 0));
}

/* 11. Pinned horizontal scroll — track #track inside section .h-scroll */
export function initHorizontalScroll() {
  const track = document.getElementById('track'); if (!track) return;
  gsap.to(track, { x: () => -(track.scrollWidth - innerWidth), ease: 'none',
    scrollTrigger: { trigger: '.h-scroll', start: 'top top', end: () => '+=' + (track.scrollWidth - innerWidth), scrub: 1, pin: true, invalidateOnRefresh: true } });
}

/* 12. Sticky stack — cards .scard with increasing CSS top */
export function initStickyStack() {
  const cards = gsap.utils.toArray('.scard');
  cards.forEach((c, i) => { if (i === cards.length - 1) return;
    gsap.to(c, { scale: 0.9, filter: 'brightness(0.7)', ease: 'none',
      scrollTrigger: { trigger: cards[i + 1], start: 'top bottom', end: 'top top', scrub: true } }); });
}

/* 13. Curved path draw + side reveals — #curvePath, items .path-item.left/.right, section .path-sec */
export function initCurvedPath() {
  const p = document.getElementById('curvePath'); if (!p) return;
  const len = p.getTotalLength();
  p.style.strokeDasharray = len; p.style.strokeDashoffset = len;
  gsap.to(p, { strokeDashoffset: 0, ease: 'none', scrollTrigger: { trigger: '.path-sec', start: 'top 72%', end: 'bottom bottom', scrub: true } });
  gsap.utils.toArray('.path-item').forEach(it =>
    gsap.from(it, { opacity: 0, x: it.classList.contains('left') ? -80 : 80, y: 40, duration: 1.1, ease: 'power3.out',
      scrollTrigger: { trigger: it, start: 'top 84%' } }));
}

/* 14. 3D tilt cards — elements [data-tilt], grid has perspective */
export function initTilt() {
  document.querySelectorAll('[data-tilt]').forEach(card => {
    card.addEventListener('mousemove', e => { const r = card.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
      card.style.transform = `rotateY(${px * 12}deg) rotateX(${-py * 12}deg) translateZ(12px)`; });
    card.addEventListener('mouseleave', () => card.style.transform = 'rotateY(0) rotateX(0)');
  });
}

/* 15. Spotlight cards — .card with ::before glow using --mx/--my */
export function initSpotlight(sel = '.card') {
  document.querySelectorAll(sel).forEach(card =>
    card.addEventListener('mousemove', e => { const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      card.style.setProperty('--my', (e.clientY - r.top) + 'px'); }));
}

/* Generic fade-up reveal for anything with .reveal { opacity:0; transform:translateY(30px) } */
export function initReveals(sel = '.reveal') {
  gsap.utils.toArray(sel).forEach(el => gsap.to(el, { opacity: 1, y: 0, duration: 1, ease: 'power3.out',
    scrollTrigger: { trigger: el, start: 'top 88%' } }));
}

/* setup.js — drop in after the GSAP/ScrollTrigger/Lenis CDN scripts.
   Wrap your whole init in window load to dodge library-timing races. */
window.addEventListener('load', () => {
  gsap.registerPlugin(ScrollTrigger);

  // Smooth scroll, synced to GSAP's ticker
  const lenis = new Lenis({
    duration: 1.2,
    smoothWheel: true,
    easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add(t => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);

  // Smooth in-page anchor links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const t = document.querySelector(a.getAttribute('href'));
      if (t) { e.preventDefault(); lenis.scrollTo(t, { offset: -40 }); }
    });
  });

  // expose for other modules
  window.__lenis = lenis;

  // call your animation initializers here, e.g. initReveals(), initScatter(), ...
});

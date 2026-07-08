// ============================
// Marquee Logos — 27zero
// WAAPI: clona logos hasta cubrir viewport + un período, luego anima
// translateX(0 → -período) en loop infinito. Período = ancho de un set
// + un gap, garantizando que el primer clon queda justo donde empezó
// el set original — loop sin saltos ni espacios en blanco.
// ============================

function initMarquee(marquee, pxPerSecond = 60) {
  const track = marquee.querySelector('.marquee-track');
  if (!track) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const origLogos = Array.from(track.querySelectorAll('.marquee-logo'));
  let anim = null;

  function setup() {
    if (anim) { anim.cancel(); anim = null; }
    track.querySelectorAll('[aria-hidden="true"]').forEach(el => el.remove());

    const gapPx = parseFloat(getComputedStyle(track).columnGap) || 0;
    const oneSetWidth = track.scrollWidth;
    const period = oneSetWidth + gapPx;

    if (period <= 0) return;

    const needed = marquee.offsetWidth + period;
    let added = 0;
    while (added < needed) {
      origLogos.forEach(logo => {
        const clone = logo.cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        clone.setAttribute('alt', '');
        track.appendChild(clone);
      });
      added += period;
    }

    anim = track.animate(
      [
        { transform: 'translateX(0)' },
        { transform: `translateX(-${period}px)` }
      ],
      {
        duration: (period / pxPerSecond) * 1000,
        iterations: Infinity,
        easing: 'linear'
      }
    );
  }

  marquee.addEventListener('mouseenter', () => { if (anim) anim.pause(); });
  marquee.addEventListener('mouseleave', () => { if (anim) anim.play(); });

  setup();
  window.addEventListener('resize', setup);
}

window.addEventListener('load', () => {
  document.querySelectorAll('.marquee').forEach((marquee) => initMarquee(marquee));
});

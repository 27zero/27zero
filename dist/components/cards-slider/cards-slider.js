// ============================
// Cards Slider — 27zero
// Extraído de /work (script.js): drag por pointer events + navegación con flechas.
// ============================

function enableSliderDrag(track) {
  let isDown  = false;
  let startX  = 0;
  let startSL = 0;

  track.addEventListener('pointerdown', (e) => {
    isDown = true;
    track.classList.add('dragging');
    startX  = e.pageX;
    startSL = track.scrollLeft;
    track.setPointerCapture(e.pointerId);
  });

  track.addEventListener('pointermove', (e) => {
    if (!isDown) return;
    track.scrollLeft = startSL - (e.pageX - startX);
  });

  const stopDrag = () => {
    isDown = false;
    track.classList.remove('dragging');
  };

  track.addEventListener('pointerup',     stopDrag);
  track.addEventListener('pointerleave',  stopDrag);
  track.addEventListener('pointercancel', stopDrag);
}

function enableSliderArrows(footer, track) {
  const prevBtn = footer.querySelector('[data-dir="prev"]');
  const nextBtn = footer.querySelector('[data-dir="next"]');

  function getScrollStep() {
    const card = track.querySelector('.card');
    if (!card) return 320;
    const gap = parseFloat(getComputedStyle(track).gap) || 0;
    return (card.getBoundingClientRect().width + gap) * 2;
  }

  function updateArrows() {
    const maxScroll = track.scrollWidth - track.clientWidth;
    prevBtn.disabled = track.scrollLeft <= 2;
    nextBtn.disabled = maxScroll <= 2 || track.scrollLeft >= maxScroll - 2;
  }

  prevBtn.addEventListener('click', () => {
    track.scrollBy({ left: -getScrollStep(), behavior: 'smooth' });
  });

  nextBtn.addEventListener('click', () => {
    track.scrollBy({ left: getScrollStep(), behavior: 'smooth' });
  });

  track.addEventListener('scroll', updateArrows);

  requestAnimationFrame(() => {
    requestAnimationFrame(updateArrows);
  });

  window.addEventListener('resize', updateArrows);
}

// ===== Init =====
// Soporta múltiples .slider-block en la misma página — cada uno con su propia instancia.
document.querySelectorAll('.slider-block').forEach((sliderBlock) => {
  const track  = sliderBlock.querySelector('.slider-track');
  const footer = sliderBlock.querySelector('.slider-footer');
  if (!track || !footer) return;
  enableSliderDrag(track);
  enableSliderArrows(footer, track);
});

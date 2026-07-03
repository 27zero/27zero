// ============================
// 27zero — Work page
// ============================

// ===== Drag (pointer events) =====

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

// ===== Arrow navigation =====

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
    // prev: disabled si estamos al inicio
    prevBtn.disabled = track.scrollLeft <= 2;
    // next: disabled solo si llegamos al final
    nextBtn.disabled = maxScroll <= 2 || track.scrollLeft >= maxScroll - 2;
  }

  prevBtn.addEventListener('click', () => {
    track.scrollBy({ left: -getScrollStep(), behavior: 'smooth' });
  });

  nextBtn.addEventListener('click', () => {
    track.scrollBy({ left: getScrollStep(), behavior: 'smooth' });
  });

  track.addEventListener('scroll', updateArrows);

  // Evaluar estado inicial tras render
  requestAnimationFrame(() => {
    requestAnimationFrame(updateArrows);
  });

  window.addEventListener('resize', updateArrows);
}

// ===== Wire interactions to Jinja-rendered DOM =====

const slidersContainer = document.getElementById('slidersContainer');

document.querySelectorAll('.slider-block').forEach(block => {
  const track  = block.querySelector('.slider-track');
  const footer = block.querySelector('.slider-footer');
  if (track)           enableSliderDrag(track);
  if (track && footer) enableSliderArrows(footer, track);
});

// ===== Pills filtering =====

const pillsWrap = document.getElementById('pillsWrap');
const pills     = pillsWrap.querySelectorAll('.pill');

pillsWrap.addEventListener('click', (e) => {
  const pill = e.target.closest('.pill');
  if (!pill) return;

  pills.forEach(p => p.classList.remove('pill--active'));
  pill.classList.add('pill--active');

  const filterId = pill.dataset.filter;
  const blocks   = slidersContainer.querySelectorAll('.slider-block');

  blocks.forEach(block => {
    block.style.display = (filterId === 'all' || block.dataset.category === filterId)
      ? ''
      : 'none';
  });
});

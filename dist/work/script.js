// ============================
// 27zero — Work page
// ============================

const CATEGORIES = [
  { id: 'los-mejores',               label: 'Los mejores',                cardType: 'featured'  },
  { id: 'ux-ui-web-design',          label: 'Ux/Ui & Web Design',         cardType: 'standard'  },
  { id: 'brand-messaging-strategy',  label: 'Brand & Messaging Strategy',  cardType: 'standard'  },
  { id: 'events',                    label: 'Events',                      cardType: 'standard'  },
  { id: 'content-marketing',         label: 'Content Marketing',           cardType: 'standard'  },
  { id: 'marketing-programs',        label: 'Marketing Programs',          cardType: 'standard'  },
  { id: 'thought-leadership-programs', label: 'Thought Leadership Programs', cardType: 'standard' },
  { id: 'strategic-services',        label: 'Strategic Services',          cardType: 'standard'  },
];

const CARDS_PER_CATEGORY = 6;

// ===== Card markup =====

function createCardElement(category) {
  const a = document.createElement('a');
  a.href = '#';
  a.className = `card card--work card--${category.cardType}`;

  a.innerHTML = `
    <div class="card-work-bg">
      <span>[PROJECT THUMBNAIL]</span>
    </div>
    <div class="card-work-body">
      <div class="card-work-content">
        <span class="card-work-eyebrow">[${category.label.toUpperCase()}]</span>
        <h3 class="card-work-title">[Project headline]</h3>
        <div class="card-work-client">
          <div class="card-work-client-logo"><span>CL</span></div>
          <span class="card-work-client-name">[CLIENT NAME]</span>
        </div>
      </div>
      <div class="card-work-footer">
        <div class="card-work-arrow">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="7" y1="17" x2="17" y2="7"></line>
            <polyline points="7 7 17 7 17 17"></polyline>
          </svg>
        </div>
      </div>
    </div>
  `;

  return a;
}

// ===== Slider block markup =====

function createSliderBlock(category) {
  const block = document.createElement('div');
  block.className = 'slider-block';
  block.dataset.category = category.id;

  // Header: solo título
  const header = document.createElement('div');
  header.className = 'slider-header';
  header.innerHTML = `<h2 class="slider-title">${category.label}</h2>`;

  // Track
  const trackWrap = document.createElement('div');
  trackWrap.className = 'slider-track-wrap';

  const track = document.createElement('div');
  track.className = 'slider-track';

  for (let i = 0; i < CARDS_PER_CATEGORY; i++) {
    track.appendChild(createCardElement(category));
  }

  trackWrap.appendChild(track);

  // Footer: flechas abajo a la derecha
  const footer = document.createElement('div');
  footer.className = 'slider-footer';
  footer.innerHTML = `
    <div class="slider-nav">
      <button class="slider-arrow" data-dir="prev" aria-label="Previous" disabled>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
      </button>
      <button class="slider-arrow" data-dir="next" aria-label="Next">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="5" y1="12" x2="19" y2="12"></line>
          <polyline points="12 5 19 12 12 19"></polyline>
        </svg>
      </button>
    </div>
  `;

  block.appendChild(header);
  block.appendChild(trackWrap);
  block.appendChild(footer);

  enableSliderDrag(track);
  enableSliderArrows(footer, track);

  return block;
}

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

// ===== Render sliders =====

const slidersContainer = document.getElementById('slidersContainer');

function renderAllSliders() {
  slidersContainer.innerHTML = '';
  CATEGORIES.forEach(cat => slidersContainer.appendChild(createSliderBlock(cat)));
}

renderAllSliders();

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

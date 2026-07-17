// ============================
// Shapes Slider — 27zero
// Desktop: bloque fijo de 3 shapes, nada se mueve — las flechas solo
// cambian el scale (activa = 1, inactivas = 0.9).
// Mobile (<=768px): sin flechas. La shape activa queda centrada con
// "peeks" de las de los lados (scroll-snap horizontal) — se navega
// con swipe o con tap en las zonas invisibles de los extremos.
// En ambos casos, el texto de .apart-home-scales cambia según la shape activa.
// ============================

const SHAPES = [
  {
    modifier: 'apart-shape--purple',
    src: '/assets/research-enhanced.png',
    alt: 'Research Enhanced',
    title: 'Research Enhanced Insights',
    text: 'Lorem ipsum is simply dummy text of the printing and typesetting industry standard, used here as placeholder copy.',
  },
  {
    modifier: 'apart-shape--indigo',
    src: '/assets/execution.png',
    alt: 'Execution',
    title: 'Execution that Scales',
    text: 'We deliver the complete capability of a full-service agency with the focus of a boutique partner — with regional expertise in North America and Europe, and agile production in Latin America.',
  },
  {
    modifier: 'apart-shape--black',
    src: '/assets/creativity.png',
    alt: 'Creativity',
    title: 'Creativity Without Limits',
    text: 'Lorem ipsum is simply dummy text of the printing and typesetting industry standard, used here as placeholder copy.',
  },
];

const MOBILE_QUERY = '(max-width: 768px)';
const isMobile = () => window.matchMedia(MOBILE_QUERY).matches;

function initApartShapes() {
  const shapesWrap = document.getElementById('apartShapes');
  const titleEl = document.getElementById('apartScalesTitle');
  const textEl = document.getElementById('apartScalesText');
  if (!shapesWrap) return;

  shapesWrap.innerHTML = `
    <div class="apart-shapes-spacer" aria-hidden="true"></div>
    ${SHAPES.map((s) => `
      <div class="apart-shape ${s.modifier}">
        <img src="${s.src}" alt="${s.alt}">
      </div>
    `).join('')}
    <div class="apart-shapes-spacer" aria-hidden="true"></div>
  `;

  const shapeEls = Array.from(shapesWrap.querySelectorAll('.apart-shape'));
  const prevBtn = document.querySelector('.apart-slider-arrow[data-dir="prev"]');
  const nextBtn = document.querySelector('.apart-slider-arrow[data-dir="next"]');
  const prevZone = document.querySelector('.apart-shapes-nav-zone--prev');
  const nextZone = document.querySelector('.apart-shapes-nav-zone--next');

  // Default: la del centro (index 1) activa, las otras dos en 0.9
  let activeIndex = 1;

  function render() {
    shapeEls.forEach((shape, i) => {
      shape.style.transform = `scale(${i === activeIndex ? 1 : 0.9})`;
    });

    if (titleEl) titleEl.textContent = SHAPES[activeIndex].title;
    if (textEl) textEl.textContent = SHAPES[activeIndex].text;
  }

  // ===== Desktop: flechas cambian el índice directo, sin scroll =====
  function goTo(index) {
    activeIndex = (index + shapeEls.length) % shapeEls.length;
    render();
    if (isMobile()) scrollToActive('smooth');
  }

  if (prevBtn) prevBtn.addEventListener('click', () => goTo(activeIndex - 1));
  if (nextBtn) nextBtn.addEventListener('click', () => goTo(activeIndex + 1));

  // ===== Mobile: swipe (scroll-snap) + tap en las zonas invisibles =====
  function scrollToActive(behavior = 'smooth') {
    const el = shapeEls[activeIndex];
    if (!el) return;
    el.scrollIntoView({ behavior, inline: 'center', block: 'nearest' });
  }

  function closestIndexToCenter() {
    const wrapRect = shapesWrap.getBoundingClientRect();
    const centerX = wrapRect.left + wrapRect.width / 2;
    let closest = 0;
    let minDist = Infinity;
    shapeEls.forEach((el, i) => {
      const r = el.getBoundingClientRect();
      const dist = Math.abs((r.left + r.width / 2) - centerX);
      if (dist < minDist) { minDist = dist; closest = i; }
    });
    return closest;
  }

  if (prevZone) prevZone.addEventListener('click', () => goTo(activeIndex - 1));
  if (nextZone) nextZone.addEventListener('click', () => goTo(activeIndex + 1));

  // Al terminar un swipe, detecta cuál shape quedó centrada y actualiza texto/scale
  let scrollTimeout;
  shapesWrap.addEventListener('scroll', () => {
    if (!isMobile()) return;
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      const idx = closestIndexToCenter();
      if (idx !== activeIndex) {
        activeIndex = idx;
        render();
      }
    }, 100);
  });

  render();

  // Centra la shape default (Execution) al cargar en mobile, sin animación
  if (isMobile()) {
    requestAnimationFrame(() => scrollToActive('auto'));
  }

  // Si cambia de mobile a desktop (o viceversa) por resize/rotación,
  // vuelve a centrar la shape activa en el nuevo layout
  let wasMobile = isMobile();
  window.addEventListener('resize', () => {
    const nowMobile = isMobile();
    if (nowMobile && !wasMobile) {
      requestAnimationFrame(() => scrollToActive('auto'));
    }
    wasMobile = nowMobile;
  });
}

initApartShapes();

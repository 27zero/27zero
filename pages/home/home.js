// ============================
// 27zero — Home page
// ============================

// La lógica de interacción de cada sección se agrega aquí paso a paso.

// ===== "What sets 27zero apart" — slider de shapes =====

function createApartSlide() {
  const slide = document.createElement('div');
  slide.className = 'apart-slide';
  slide.innerHTML = `
    <div class="apart-shape apart-shape--purple">
      <img src="/assets/research-enhanced.png" alt="Research Enhanced">
    </div>
    <div class="apart-shape apart-shape--indigo">
      <img src="/assets/execution.png" alt="Execution">
    </div>
    <div class="apart-shape apart-shape--black">
      <img src="/assets/creativity.png" alt="Creativity">
    </div>
  `;
  return slide;
}

function initApartSlider() {
  const track = document.getElementById('apartSliderTrack');
  if (!track) return;

  const SLIDE_COUNT = 2; // mismo slide duplicado para mostrar la funcionalidad
  for (let i = 0; i < SLIDE_COUNT; i++) {
    track.appendChild(createApartSlide());
  }

  const prevBtn = document.querySelector('.apart-slider-arrow[data-dir="prev"]');
  const nextBtn = document.querySelector('.apart-slider-arrow[data-dir="next"]');
  let index = 0;

  function update() {
    track.style.transform = `translateX(-${index * 100}%)`;
    prevBtn.disabled = index === 0;
    nextBtn.disabled = index === SLIDE_COUNT - 1;
  }

  prevBtn.addEventListener('click', () => {
    if (index > 0) { index--; update(); }
  });

  nextBtn.addEventListener('click', () => {
    if (index < SLIDE_COUNT - 1) { index++; update(); }
  });

  update();
}

initApartSlider();

// ===== Testimonials =====

const QUOTE_ICON_SVG = `
  <svg class="testimonial-quote-icon" viewBox="0 0 376 296" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M63.1627 124.2H0V0H170.91V29.0037C170.91 163.619 152.334 256.584 135.985 295.997H52.759C60.9337 243.937 63.9066 174.773 63.1627 124.2ZM268.253 124.2H205.09V0H376V29.0037C376 163.619 357.422 256.584 341.075 295.997H257.849C266.021 243.937 268.994 174.773 268.253 124.2Z" fill="#C286FF"/>
  </svg>
`;

const TESTIMONIALS = [
  { quote: `The quality of the design was impressive. We're looking forward to continue our collaboration with 27zero.`, name: 'Erin Grant', role: 'Vice President of Marketing', initials: 'EG' },
  { quote: `Lorem ipsum is simply dummy text of the printing and typesetting industry standard.`, name: 'Lorem Ipsum', role: 'Director of Growth', initials: 'LI' },
  { quote: `Lorem ipsum is simply dummy text of the printing and typesetting industry standard.`, name: 'Lorem Ipsum', role: 'Head of Admissions', initials: 'LI' },
  { quote: `Lorem ipsum is simply dummy text of the printing and typesetting industry standard.`, name: 'Lorem Ipsum', role: 'Chief Marketing Officer', initials: 'LI' },
];

function createTestimonialSlide(t) {
  const slide = document.createElement('div');
  slide.className = 'testimonial-slide';
  slide.innerHTML = `
    ${QUOTE_ICON_SVG}
    <div class="testimonial-content">
      <p class="testimonial-text">${t.quote}</p>
      <div class="testimonial-divider"></div>
      <div class="testimonial-author">
        <div class="testimonial-avatar"><span>${t.initials}</span></div>
        <div class="testimonial-author-info">
          <span class="testimonial-name">${t.name}</span>
          <span class="testimonial-role">${t.role}</span>
        </div>
      </div>
    </div>
  `;
  return slide;
}

function initTestimonialsSlider() {
  const track = document.getElementById('testimonialsTrack');
  const dotsWrap = document.getElementById('testimonialsDots');
  if (!track || !dotsWrap) return;

  TESTIMONIALS.forEach(t => track.appendChild(createTestimonialSlide(t)));

  dotsWrap.innerHTML = TESTIMONIALS
    .map((_, i) => `<button class="testimonial-dot${i === 0 ? ' testimonial-dot--active' : ''}" data-index="${i}" aria-label="Go to slide ${i + 1}"></button>`)
    .join('');

  const prevBtn = document.querySelector('.testimonials-arrow[data-dir="prev"]');
  const nextBtn = document.querySelector('.testimonials-arrow[data-dir="next"]');
  const dots = dotsWrap.querySelectorAll('.testimonial-dot');
  let index = 0;

  function update() {
    track.style.transform = `translateX(-${index * 100}%)`;
    prevBtn.disabled = index === 0;
    nextBtn.disabled = index === TESTIMONIALS.length - 1;
    dots.forEach((dot, i) => dot.classList.toggle('testimonial-dot--active', i === index));
  }

  prevBtn.addEventListener('click', () => {
    if (index > 0) { index--; update(); }
  });

  nextBtn.addEventListener('click', () => {
    if (index < TESTIMONIALS.length - 1) { index++; update(); }
  });

  dots.forEach(dot => {
    dot.addEventListener('click', () => {
      index = parseInt(dot.dataset.index, 10);
      update();
    });
  });

  update();
}

initTestimonialsSlider();

// ============================
// Navbar — 27zero
// Dos estados basados únicamente en scroll position:
//   Hero    : scrollY <= innerHeight * 0.30  → transparente, todo blanco
//   Scrolled: scrollY >  innerHeight * 0.30  → pill indigo
// No depende de la página actual ni de variantes Jinja.
// ============================

const nav = document.querySelector('.nav');

function updateNav() {
  const threshold = window.innerHeight * 0.30;
  if (window.scrollY > threshold) {
    nav.classList.add('nav--scrolled');
    nav.classList.remove('nav--hero');
    nav.style.top = '2.2em';
  } else {
    nav.classList.remove('nav--scrolled');
    nav.classList.add('nav--hero');
    nav.style.top = '0';
  }
}

window.addEventListener('scroll', updateNav, { passive: true });
window.addEventListener('resize', updateNav, { passive: true });
updateNav(); // run once on load

// ============================
// Mobile menu — modal fullscreen
// Click en el hamburger: abre el modal (ícono estático, sin animación).
// El cierre es explícito (botón × dentro del modal, o tocar el hamburger
// de nuevo) — al ser fullscreen ya no existe un "afuera" del menú.
// ============================

const hamburgerBtn = document.querySelector('.nav-hamburger');
const mobileMenu = document.querySelector('.nav-mobile-menu');
const mobileCloseBtn = document.querySelector('.nav-mobile-close');

if (hamburgerBtn && mobileMenu) {
  let isMenuOpen = false;

  function openMobileMenu() {
    isMenuOpen = true;
    mobileMenu.classList.add('is-open');
  }

  function closeMobileMenu() {
    isMenuOpen = false;
    mobileMenu.classList.remove('is-open');
  }

  hamburgerBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    isMenuOpen ? closeMobileMenu() : openMobileMenu();
  });

  if (mobileCloseBtn) {
    mobileCloseBtn.addEventListener('click', closeMobileMenu);
  }
}

// ===== "Work" como acordeón inline dentro del modal mobile =====
// Mismo approach que /components/dropdown: height 0 -> scrollHeight -> auto.
const mobileGroup = document.querySelector('.nav-mobile-group');

if (mobileGroup) {
  const mobileGroupToggle = mobileGroup.querySelector('.nav-mobile-group-toggle');
  const mobileGroupContent = mobileGroup.querySelector('.nav-mobile-group-content');

  mobileGroupToggle.addEventListener('click', () => {
    const isOpen = mobileGroup.classList.contains('is-open');

    if (!isOpen) {
      mobileGroup.classList.add('is-open');
      mobileGroupToggle.setAttribute('aria-expanded', 'true');
      mobileGroupContent.style.height = mobileGroupContent.scrollHeight + 'px';

      mobileGroupContent.addEventListener('transitionend', function onOpen(e) {
        if (e.propertyName !== 'height') return;
        if (mobileGroup.classList.contains('is-open')) {
          mobileGroupContent.style.height = 'auto';
        }
        mobileGroupContent.removeEventListener('transitionend', onOpen);
      });
    } else {
      mobileGroupContent.style.height = mobileGroupContent.scrollHeight + 'px';
      mobileGroupContent.offsetHeight; // fuerza reflow
      mobileGroup.classList.remove('is-open');
      mobileGroupToggle.setAttribute('aria-expanded', 'false');
      mobileGroupContent.style.height = '0px';
    }
  });
}

// ============================
// Dropdown "Work" (desktop) — click para abrir/cerrar, click afuera cierra.
// ============================

const navDropdown = document.querySelector('.nav-dropdown');

if (navDropdown) {
  const dropdownToggle = navDropdown.querySelector('.nav-dropdown-toggle');

  dropdownToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = navDropdown.classList.toggle('is-open');
    dropdownToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  document.addEventListener('click', (e) => {
    if (navDropdown.classList.contains('is-open') && !navDropdown.contains(e.target)) {
      navDropdown.classList.remove('is-open');
      dropdownToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

// ============================
// Language switcher — 27zero i18n
// Opens/closes #lang-dropdown on button click.
// Keyboard: ArrowDown/ArrowUp to navigate, Escape to close.
// ============================

(function () {
  var btn  = document.querySelector('.lang-switcher-btn');
  var menu = document.getElementById('lang-dropdown');
  if (!btn || !menu) return;

  function openLang() {
    menu.classList.add('is-open');
    btn.setAttribute('aria-expanded', 'true');
    var first = menu.querySelector('a');
    if (first) first.focus();
  }
  function closeLang() {
    menu.classList.remove('is-open');
    btn.setAttribute('aria-expanded', 'false');
    btn.focus();
  }
  function toggleLang() {
    menu.classList.contains('is-open') ? closeLang() : openLang();
  }

  btn.addEventListener('click', function (e) { e.stopPropagation(); toggleLang(); });

  document.addEventListener('click', function (e) {
    if (!btn.contains(e.target) && !menu.contains(e.target)) closeLang();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menu.classList.contains('is-open')) closeLang();
  });

  menu.addEventListener('keydown', function (e) {
    var items = Array.from(menu.querySelectorAll('a'));
    var idx   = items.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') { e.preventDefault(); items[(idx + 1) % items.length].focus(); }
    if (e.key === 'ArrowUp')   { e.preventDefault(); items[(idx - 1 + items.length) % items.length].focus(); }
  });
}());

// ============================
// Navbar — 27zero
// Cambia a nav--scrolled al pasar 50px de scroll.
// Guarda la variante inicial (nav--white o nav--black) para restaurarla al volver arriba.
// ============================

const nav = document.querySelector('.nav');
const initialVariant = nav.classList.contains('nav--black') ? 'nav--black' : 'nav--white';

window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    nav.classList.add('nav--scrolled');
    nav.classList.remove('nav--white', 'nav--black');
    nav.style.top = '2.2em';
  } else {
    nav.classList.remove('nav--scrolled');
    nav.classList.add(initialVariant);
    nav.style.top = '0';
  }
});

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

// ============================
// Navbar — 27zero scroll behavior
// ============================

const nav = document.querySelector('.nav');
if (!nav) throw new Error('Navbar element .nav not found');

const initialVariant = nav.classList.contains('nav--hero') ? 'nav--hero' : 'nav--white';

function updateNav() {
  const threshold = 80;
  if (window.scrollY > threshold) {
    nav.classList.remove('nav--hero', 'nav--white');
    nav.classList.add('nav--scrolled');
    nav.style.top = '2.2em';
  } else {
    nav.classList.remove('nav--scrolled');
    nav.classList.add(initialVariant);
    nav.style.top = '0';
  }
}

window.addEventListener('scroll', updateNav, { passive: true });
window.addEventListener('resize', updateNav, { passive: true });
// Run on load using rAF to ensure layout is ready
requestAnimationFrame(updateNav);

// ============================
// Mobile menu
// ============================

const hamburgerBtn = document.getElementById('nav-hamburger-btn');
const mobileMenu   = document.getElementById('navMobileMenu');
const mobileCloseBtn = document.getElementById('nav-mobile-close-btn');

if (hamburgerBtn && mobileMenu) {
  hamburgerBtn.addEventListener('click', () => {
    const isOpen = mobileMenu.classList.toggle('is-open');
    hamburgerBtn.setAttribute('aria-expanded', String(isOpen));
  });

  if (mobileCloseBtn) {
    mobileCloseBtn.addEventListener('click', () => {
      mobileMenu.classList.remove('is-open');
      hamburgerBtn.setAttribute('aria-expanded', 'false');
    });
  }
}

// ============================
// Work dropdown — desktop
// ============================

const navDropdown = document.querySelector('.nav-dropdown');
if (navDropdown) {
  const dropdownToggle = navDropdown.querySelector('.nav-dropdown-toggle');

  dropdownToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = navDropdown.classList.toggle('is-open');
    dropdownToggle.setAttribute('aria-expanded', String(isOpen));
  });

  document.addEventListener('click', (e) => {
    if (navDropdown.classList.contains('is-open') && !navDropdown.contains(e.target)) {
      navDropdown.classList.remove('is-open');
      dropdownToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

// ============================
// Work accordion — mobile
// ============================

const mobileGroup = document.querySelector('.nav-mobile-group');
if (mobileGroup) {
  const toggle  = mobileGroup.querySelector('.nav-mobile-group-toggle');
  const content = mobileGroup.querySelector('.nav-mobile-group-content');

  toggle.addEventListener('click', () => {
    const isOpen = mobileGroup.classList.contains('is-open');
    if (!isOpen) {
      mobileGroup.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
      content.style.height = content.scrollHeight + 'px';
      content.addEventListener('transitionend', function onEnd(e) {
        if (e.propertyName !== 'height') return;
        if (mobileGroup.classList.contains('is-open')) content.style.height = 'auto';
        content.removeEventListener('transitionend', onEnd);
      });
    } else {
      content.style.height = content.scrollHeight + 'px';
      content.offsetHeight;
      mobileGroup.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      content.style.height = '0px';
    }
  });
}

// ============================
// Language switcher
// ============================
(function () {
  const btn  = document.querySelector('.lang-switcher-btn');
  const menu = document.getElementById('lang-dropdown');
  if (!btn || !menu) return;

  const open  = () => { menu.classList.add('is-open');    btn.setAttribute('aria-expanded', 'true');  const f = menu.querySelector('a'); if (f) f.focus(); };
  const close = () => { menu.classList.remove('is-open'); btn.setAttribute('aria-expanded', 'false'); btn.focus(); };

  btn.addEventListener('click', (e) => { e.stopPropagation(); menu.classList.contains('is-open') ? close() : open(); });
  document.addEventListener('click', (e) => { if (!btn.contains(e.target) && !menu.contains(e.target)) close(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && menu.classList.contains('is-open')) close(); });
  menu.addEventListener('keydown', (e) => {
    const items = [...menu.querySelectorAll('a')];
    const idx = items.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') { e.preventDefault(); items[(idx + 1) % items.length].focus(); }
    if (e.key === 'ArrowUp')   { e.preventDefault(); items[(idx - 1 + items.length) % items.length].focus(); }
  });
}());

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
// Mobile menu — hamburger animado (Lottie) + dropdown
// Requiere lottie-web cargado antes de este script.
// Click en el hamburger: toggle del menú y de la animación (0% -> 100% / 100% -> 0%).
// Click afuera del menú: lo cierra.
// ============================

const hamburgerBtn = document.querySelector('.nav-hamburger');
const hamburgerIcon = document.querySelector('.nav-hamburger-icon');
const mobileMenu = document.querySelector('.nav-mobile-menu');

if (hamburgerBtn && hamburgerIcon && mobileMenu && window.lottie) {
  const hamburgerAnim = lottie.loadAnimation({
    container: hamburgerIcon,
    renderer: 'svg',
    loop: false,
    autoplay: false,
    path: '/components/navbar/hamburger-menu-animation.json'
  });

  let isMenuOpen = false;

  function openMobileMenu() {
    isMenuOpen = true;
    mobileMenu.classList.add('is-open');
    hamburgerAnim.setDirection(1);
    hamburgerAnim.play();
  }

  function closeMobileMenu() {
    isMenuOpen = false;
    mobileMenu.classList.remove('is-open');
    hamburgerAnim.setDirection(-1);
    hamburgerAnim.play();
  }

  hamburgerBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    isMenuOpen ? closeMobileMenu() : openMobileMenu();
  });

  document.addEventListener('click', (e) => {
    if (isMenuOpen && !mobileMenu.contains(e.target) && !hamburgerBtn.contains(e.target)) {
      closeMobileMenu();
    }
  });
}

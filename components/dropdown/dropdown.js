// ============================
// Dropdown (FAQ) — 27zero
// Múltiples dropdowns por página, cada uno independiente — abrir uno
// NO cierra los demás.
//
// Animación de altura: height 0 -> Xpx (medido con scrollHeight) -> auto.
// Al terminar de abrir, pasa a height:auto para adaptarse solo si el
// contenido cambia después (ej. contenido dinámico). Al cerrar, primero
// fija la altura actual en px (no se puede transicionar desde 'auto'),
// fuerza reflow, y recién ahí anima a 0.
// ============================

document.querySelectorAll('.dropdown').forEach((dropdown) => {
  const toggle = dropdown.querySelector('.dropdown-toggle');
  const content = dropdown.querySelector('.dropdown-content');
  if (!toggle || !content) return;

  toggle.addEventListener('click', () => {
    const isOpen = dropdown.classList.contains('is-open');

    if (!isOpen) {
      // Abrir: 0 -> altura real medida
      dropdown.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
      content.style.height = content.scrollHeight + 'px';

      content.addEventListener('transitionend', function onOpen(e) {
        if (e.propertyName !== 'height') return;
        if (dropdown.classList.contains('is-open')) {
          content.style.height = 'auto';
        }
        content.removeEventListener('transitionend', onOpen);
      });
    } else {
      // Cerrar: altura actual (fijada en px) -> 0
      content.style.height = content.scrollHeight + 'px';
      content.offsetHeight; // fuerza reflow, necesario para animar desde este valor
      dropdown.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      content.style.height = '0px';
    }
  });
});

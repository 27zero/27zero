// ============================
// 27zero — Let's Talk (Contact) page
// El navbar (scroll/hamburger) se maneja en /components/navbar/navbar.js
// ============================

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('contactForm');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    // TODO: conectar con el endpoint/servicio de envío real.
    console.log('Contact form submitted (placeholder — sin backend conectado aún).');
  });
});

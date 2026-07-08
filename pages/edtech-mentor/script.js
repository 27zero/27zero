// ============================
// 27zero — The EdTech Mentor page
// ============================

// ===== Pills — anchor scroll =====
// "Subscribe on LinkedIn" es un link externo real (sin data-filter), no participa del filtro.

const pillsWrap = document.getElementById('pillsWrap');
const pills     = pillsWrap.querySelectorAll('.pill[data-filter]');

pillsWrap.addEventListener('click', (e) => {
  const pill = e.target.closest('.pill[data-filter]');
  if (!pill) return;

  pills.forEach(p => p.classList.remove('pill--active'));
  pill.classList.add('pill--active');

  const targetId = pill.dataset.filter;
  const target = document.getElementById(targetId);
  if (!target) return;

  target.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

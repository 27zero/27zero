// ============================
// 27zero — Work page
// ============================

// ===== Pills — anchor scroll =====

const pillsWrap = document.getElementById('pillsWrap');
const pills     = pillsWrap.querySelectorAll('.pill');

pillsWrap.addEventListener('click', (e) => {
  const pill = e.target.closest('.pill');
  if (!pill) return;

  pills.forEach(p => p.classList.remove('pill--active'));
  pill.classList.add('pill--active');

  const filterId = pill.dataset.filter;
  if (filterId === 'all') return;

  const target = document.getElementById(filterId);
  if (!target) return;

  target.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// ============================
// 27zero — Resources CMS page
// El comportamiento del navbar (scroll + hamburger) vive en
// /components/navbar/navbar.js, importado aparte en index.html.
// ============================

// TOC — el link clickeado pasa a ser el activo
document.addEventListener('DOMContentLoaded', function () {
  var tocLinks = document.querySelectorAll('.toc-link');

  tocLinks.forEach(function (link) {
    link.addEventListener('click', function () {
      tocLinks.forEach(function (l) { l.classList.remove('toc-link--active'); });
      link.classList.add('toc-link--active');
    });
  });
});

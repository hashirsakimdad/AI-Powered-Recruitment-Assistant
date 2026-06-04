/** Smooth in-page navigation for sidebar hash links. */
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      const id = this.getAttribute('href').slice(1);
      if (!id) return;
      const target = document.getElementById(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      if (window.history && window.history.replaceState) {
        window.history.replaceState(null, '', '#' + id);
      }
    });
  });

  if (window.location.hash) {
    const el = document.getElementById(window.location.hash.slice(1));
    if (el) {
      setTimeout(function () {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
  }
});

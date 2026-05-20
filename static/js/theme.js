(function () {
  const saved = localStorage.getItem('theme');
  if (saved === 'light') document.documentElement.setAttribute('data-theme', 'light');
})();

function toggleTheme() {
  const root = document.documentElement;
  const isLight = root.getAttribute('data-theme') === 'light';
  const btn = document.querySelector('.theme-toggle');
  if (isLight) {
    root.removeAttribute('data-theme');
    localStorage.setItem('theme', 'dark');
    if (btn) btn.textContent = '🌙 Dark';
  } else {
    root.setAttribute('data-theme', 'light');
    localStorage.setItem('theme', 'light');
    if (btn) btn.textContent = '☀️ Light';
  }
}

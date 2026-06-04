(function () {
  const STORAGE_KEY = 'theme';

  function applyTheme(theme) {
    const root = document.documentElement;
    const isLight = theme === 'light';
    if (isLight) {
      root.setAttribute('data-theme', 'light');
    } else {
      root.removeAttribute('data-theme');
    }
    document.querySelectorAll('.theme-toggle').forEach(function (btn) {
      btn.textContent = isLight ? '☀️ Light' : '🌙 Dark';
    });
  }

  const saved = localStorage.getItem(STORAGE_KEY);
  applyTheme(saved === 'light' ? 'light' : 'dark');

  window.toggleTheme = function toggleTheme() {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const next = isLight ? 'dark' : 'light';
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  };

  window.applyTheme = applyTheme;
})();

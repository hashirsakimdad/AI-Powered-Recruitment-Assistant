// Toast notification system
// Usage: showToast('message', 'success' | 'danger' | 'info' | 'warning')

function showToast(message, type = 'info', duration = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = { success: '✓', danger: '✕', info: 'ℹ', warning: '⚠' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span style="font-size:1.1rem;">${icons[type] || 'ℹ'}</span>
    <span style="flex:1;">${message}</span>
    <button type="button" onclick="this.parentElement.remove()"
      style="background:none;border:none;color:#94A3B8;cursor:pointer;font-size:1.2rem;line-height:1;padding:0;">×</button>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'toastOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-flash-message]').forEach((el) => {
    showToast(el.dataset.flashMessage, el.dataset.flashCategory || 'info');
    el.remove();
  });
});

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toggle-actions').forEach(btn => {
      btn.addEventListener('click', e => {
          e.stopPropagation();
          document.querySelectorAll('.action-dropdown').forEach(d => d.style.display = 'none');
          btn.nextElementSibling.style.display = 'block';
      });
  });

  document.addEventListener('click', () => {
      document.querySelectorAll('.action-dropdown').forEach(d => d.style.display = 'none');
  });
});
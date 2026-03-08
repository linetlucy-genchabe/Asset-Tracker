/* ============================================================
   CHIS Device Manager – Main JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Auto-dismiss alerts after 4 seconds ──────────────────
  document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 4000);
  });

  // ── Confirm on destructive status changes ────────────────
  const statusForm = document.querySelector('form[data-confirm-status]');
  if (statusForm) {
    statusForm.addEventListener('submit', function (e) {
      const select = statusForm.querySelector('select[name="status"]');
      const dangerous = ['lost', 'damaged'];
      if (select && dangerous.includes(select.value)) {
        const label = select.options[select.selectedIndex].text;
        if (!confirm(`Are you sure you want to mark this device as "${label}"?`)) {
          e.preventDefault();
        }
      }
    });
  }

  // ── Device list: highlight row on click ──────────────────
  document.querySelectorAll('table tbody tr[data-href]').forEach(function (row) {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function () {
      window.location.href = row.dataset.href;
    });
  });

  // ── Filter form: submit on select change ─────────────────
  document.querySelectorAll('.auto-submit-select').forEach(function (select) {
    select.addEventListener('change', function () {
      select.closest('form').submit();
    });
  });

  // ── Search: clear button ─────────────────────────────────
  const searchInput = document.querySelector('input[name="q"]');
  const clearBtn    = document.querySelector('.clear-search');
  if (searchInput && clearBtn) {
    clearBtn.style.display = searchInput.value ? 'inline-block' : 'none';
    searchInput.addEventListener('input', function () {
      clearBtn.style.display = searchInput.value ? 'inline-block' : 'none';
    });
  }

  // ── Stat card counter animation ───────────────────────────
  document.querySelectorAll('.stat-value[data-target]').forEach(function (el) {
    const target = parseInt(el.dataset.target, 10);
    if (isNaN(target) || target === 0) { el.textContent = '0'; return; }
    let current = 0;
    const step     = Math.ceil(target / 30);
    const interval = setInterval(function () {
      current = Math.min(current + step, target);
      el.textContent = current;
      if (current >= target) clearInterval(interval);
    }, 20);
  });

  // ── Tooltips ─────────────────────────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    bootstrap.Tooltip.getOrCreateInstance(el);
  });

});
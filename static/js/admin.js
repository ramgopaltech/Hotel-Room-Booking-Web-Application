/**
 * GRAND ROYALE LUXURY HOTEL - ADMIN PANEL JAVASCRIPT
 */

document.addEventListener('DOMContentLoaded', () => {
  initAdminTabs();
  initModals();
  initTableSearch();
});

// Sidebar Tab Switcher
function initAdminTabs() {
  const tabs = document.querySelectorAll('.sidebar-link[data-tab]');
  const tabContents = document.querySelectorAll('.tab-content');

  if (tabs.length === 0) return;

  tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      const targetTabId = tab.getAttribute('data-tab');

      tabs.forEach(t => t.classList.remove('active'));
      tabContents.forEach(c => c.style.display = 'none');

      tab.classList.add('active');
      const activeContent = document.getElementById(targetTabId);
      if (activeContent) {
        activeContent.style.display = 'block';
      }
    });
  });
}

// Modals Trigger (Add Room, Edit Room)
function initModals() {
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  const modalCloses = document.querySelectorAll('.modal-close');

  modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const targetModalId = trigger.getAttribute('data-modal-target');
      const modal = document.getElementById(targetModalId);
      if (modal) {
        modal.classList.add('active');
      }
    });
  });

  modalCloses.forEach(closeBtn => {
    closeBtn.addEventListener('click', () => {
      const modal = closeBtn.closest('.modal');
      if (modal) modal.classList.remove('active');
    });
  });

  // Close modal when clicking outside modal-content
  window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
      e.target.classList.remove('active');
    }
  });
}

// Client-side search for admin tables
function initTableSearch() {
  const searchInputs = document.querySelectorAll('.admin-search-input');
  searchInputs.forEach(input => {
    const targetTableId = input.getAttribute('data-table-target');
    const table = document.getElementById(targetTableId);
    if (!table) return;

    input.addEventListener('keyup', () => {
      const filter = input.value.toLowerCase();
      const rows = table.querySelectorAll('tbody tr');

      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
      });
    });
  });
}

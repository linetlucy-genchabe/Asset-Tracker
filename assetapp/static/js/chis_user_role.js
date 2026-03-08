/**
 * CHIS User Admin — show/hide location fields based on selected role.
 * Runs on both the Add User and Change User admin pages.
 */
(function () {
  'use strict';

  // Row finders — works for both Jazzmin and plain Django admin
  function getRow(fieldName) {
    // Try .form-row (plain admin) then .field- prefix (jazzmin)
    return (
      document.querySelector('.field-' + fieldName) ||
      document.querySelector('div[class*="field-' + fieldName + '"]')
    );
  }

  function setVisible(fieldName, visible) {
    var row = getRow(fieldName);
    if (row) {
      row.style.display = visible ? '' : 'none';
    }
  }

  function applyRoleVisibility(role) {
    // county — only for County Focal
    setVisible('county',    role === 'county_focal');

    // subcounty — only for Sub-County Focal
    setVisible('subcounty', role === 'subcounty_focal');

    // chus — only for CHA
    setVisible('chus',      role === 'cha');
  }

  function init() {
    var roleSelect = document.getElementById('id_role');
    if (!roleSelect) return;

    // Set initial state
    applyRoleVisibility(roleSelect.value);

    // Update on change
    roleSelect.addEventListener('change', function () {
      applyRoleVisibility(this.value);
    });
  }

  // Wait for DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
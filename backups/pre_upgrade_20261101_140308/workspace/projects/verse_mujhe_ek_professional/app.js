function triggerAction(feature) {
  const statusEl = document.getElementById('status-banner');
  if (statusEl) {
    statusEl.textContent = 'Active Feature Selected: ' + feature;
  }
}

// Runtime-injected config (overwritten in container at startup).
// Local dev: safe defaults.
window.__ENV__ = window.__ENV__ || {};
window.__ENV__.API_BASE_URL = window.__ENV__.API_BASE_URL || '';

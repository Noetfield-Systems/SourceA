/**
 * Hero live console — founder-home entry (WS-03).
 * Loads after sourcea-live-console.js; polls boot/AEG; wires tracking + mobile class.
 */
(function () {
  "use strict";

  if (!document.body.classList.contains("sa-root-home")) return;

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function boot() {
    const panel = document.getElementById("sa-biz-command");
    if (panel) panel.classList.add("sa-hero-console-v1");
    if (window.SourceALiveConsole && typeof window.SourceALiveConsole.init === "function") {
      return window.SourceALiveConsole.init();
    }
    return Promise.resolve();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  window.SourceAHeroConsole = { boot, reduced };
})();

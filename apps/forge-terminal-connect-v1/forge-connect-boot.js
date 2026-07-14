(function () {
  "use strict";
  /** Forge Terminal Connect — default Forge IDE tab + outer window scroll + iframe auto-height */
  function resizeForgeIdeFrame(height) {
    var frame = document.getElementById("forge-ide-frame");
    if (!frame || !height) return;
    var h = Math.max(height, window.innerHeight);
    frame.style.height = h + "px";
    frame.style.minHeight = window.innerHeight + "px";
  }

  window.addEventListener("message", function (ev) {
    if (!ev.data || ev.data.type !== "forge-ide-height") return;
    resizeForgeIdeFrame(ev.data.height);
  });

  document.addEventListener("DOMContentLoaded", function () {
    var defaultTab = "forge-ide";
    document.querySelectorAll(".cu-tab").forEach(function (tab) {
      var isForge = tab.getAttribute("data-tab") === defaultTab;
      tab.classList.toggle("cu-tab-active", isForge);
      tab.setAttribute("aria-selected", isForge ? "true" : "false");
    });
    document.querySelectorAll(".cu-tab-panel").forEach(function (panel) {
      var active = panel.id === "panel-forge-ide";
      panel.classList.toggle("cu-tab-panel-active", active);
      panel.hidden = !active;
    });
    document.body.classList.add("cu-forge-ide-focus");
    document.documentElement.classList.add("cu-forge-ide-focus");
    try {
      localStorage.setItem("chat-unify-active-tab-v1", "forge-ide");
    } catch (e) { /* ignore */ }
    document.querySelectorAll(".cu-forge-machines-scroll [data-goto-tab]").forEach(function (btn) {
      btn.classList.toggle("is-active", btn.getAttribute("data-goto-tab") === defaultTab);
    });
    var frame = document.getElementById("forge-ide-frame");
    if (frame) {
      frame.addEventListener("load", function () {
        try {
          frame.contentWindow.postMessage({ type: "forge-parent-ready" }, window.location.origin);
        } catch (e) { /* ignore */ }
      });
    }
  });
})();

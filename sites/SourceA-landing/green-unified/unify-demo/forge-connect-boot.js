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

  window.addEventListener("message", function (ev) {
    if (!ev.data || ev.data.type !== "cu-goto-tab") return;
    var tab = ev.data.tab || "";
    if (tab === "cu-ide") tab = "forge-ide";
    if (tab && window.switchTab) window.switchTab(tab);
  });

  document.addEventListener("DOMContentLoaded", function () {
    var path = window.location.pathname || "";
    var isDemo = /\/unify-demo(\/|$)/.test(path);
    var isFullWeb = /\/unify(\/|$)/.test(path) && !isDemo;
    var isWeb = isDemo || isFullWeb;
    var defaultTab = isWeb ? "home" : "forge-ide";
    document.querySelectorAll(".cu-tab").forEach(function (tab) {
      var isForge = tab.getAttribute("data-tab") === defaultTab;
      tab.classList.toggle("cu-tab-active", isForge);
      tab.setAttribute("aria-selected", isForge ? "true" : "false");
    });
    document.querySelectorAll(".cu-tab-panel").forEach(function (panel) {
      var panelId = defaultTab === "forge-ide" ? "panel-forge-ide" : "panel-" + defaultTab;
      var active = panel.id === panelId;
      panel.classList.toggle("cu-tab-panel-active", active);
      panel.hidden = !active;
    });
    if (defaultTab === "forge-ide") {
      document.body.classList.add("cu-forge-ide-focus");
      document.documentElement.classList.add("cu-forge-ide-focus");
    }
    try {
      localStorage.setItem("chat-unify-active-tab-v1", defaultTab);
    } catch (e) { /* ignore */ }
    document.querySelectorAll(".cu-forge-machines-scroll [data-goto-tab]").forEach(function (btn) {
      btn.classList.toggle("is-active", btn.getAttribute("data-goto-tab") === defaultTab);
    });
    var frame = document.getElementById("forge-ide-frame");
    if (frame) {
      frame.addEventListener("load", function () {
        try {
          frame.contentWindow.postMessage({ type: "forge-parent-ready" }, "*");
        } catch (e) { /* ignore */ }
      });
    }
  });
})();

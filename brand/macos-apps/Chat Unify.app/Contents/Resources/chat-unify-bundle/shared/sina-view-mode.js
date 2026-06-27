(function (global) {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function appRoot() {
    return (
      document.querySelector("[data-sina-app-root]") ||
      document.querySelector("main") ||
      document.querySelector(".wrap") ||
      document.body
    );
  }

  function mountModeBar() {
    if ($("sina-mode-bar")) return;
    var bar = document.createElement("nav");
    bar.id = "sina-mode-bar";
    bar.className = "sina-mode-bar";
    bar.setAttribute("aria-label", "View mode");
    bar.innerHTML =
      '<span class="mode-label">View</span>' +
      '<button type="button" class="sina-mode-tab active" data-mode="app">App</button>' +
      '<button type="button" class="sina-mode-tab station" data-mode="station">API Station</button>' +
      '<button type="button" class="sina-mode-tab hubpro" data-mode="hubpro">Hub Pro</button>';
    var links = document.querySelector(".official-links-bar");
    if (links && links.parentNode) {
      links.parentNode.insertBefore(bar, links.nextSibling);
    } else {
      document.body.insertBefore(bar, document.body.firstChild);
    }
    bar.querySelectorAll(".sina-mode-tab").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setMode(btn.getAttribute("data-mode") || "app");
      });
    });
  }

  function setMode(mode) {
    mode = mode || "app";
    var isApp = mode === "app";
    var isStation = mode === "station";
    var isHubPro = mode === "hubpro";

    document.querySelectorAll(".sina-mode-tab").forEach(function (b) {
      var m = b.getAttribute("data-mode");
      b.classList.toggle("active", m === mode);
      if (m === "station") b.classList.toggle("station", isStation);
      if (m === "hubpro") b.classList.toggle("hubpro", isHubPro);
    });

    var root = appRoot();
    if (root && root.id !== "api-station-panel" && root.id !== "hub-pro-panel") {
      root.classList.toggle("sina-view-hidden", !isApp);
    }

    document.querySelectorAll(".submit-bar").forEach(function (el) {
      el.classList.toggle("sina-view-hidden", !isApp);
    });

    var station = $("api-station-panel");
    if (station) station.classList.toggle("hidden", !isStation);
    var hubpro = $("hub-pro-panel");
    if (hubpro) hubpro.classList.toggle("hidden", !isHubPro);

    if (isStation) {
      if (global.sinaLoadApiStation) global.sinaLoadApiStation();
      else if (global.SinaApiStation && global.SinaApiStation.loadStation) global.SinaApiStation.loadStation();
    }
    if (isHubPro) {
      if (global.sinaLoadHubPro) global.sinaLoadHubPro();
    }

    try {
      sessionStorage.setItem("sina-view-mode", mode);
    } catch (e) {}
  }

  global.sinaSetViewMode = setMode;
  global.sinaMountViewModeBar = mountModeBar;

  function boot() {
    mountModeBar();
    var saved = "app";
    try {
      saved = sessionStorage.getItem("sina-view-mode") || "app";
    } catch (e) {}
    if (location.search.indexOf("station=1") >= 0) saved = "station";
    if (location.search.indexOf("hubpro=1") >= 0) saved = "hubpro";
    if (saved !== "app") setMode(saved);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})(window);

(function () {
  "use strict";
  var STORAGE_PREFIX = "wbc-sandbox-v1:";
  var templates = [];
  var select = null;
  var area = null;
  var status = null;

  function loadTemplates(cb) {
    fetch("/data/toolkits-v1.json", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        templates = (d && d.free_pages) || [];
        if (typeof cb === "function") cb();
      })
      .catch(function () { if (typeof cb === "function") cb(); });
  }

  function slug() {
    return select ? select.value : "";
  }

  function tpl() {
    var s = slug();
    for (var i = 0; i < templates.length; i++) {
      if (templates[i].slug === s) return templates[i];
    }
    return templates[0] || null;
  }

  function persist() {
    if (!area) return;
    try { localStorage.setItem(STORAGE_PREFIX + slug(), area.value); } catch (_e) {}
  }

  function restore() {
    if (!area) return;
    var row = tpl();
    var saved = "";
    try { saved = localStorage.getItem(STORAGE_PREFIX + slug()) || ""; } catch (_e) {}
    area.value = saved || (row && row.template_text) || "";
    if (status) {
      status.textContent = "Sandbox · browser-local · " + (row ? row.title : "—");
    }
  }

  function wire() {
    select = document.getElementById("sandbox-select");
    area = document.getElementById("sandbox-editor");
    status = document.getElementById("sandbox-status");
    if (!select || !area) return;
    select.addEventListener("change", function () { restore(); });
    area.addEventListener("input", persist);
    var copyBtn = document.getElementById("sandbox-copy");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        area.select();
        if (navigator.clipboard) navigator.clipboard.writeText(area.value).catch(function () {});
      });
    }
    var resetBtn = document.getElementById("sandbox-reset");
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        try { localStorage.removeItem(STORAGE_PREFIX + slug()); } catch (_e) {}
        restore();
      });
    }
    restore();
  }

  function init() {
    loadTemplates(wire);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

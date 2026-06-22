(function () {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function appId() {
    var qs = new URLSearchParams(window.location.search || "");
    var forced = qs.get("app");
    if (forced) return forced;
    var meta = document.querySelector('meta[name="sina-app-id"]');
    if (meta && meta.content) return meta.content;
    var port = String(window.location.port || "");
    var path = window.location.pathname || "";
    if (port === "13023") return "chat-unify";
    if (port === "13026") return "n8n-integration";
    if (port === "13027") return "cloud-workers";
    if (path.indexOf("/machines") !== -1) return "machine-hub";
    if (path.indexOf("/form") !== -1) return "hub-form";
    if (path.indexOf("/mail-hub") !== -1) return "portfolio-mail";
    if (path.indexOf("/cloud-workers") !== -1) return "cloud-workers";
    if (port === "13020") return "worker-hub";
    return "worker-hub";
  }

  function apiBase() {
    var id = appId();
    if (id === "chat-unify") return "http://127.0.0.1:13023/api/api-station/v1";
    if (id === "n8n-integration") return "http://127.0.0.1:13026/api/api-station/v1";
    if (id === "cloud-workers") return "http://127.0.0.1:13027/api/api-station/v1";
    return "http://127.0.0.1:13020/api/api-station/v1?app=" + encodeURIComponent(id);
  }

  function ensurePanel() {
    if ($("api-station-panel")) return;
    var panel = document.createElement("section");
    panel.id = "api-station-panel";
    panel.className = "api-station-panel hidden";
    panel.innerHTML =
      '<div class="api-station-hero">' +
      '<h1 id="station-title">API Station</h1>' +
      '<p id="station-line">Local task router — founder runs any task · no Worker chat</p>' +
      '<div class="api-station-meta" id="station-meta"></div>' +
      '<div class="api-station-filters" id="station-filters"></div>' +
      '<div class="api-station-endpoint" id="station-endpoint"></div>' +
      "</div>" +
      '<div class="api-station-grid" id="station-tasks"></div>' +
      '<pre class="api-station-output" id="station-output">Run a task…</pre>';
    document.body.appendChild(panel);
  }

  var lastManifest = null;
  var activeCategory = "all";

  function renderManifest(data) {
    lastManifest = data;
    $("station-title").textContent = "API Station · " + (data.title || appId());
    $("station-line").textContent = data.founder_line || "POST { task, payload } to run";
    $("station-endpoint").textContent =
      "POST " + apiBase() + '\nBody: { "task": "<id>", "payload": {} }' +
      "\nAll ops: ?app=founder-ops on URL or View → API Station";
    $("station-meta").innerHTML = [
      '<span class="api-station-pill ' + (data.service_up ? "ok" : "bad") + '">' +
        (data.service_up ? "Service UP" : "Service DOWN") +
        "</span>",
      '<span class="api-station-pill">' + (data.tasks || []).length + " tasks</span>",
      '<a class="api-station-pill" href="?station=1&amp;app=founder-ops" style="text-decoration:none">All ASF ops</a>',
    ].join("");
    var cats = ["all"];
    (data.tasks || []).forEach(function (t) {
      if (t.category && cats.indexOf(t.category) < 0) cats.push(t.category);
    });
    var filters = $("station-filters");
    if (filters) {
      filters.innerHTML = cats
        .map(function (c) {
          return (
            '<button type="button" class="station-cat-btn' +
            (c === activeCategory ? " active" : "") +
            '" data-cat="' +
            c +
            '">' +
            c +
            "</button>"
          );
        })
        .join("");
      filters.querySelectorAll(".station-cat-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
          activeCategory = btn.getAttribute("data-cat") || "all";
          renderManifest(lastManifest);
        });
      });
    }
    var tasks = data.tasks || [];
    if (activeCategory !== "all") {
      tasks = tasks.filter(function (t) {
        return t.category === activeCategory;
      });
    }
    var grid = $("station-tasks");
    grid.innerHTML = tasks
      .map(function (t) {
        var tier = t.tier || "light";
        var tierCls = tier === "heavy" ? "heavy" : "light";
        return (
          '<article class="api-station-task ' + tierCls + '">' +
          "<h3>" +
          t.label +
          ' <span class="api-station-tier">' +
          tier +
          "</span></h3>" +
          "<p>" +
          (t.desc || "") +
          " · " +
          t.method +
          "</p>" +
          '<button type="button" data-task="' +
          t.id +
          '" data-tier="' +
          tier +
          '">Run · ' +
          t.id +
          "</button>" +
          "</article>"
        );
      })
      .join("");
    grid.querySelectorAll("button[data-task]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        runTask(btn.getAttribute("data-task"), btn);
      });
    });
  }

  async function loadStation() {
    ensurePanel();
    try {
      var r = await fetch(apiBase());
      renderManifest(await r.json());
    } catch (e) {
      if ($("station-output")) $("station-output").textContent = "Could not load station: " + e.message;
    }
  }

  async function runTask(taskId, btn) {
    var out = $("station-output");
    if (btn) btn.disabled = true;
    var tier = (btn && btn.getAttribute("data-tier")) || "light";
    var timeoutMs = tier === "heavy" ? 180000 : 90000;
    out.textContent = "Running " + taskId + " (" + tier + ")…";
    var ctrl = new AbortController();
    var timer = setTimeout(function () {
      ctrl.abort();
    }, timeoutMs);
    try {
      var r = await fetch(apiBase(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: taskId, payload: {} }),
        signal: ctrl.signal,
      });
      var data = await r.json();
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
      out.textContent =
        "Task failed: " +
        (e.name === "AbortError" ? "timed out after " + timeoutMs / 1000 + "s" : e.message);
    } finally {
      clearTimeout(timer);
      if (btn) btn.disabled = false;
    }
  }

  function init() {
    ensurePanel();
    window.sinaLoadApiStation = loadStation;
    if (location.search.indexOf("station=1") >= 0 && window.sinaSetViewMode) {
      window.sinaSetViewMode("station");
    }
  }

  window.SinaApiStation = {
    loadStation: loadStation,
    runTask: runTask,
    appId: appId,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

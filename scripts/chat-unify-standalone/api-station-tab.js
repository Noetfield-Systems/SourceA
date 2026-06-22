(function () {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function appId() {
    var meta = document.querySelector('meta[name="sina-app-id"]');
    if (meta && meta.content) return meta.content;
    var port = String(window.location.port || "");
    var path = window.location.pathname || "";
    if (port === "13023") return "chat-unify";
    if (port === "13026") return "n8n-integration";
    if (path.indexOf("/mail-hub") !== -1) return "portfolio-mail";
    if (port === "13020") return "worker-hub";
    return "worker-hub";
  }

  function apiBase() {
    var id = appId();
    if (id === "chat-unify") return "http://127.0.0.1:13023/api/api-station/v1";
    if (id === "n8n-integration") return "http://127.0.0.1:13026/api/api-station/v1";
    return "http://127.0.0.1:13020/api/api-station/v1?app=" + encodeURIComponent(id);
  }

  function mountModeBar() {
    if ($("sina-mode-bar")) return;
    var bar = document.createElement("nav");
    bar.id = "sina-mode-bar";
    bar.className = "sina-mode-bar";
    bar.innerHTML =
      '<span class="mode-label">View</span>' +
      '<button type="button" class="sina-mode-tab active" data-mode="app">App</button>' +
      '<button type="button" class="sina-mode-tab station" data-mode="station">API Station</button>';
    var links = document.querySelector(".official-links-bar");
    if (links && links.parentNode) {
      links.parentNode.insertBefore(bar, links.nextSibling);
    } else {
      document.body.insertBefore(bar, document.body.firstChild);
    }
    bar.querySelectorAll(".sina-mode-tab").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setMode(btn.getAttribute("data-mode"));
      });
    });
  }

  function appRoot() {
    return document.querySelector("[data-sina-app-root]") || document.querySelector("main") || document.body;
  }

  function setMode(mode) {
    var isStation = mode === "station";
    document.querySelectorAll(".sina-mode-tab").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-mode") === mode);
    });
    var root = appRoot();
    if (root) root.classList.toggle("hidden", isStation);
    var panel = $("api-station-panel");
    if (panel) panel.classList.toggle("hidden", !isStation);
    if (isStation) loadStation();
  }

  function ensurePanel() {
    if ($("api-station-panel")) return;
    var panel = document.createElement("section");
    panel.id = "api-station-panel";
    panel.className = "api-station-panel hidden";
    panel.innerHTML =
      '<div class="api-station-hero">' +
      '<h1 id="station-title">API Station</h1>' +
      '<p id="station-line">Local task router — AI agents POST task ids here</p>' +
      '<div class="api-station-meta" id="station-meta"></div>' +
      '<div class="api-station-endpoint" id="station-endpoint"></div>' +
      "</div>" +
      '<div class="api-station-grid" id="station-tasks"></div>' +
      '<pre class="api-station-output" id="station-output">Run a task…</pre>';
    document.body.appendChild(panel);
  }

  function renderManifest(data) {
    $("station-title").textContent = "API Station · " + (data.title || appId());
    $("station-line").textContent = data.founder_line || "POST { task, payload } to run";
    $("station-endpoint").textContent = "POST " + apiBase() + '\nBody: { "task": "<id>", "payload": {} }';
    $("station-meta").innerHTML = [
      '<span class="api-station-pill ' + (data.service_up ? "ok" : "bad") + '">' +
        (data.service_up ? "Service UP" : "Service DOWN") +
        "</span>",
      '<span class="api-station-pill">' + (data.tasks || []).length + " tasks</span>",
    ].join("");
    var grid = $("station-tasks");
    grid.innerHTML = (data.tasks || [])
      .map(function (t) {
        return (
          '<article class="api-station-task">' +
          "<h3>" +
          t.label +
          "</h3>" +
          "<p>" +
          (t.desc || "") +
          " · " +
          t.method +
          "</p>" +
          '<button type="button" data-task="' +
          t.id +
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
    try {
      var r = await fetch(apiBase());
      renderManifest(await r.json());
    } catch (e) {
      $("station-output").textContent = "Could not load station: " + e.message;
    }
  }

  async function runTask(taskId, btn) {
    var out = $("station-output");
    if (btn) btn.disabled = true;
    out.textContent = "Running " + taskId + "…";
    try {
      var r = await fetch(apiBase(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: taskId, payload: {} }),
      });
      var data = await r.json();
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
      out.textContent = "Task failed: " + e.message;
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  function init() {
    mountModeBar();
    ensurePanel();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.SinaApiStation = { loadStation: loadStation, runTask: runTask, setMode: setMode, appId: appId };
})();

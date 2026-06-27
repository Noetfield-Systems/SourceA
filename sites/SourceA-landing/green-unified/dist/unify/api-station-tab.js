(function () {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function appId() {
    var meta = document.querySelector('meta[name="sina-app-id"]');
    if (meta && meta.content) return meta.content;
    return "chat-unify";
  }

  function apiBase() {
    return window.location.origin + "/api/api-station/v1";
  }

  function tabShell() {
    return document.querySelector("[data-cu-tab-shell]");
  }

  function mountTarget() {
    return $("panel-api-station") || document.body;
  }

  function mountModeBar() {
    if (tabShell() || $("sina-mode-bar")) return;
    var bar = document.createElement("nav");
    bar.id = "sina-mode-bar";
    bar.className = "sina-mode-bar";
    bar.innerHTML =
      '<span class="mode-label">View</span>' +
      '<button type="button" class="sina-mode-tab active" data-mode="app">App</button>' +
      '<button type="button" class="sina-mode-tab station" data-mode="station">API Station</button>';
    var links = document.querySelector(".official-links-bar");
    if (links && links.parentNode) links.parentNode.insertBefore(bar, links.nextSibling);
  }

  function appRoot() {
    return document.querySelector("[data-sina-app-root]") || document.querySelector("main") || document.body;
  }

  function setMode(mode) {
    if (tabShell() && mode === "station" && window.switchTab) {
      window.switchTab("api");
      return;
    }
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
      '<h1 id="station-title">Tasks</h1>' +
      '<p id="station-line">Queue and dispatch agent work — every outcome writes a receipt you can verify</p>' +
      '<div class="api-station-meta" id="station-meta"></div>' +
      '<div class="api-station-endpoint" id="station-endpoint"></div>' +
      "</div>" +
      '<div class="api-station-grid" id="station-tasks"></div>' +
      '<pre class="api-station-output" id="station-output">Run a task…</pre>';
    mountTarget().appendChild(panel);
  }

  async function loadStation() {
    ensurePanel();
    var panel = $("api-station-panel");
    if (panel && mountTarget() !== document.body) panel.classList.remove("hidden");
    var meta = $("station-meta");
    var endpoint = $("station-endpoint");
    var grid = $("station-tasks");
    var out = $("station-output");
    try {
      var res = await fetch(apiBase() + "?app=" + encodeURIComponent(appId()), { cache: "no-store" });
      var data = await res.json();
      if ($("station-title")) $("station-title").textContent = data.title || "API Station";
      if ($("station-line")) $("station-line").textContent = data.line || "";
      if (meta) {
        meta.innerHTML =
          '<span class="api-station-pill ' + (data.service_up ? "ok" : "bad") + '">' +
          (data.service_up ? "Service UP" : "Service DOWN") +
          "</span>" +
          '<span class="api-station-pill">' + (data.tasks || []).length + " tasks</span>";
      }
      if (endpoint) endpoint.textContent = apiBase();
      if (grid) {
        grid.innerHTML = (data.tasks || [])
          .map(function (t) {
            return (
              '<article class="api-station-task">' +
              "<h3>" + t.id + "</h3><p>" + (t.description || "") + '</p>' +
              '<button type="button" data-task="' + t.id + '">Run</button></article>'
            );
          })
          .join("");
        grid.querySelectorAll("button[data-task]").forEach(function (btn) {
          btn.addEventListener("click", function () {
            runTask(btn.getAttribute("data-task"));
          });
        });
      }
      if (out && !out.dataset.hasRun) out.textContent = "Ready — pick a task.";
    } catch (e) {
      if (out) out.textContent = "Load failed: " + e.message;
    }
  }

  async function runTask(taskId) {
    var out = $("station-output");
    var btn = document.querySelector('button[data-task="' + taskId + '"]');
    if (btn) btn.disabled = true;
    if (out) out.textContent = "Running " + taskId + "…";
    try {
      var r = await fetch(apiBase(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: taskId, app: appId() }),
      });
      var data = await r.json();
      if (out) {
        out.dataset.hasRun = "1";
        out.textContent = JSON.stringify(data, null, 2);
      }
    } catch (e) {
      if (out) out.textContent = "Task failed: " + e.message;
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  function init() {
    mountModeBar();
    ensurePanel();
    if (tabShell() && $("api-station-panel")) $("api-station-panel").classList.add("hidden");
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();

  window.SinaApiStation = { loadStation: loadStation, runTask: runTask, setMode: setMode, appId: appId };
  window.sinaLoadApiStation = loadStation;
})();

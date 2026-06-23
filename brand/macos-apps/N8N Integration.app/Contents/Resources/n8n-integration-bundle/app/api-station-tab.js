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

  function stationAppId() {
    var qs = new URLSearchParams(window.location.search || "");
    return qs.get("app") || appId();
  }

  function apiBase() {
    var id = stationAppId();
    var base;
    if (id === "chat-unify") base = "http://127.0.0.1:13023/api/api-station/v1";
    else if (id === "n8n-integration") base = "http://127.0.0.1:13026/api/api-station/v1";
    else if (id === "cloud-workers") base = "http://127.0.0.1:13027/api/api-station/v1";
    else base = "http://127.0.0.1:13020/api/api-station/v1";
    if (id !== "chat-unify" && id !== "n8n-integration" && id !== "cloud-workers" && id !== "worker-hub") {
      base += "?app=" + encodeURIComponent(id);
    } else if (id === "worker-hub" && stationAppId() !== "worker-hub") {
      base += "?app=" + encodeURIComponent(stationAppId());
    } else if (id === "n8n-integration" && stationAppId() !== "n8n-integration") {
      base += "?app=" + encodeURIComponent(stationAppId());
    }
    return base;
  }

  function terminalBase() {
    return apiBase().replace("/api/api-station/v1", "/api/api-station/terminal/v1");
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
      '<div class="api-station-terminal-wrap">' +
      '<div class="api-station-terminal-head"><span>Live terminal</span><span id="station-terminal-badge" class="api-station-terminal-badge">idle</span></div>' +
      '<pre class="api-station-output api-station-terminal" id="station-output">Run a task — real process output appears here.</pre>' +
      "</div>";
    document.body.appendChild(panel);
  }

  var lastManifest = null;
  var activeCategory = "all";

  function renderStationTerminal(lines, running) {
    var out = $("station-output");
    var badge = $("station-terminal-badge");
    if (out) {
      out.textContent = lines && lines.length ? lines.join("\n") : "Run a task — real process output appears here.";
      out.classList.toggle("api-station-terminal-running", !!running);
      out.scrollTop = out.scrollHeight;
    }
    if (badge) {
      badge.textContent = running ? "running" : lines && lines.length > 2 ? "done" : "idle";
      badge.className = "api-station-terminal-badge" + (running ? " is-running" : "");
    }
  }

  function renderManifest(data) {
    lastManifest = data;
    $("station-title").textContent = "API Station · " + (data.title || stationAppId());
    $("station-line").textContent = data.founder_line || "POST { task, payload } to run";
    $("station-endpoint").textContent =
      "POST " + apiBase() + '\nBody: { "task": "<id>", "payload": {} }' +
      "\nTerminal: GET " + terminalBase() +
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

  async function loadTerminalTail() {
    try {
      var r = await fetch(terminalBase() + "?lines=120", { cache: "no-store" });
      var data = await r.json();
      if (data.terminal_lines && data.terminal_lines.length) {
        renderStationTerminal(data.terminal_lines, data.running);
      }
      return data;
    } catch (e) {
      return null;
    }
  }

  async function pollTerminalUntilDone(maxMs) {
    var deadline = Date.now() + (maxMs || 360000);
    while (Date.now() < deadline) {
      var tail = await loadTerminalTail();
      if (tail && !tail.running) return tail;
      await new Promise(function (r) {
        setTimeout(r, 400);
      });
    }
    return null;
  }

  async function loadStation() {
    ensurePanel();
    try {
      var r = await fetch(apiBase(), { cache: "no-store" });
      renderManifest(await r.json());
      await loadTerminalTail();
    } catch (e) {
      if ($("station-output")) $("station-output").textContent = "Could not load station: " + e.message;
    }
  }

  async function runTask(taskId, btn) {
    if (btn) btn.disabled = true;
    var tier = (btn && btn.getAttribute("data-tier")) || "light";
    var timeoutMs = tier === "heavy" ? 360000 : 120000;
    var term = window.SinaMainTerminal;
    if (term) term.start(taskId, "API Station · " + taskId);
    else renderStationTerminal(["═══ starting " + taskId + " (" + tier + ") ═══"], true);

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
        cache: "no-store",
      });
      var data = await r.json();

      if (tier === "heavy" || data.async || data.started) {
        await pollTerminalUntilDone(timeoutMs);
        var tail = await loadTerminalTail();
        if (tail && tail.terminal_lines && tail.terminal_lines.length) {
          if (term) term.appendBlock(tail.terminal_lines);
          else renderStationTerminal(tail.terminal_lines, false);
          var badge = $("station-terminal-badge");
          if (badge) {
            var ok = tail.finished_ok !== undefined && tail.finished_ok !== null ? tail.finished_ok : data.ok;
            badge.textContent = ok ? "pass" : "fail";
            badge.className = "api-station-terminal-badge " + (ok ? "is-pass" : "is-fail");
          }
          if (term) term.finish(!!tail.finished_ok, "API Station · " + taskId + " complete");
        }
      } else {
        var lines = data.terminal_lines || [];
        if (term) {
          term.appendBlock(lines);
          term.finish(!!data.ok, "API Station · " + taskId + " complete");
        } else {
          renderStationTerminal(lines.length ? lines : ["(no terminal output)", JSON.stringify(data, null, 2)], false);
        }
      }
    } catch (e) {
      var errLines = ["[ERROR] " + (e.name === "AbortError" ? "timed out after " + timeoutMs / 1000 + "s" : e.message)];
      var tailErr = await loadTerminalTail();
      if (tailErr && tailErr.terminal_lines && tailErr.terminal_lines.length) {
        errLines = tailErr.terminal_lines.concat(errLines);
      }
      renderStationTerminal(errLines, false);
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
    loadTerminalTail: loadTerminalTail,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

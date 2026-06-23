(function () {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function appId() {
    var meta = document.querySelector('meta[name="sina-app-id"]');
    if (meta && meta.content) return meta.content;
    var port = String(window.location.port || "");
    if (port === "13024") return "mac_health";
    if (port === "13023") return "chat_unify";
    if (port === "13026") return "n8n_integration";
    if (window.location.pathname.indexOf("/machines") !== -1) return "machine_hub";
    if (window.location.pathname.indexOf("/form") !== -1) return "hub_form";
    if (window.location.pathname.indexOf("/mail-hub") !== -1) return "portfolio_mail";
    return "worker_hub";
  }

  function hubBase() {
    var port = String(window.location.port || "");
    if (port === "13024" || port === "13023" || port === "13026") {
      return "http://127.0.0.1:13020";
    }
    return window.location.origin;
  }

  function apiUrl() {
    return hubBase() + "/api/hub-pro-skills/v1?app=" + encodeURIComponent(appId());
  }

  function mountModeBar() {
    var bar = $("sina-mode-bar");
    if (!bar) {
      bar = document.createElement("nav");
      bar.id = "sina-mode-bar";
      bar.className = "sina-mode-bar";
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
          setMode(btn.getAttribute("data-mode"));
        });
      });
      return;
    }
    if (!bar.querySelector('[data-mode="hubpro"]')) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "sina-mode-tab hubpro";
      btn.setAttribute("data-mode", "hubpro");
      btn.textContent = "Hub Pro";
      btn.addEventListener("click", function () {
        setMode("hubpro");
      });
      bar.appendChild(btn);
    }
  }

  function appRoot() {
    return document.querySelector("[data-sina-app-root]") || document.querySelector("main") || document.querySelector(".wrap") || document.body;
  }

  function setMode(mode) {
    var isHubPro = mode === "hubpro";
    var isStation = mode === "station";
    document.querySelectorAll(".sina-mode-tab").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-mode") === mode);
    });
    var root = appRoot();
    if (root && !root.id) root.classList.toggle("hidden", isStation || isHubPro);
    var station = $("api-station-panel");
    if (station) station.classList.toggle("hidden", !isStation);
    var hubpro = $("hub-pro-panel");
    if (hubpro) hubpro.classList.toggle("hidden", !isHubPro);
    if (isStation && window.sinaLoadApiStation) window.sinaLoadApiStation();
    if (isHubPro) loadHubPro();
  }

  window.sinaSetViewMode = setMode;

  function ensurePanel() {
    if ($("hub-pro-panel")) return;
    var panel = document.createElement("section");
    panel.id = "hub-pro-panel";
    panel.className = "hub-pro-panel hidden";
    panel.innerHTML =
      '<div class="hub-pro-hero">' +
      '<h1>Hub Pro — skills &amp; experience</h1>' +
      '<p id="hub-pro-line">Checklists · golden tips · agent change log</p>' +
      "</div>" +
      '<div class="hub-pro-law" id="hub-pro-law">Loading…</div>' +
      '<div class="hub-pro-section"><h2>Skills batch</h2><div class="hub-pro-grid" id="hub-pro-skills"></div></div>' +
      '<div class="hub-pro-section"><h2>Experience log — this app</h2><div id="hub-pro-entries"></div></div>' +
      '<div class="hub-pro-append">' +
      "<h2>Append agent note</h2>" +
      '<p class="meta">After you ship — one line summary for the next agent.</p>' +
      '<textarea id="hub-pro-note" placeholder="Summary of what you changed…"></textarea>' +
      '<button type="button" id="hub-pro-append-btn">Save to experience log</button>' +
      '<p id="hub-pro-append-msg"></p>' +
      "</div>";
    document.body.appendChild(panel);
    $("hub-pro-append-btn").addEventListener("click", appendNote);
  }

  function renderSkills(skills) {
    var grid = $("hub-pro-skills");
    if (!grid) return;
    grid.innerHTML = (skills || [])
      .map(function (s) {
        return (
          '<article class="hub-pro-card">' +
          "<h3>" +
          esc(s.title || s.id) +
          "</h3>" +
          "<p>" +
          esc(s.when || "") +
          "</p>" +
          "<p><code>" +
          esc(s.path || "") +
          "</code></p>" +
          "</article>"
        );
      })
      .join("");
  }

  function renderEntries(entries) {
    var el = $("hub-pro-entries");
    if (!el) return;
    if (!entries || !entries.length) {
      el.innerHTML = "<p>No entries yet for this app.</p>";
      return;
    }
    el.innerHTML = entries
      .map(function (e) {
        var tips = (e.golden_tips || []).join(" · ");
        return (
          '<div class="hub-pro-entry">' +
          '<div class="meta">' +
          esc(e.at) +
          " · " +
          esc(e.agent) +
          " · " +
          esc(e.id) +
          "</div>" +
          "<strong>" +
          esc(e.summary) +
          "</strong>" +
          (tips ? "<p><em>Tip:</em> " + esc(tips) + "</p>" : "") +
          "</div>"
        );
      })
      .join("");
  }

  async function loadHubPro() {
    try {
      var res = await fetch(apiUrl(), { cache: "no-store" });
      var d = await res.json();
      if ($("hub-pro-law")) $("hub-pro-law").textContent = d.index && d.index.one_law ? d.index.one_law : "";
      if ($("hub-pro-line")) {
        $("hub-pro-line").textContent =
          "App: " + (d.app_id || appId()) + " · " + ((d.app && d.app.url) || "");
      }
      renderSkills(d.skills);
      renderEntries((d.experience && d.experience.entries_for_app) || []);
    } catch (e) {
      if ($("hub-pro-law")) $("hub-pro-law").textContent = "Load failed: " + e.message;
    }
  }

  async function appendNote() {
    var note = ($("hub-pro-note") && $("hub-pro-note").value) || "";
    var msg = $("hub-pro-append-msg");
    if (!note.trim()) {
      if (msg) msg.textContent = "Type a summary first.";
      return;
    }
    try {
      var res = await fetch(hubBase() + "/api/hub-pro-skills/v1", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "append",
          app_id: appId(),
          agent: "founder-ui",
          summary: note.trim(),
        }),
      });
      var d = await res.json();
      if (d.ok) {
        if (msg) msg.textContent = "Saved " + (d.entry && d.entry.id ? d.entry.id : "");
        if ($("hub-pro-note")) $("hub-pro-note").value = "";
        loadHubPro();
      } else if (msg) msg.textContent = d.error || "Failed";
    } catch (e) {
      if (msg) msg.textContent = e.message;
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
})();

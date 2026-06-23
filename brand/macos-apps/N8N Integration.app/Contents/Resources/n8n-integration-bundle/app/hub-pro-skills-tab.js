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

  function normalizeAppId(id) {
    var map = {
      "n8n-integration": "n8n_integration",
      "chat-unify": "chat_unify",
      "cloud-workers": "cloud_workers",
      "worker-hub": "worker_hub",
      "portfolio-mail": "portfolio_mail",
    };
    return map[id] || id;
  }

  function appId() {
    var qs = new URLSearchParams(window.location.search || "");
    var forced = qs.get("app");
    if (forced) return normalizeAppId(forced);
    var meta = document.querySelector('meta[name="sina-app-id"]');
    if (meta && meta.content) return normalizeAppId(meta.content);
    var port = String(window.location.port || "");
    if (port === "13024") return "mac_health";
    if (port === "13023") return "chat_unify";
    if (port === "13026") return "n8n_integration";
    if (port === "13027") return "cloud_workers";
    if (window.location.pathname.indexOf("/machines") !== -1) return "machine_hub";
    if (window.location.pathname.indexOf("/form") !== -1) return "hub_form";
    if (window.location.pathname.indexOf("/mail-hub") !== -1) return "portfolio_mail";
    if (window.location.pathname.indexOf("/cloud-workers") !== -1) return "cloud_workers";
    return "worker_hub";
  }

  function hubBase() {
    var port = String(window.location.port || "");
    if (port === "13024" || port === "13023" || port === "13026" || port === "13027") {
      return "http://127.0.0.1:13020";
    }
    return window.location.origin;
  }

  function apiUrl() {
    var port = String(window.location.port || "");
    if (port === "13023" || port === "13026" || port === "13027") {
      return window.location.origin + "/api/hub-pro-skills/v1?app=" + encodeURIComponent(appId());
    }
    return hubBase() + "/api/hub-pro-skills/v1?app=" + encodeURIComponent(appId());
  }

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
      '<div class="hub-pro-section"><h2>Technical upgrade checklist (UP-0 … UP-7)</h2><ol class="hub-pro-checklist" id="hub-pro-tech-checklist"></ol></div>' +
      '<div class="hub-pro-section"><h2>UI upgrade checklist — this app</h2><p class="meta" id="hub-pro-ledger-meta"></p><ul class="hub-pro-checklist" id="hub-pro-ui-checklist"></ul><p class="meta" id="hub-pro-last-upgrade"></p></div>' +
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

  function renderTechChecklist(rows) {
    var el = $("hub-pro-tech-checklist");
    if (!el) return;
    el.innerHTML = (rows || [])
      .map(function (r) {
        return "<li><strong>" + esc(r.id) + "</strong> — " + esc(r.step || "") + "</li>";
      })
      .join("");
  }

  function renderUiChecklist(ledger) {
    var meta = $("hub-pro-ledger-meta");
    var list = $("hub-pro-ui-checklist");
    var last = $("hub-pro-last-upgrade");
    if (!list) return;
    if (!ledger || ledger.ok === false) {
      if (meta) meta.textContent = ledger && ledger.error ? ledger.error : "No ledger for this app yet.";
      list.innerHTML = "";
      if (last) last.textContent = "";
      return;
    }
    if (meta) {
      meta.textContent =
        (ledger.label || ledger.surface_id || "") +
        " · frozen " +
        (ledger.frozen_inventory_count || 0) +
        " · upgrades " +
        (ledger.upgrade_count || 0);
    }
    var items = ledger.app_checklist || [];
    list.innerHTML = items
      .map(function (r) {
        var mark = r.done ? "✓" : "○";
        return (
          '<li><span class="hub-pro-chk">' +
          mark +
          '</span> <strong>' +
          esc(r.id) +
          "</strong> — " +
          esc(r.step || "") +
          "</li>"
        );
      })
      .join("");
    var lu = ledger.last_upgrade;
    if (last) {
      last.textContent = lu
        ? "Last upgrade: " + (lu.upgrade_id || "") + " · " + (lu.saved_at || "") + " — " + (lu.changed || lu.achieved || "")
        : "";
    }
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
    ensurePanel();
    try {
      var res = await fetch(apiUrl(), { cache: "no-store" });
      var d = await res.json();
      if ($("hub-pro-law")) $("hub-pro-law").textContent = d.index && d.index.one_law ? d.index.one_law : "";
      if ($("hub-pro-line")) {
        $("hub-pro-line").textContent =
          "App: " + (d.app_id || appId()) + " · " + ((d.app && d.app.url) || "");
      }
      renderTechChecklist(d.technical_checklist);
      renderUiChecklist(d.upgrade_ledger);
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
    ensurePanel();
    window.sinaLoadHubPro = loadHubPro;
    if (location.search.indexOf("hubpro=1") >= 0 && window.sinaSetViewMode) {
      window.sinaSetViewMode("hubpro");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

(function () {
  "use strict";

  const API = window.location.origin;

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s || "";
    return d.innerHTML;
  }

  function renderAudiences(rows) {
    const el = $("start-audience-grid") || $("home-audience-grid");
    if (!el) return;
    el.innerHTML = (rows || [])
      .map(function (a) {
        return (
          '<button type="button" class="cu-audience-card" data-goto-tab="' +
          esc(a.cta_tab) +
          '">' +
          "<h3>" +
          esc(a.title) +
          "</h3><em>" +
          esc(a.subtitle) +
          "</em><p>" +
          esc(a.description) +
          '</p><span class="cu-audience-link">' +
          esc(a.cta_label) +
          " →</span></button>"
        );
      })
      .join("");
    el.querySelectorAll("[data-goto-tab]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const tab = btn.getAttribute("data-goto-tab");
        if (tab && window.switchTab) window.switchTab(tab);
      });
    });
  }

  function renderMachines(rows) {
    const el = $("start-machines-grid") || $("home-machines-grid");
    if (!el) return;
    el.innerHTML = (rows || [])
      .map(function (m) {
        const steps = m.steps ? m.steps + " steps · " : "";
        return (
          '<button type="button" class="cu-machine-chip" data-goto-tab="' +
          esc(m.tab) +
          '"><strong>' +
          esc(m.name) +
          "</strong><span>" +
          esc(m.desc) +
          '</span><em>' +
          steps +
          "Open workspace →</em></button>"
        );
      })
      .join("");
    el.querySelectorAll("[data-goto-tab]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const tab = btn.getAttribute("data-goto-tab");
        if (tab && window.switchTab) window.switchTab(tab);
      });
    });
  }

  function renderUpdatePanel(json) {
    const status = $("cu-update-status");
    const btn = $("cu-update-download");
    const footer = $("footer-update-line");
    if (!json || !json.ok) {
      if (status) {
        status.textContent = "Could not check for updates — try again later.";
        status.className = "cu-update-status";
      }
      if (footer) footer.textContent = "Update check offline";
      return;
    }
    const line = json.founder_line || "";
    if (status) {
      status.textContent = line;
      status.className =
        "cu-update-status " + (json.update_available ? "is-available" : "is-latest");
    }
    if (btn) {
      if (json.update_available && json.download_url) {
        btn.href = json.download_url;
        btn.hidden = false;
        btn.textContent = "Download v" + (json.latest_version || "latest");
      } else {
        btn.hidden = true;
      }
    }
    if (footer) {
      footer.textContent = json.update_available
        ? "Update available · open Start tab"
        : "v" + (json.current_version || "—") + " · up to date";
    }
  }

  async function loadUpdateCheck() {
    const status = $("cu-update-status");
    if (status) status.textContent = "Checking for updates…";
    try {
      const res = await fetch(API + "/api/chat-unify-update/v1");
      const json = await res.json();
      renderUpdatePanel(json);
      return json;
    } catch {
      renderUpdatePanel(null);
      return null;
    }
  }

  async function loadPlatformHome() {
    const line = $("start-platform-line") || $("home-platform-line");
    try {
      const res = await fetch(API + "/api/platform-catalog/v1");
      const json = await res.json();
      if (!json.ok) return;
      const cat = json.catalog || {};
      renderAudiences(cat.audiences);
      renderMachines(cat.machines);
      if (line) {
        const ig = json.integrations || {};
        const machineCount = (cat.machines || []).length;
        line.textContent =
          "Chat Unify · " +
          machineCount +
          " workspaces · Connect " +
          (ig.lanes_live || 0) +
          "/" +
          (ig.lanes_total || 0) +
          " lanes live · UI " +
          (ig.ui_version || "—");
      }
    } catch {
      if (line) line.textContent = "Loading workspace catalog…";
    }
    await loadUpdateCheck();
  }

  window.sinaLoadPlatformHome = loadPlatformHome;
  window.sinaLoadUpdateCheck = loadUpdateCheck;

  document.addEventListener("DOMContentLoaded", function () {
    $("btn-enterprise-connect")?.addEventListener("click", function () {
      if (window.switchTab) window.switchTab("connect");
    });
    $("cu-update-recheck")?.addEventListener("click", function () {
      loadUpdateCheck();
    });
    loadUpdateCheck();
  });
})();

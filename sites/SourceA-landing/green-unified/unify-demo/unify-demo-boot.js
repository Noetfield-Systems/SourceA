(function () {
  "use strict";
  /** Public demo — 4.6.x-style browser demo; Chat-first; no Workspace terminal. */
  var cu = window.__cuWebPath && window.__cuWebPath();
  if (!cu || !cu.isDemo) return;

  document.documentElement.setAttribute("data-cu-web", "demo");
  if (window.location.hash === "#forge-ide" || window.location.hash === "#vocab") {
    try {
      window.history.replaceState(null, "", window.location.pathname + window.location.search);
    } catch (e) { /* ignore */ }
  }

  var WEB_API = window.location.origin + "/api/chat-unify-demo-cloud/v1";
  window.__CHAT_UNIFY_API_BASE__ = WEB_API;

  var DEMO_HIDE_TABS = ["forge-ide", "vocab"];
  var DEMO_HIDE_PANELS = ["panel-forge-ide", "panel-vocabulary-intelligence"];

  function canonicalizeDemoUrl() {
    if (window.location.hash === "#forge-ide" || window.location.hash === "#vocab") {
      try {
        window.history.replaceState(null, "", window.location.pathname + window.location.search);
      } catch (e) { /* ignore */ }
    }
  }

  canonicalizeDemoUrl();

  var nativeFetch = window.fetch.bind(window);
  function mapUrl(url) {
    if (typeof url !== "string") return url;
    var origin = window.location.origin;
    if (url === origin + "/health") return WEB_API + "/health";
    if (url.indexOf(origin + "/api/") === 0) return WEB_API + url.slice(origin.length + 4);
    if (url.indexOf(origin + "/form") === 0) return WEB_API + url.slice(origin.length);
    return url;
  }

  window.fetch = function (url, opts) {
    return nativeFetch(mapUrl(url), opts);
  };

  document.addEventListener("DOMContentLoaded", function () {
    document.title = "Chat Unify Demo — paste · verify · unify";
    canonicalizeDemoUrl();
    DEMO_HIDE_TABS.forEach(function (tabId) {
      var tab = document.querySelector('.cu-tab[data-tab="' + tabId + '"]');
      if (tab) tab.hidden = true;
      var btn = document.querySelector('.cu-forge-machines-scroll [data-goto-tab="' + tabId + '"]');
      if (btn) btn.hidden = true;
      var card = document.querySelector('.sa-unify-machine-card[data-goto-tab="' + tabId + '"]');
      if (card) card.hidden = true;
    });
    DEMO_HIDE_PANELS.forEach(function (panelId) {
      var panel = document.getElementById(panelId);
      if (panel) {
        panel.hidden = true;
        panel.classList.remove("cu-tab-panel-active");
      }
    });

    document.querySelectorAll('a[href^="http://127.0.0.1:"]').forEach(function (a) {
      a.hidden = true;
    });
    var hook = document.getElementById("connect-hook-url");
    if (hook) hook.value = WEB_API + "/integrations/v1/hook";

    var lead = document.querySelector(".cu-enterprise-lead");
    if (lead) {
      lead.textContent =
        "Try Chat Unify in your browser — a 4.6.x-style public demo for Chat, Start, Prompt Forge, Connect, Verify, Audit, Decisions, Tasks, Operations, and Proof Pack. The full paid desk adds Workspace IDE and Vocabulary Intel.";
    }
    var kicker = document.querySelector(".cu-kicker");
    if (kicker) kicker.textContent = "SourceA · Chat Unify Demo";

    var subKicker = document.getElementById("sa-unify-sub-kicker");
    var subTitle = document.getElementById("sa-unify-sub-title");
    var subLead = document.getElementById("sa-unify-sub-lead");
    if (subKicker) subKicker.textContent = "Public demo · 4.6.x-style browser profile";
    if (subTitle) subTitle.textContent = "Try the clean Chat Unify demo";
    if (subLead) {
      subLead.textContent =
        "Paste agent replies, verify PASS or BLOCK, audit output, forge missions, and unify sessions — no install and no Workspace terminal in the demo.";
    }
    var machineKicker = document.getElementById("sa-unify-machine-kicker");
    var machineTitle = document.getElementById("sa-unify-machine-title");
    var machineLead = document.getElementById("sa-unify-machine-lead");
    if (machineKicker) machineKicker.textContent = "Demo machine set";
    if (machineTitle) machineTitle.textContent = "Demo keeps the clean 4.6.x machine set.";
    if (machineLead) {
      machineLead.textContent =
        "This page is intentionally simpler than the full paid desk: no Workspace terminal, no Vocabulary Intel, and no desktop-only chrome.";
    }
    var proofStats = document.querySelectorAll(".sa-unify-proof-card .sa-fleet-stats strong");
    if (proofStats[0]) proofStats[0].textContent = "10";
    document.querySelectorAll(".sa-unify-nav-active").forEach(function (el) {
      el.classList.remove("sa-unify-nav-active");
      el.removeAttribute("aria-current");
    });
    var demoNav = document.querySelector('.ar-nav a[href="/unify-demo/"]');
    if (demoNav) {
      demoNav.classList.add("sa-unify-nav-active");
      demoNav.setAttribute("aria-current", "page");
    }

    var banner = document.createElement("div");
    banner.className = "cu-web-banner cu-web-banner-demo";
    banner.setAttribute("role", "status");
    banner.innerHTML =
      '<strong>Public demo</strong> — 4.6.x-style clean demo: Chat · Start · Forge · Connect · Verify · Audit · Decisions · Tasks · Operations · Proof Pack. ' +
      '<a href="/unify/">Open full 4.9.9 paid desk</a> · ' +
      '<a href="/downloads/chat-unify-mac-v1.dmg">Download Mac app</a>';
    var app = document.querySelector(".cu-app");
    if (app && app.parentNode) app.parentNode.insertBefore(banner, app);

    try {
      localStorage.setItem("chat-unify-active-tab-v1", "home");
    } catch (e) { /* ignore */ }
    window.setTimeout(canonicalizeDemoUrl, 0);
    window.setTimeout(canonicalizeDemoUrl, 250);
  });
  window.addEventListener("load", canonicalizeDemoUrl);
})();

/**
 * SourceA cookie consent — GDPR-style banner, preferences, consent-gated analytics.
 * SSOT: /sourcea/data/sourcea-cookie-consent-config-v1.json
 */
(function (global) {
  "use strict";

  const STORAGE_KEY = "sourcea-cookie-consent-v1";
  const CONFIG_URL = "/sourcea/data/sourcea-cookie-consent-config-v1.json";
  const VERSION = "1.0.0";

  let config = {};
  let consent = null;
  let ready = false;

  function loadStored() {
    try {
      const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (raw && raw.schema === STORAGE_KEY) return raw;
    } catch (_) {
      /* quiet */
    }
    return null;
  }

  function saveConsent(categories, source) {
    consent = {
      schema: STORAGE_KEY,
      at: new Date().toISOString(),
      policy_version: config.policy_version || 1,
      source: source || "banner",
      categories: {
        necessary: true,
        analytics: !!categories.analytics,
        functional: !!categories.functional,
      },
    };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(consent));
    } catch (_) {
      /* quiet */
    }
    dispatchChange();
  }

  function dispatchChange() {
    global.dispatchEvent(
      new CustomEvent("sourcea:consent-changed", { detail: { consent: consent, categories: consent?.categories } })
    );
  }

  function dispatchReady() {
    ready = true;
    global.dispatchEvent(new CustomEvent("sourcea:consent-ready", { detail: { consent: consent } }));
  }

  function has(category) {
    if (!consent) return category === "necessary";
    if (category === "necessary") return true;
    return !!(consent.categories && consent.categories[category]);
  }

  function needsBanner() {
    if (!consent) return true;
    return (consent.policy_version || 0) < (config.policy_version || 1);
  }

  async function loadConfig() {
    try {
      const r = await fetch(CONFIG_URL, { cache: "no-store" });
      if (r.ok) config = await r.json();
    } catch (_) {
      config = {};
    }
  }

  function mountPreferences(onSave) {
    const existing = document.getElementById("sa-cookie-prefs");
    if (existing) {
      existing.hidden = false;
      return;
    }
    const cats = config.categories || [
      { id: "necessary", label: "Strictly necessary", required: true, description: "Required for sign-in and security." },
      { id: "analytics", label: "Analytics", required: false, description: "Anonymous usage to improve the site." },
      { id: "functional", label: "Functional", required: false, description: "Feedback and UX helpers." },
    ];

    const wrap = document.createElement("div");
    wrap.id = "sa-cookie-prefs";
    wrap.className = "sa-cookie-prefs-panel";
    wrap.setAttribute("role", "dialog");
    wrap.setAttribute("aria-modal", "true");
    wrap.setAttribute("aria-label", "Cookie preferences");

    const rows = cats
      .map(function (c) {
        const checked = c.required || has(c.id);
        const disabled = c.required ? " disabled checked" : checked ? " checked" : "";
        return (
          '<div class="sa-cookie-category">' +
          "<strong>" +
          c.label +
          "</strong>" +
          '<input type="checkbox" class="sa-cookie-toggle" data-cat="' +
          c.id +
          '"' +
          disabled +
          " />" +
          "<p>" +
          (c.description || "") +
          "</p></div>"
        );
      })
      .join("");

    wrap.innerHTML =
      '<div class="sa-cookie-prefs-backdrop" data-close></div>' +
      '<div class="sa-cookie-prefs-card">' +
      "<h2>Cookie preferences</h2>" +
      "<p style=\"font-size:0.85rem;color:var(--ar-text-muted);margin:0 0 0.75rem\">Choose what we may use. You can change this anytime.</p>" +
      rows +
      '<div class="sa-cookie-prefs-actions">' +
      '<button type="button" class="ar-btn ar-btn-primary ar-btn-sm" id="sa-cookie-prefs-save">Save preferences</button>' +
      '<button type="button" class="ar-btn ar-btn-ghost ar-btn-sm" data-close>Cancel</button>' +
      "</div></div>";

    document.body.appendChild(wrap);
    document.body.classList.add("sa-cookie-prefs-open");

    function close() {
      wrap.hidden = true;
      document.body.classList.remove("sa-cookie-prefs-open");
    }

    wrap.querySelectorAll("[data-close]").forEach(function (el) {
      el.addEventListener("click", close);
    });

    wrap.querySelector("#sa-cookie-prefs-save").addEventListener("click", function () {
      const next = { analytics: false, functional: false };
      wrap.querySelectorAll(".sa-cookie-toggle[data-cat]").forEach(function (input) {
        const id = input.getAttribute("data-cat");
        if (id && id !== "necessary") next[id] = input.checked;
      });
      saveConsent(next, "preferences");
      close();
      hideBanner();
      mountManageFab();
      if (onSave) onSave();
    });
  }

  function hideBanner() {
    const b = document.getElementById("sa-cookie-banner");
    if (b) b.remove();
    document.body.classList.remove("sa-cookie-banner-open");
  }

  function mountBanner() {
    if (document.getElementById("sa-cookie-banner")) return;
    const privacy = (config.links && config.links.privacy) || "/privacy";
    const cookies = (config.links && config.links.cookies) || "/cookies";

    const el = document.createElement("aside");
    el.id = "sa-cookie-banner";
    el.className = "sa-cookie-banner";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-label", "Cookie consent");
    el.innerHTML =
      '<div class="sa-cookie-banner-inner">' +
      "<h2>We value your privacy</h2>" +
      "<p>We use essential cookies for sign-in and security. With your consent we also use anonymous analytics and optional feedback tools — no ad trackers.</p>" +
      '<div class="sa-cookie-banner-actions">' +
      '<button type="button" class="ar-btn ar-btn-primary ar-btn-sm" id="sa-cookie-accept-all">Accept all</button>' +
      '<button type="button" class="ar-btn ar-btn-ghost ar-btn-sm" id="sa-cookie-reject">Reject non-essential</button>' +
      '<button type="button" class="ar-btn ar-btn-ghost ar-btn-sm" id="sa-cookie-customize">Customize</button>' +
      "</div>" +
      '<p class="sa-cookie-banner-links"><a href="' +
      privacy +
      '">Privacy</a> · <a href="' +
      cookies +
      '">Cookie policy</a></p></div>";

    document.body.appendChild(el);
    document.body.classList.add("sa-cookie-banner-open");

    el.querySelector("#sa-cookie-accept-all").addEventListener("click", function () {
      saveConsent({ analytics: true, functional: true }, "accept_all");
      hideBanner();
      mountManageFab();
    });
    el.querySelector("#sa-cookie-reject").addEventListener("click", function () {
      saveConsent({ analytics: false, functional: false }, "reject");
      hideBanner();
      mountManageFab();
    });
    el.querySelector("#sa-cookie-customize").addEventListener("click", function () {
      mountPreferences();
    });
  }

  function mountManageFab() {
    if (document.getElementById("sa-cookie-manage-fab")) return;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.id = "sa-cookie-manage-fab";
    btn.className = "sa-cookie-manage-fab";
    btn.textContent = "Cookies";
    btn.setAttribute("aria-label", "Manage cookie preferences");
    btn.addEventListener("click", function () {
      mountPreferences();
    });
    document.body.appendChild(btn);
  }

  function wireManageLinks() {
    document.querySelectorAll("[data-sa-manage-cookies]").forEach(function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault();
        mountPreferences();
      });
    });
  }

  async function init() {
    await loadConfig();
    consent = loadStored();
    wireManageLinks();

    if (needsBanner()) {
      mountBanner();
    } else {
      mountManageFab();
    }
    dispatchReady();
  }

  global.SourceACookieConsent = {
    VERSION: VERSION,
    has: has,
    getConsent: function () {
      return consent;
    },
    openPreferences: mountPreferences,
    get ready() {
      return ready;
    },
    whenReady: function () {
      return new Promise(function (resolve) {
        if (ready) return resolve(consent);
        global.addEventListener("sourcea:consent-ready", function () {
          resolve(consent);
        }, { once: true });
      });
    },
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : globalThis);

/**
 * SourceA site pulse — page analytics + stranger feedback (bug / confused / ideas).
 */
(function () {
  "use strict";

  const CONFIG_URL = "/sourcea/data/sourcea-site-pulse-config-v1.json";
  const DEFAULT_WORKER = "https://sourcea-site-pulse-v1.sina-kazemnezhad-ca.workers.dev";
  const SESSION_KEY = "sourcea-pulse-session-v1";

  let config = {};
  let queue = [];
  let flushTimer = null;

  function apiBase() {
    const host = window.location.hostname;
    if (host === "127.0.0.1" || host === "localhost") {
      return config.api_worker_url || DEFAULT_WORKER;
    }
    return config.api_worker_url || DEFAULT_WORKER;
  }

  function sessionId() {
    try {
      let id = sessionStorage.getItem(SESSION_KEY);
      if (!id) {
        id = "s-" + Math.random().toString(36).slice(2, 12);
        sessionStorage.setItem(SESSION_KEY, id);
      }
      return id;
    } catch {
      return "s-anon";
    }
  }

  function pageMeta() {
    return {
      page: document.body.dataset.saPage || document.title || "",
      path: window.location.pathname + window.location.search,
      url: window.location.href,
      session_id: sessionId(),
    };
  }

  async function loadConfig() {
    try {
      const r = await fetch(CONFIG_URL, { cache: "no-store" });
      if (r.ok) config = await r.json();
    } catch {
      config = {};
    }
  }

  function track(event, meta) {
    if (window.SourceACookieConsent && !window.SourceACookieConsent.has("analytics")) return;
    queue.push({
      event,
      at: new Date().toISOString(),
      ...pageMeta(),
      ...(meta || {}),
    });
    if (!flushTimer) {
      flushTimer = setTimeout(flushEvents, 1200);
    }
  }

  async function flushEvents() {
    flushTimer = null;
    if (!queue.length) return;
    const batch = queue.splice(0, 25);
    try {
      await fetch(apiBase() + (config.event_path || "/api/site/event/v1"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ events: batch }),
        keepalive: true,
      });
    } catch {
      queue.unshift(...batch);
    }
  }

  async function submitFeedback({ type, message, email }) {
    track("feedback_submit", { type });
    const r = await fetch(apiBase() + (config.feedback_path || "/api/site/feedback/v1"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type: type || "feedback",
        message: String(message || "").trim(),
        email: email || undefined,
        ...pageMeta(),
      }),
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok || !data.ok) {
      throw new Error((data.errors || []).join(", ") || "feedback_failed");
    }
    return data;
  }

  let clicksBound = false;
  function bindTrackClicks() {
    if (clicksBound) return;
    clicksBound = true;
    document.addEventListener(
      "click",
      function (e) {
        const el = e.target.closest("[data-sa-track]");
        if (!el) return;
        track("click", {
          label: el.getAttribute("data-sa-track") || el.textContent?.trim().slice(0, 80),
          href: el.getAttribute("href") || undefined,
        });
      },
      true
    );
  }

  function mountFeedbackFab() {
    if (document.getElementById("sa-pulse-feedback-fab")) return;
    if (window.SourceACookieConsent && !window.SourceACookieConsent.has("functional")) return;

    const fab = document.createElement("button");
    fab.type = "button";
    fab.id = "sa-pulse-feedback-fab";
    fab.className = "sa-pulse-feedback-fab";
    fab.setAttribute("aria-label", "Report a bug or give feedback");
    fab.innerHTML = "<span aria-hidden=\"true\">💬</span><span class=\"sa-pulse-feedback-label\">Feedback</span>";

    const backdrop = document.createElement("div");
    backdrop.className = "sa-pulse-feedback-backdrop";
    backdrop.id = "sa-pulse-feedback-backdrop";
    backdrop.hidden = true;

    const panel = document.createElement("div");
    panel.className = "sa-pulse-feedback-panel";
    panel.id = "sa-pulse-feedback-panel";
    panel.hidden = true;
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Site feedback");
    panel.innerHTML = `
      <form class="sa-pulse-feedback-form" id="sa-pulse-feedback-form" novalidate>
      <header class="sa-pulse-feedback-head">
        <strong>Help us improve</strong>
        <button type="button" class="sa-pulse-feedback-close" aria-label="Close">×</button>
      </header>
      <p class="sa-pulse-feedback-lead">Strangers welcome — tell us what's broken, confusing, or missing.</p>
      <div class="sa-pulse-feedback-types" id="sa-pulse-feedback-types"></div>
      <label class="sa-pulse-feedback-field">
        <span>What happened?</span>
        <textarea id="sa-pulse-feedback-msg" name="message" rows="4" maxlength="4000" placeholder="e.g. Book button 404'd · pricing unclear · want live status" required></textarea>
      </label>
      <label class="sa-pulse-feedback-field">
        <span>Email (optional)</span>
        <input type="email" id="sa-pulse-feedback-email" name="email" placeholder="you@company.com" autocomplete="email" />
      </label>
      <p class="sa-pulse-feedback-error" id="sa-pulse-feedback-error" hidden role="alert"></p>
      <button type="submit" class="ar-btn ar-btn-primary sa-btn-glow" id="sa-pulse-feedback-send">Send feedback →</button>
      <p class="sa-pulse-feedback-done" id="sa-pulse-feedback-done" hidden></p>
      </form>
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(panel);
    document.body.appendChild(fab);

    const typesWrap = panel.querySelector("#sa-pulse-feedback-types");
    const types = config.feedback_types || [
      { id: "bug", label: "Something is broken" },
      { id: "confused", label: "This confused me" },
      { id: "idea", label: "You should add…" },
    ];
    let selectedType = types[0]?.id || "feedback";
    types.forEach(function (t) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "sa-pulse-type-chip" + (t.id === selectedType ? " is-active" : "");
      b.textContent = t.label;
      b.dataset.type = t.id;
      b.addEventListener("click", function () {
        selectedType = t.id;
        typesWrap.querySelectorAll(".sa-pulse-type-chip").forEach(function (c) {
          c.classList.toggle("is-active", c.dataset.type === selectedType);
        });
      });
      typesWrap.appendChild(b);
    });

    function toggle(open) {
      const on = typeof open === "boolean" ? open : panel.hidden;
      panel.hidden = !on;
      backdrop.hidden = !on;
      fab.setAttribute("aria-expanded", String(on));
      document.body.classList.toggle("sa-pulse-feedback-open", on);
      if (on) {
        track("feedback_open");
        panel.querySelector("#sa-pulse-feedback-msg")?.focus();
      }
    }

    fab.addEventListener("click", function () {
      toggle(true);
    });
    backdrop.addEventListener("click", function () {
      toggle(false);
    });
    panel.querySelector(".sa-pulse-feedback-close").addEventListener("click", function () {
      toggle(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !panel.hidden) toggle(false);
    });

    panel.querySelector("#sa-pulse-feedback-form").addEventListener("submit", async function (e) {
      e.preventDefault();
      e.stopPropagation();
      const errEl = panel.querySelector("#sa-pulse-feedback-error");
      const doneEl = panel.querySelector("#sa-pulse-feedback-done");
      const btn = panel.querySelector("#sa-pulse-feedback-send");
      const msg = panel.querySelector("#sa-pulse-feedback-msg").value.trim();
      const email = panel.querySelector("#sa-pulse-feedback-email").value.trim();
      errEl.hidden = true;
      doneEl.hidden = true;
      if (msg.length < 4) {
        errEl.textContent = "Please describe the issue in a few words.";
        errEl.hidden = false;
        return;
      }
      btn.disabled = true;
      btn.textContent = "Sending…";
      try {
        const data = await submitFeedback({ type: selectedType, message: msg, email });
        doneEl.hidden = false;
        doneEl.textContent =
          (data.end_screen || "Thanks — we read every report.") +
          (data.feedback_id ? " Reference: " + data.feedback_id + "." : "");
        panel.querySelector("#sa-pulse-feedback-msg").value = "";
        btn.hidden = true;
        track("feedback_sent", { feedback_id: data.feedback_id });
      } catch {
        errEl.textContent =
          "Could not send — copy your note and email hello@sourcea.app with this page URL.";
        errEl.hidden = false;
      } finally {
        btn.disabled = false;
        btn.textContent = "Send feedback →";
      }
    });

    panel.addEventListener("click", function (e) {
      e.stopPropagation();
    });
  }

  async function init() {
    if (window.SourceACookieConsent && window.SourceACookieConsent.whenReady) {
      await window.SourceACookieConsent.whenReady();
    }
    await loadConfig();
    if (!window.SourceACookieConsent || window.SourceACookieConsent.has("analytics")) {
      track("pageview");
      bindTrackClicks();
    }
    mountFeedbackFab();
    window.addEventListener("sourcea:consent-changed", function () {
      if (window.SourceACookieConsent.has("analytics")) {
        track("pageview");
        bindTrackClicks();
      }
      if (window.SourceACookieConsent.has("functional")) {
        mountFeedbackFab();
      }
    });
    window.addEventListener("pagehide", flushEvents);
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden") flushEvents();
    });
  }

  window.SourceAPulse = {
    track,
    submitFeedback,
    flushEvents,
    init,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

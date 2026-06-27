/**
 * SourceA pulse — public stats strip (status page · no founder key).
 */
(function () {
  "use strict";

  const CONFIG_URL = "/sourcea/data/sourcea-site-pulse-config-v1.json";
  const DEFAULT_WORKER = "https://sourcea-site-pulse-v1.sina-kazemnezhad-ca.workers.dev";

  async function apiBase() {
    try {
      const r = await fetch(CONFIG_URL, { cache: "no-store" });
      if (r.ok) {
        const cfg = await r.json();
        if (cfg.api_worker_url) return cfg.api_worker_url;
      }
    } catch {
      /* ignore */
    }
    return DEFAULT_WORKER;
  }

  function fmt(n) {
    const x = Number(n) || 0;
    return x.toLocaleString("en-US");
  }

  function renderTopEvents(el, events) {
    if (!el) return;
    el.innerHTML = "";
    if (!events?.length) {
      el.textContent = "No interaction events yet today.";
      return;
    }
    const ul = document.createElement("ul");
    ul.className = "sa-pulse-event-list";
    events.slice(0, 6).forEach(function (row) {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${row.name}</strong> <span>${fmt(row.count)}</span>`;
      ul.appendChild(li);
    });
    el.appendChild(ul);
  }

  async function init() {
    const root = document.getElementById("sa-pulse-public");
    if (!root) return;
    const pv = root.querySelector("[data-pulse-pageviews]");
    const fb = root.querySelector("[data-pulse-feedback]");
    const ev = root.querySelector("[data-pulse-events]");
    const note = root.querySelector("[data-pulse-note]");
    try {
      const base = await apiBase();
      const r = await fetch(`${base}/api/site/stats/v1`, { cache: "no-store" });
      const data = await r.json();
      if (!data.ok) throw new Error("stats_failed");
      const s = data.stats || {};
      if (pv) pv.textContent = fmt(s.pageviews);
      if (fb) fb.textContent = fmt(s.feedback_count);
      renderTopEvents(ev, s.top_events);
      if (note) {
        note.textContent = s.updated_at
          ? `Updated ${s.updated_at} UTC · day ${s.day || "today"}`
          : "Live from Site Pulse worker";
      }
    } catch {
      if (note) note.textContent = "Pulse stats unavailable — worker or KV not wired yet.";
      if (pv) pv.textContent = "—";
      if (fb) fb.textContent = "—";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

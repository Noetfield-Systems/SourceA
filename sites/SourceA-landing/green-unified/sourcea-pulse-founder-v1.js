/**
 * SourceA pulse — founder dashboard (stats + feedback inbox).
 * Requires FOUNDER_PULSE_KEY — stored in sessionStorage after unlock.
 */
(function () {
  "use strict";

  const CONFIG_URL = "/sourcea/data/sourcea-site-pulse-config-v1.json";
  const DEFAULT_WORKER = "https://sourcea-site-pulse-v1.sina-kazemnezhad-ca.workers.dev";
  const KEY_STORAGE = "sourcea-pulse-founder-key-v1";

  let apiWorker = DEFAULT_WORKER;

  async function loadConfig() {
    try {
      const r = await fetch(CONFIG_URL, { cache: "no-store" });
      if (r.ok) {
        const cfg = await r.json();
        if (cfg.api_worker_url) apiWorker = cfg.api_worker_url;
      }
    } catch {
      /* ignore */
    }
  }

  function fmt(n) {
    return (Number(n) || 0).toLocaleString("en-US");
  }

  function typeClass(type) {
    return `sa-pulse-type-${String(type || "feedback").replace(/[^a-z0-9_-]/gi, "")}`;
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = String(s || "");
    return d.innerHTML;
  }

  async function fetchDashboard(key) {
    const r = await fetch(`${apiWorker}/api/site/dashboard/v1?days=7&limit=50`, {
      headers: { "X-SourceA-Pulse-Key": key },
      cache: "no-store",
    });
    const data = await r.json().catch(() => ({}));
    return { status: r.status, data };
  }

  function renderDashboard(root, data) {
    const today = data.today || {};
    const rollup = data.rollup || {};
    root.querySelector("[data-dash-pv-today]").textContent = fmt(today.pageviews);
    root.querySelector("[data-dash-fb-today]").textContent = fmt(today.feedback_count);
    root.querySelector("[data-dash-pv-week]").textContent = fmt(rollup.pageviews);
    root.querySelector("[data-dash-fb-week]").textContent = fmt(rollup.feedback_count);

    const eventsEl = root.querySelector("[data-dash-top-events]");
    eventsEl.innerHTML = "";
    (today.top_events || []).slice(0, 8).forEach(function (row) {
      const li = document.createElement("li");
      li.innerHTML = `<span>${esc(row.name)}</span><strong>${fmt(row.count)}</strong>`;
      eventsEl.appendChild(li);
    });
    if (!eventsEl.children.length) {
      eventsEl.innerHTML = "<li><span>No events yet today</span></li>";
    }

    const pagesEl = root.querySelector("[data-dash-top-pages]");
    pagesEl.innerHTML = "";
    (today.top_pages || []).slice(0, 8).forEach(function (row) {
      const li = document.createElement("li");
      const path = String(row.path || "").replace(/_/g, "/");
      li.innerHTML = `<span>${esc(path)}</span><strong>${fmt(row.count)}</strong>`;
      pagesEl.appendChild(li);
    });
    if (!pagesEl.children.length) {
      pagesEl.innerHTML = "<li><span>No page paths yet today</span></li>";
    }

    const tbody = root.querySelector("[data-dash-inbox]");
    tbody.innerHTML = "";
    (data.inbox || []).forEach(function (row) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><span class="sa-pulse-type-chip ${typeClass(row.type)}">${esc(row.type)}</span></td>
        <td>${esc(row.message)}</td>
        <td>${esc(row.page || "—")}</td>
        <td>${row.email ? `<a href="mailto:${esc(row.email)}">${esc(row.email)}</a>` : "—"}</td>
        <td><time datetime="${esc(row.at)}">${esc((row.at || "").replace("T", " ").replace("Z", " UTC"))}</time></td>
      `;
      tbody.appendChild(tr);
    });
    if (!data.inbox?.length) {
      tbody.innerHTML = '<tr><td colspan="5">No stranger feedback yet — share the site and watch this inbox.</td></tr>';
    }

    root.querySelector("[data-dash-updated]").textContent = `Synced ${data.at || "—"}`;
    root.hidden = false;
    document.getElementById("sa-pulse-unlock")?.setAttribute("hidden", "");
  }

  async function init() {
    const app = document.getElementById("sa-pulse-founder-app");
    const dash = document.getElementById("sa-pulse-founder-dash");
    const unlock = document.getElementById("sa-pulse-unlock");
    if (!app || !dash || !unlock) return;

    function showUnlockPanel() {
      dash.hidden = true;
      unlock.hidden = false;
    }

    async function refresh(key) {
      const errEl = dash.querySelector("[data-dash-error]");
      if (errEl) {
        errEl.hidden = true;
        errEl.textContent = "";
      }
      const { status, data } = await fetchDashboard(key);
      if (status === 401 || !data.ok) {
        try {
          sessionStorage.removeItem(KEY_STORAGE);
        } catch {
          /* ignore */
        }
        showUnlockPanel();
        if (errEl) {
          errEl.textContent =
            status === 401
              ? "Wrong key — or FOUNDER_PULSE_KEY not set on the worker yet. Run wrangler secret put FOUNDER_PULSE_KEY first."
              : "Dashboard unavailable — check worker logs.";
          errEl.hidden = false;
        }
        return;
      }
      renderDashboard(dash, data);
    }

    await loadConfig();

    const form = unlock.querySelector("form");
    const input = unlock.querySelector("#sa-pulse-key-input");
    const stored = (function () {
      try {
        return sessionStorage.getItem(KEY_STORAGE) || "";
      } catch {
        return "";
      }
    })();

    if (stored) {
      unlock.hidden = true;
      await refresh(stored);
    }

    form?.addEventListener("submit", async function (e) {
      e.preventDefault();
      const key = (input?.value || "").trim();
      if (!key) return;
      try {
        sessionStorage.setItem(KEY_STORAGE, key);
      } catch {
        /* ignore */
      }
      unlock.hidden = true;
      await refresh(key);
    });

    app.querySelector("[data-dash-refresh]")?.addEventListener("click", function () {
      const key = sessionStorage.getItem(KEY_STORAGE) || "";
      if (key) refresh(key);
    });

    app.querySelector("[data-dash-lock]")?.addEventListener("click", function () {
      try {
        sessionStorage.removeItem(KEY_STORAGE);
      } catch {
        /* ignore */
      }
      dash.hidden = true;
      unlock.hidden = false;
      if (input) input.value = "";
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

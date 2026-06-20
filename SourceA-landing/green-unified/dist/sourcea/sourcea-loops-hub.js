/**
 * Factory loops hub — catalog · lane filters · live factory metrics.
 * Patterns: modular capability rows (enterprise iPaaS) · governance badges · live disk truth.
 */
(function () {
  const CATALOG_URL = "/sourcea/data/loops-catalog.json";
  const LIVE_URL = "/sourcea/data/factory-live.json";

  const laneLabels = { revenue: "Revenue", ops: "Ops", proof: "Proof" };
  const tierLabels = { starter: "Starter", core: "Core", growth: "Growth" };

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function badgeClass(b) {
    const map = { pass: "pass", block: "block", save: "save", live: "pass", boot: "block", replay: "save" };
    return map[b] || "save";
  }

  function liveMetric(loop, live) {
    const m = live?.metrics || {};
    const c = live?.pipeline?.counts || {};
    switch (loop.id) {
      case "outreach":
        return `${m.sent || 0} sent · ${c.proof_viewed || 0} proof viewed`;
      case "eval-booking":
        return `${c.eval_scheduled || 0} eval scheduled`;
      case "ops-monitor":
        return `${live?.boot?.block_count || 0} BLOCK on boot`;
      case "session-gate":
        return `boot ${live?.boot?.verdict || "—"}`;
      case "research":
        return "SAVE · one file law";
      case "proof-export":
        return `${live?.boot?.pass_count || 0}/${(live?.boot?.checks || []).length} checks`;
      default:
        return loop.badge_label;
    }
  }

  function cardHtml(loop, live) {
    const steps = (loop.steps || [])
      .map((s) => `<li>${esc(s)}</li>`)
      .join("");
    return `
      <a class="sa-loop-hub-card sa-loop-pro-card sa-card-lift" href="${esc(loop.href)}" data-loop-lane="${esc(loop.lane)}" data-loop-tier="${esc(loop.tier)}">
        <div class="sa-loop-pro-head">
          <span class="sa-loop-pro-icon" aria-hidden="true">${esc(loop.icon)}</span>
          <span class="sa-loop-badge ${badgeClass(loop.badge)}">${esc(loop.badge_label)}</span>
        </div>
        <span class="sa-loop-pro-tier">${esc(tierLabels[loop.tier] || loop.tier)} · ${esc(laneLabels[loop.lane] || loop.lane)}</span>
        <h3>${esc(loop.title)}</h3>
        <p>${esc(loop.summary)}</p>
        <ol class="sa-loop-pro-steps">${steps}</ol>
        <div class="sa-loop-pro-foot">
          <em>${esc(loop.tagline)}</em>
          <span class="sa-loop-pro-live" data-loop-metric="${esc(loop.id)}">${esc(liveMetric(loop, live))}</span>
        </div>
      </a>`;
  }

  function renderStrip(live) {
    const el = document.getElementById("sa-loops-live-strip");
    if (!el || !live) return;
    const pipe = live.pipeline || {};
    el.innerHTML = `
      <div class="sa-loops-strip-metric"><strong>${live.metrics?.active || 0}</strong><span>Active deals</span></div>
      <div class="sa-loops-strip-metric"><strong>${pipe.counts?.eval_scheduled || 0}</strong><span>Evals booked</span></div>
      <div class="sa-loops-strip-metric"><strong>${live.boot?.verdict || "—"}</strong><span>Factory boot</span></div>
      <div class="sa-loops-strip-metric sa-loops-strip-wide"><span>${esc(live.factory_now_line || pipe.headline || "")}</span></div>`;
  }

  function bindFilters() {
    const tabs = document.querySelectorAll("[data-loops-filter]");
    const cards = document.querySelectorAll(".sa-loop-pro-card");
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const lane = tab.dataset.loopsFilter;
        tabs.forEach((t) => t.classList.toggle("is-active", t === tab));
        cards.forEach((c) => {
          const show = lane === "all" || c.dataset.loopLane === lane;
          c.classList.toggle("is-hidden", !show);
        });
      });
    });
  }

  async function init() {
    const grid = document.getElementById("sa-loops-catalog");
    if (!grid) return;

    let catalog = { loops: [] };
    let live = null;
    try {
      const [catRes, liveRes] = await Promise.all([
        fetch(CATALOG_URL, { cache: "no-store" }),
        fetch(LIVE_URL, { cache: "no-store" }),
      ]);
      if (catRes.ok) catalog = await catRes.json();
      if (liveRes.ok) live = await liveRes.json();
    } catch (_) {
      /* static fallback stays */
    }

    if (catalog.loops?.length) {
      grid.innerHTML = catalog.loops.map((loop) => cardHtml(loop, live)).join("");
      bindFilters();
    }
    renderStrip(live);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

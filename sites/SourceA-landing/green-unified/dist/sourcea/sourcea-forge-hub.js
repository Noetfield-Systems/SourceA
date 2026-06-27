/**
 * Prompt Forge hub — catalog cards from forge-catalog.json
 */
(function () {
  const CATALOG_URL = "/sourcea/data/forge-catalog.json";

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function badgeClass(b) {
    const map = { pass: "pass", block: "block", save: "save", live: "pass" };
    return map[b] || "save";
  }

  function cardHtml(page) {
    const steps = (page.steps || []).map((s) => `<li>${esc(s)}</li>`).join("");
    return `
      <a class="sa-loop-hub-card sa-loop-pro-card sa-card-lift" href="${esc(page.href)}">
        <div class="sa-loop-pro-head">
          <span class="sa-loop-pro-icon" aria-hidden="true">${esc(page.icon)}</span>
          <span class="sa-loop-badge ${badgeClass(page.badge)}">${esc(page.badge_label)}</span>
        </div>
        <h3>${esc(page.title)}</h3>
        <p>${esc(page.summary)}</p>
        <ol class="sa-loop-pro-steps">${steps}</ol>
        <div class="sa-loop-pro-foot"><em>${esc(page.tagline)}</em></div>
      </a>`;
  }

  async function init() {
    const grid = document.getElementById("sa-forge-catalog");
    if (!grid) return;
    try {
      const res = await fetch(CATALOG_URL, { cache: "no-store" });
      if (!res.ok) return;
      const catalog = await res.json();
      if (catalog.pages?.length) {
        grid.innerHTML = catalog.pages.map(cardHtml).join("");
      }
    } catch (_) {
      /* static fallback */
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

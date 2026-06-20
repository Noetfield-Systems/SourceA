/**
 * Noetfield Factory catalog hub — static JSON + deploy CTAs.
 */
(function () {
  const CATALOG_URL = "/sourcea/data/factories-catalog.json";

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function tierLabel(t) {
    const map = {
      engines: "Factory App",
      policy_packs: "Policy Pack",
      sandbox: "Sandbox",
    };
    return map[t] || t;
  }

  function cardHtml(f) {
    const hero = f.hero ? '<span class="sa-loop-badge pass">HERO</span>' : "";
    const fee = f.maintenance_fee_usd ? `$${f.maintenance_fee_usd}/mo` : "Free";
    return `
      <a class="sa-loop-hub-card sa-loop-pro-card sa-card-lift" href="${esc(f.href)}" data-factory-tier="${esc(f.tier)}">
        ${hero}
        <span class="sa-loop-badge save">${esc(tierLabel(f.tier))}</span>
        <h3>${esc(f.name)}</h3>
        <p>${esc(f.tagline)}</p>
        <em>${esc(f.operational_nodes)} nodes · ${esc(f.guaranteed_output)}</em>
        <p class="sa-metric-note">${esc(fee)} · ${esc(f.install_label || "Deploy")}</p>
      </a>`;
  }

  function renderCatalog(data) {
    const grid = document.getElementById("sa-factories-catalog");
    if (!grid) return;
    const factories = data.factories || [];
    grid.innerHTML = factories.map(cardHtml).join("");
  }

  function bindFilters() {
    const buttons = document.querySelectorAll("[data-factories-filter]");
    const cards = document.querySelectorAll("[data-factory-tier]");
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
        const tier = btn.getAttribute("data-factories-filter");
        cards.forEach((card) => {
          const show = tier === "all" || card.getAttribute("data-factory-tier") === tier;
          card.style.display = show ? "" : "none";
        });
      });
    });
  }

  function runSandboxDemo() {
    const box = document.getElementById("sa-sandbox-demo");
    const out = document.getElementById("sa-demo-output");
    if (!box || !out) return;
    const kind = box.getAttribute("data-kind");
    if (kind !== "sandbox") return;
    box.style.display = "block";
    const demo = {
      job_id: "demo-" + Date.now(),
      policy_passed: true,
      tier_achieved: "BRONZE",
      kernel_hash: "mock-demo",
      summary: "30s mock Certainty Report — upgrade for real MicroVM execution.",
    };
    let i = 0;
    const lines = ["Waking mock factory…", "Policy check PASS", "Simulating 76-node graph…", JSON.stringify(demo, null, 2)];
    const timer = setInterval(() => {
      out.textContent = lines.slice(0, i + 1).join("\n");
      i += 1;
      if (i >= lines.length) clearInterval(timer);
    }, 800);
  }

  fetch(CATALOG_URL)
    .then((r) => r.json())
    .then((data) => {
      renderCatalog(data);
      bindFilters();
      runSandboxDemo();
    })
    .catch(() => {
      const grid = document.getElementById("sa-factories-catalog");
      if (grid) grid.innerHTML = "<p>Catalog unavailable — run build-landing-factories-catalog-v1.py</p>";
    });
})();

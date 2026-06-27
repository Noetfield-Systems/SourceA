/**
 * Hydrate product grids from sourcea-products-catalog-v1.json
 * Modes: full (platform) · case-studies (2 cards) · compact (footer strip)
 */
(function () {
  "use strict";

  const CATALOG_URL = "/sourcea/data/sourcea-products-catalog-v1.json";

  const KIND_LABEL = {
    case_study: "Case study",
    platform: "Platform",
    service: "Service",
    eval: "Eval",
  };

  const FALLBACK_CASE_STUDIES = [
    {
      id: "pureflow-case-study",
      rank: 1,
      kind: "case_study",
      title: "PureFlow",
      subtitle: "Case study #1 · Local trades acquisition",
      buyer: "Pool & spa operators · local service businesses",
      proof: "Live site + visit reports · 48-hour acquisition path",
      url: "/sourcea/case-studies/pureflow",
      live_url: "https://pureflow.sourcea.app/",
    },
    {
      id: "agentgo-case-study",
      rank: 2,
      kind: "case_study",
      title: "AgentGo",
      subtitle: "Case study #2 · Factory-scale GEO surface",
      buyer: "SaaS & marketing leaders · agency CTOs",
      proof: "1,259 HTML pages · dual deploy · Wil L3 separation",
      url: "/sourcea/case-studies/agentgo",
      live_url: null,
    },
  ];

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function cardHtml(p) {
    const kind = KIND_LABEL[p.kind] || p.kind || "Product";
    const price = p.price_band ? `<span class="sa-product-price">${escapeHtml(p.price_band)}</span>` : "";
    const live =
      p.live_url
        ? `<p class="sa-metric-note"><a href="${escapeHtml(p.live_url)}" target="_blank" rel="noopener">Live demo →</a></p>`
        : "";
    const ext = /^https?:/.test(p.url || "") ? ' target="_blank" rel="noopener"' : "";
    return `<article class="sa-product-card sa-card-lift${p.rank <= 2 ? " is-featured" : ""}" data-product-id="${escapeHtml(p.id)}">
      <p class="sa-product-kind">${escapeHtml(kind)} · #${p.rank}</p>
      <h3><a href="${escapeHtml(p.url)}"${ext}>${escapeHtml(p.title)}</a></h3>
      <p class="sa-product-sub">${escapeHtml(p.subtitle)}</p>
      <p><strong>Buyer:</strong> ${escapeHtml(p.buyer)}</p>
      <p class="sa-product-proof">${escapeHtml(p.proof)}</p>
      ${price}
      ${live}
      <a class="sa-product-cta" href="${escapeHtml(p.url)}"${ext}>Explore →</a>
    </article>`;
  }

  function compactHtml(p) {
    return `<a class="sa-product-compact" href="${escapeHtml(p.url)}">${escapeHtml(p.title)} · ${escapeHtml(p.subtitle)}</a>`;
  }

  function pickProducts(catalog, mode) {
    const all = (catalog.products || []).slice().sort((a, b) => (a.rank || 99) - (b.rank || 99));
    if (mode === "case-studies") {
      const cs = catalog.case_studies || all.filter((p) => p.kind === "case_study");
      return cs.length ? cs : FALLBACK_CASE_STUDIES;
    }
    if (mode === "compact") {
      return (catalog.case_studies || FALLBACK_CASE_STUDIES).slice(0, 2);
    }
    return all.length ? all : FALLBACK_CASE_STUDIES;
  }

  async function loadCatalog() {
    try {
      const r = await fetch(CATALOG_URL, { cache: "no-store" });
      if (r.ok) return await r.json();
    } catch (_) {
      /* fallback */
    }
    return { products: [], case_studies: FALLBACK_CASE_STUDIES };
  }

  async function mountRoot(root) {
    if (!root || root.dataset.mounted === "1") return;
    const mode = root.dataset.mode || "full";
    const catalog = await loadCatalog();
    const products = pickProducts(catalog, mode);
    if (!products.length) return;

    root.dataset.mounted = "1";
    if (mode === "compact") {
      root.innerHTML = products.map(compactHtml).join("");
    } else {
      root.innerHTML = products.map(cardHtml).join("");
    }

    const note = document.getElementById("sa-products-note");
    if (note) {
      if (catalog.generated_at) {
        note.textContent = `Catalog synced ${catalog.generated_at.slice(0, 10)} · ${products.length} shown`;
      } else if (mode === "case-studies") {
        note.textContent = "PureFlow (#1 trades) · AgentGo (#2 factory scale) · same controlled spine";
      }
    }
  }

  async function mountAll() {
    const roots = document.querySelectorAll("#sa-products-grid, [data-sa-products-grid]");
    for (const root of roots) {
      await mountRoot(root);
    }
  }

  document.addEventListener("DOMContentLoaded", mountAll);
})();

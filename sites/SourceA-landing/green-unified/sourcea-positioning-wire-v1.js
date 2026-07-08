/**
 * Positioning SSOT wire — hero copy, taxonomy, CTAs from sourcea-positioning-v1.json.
 */
(function () {
  const URL = "/sourcea/data/sourcea-positioning-v1.json";

  function setText(sel, text) {
    if (!text) return;
    document.querySelectorAll(sel).forEach((el) => {
      el.textContent = text;
    });
  }

  function setCta(sel, href, label) {
    document.querySelectorAll(sel).forEach((el) => {
      if (href) el.setAttribute("href", href);
      if (label) {
        const arrow = el.querySelector(".ar-btn-arrow, .ar-btn-arrow-dark");
        el.childNodes.forEach((n) => {
          if (n.nodeType === Node.TEXT_NODE) el.removeChild(n);
        });
        const text = document.createTextNode(label);
        if (arrow) el.insertBefore(text, arrow);
        else el.appendChild(text);
      }
    });
  }

  function apply(pos) {
    const hero = pos.hero || {};
    setText("[data-sa-positioning='kicker']", hero.kicker);
    setText("[data-sa-positioning='category']", hero.category_tag);
    setText("[data-sa-positioning='h1-line1']", hero.h1_line1);
    setText("[data-sa-positioning='h1-accent']", hero.h1_accent);

    const lead = document.querySelector("[data-sa-positioning='lead']");
    if (lead && hero.lead) {
      lead.innerHTML = hero.lead.replace(/sourcea-boot/g, "<strong>sourcea-boot</strong>");
    }

    document.querySelectorAll("[data-sa-taxonomy]").forEach((box) => {
      if (hero.taxonomy_html) box.innerHTML = hero.taxonomy_html;
    });

    setCta("[data-sa-primary-cta]", pos.primary_cta, pos.primary_cta_label);
    setCta("[data-sa-secondary-cta]", pos.secondary_cta, pos.secondary_cta_label);
    setCta("[data-sa-tertiary-cta]", pos.tertiary_cta, pos.tertiary_cta_label);
    setCta("[data-sa-intake-cta]", pos.intake_cta, pos.intake_cta_label);
    setCta("[data-sa-book-fallback]", pos.escalation_cta, pos.escalation_cta_label);

    document.querySelectorAll("[data-sa-legal-entity]").forEach((el) => {
      if (pos.legal_entity) el.textContent = pos.legal_entity;
    });

    const deny = pos.hero_denylist || [];
    const heroBand = document.querySelector(".sa-root-hero, .sa-sub-hero, #top");
    if (heroBand && deny.length) {
      const text = heroBand.textContent || "";
      deny.forEach((phrase) => {
        if (phrase && text.toLowerCase().includes(String(phrase).toLowerCase())) {
          console.warn("[positioning-wire] hero denylist hit:", phrase);
        }
      });
    }
  }

  async function init() {
    try {
      const res = await fetch(URL, { cache: "no-store" });
      if (!res.ok) return;
      apply(await res.json());
    } catch (_) {
      /* static HTML fallback */
    }
  }

  window.SourceAPositioningWire = { init, apply };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

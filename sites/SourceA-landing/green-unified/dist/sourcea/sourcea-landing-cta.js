/* sourcea-landing-cta:v1 — proof hero + booking fallback from disk SSOT */
(function () {
  var DEFAULTS = {
    proof_url: "/sourcea/proof/live",
    proof_label: "See live receipt",
    booking_url: "https://cal.com/sourcea/proof-demo",
    booking_label: "Talk to a human",
    sandbox_url: "/sandbox",
    sandbox_label: "Submit a bounded job",
  };

  function setBtnLabel(el, label) {
    if (!label || !el.classList.contains("ar-btn")) return;
    var arrow = el.querySelector(".ar-btn-arrow");
    el.textContent = label;
    if (arrow) el.appendChild(arrow);
  }

  function apply(cfg) {
    document.querySelectorAll("[data-sa-proof-cta]").forEach(function (el) {
      if (cfg.proof_url) el.setAttribute("href", cfg.proof_url);
      setBtnLabel(el, cfg.proof_label);
    });
    document.querySelectorAll("[data-sa-book-fallback], [data-sa-book-cta]").forEach(function (el) {
      if (cfg.booking_url) el.setAttribute("href", cfg.booking_url);
      setBtnLabel(el, cfg.booking_label);
    });
    document.querySelectorAll("[data-sa-sandbox-cta]").forEach(function (el) {
      if (cfg.sandbox_url) el.setAttribute("href", cfg.sandbox_url);
      if (cfg.sandbox_label && !el.querySelector(".ar-btn-arrow")) {
        el.textContent = cfg.sandbox_label;
      }
    });
  }

  function run() {
    fetch("/sourcea/data/sourcea-landing-cta-v1.json", { cache: "no-store" })
      .then(function (r) {
        return r.ok ? r.json() : DEFAULTS;
      })
      .catch(function () {
        return DEFAULTS;
      })
      .then(apply);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
})();

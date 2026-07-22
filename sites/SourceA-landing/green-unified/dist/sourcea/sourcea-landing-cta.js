/* sourcea-landing-cta:v1 — proof hero + booking fallback from disk SSOT */
(function () {
  var DEFAULTS = {
    proof_url: "/sourcea/proof/live.html",
    proof_label: "See live receipt",
    booking_url: "/start?source=cta-proof-escalation",
    booking_label: "Need proof-led escalation?",
    sandbox_url: "/sandbox",
    sandbox_label: "Submit a bounded job",
  };

  function setBtnLabel(el, label) {
    if (!label || !el.classList.contains("ar-btn")) return;
    var arrow = el.querySelector(".ar-btn-arrow");
    el.textContent = label;
    if (arrow) el.appendChild(arrow);
  }

  function hasProofIntentText(el) {
    return /(proof|receipt|live|verify|audit)/i.test((el.textContent || "").toLowerCase());
  }

  function parseMailtoSubject(href) {
    if (!href) return "";
    var marker = href.indexOf("?");
    if (marker === -1) return "";
    var params = href.slice(marker + 1).split("&");
    var i;
    for (i = 0; i < params.length; i++) {
      var part = params[i];
      if (part.toLowerCase().indexOf("subject=") !== 0) continue;
      var value = part.slice(8);
      try {
        return decodeURIComponent(value.replace(/\+/g, " "));
      } catch (error) {
        return value;
      }
    }
    return "";
  }

  function addQueryParam(baseUrl, key, value) {
    if (!value) return baseUrl;
    return (baseUrl.indexOf("?") === -1 ? "?" : "&") + encodeURIComponent(key) + "=" + encodeURIComponent(value);
  }

  function wireMailtoProofFallback(cfg) {
    var bookingTarget = cfg.booking_url || "/start?source=cta-proof-escalation";
    var proofTarget = cfg.proof_url || "/sourcea/proof/live.html";
    var mailtoAnchors = document.querySelectorAll('a[href^="mailto:hello@sourcea.app"]');
    for (var i = 0; i < mailtoAnchors.length; i++) {
      var anchor = mailtoAnchors[i];
      if (!anchor.classList.contains("ar-btn")) continue;
      var href = anchor.getAttribute("href") || "";
      var next = hasProofIntentText(anchor) ? proofTarget : bookingTarget;
      if (next !== proofTarget) {
        var subject = parseMailtoSubject(href);
        next += addQueryParam(next, "sourcea_mail_subject", subject);
      }
      anchor.setAttribute("href", next);
    }
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
    wireMailtoProofFallback(cfg);
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

/**
 * SourceA segment router — mounts 5-door lane picker on subpages from interact SSOT.
 */
(function () {
  "use strict";

  const CONFIG_URL = "/sourcea/data/sourcea-site-interact-v1.json";
  const SKIP_PAGES = new Set(["founder-home", "learn-onramp", "pulse-founder"]);

  function track(id) {
    if (window.SourceAPulse) window.SourceAPulse.track("segment_strip_click", { segment: id });
  }

  function hints(id) {
    const map = {
      startup: "48h MVP intake · scoped ship",
      "vc-proof": "Live factory receipt · audit-ready",
      beginner: "Quiz → receipt → Forge · 15 min",
      agency: "Case studies · client proof paths",
      cursor: "Forge Terminal · lives in your stack",
    };
    return map[id] || "";
  }

  function mount(segments) {
    if (!segments.length || document.querySelector(".sa-segment-grid")) return;

    const section = document.createElement("section");
    section.className = "ar-section ar-section-muted ar-reveal sa-segment-strip-section";
    section.setAttribute("aria-label", "Pick your lane");
    section.innerHTML =
      '<div class="ar-container ar-section-head ar-section-head-center">' +
      '<p class="ar-kicker">What brings you here?</p>' +
      "<h2>Pick your <span class=\"ar-hero-accent\">lane.</span></h2>" +
      '<p class="ar-section-copy">Self-serve paths — proof, intake, or learn-by-doing. No calendar required.</p>' +
      '<nav class="sa-segment-grid" aria-label="Audience segments"></nav></div>';

    const nav = section.querySelector(".sa-segment-grid");
    segments.forEach(function (seg) {
      const a = document.createElement("a");
      a.className = "sa-segment-card";
      a.href = seg.href;
      a.setAttribute("data-sa-track", seg.track || "segment_" + seg.id);
      a.innerHTML = seg.label + "<em>" + hints(seg.id) + "</em>";
      a.addEventListener("click", function () {
        track(seg.id);
      });
      nav.appendChild(a);
    });

    const anchor =
      document.querySelector("main .sa-cta-band") ||
      document.querySelector("main footer") ||
      document.querySelector(".sa-cta-band") ||
      document.querySelector("footer");
    if (!anchor || !anchor.parentNode) return;
    anchor.parentNode.insertBefore(section, anchor);
  }

  function run() {
    const page = document.body.getAttribute("data-sa-page") || "";
    if (SKIP_PAGES.has(page) || document.body.getAttribute("data-sa-no-segment") === "1") return;

    fetch(CONFIG_URL, { cache: "no-store" })
      .then(function (r) {
        return r.ok ? r.json() : null;
      })
      .then(function (cfg) {
        if (!cfg) return;
        mount(cfg.segments || cfg.guided_prompts || []);
      })
      .catch(function () {
        /* silent */
      });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
})();

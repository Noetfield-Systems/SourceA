/**
 * SourceA site UX — 2026 polish: reduced motion, back-to-top, focus helpers.
 */
(function () {
  "use strict";

  function applyReducedMotion() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      document.body.classList.add("sa-reduced-motion");
    }
  }

  function mountBackToTop() {
    if (document.getElementById("sa-back-to-top")) return;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.id = "sa-back-to-top";
    btn.className = "sa-back-to-top";
    btn.setAttribute("aria-label", "Back to top");
    btn.innerHTML = "↑";
    btn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: document.body.classList.contains("sa-reduced-motion") ? "auto" : "smooth" });
    });
    document.body.appendChild(btn);

    function onScroll() {
      const show = window.scrollY > 480;
      btn.classList.toggle("is-visible", show);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  function wireSkipEnhancements() {
    document.documentElement.style.scrollBehavior = document.body.classList.contains("sa-reduced-motion")
      ? "auto"
      : "smooth";
  }

  function init() {
    applyReducedMotion();
    wireSkipEnhancements();
    if (document.body.scrollHeight > window.innerHeight * 1.6) {
      mountBackToTop();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

/* sourcea-cta-gate:v1 — STAB-009 */
(function () {
  var VERIFIED = {"hello@sourcea.app": false, "contact@sourcea.app": false, "proof@sourcea.app": false, "forge@sourcea.app": false};
  var FALLBACK = {"label": "Run a free proof", "href": "/sourcea/sandbox"};
  var MAILTO = /^mailto:([^?]+)/i;

  function gate(el) {
    var href = el.getAttribute("href") || "";
    var m = href.match(MAILTO);
    if (!m) return;
    var addr = m[1].toLowerCase();
    if (VERIFIED[addr]) return;
    el.setAttribute("data-sa-cta-gated", "1");
    el.setAttribute("data-sa-original-href", href);
    if (FALLBACK.href) {
      el.setAttribute("href", FALLBACK.href);
      var label = FALLBACK.label || "Start free sandbox";
      if (el.textContent && el.textContent.indexOf("@") >= 0) el.textContent = label;
    } else {
      el.setAttribute("href", "#");
      el.setAttribute("aria-disabled", "true");
      el.classList.add("sa-cta-gated");
    }
    el.title = "Email inbox pending — use sandbox or intake form";
  }

  function run() {
    document.querySelectorAll('a[href^="mailto:"]').forEach(gate);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
})();

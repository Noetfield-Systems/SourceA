(function () {
  "use strict";

  var LINKS = {};
  var CHECKOUT_LIVE = false;

  function loadLinks(cb) {
    fetch("/data/stripe-links-v1.json", { cache: "no-store" })
      .then(function (r) {
        return r.ok ? r.json() : null;
      })
      .then(function (data) {
        if (data && data.links) LINKS = data.links;
        applyCheckoutState(data);
        if (typeof cb === "function") cb();
      })
      .catch(function () {
        if (typeof cb === "function") cb();
      });
  }

  function isLive(url) {
    return (
      typeof url === "string" &&
      url.indexOf("https://buy.stripe.com/") === 0 &&
      url.indexOf("REPLACE_") === -1
    );
  }

  function applyCheckoutState(data) {
    CHECKOUT_LIVE = !!(data && data.stripe_links_live);
    if (CHECKOUT_LIVE || document.body.getAttribute("data-stripe-live") === "true") {
      document.body.classList.add("checkout-live");
    }
    document.querySelectorAll("[data-buy]").forEach(function (el) {
      var key = el.getAttribute("data-buy");
      var url = LINKS[key];
      if (isLive(url)) {
        el.removeAttribute("disabled");
        el.setAttribute("aria-disabled", "false");
        var label = (el.textContent || "").trim();
        el.setAttribute("aria-label", label + " — Opens Stripe checkout (CAD)");
      } else {
        el.setAttribute("disabled", "disabled");
        el.setAttribute("aria-disabled", "true");
      }
    });
  }

  function buy(key, el) {
    var url = LINKS[key];
    if (isLive(url)) {
      if (el && el.tagName === "BUTTON") {
        var prev = el.textContent;
        el.textContent = "Opening checkout…";
        setTimeout(function () {
          el.textContent = prev;
        }, 1200);
      }
      window.open(url, "_blank", "noopener,noreferrer");
      return;
    }
    var hub = document.querySelector('a[href*="toolkits"]');
    var fallback = hub ? hub.getAttribute("href") : "toolkits.html";
    if (fallback.indexOf("http") !== 0) {
      fallback = new URL(fallback, window.location.href).href;
    }
    window.location.href = fallback + "#bundles";
  }

  function wireBuyButtons() {
    document.querySelectorAll("[data-buy]").forEach(function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault();
        buy(el.getAttribute("data-buy"), el);
      });
    });
  }

  function wireCopyButtons() {
    document.querySelectorAll("#copyTpl, [data-copy-target]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = btn.getAttribute("data-target") || btn.getAttribute("data-copy-target");
        var ta = id ? document.getElementById(id) : document.querySelector(".toolkit-textarea");
        if (!ta) return;
        ta.select();
        ta.setSelectionRange(0, ta.value.length);
        var ok = false;
        try {
          ok = document.execCommand("copy");
        } catch (_e) {
          ok = false;
        }
        if (!ok && navigator.clipboard) {
          navigator.clipboard.writeText(ta.value).catch(function () {});
        }
        var prev = btn.textContent;
        btn.textContent = "Copied";
        setTimeout(function () {
          btn.textContent = prev;
        }, 1400);
      });
    });
  }

  function init() {
    loadLinks(function () {
      wireBuyButtons();
      wireCopyButtons();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

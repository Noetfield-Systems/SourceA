/**
 * Wire canonical auth URLs on static landing pages (Tier 0 public — header CTAs only).
 * SSOT: data/cross-domain-auth-surfaces-v1.json
 */
(function () {
  "use strict";

  var SIGN_IN = "/auth/sign-in";
  var SIGN_UP = "/auth/sign-up";

  function wire() {
    document.querySelectorAll(".ar-header-signin, .ar-nav-signin-mobile").forEach(function (el) {
      if (el.getAttribute("href") === "/platform") {
        el.setAttribute("href", SIGN_IN);
        el.textContent = el.textContent.trim() === "Sign in" ? "Sign in" : el.textContent;
      }
    });
    document.querySelectorAll("[data-sa-auth-signin]").forEach(function (el) {
      el.setAttribute("href", SIGN_IN);
    });
    document.querySelectorAll("[data-sa-auth-signup]").forEach(function (el) {
      el.setAttribute("href", SIGN_UP);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wire);
  } else {
    wire();
  }
})();

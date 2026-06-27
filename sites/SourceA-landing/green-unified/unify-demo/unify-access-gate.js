(function () {
  "use strict";
  /** Full /unify — paid desk; limited-time free promo; sign-in after promo ends. */
  var cu = window.__cuWebPath && window.__cuWebPath();
  if (!cu || !cu.isFull) return;

  var CONFIG_URL = "/sourcea/data/chat-unify-web-access-v1.json";
  var SESSION_KEY = "sourcea-platform-session-v1";
  var ACCESS_KEY = "chat-unify-web-access-v1";

  function readSession() {
    try {
      var raw = JSON.parse(localStorage.getItem(SESSION_KEY) || "{}");
      return raw && (raw.email || raw.supabase_user_id) && raw.signed_in_at ? raw : null;
    } catch (e) {
      return null;
    }
  }

  function promoActive(cfg) {
    if (!cfg || !cfg.promo_free_until) return false;
    return Date.now() < Date.parse(cfg.promo_free_until);
  }

  function hasAccess(cfg) {
    if (promoActive(cfg)) return { ok: true, reason: "promo" };
    if (readSession()) return { ok: true, reason: "signed_in" };
    try {
      var row = JSON.parse(localStorage.getItem(ACCESS_KEY) || "{}");
      if (row && row.granted_at && row.until && Date.now() < Date.parse(row.until)) {
        return { ok: true, reason: "access_grant" };
      }
    } catch (e) { /* ignore */ }
    if (cfg && cfg.open_access === true) return { ok: true, reason: "open" };
    return { ok: false, reason: "paywall" };
  }

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = String(s || "");
    return d.innerHTML;
  }

  function formatDate(iso) {
    try {
      return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
    } catch (e) {
      return iso || "";
    }
  }

  function showGate(cfg) {
    document.documentElement.classList.add("cu-unify-gated");
    var gate = document.createElement("div");
    gate.className = "cu-unify-gate";
    gate.setAttribute("role", "dialog");
    gate.setAttribute("aria-modal", "true");
    gate.setAttribute("aria-labelledby", "cu-unify-gate-title");
    var returnTo = encodeURIComponent("/unify/");
    gate.innerHTML =
      '<div class="cu-unify-gate-card">' +
      '<p class="cu-unify-gate-kicker">Chat Unify · full desk</p>' +
      '<h2 id="cu-unify-gate-title">Full web desk — for paying teams</h2>' +
      '<p>All machines · Workspace IDE · cloud receipts · Connect + Proof Pack.</p>' +
      (cfg.promo_free_until
        ? "<p class=\"cu-unify-gate-promo-ended\">Free preview ended " + esc(formatDate(cfg.promo_free_until)) + ".</p>"
        : "") +
      '<div class="cu-unify-gate-actions">' +
      '<a class="cu-btn cu-btn-primary" href="/sourcea/forge/terminal/signin?return=' + returnTo + '">Sign in</a>' +
      '<a class="cu-btn" href="/sourcea/pricing">Pricing</a>' +
      '<a class="cu-btn" href="/unify-demo/">Try free demo</a>' +
      '<a class="cu-btn" href="/downloads/chat-unify-mac-v1.dmg">Download Mac app</a>' +
      "</div>" +
      '<p class="cu-unify-gate-foot"><a href="mailto:hello@sourcea.app?subject=Chat%20Unify%20web%20access">hello@sourcea.app</a> for team access</p>' +
      "</div>";
    document.body.appendChild(gate);
  }

  function showPromoBanner(cfg) {
    var banner = document.createElement("div");
    banner.className = "cu-web-banner cu-web-banner-promo";
    banner.setAttribute("role", "status");
    banner.innerHTML =
      "<strong>Limited-time free</strong> — full Chat Unify web desk until " +
      esc(formatDate(cfg.promo_free_until)) +
      '. After that, sign in or <a href="/sourcea/pricing">see pricing</a>. ' +
      '<a href="/unify-demo/">Public demo</a> stays free.';
    document.addEventListener("DOMContentLoaded", function () {
      var app = document.querySelector(".cu-app");
      if (app && app.parentNode) app.parentNode.insertBefore(banner, app);
    });
  }

  fetch(CONFIG_URL, { cache: "no-store" })
    .then(function (r) {
      return r.json();
    })
    .then(function (cfg) {
      window.__CHAT_UNIFY_ACCESS__ = cfg;
      var access = hasAccess(cfg);
      if (!access.ok) {
        if (document.readyState === "loading") {
          document.addEventListener("DOMContentLoaded", function () {
            showGate(cfg);
          });
        } else {
          showGate(cfg);
        }
        return;
      }
      if (access.reason === "promo") showPromoBanner(cfg);
      document.documentElement.setAttribute("data-cu-access", access.reason);
    })
    .catch(function () {
      document.documentElement.setAttribute("data-cu-access", "config_missing");
    });
})();

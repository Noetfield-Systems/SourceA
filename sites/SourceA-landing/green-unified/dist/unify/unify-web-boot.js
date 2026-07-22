(function () {
  "use strict";
  /** Full web desk on sourcea.app/unify — API under /unify/api, hide Mac-only chrome. */
  var cu = window.__cuWebPath && window.__cuWebPath();
  if (!cu || !cu.isFull) return;

  document.documentElement.setAttribute("data-cu-web", "full");

  var WEB_API = window.location.origin + "/api/chat-unify-cloud/v1";
  window.__CHAT_UNIFY_API_BASE__ = WEB_API;

  var nativeFetch = window.fetch.bind(window);
  function mapUrl(url) {
    if (typeof url !== "string") return url;
    var origin = window.location.origin;
    if (url === origin + "/health") return WEB_API + "/health";
    if (url.indexOf(origin + "/api/") === 0) return WEB_API + url.slice(origin.length + 4);
    if (url.indexOf(origin + "/form") === 0) return WEB_API + url.slice(origin.length);
    if (url.indexOf(origin + "/terminal/") === 0) {
      return origin + "/unify/terminal/" + url.slice((origin + "/terminal/").length);
    }
    return url;
  }

  window.fetch = function (url, opts) {
    return nativeFetch(mapUrl(url), opts);
  };

  document.addEventListener("DOMContentLoaded", function () {
    if (document.documentElement.classList.contains("cu-unify-gated")) return;

    document.title = "Chat Unify — full web desk";
    var frame = document.getElementById("forge-ide-frame");
    if (frame && frame.getAttribute("src") && frame.getAttribute("src").indexOf("/terminal/") === 0) {
      frame.setAttribute("src", "terminal/index.html?v=4.9.9-guide-collapse&embed=1");
    }
    var formFrame = document.getElementById("official-form-iframe");
    if (formFrame && String(formFrame.getAttribute("src") || "").indexOf("/form/") === 0) {
      formFrame.setAttribute("src", WEB_API + "/form/?embedded=1");
    }
    document.querySelectorAll('a[href^="http://127.0.0.1:"]').forEach(function (a) {
      a.hidden = true;
    });
    var hook = document.getElementById("connect-hook-url");
    if (hook) hook.value = WEB_API + "/integrations/v1/hook";

    var kicker = document.querySelector(".cu-kicker");
    if (kicker) kicker.textContent = "SourceA · Chat Unify · full web";

    var subKicker = document.getElementById("sa-unify-sub-kicker");
    var subTitle = document.getElementById("sa-unify-sub-title");
    var subLead = document.getElementById("sa-unify-sub-lead");
    if (subKicker) subKicker.textContent = "Full desk · all machines · cloud receipts";
    if (subTitle) subTitle.textContent = "Chat Unify — your governed agent desk";
    if (subLead) {
      subLead.textContent =
        "Workspace IDE, Verify & Act, Audit Trail, Proof Pack, Connect — every run receipted when the cloud API is live.";
    }
    document.querySelectorAll(".sa-unify-nav-active").forEach(function (el) {
      el.classList.remove("sa-unify-nav-active");
      el.removeAttribute("aria-current");
    });
    var fullNav = document.querySelector('.ar-nav a[href="/unify/"]');
    if (fullNav) {
      fullNav.classList.add("sa-unify-nav-active");
      fullNav.setAttribute("aria-current", "page");
    }

    var banner = document.createElement("div");
    banner.className = "cu-web-banner cu-web-banner-full";
    banner.setAttribute("role", "status");
    banner.innerHTML =
      "<strong>Full desk</strong> — all machines · Workspace IDE · cloud receipts when API is wired. " +
      '<a href="/downloads/chat-unify-mac-v1.dmg">Mac app</a> · ' +
      '<a href="/unify-demo/">Public demo</a>';
    var app = document.querySelector(".cu-app");
    if (app && app.parentNode) app.parentNode.insertBefore(banner, app);

    try {
      if (localStorage.getItem("chat-unify-active-tab-v1") === "forge-ide") {
        localStorage.setItem("chat-unify-active-tab-v1", "home");
      }
    } catch (e) { /* ignore */ }
  });
})();

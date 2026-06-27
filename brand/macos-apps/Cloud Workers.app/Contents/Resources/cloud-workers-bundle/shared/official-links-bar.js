(function () {
  "use strict";

  var PLAIN_HUB = "Worker Hub retired — use Cloud Workers :13027.";
  var PLAIN_CLOUD = "Cloud Workers — CLOUD-SEC queue · Railway full-pack Proceed (:13027).";
  var PLAIN_MAIL = "Switch to Portfolio Mail — inbox hub and mail wiring.";
  var PLAIN_CHAT = "Switch to Chat Unify — merge Cursor chats, n8n webhook.";
  var PLAIN_FORM = "Official founder form — A–D + write your own · picks land on disk · :13023/form/.";
  var PLAIN_N8N = "Switch to N8N Integration — automation spine and validators.";
  var PLAIN_AG = "Switch to AG Routing Panel — agent cost · route · ROI · start here on :8782.";
  var PLAIN_MAC = "Switch to Mac Law — routing and control-plane rules.";

  /* Cloud Workers only — Worker Hub trashed ASF 2026-06-23 */
  var LINKS = [
    { id: "cloud", label: "Cloud Workers", href: "http://127.0.0.1:13027/", plain: PLAIN_CLOUD, agentPriority: true },
    { id: "ag-routing", label: "AG Routing", href: "http://127.0.0.1:8782/", plain: PLAIN_AG },
    { id: "n8n", label: "N8N Integration", href: "http://127.0.0.1:13026/", plain: PLAIN_N8N },
    { id: "chat", label: "Chat Unify", href: "http://127.0.0.1:13023/", plain: PLAIN_CHAT },
    { id: "form", label: "Official Form", href: "http://127.0.0.1:13023/form/", plain: PLAIN_FORM },
    { id: "mail", label: "Portfolio Mail", href: "http://127.0.0.1:13028/mail-hub/", plain: PLAIN_MAIL },
    { id: "mac-law", label: "Mac Law", href: "http://127.0.0.1:8781/", plain: PLAIN_MAC },
  ];

  function isStandaloneShell() {
    return !!(
      window.webkit &&
      window.webkit.messageHandlers &&
      window.webkit.messageHandlers.sinaAppOpen
    );
  }

  function detectActive() {
    var port = String(window.location.port || "");
    var path = window.location.pathname || "";
    if (port === "13023" && path.indexOf("/form") !== -1) return "form";
    if (port === "13023") return "chat";
    if (port === "13026") return "n8n";
    if (port === "13027") return "cloud";
    if (port === "8782") return "ag-routing";
    if (port === "8781") return "mac-law";
    if (port === "13028") return "mail";
    if (port === "13024") return "mac_health";
    if (path.indexOf("/mail-hub") !== -1) return "mail";
    if (path.indexOf("/cloud-workers") !== -1) return "cloud";
    return "hub";
  }

  function openNativeApp(appId, e) {
    if (!isStandaloneShell()) return false;
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    window.webkit.messageHandlers.sinaAppOpen.postMessage({ app: appId });
    return true;
  }

  function mount(el, activeId) {
    if (!el) return;
    var active = activeId || detectActive();
    el.innerHTML =
      '<span class="official-links-label">Official links</span>' +
      LINKS.map(function (l) {
        var cls = "official-link-tab" + (l.id === active ? " active" : "");
        if (l.agentPriority && l.id !== active) cls += " agent-priority";
        return (
          '<a class="' +
          cls +
          '" href="' +
          l.href +
          '" data-sina-app="' +
          l.id +
          '" rel="noopener"><span class="dot"></span>' +
          l.label +
          "</a>"
        );
      }).join("");
    el.querySelectorAll("[data-sina-app]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        var appId = a.getAttribute("data-sina-app");
        var link = LINKS.find(function (l) {
          return l.id === appId;
        });
        if (window.SinaMainTerminal && link) {
          window.SinaMainTerminal.log("→ Official link: " + link.label);
          window.SinaMainTerminal.log("  " + (link.plain || ""));
        }
        if (appId === active && isStandaloneShell()) {
          e.preventDefault();
          return;
        }
        openNativeApp(appId, e);
      });
    });
  }

  window.SinaOfficialLinks = { mount: mount, links: LINKS, openNativeApp: openNativeApp };
  document.querySelectorAll("[data-official-links]").forEach(function (el) {
    mount(el, el.getAttribute("data-active"));
  });
})();

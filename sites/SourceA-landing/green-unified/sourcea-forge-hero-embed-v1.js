/**
 * Forge Terminal hero embed — founder-home only (WS-04).
 * Lazy-load after LCP · postMessage height · mobile tap-to-open.
 */
(function () {
  "use strict";

  if (!document.body.classList.contains("sa-root-home")) return;

  const EMBED_URL = "/sourcea/forge/terminal?embed=1";
  const FULL_URL = "/sourcea/forge/terminal";
  const MOBILE_MQ = window.matchMedia("(max-width: 768px)");
  const STATUS_URL =
    "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/api/brain/status/v1";

  const root = document.getElementById("sa-forge-hero-embed");
  const shell = document.getElementById("sa-forge-hero-embed-shell");
  const launch = document.getElementById("sa-forge-hero-embed-launch");
  const offline = document.getElementById("sa-forge-hero-embed-offline");
  if (!root || !shell) return;

  let loaded = false;
  let iframe = null;
  let embedReady = false;
  let embedFailTimer = null;

  function track(event, meta) {
    if (window.SourceAPulse && typeof window.SourceAPulse.track === "function") {
      window.SourceAPulse.track(event, meta || {});
    }
  }

  function showOffline() {
    if (offline) offline.hidden = false;
    if (launch) launch.hidden = true;
  }

  async function probeOnline() {
    try {
      const ctrl = new AbortController();
      const t = setTimeout(() => ctrl.abort(), 8000);
      const r = await fetch(STATUS_URL, { signal: ctrl.signal, cache: "no-store" });
      clearTimeout(t);
      if (!r.ok) return false;
      const d = await r.json();
      return Boolean(d.ai_model_ready || d.openrouter_ready);
    } catch {
      return true;
    }
  }

  function mountIframe() {
    if (loaded) return;
    loaded = true;
    if (launch) launch.hidden = true;
    if (offline) offline.hidden = true;
    track("forge_hero_embed_open", { mobile: MOBILE_MQ.matches });

    iframe = document.createElement("iframe");
    iframe.src = EMBED_URL;
    iframe.title = "Forge Terminal living chat demo";
    iframe.className = "sa-forge-hero-embed-frame";
    iframe.setAttribute("loading", "lazy");
    iframe.setAttribute(
      "sandbox",
      "allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
    );
    iframe.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
    shell.appendChild(iframe);

    iframe.addEventListener("error", showEmbedFailed);
    embedFailTimer = setTimeout(function () {
      if (!embedReady) showEmbedFailed();
    }, 6000);
  }

  function showEmbedFailed() {
    if (iframe) {
      iframe.remove();
      iframe = null;
    }
    loaded = false;
    if (offline) {
      offline.hidden = false;
      offline.innerHTML =
        'Embed blocked — <a href="' +
        FULL_URL +
        '">open Forge Terminal full page</a>';
    }
    if (launch) {
      launch.hidden = false;
      launch.textContent = "Open Forge Terminal full page";
      launch.onclick = function () {
        window.location.href = FULL_URL;
      };
    }
  }

  function onHeightMessage(ev) {
    if (!iframe || ev.source !== iframe.contentWindow) return;
    const data = ev.data;
    if (!data || data.schema !== "sa-forge-embed-v1") return;
    if (data.type === "ready") {
      embedReady = true;
      if (embedFailTimer) clearTimeout(embedFailTimer);
      if (offline) offline.hidden = true;
      return;
    }
    if (data.type !== "height") return;
    const h = Math.min(Math.max(Number(data.height) || 340, 280), 520);
    iframe.style.height = h + "px";
  }

  function scheduleLoad() {
    if (MOBILE_MQ.matches) return;
    const run = () => {
      probeOnline().then((ok) => {
        if (!ok) {
          showOffline();
          return;
        }
        mountIframe();
      });
    };
    if ("requestIdleCallback" in window) {
      requestIdleCallback(run, { timeout: 3500 });
    } else {
      setTimeout(run, 2000);
    }
  }

  if (launch) {
    launch.addEventListener("click", () => {
      probeOnline().then((ok) => {
        if (!ok) {
          showOffline();
          return;
        }
        mountIframe();
      });
    });
  }

  window.addEventListener("message", onHeightMessage);

  if (document.readyState === "complete") {
    scheduleLoad();
  } else {
    window.addEventListener("load", scheduleLoad, { once: true });
  }

  window.SourceAForgeHeroEmbed = { mountIframe, FULL_URL };
})();

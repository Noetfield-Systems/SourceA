(function () {
  "use strict";

  const FORGE_API = window.location.origin + "/api/forge-terminal/v1";
  const CU_IDE_API = window.location.origin + "/api/chat-unify-ide/v1";
  const CU_ENGINE_API = window.location.origin + "/api/chat-unify-engine/v1";
  let API = FORGE_API;
  let inChatUnifyShell = false;
  const AGENT_KEY = "forge_ide_agent_v1";
  const WS_PATH_KEY = "forge_ide_workspace_path_v2";
  const DOCK_H_KEY = "forge_ide_dock_h_v1";
  const DOCK_KEY = "forge_ide_dock_open_v1";
  const SIDEBAR_W_KEY = "forge_ide_sidebar_w_v1";
  const EMBED_SIDEBAR_KEY = "forge_ide_embed_sidebar_v1";
  const DRAFT_KEY = "forge_ide_draft_v1";
  const ROLE_KEY = "forge_ide_role_v1";
  const MODEL_KEY = "forge_ide_model_v1";
  const MODEL_LOCK_KEY = "forge_ide_model_locked_v1";
  const MODE_KEY = "forge_ide_mode_v3";
  const CLOUD_L3_KEY = "forge_ide_cloud_l3_v1";
  const UI_VERSION = "4.9.9-cu-combined";
  const CU_IDE_LABEL = "Chat Unify Workspace";
  const HIDDEN_DEFAULT_MODELS = ["gemini-3.1-flash-lite"];
  let engineRouteReady = Promise.resolve();
  const CHAT_SCROLL_THRESHOLD = 120;
  let chatStickToBottom = true;
  let chatClearGuardUntil = 0;
  let suppressThreadReload = false;
  let lastThreadTurns = [];
  let lastSessionTitle = "Chat";
  const $ = (id) => document.getElementById(id);

  function getForgeMode() {
    return localStorage.getItem(MODE_KEY) || "chat";
  }

  function setForgeMode(mode) {
    localStorage.setItem(MODE_KEY, mode);
    document.querySelectorAll(".forge-mode-pill").forEach(function (btn) {
      btn.classList.toggle("is-active", btn.getAttribute("data-mode") === mode);
    });
  }

  function initModePills() {
    const mode = getForgeMode();
    setForgeMode(mode);
    const host = $("forge-mode-pills");
    if (host && host.dataset.modeWired !== "1") {
      host.dataset.modeWired = "1";
      host.addEventListener("click", function (ev) {
        const btn = ev.target.closest(".forge-mode-pill");
        if (!btn) return;
        setForgeMode(btn.getAttribute("data-mode") || "chat");
      });
    }
    const l3 = $("opt-cloud-l3");
    if (l3) {
      l3.checked = localStorage.getItem(CLOUD_L3_KEY) === "1";
      l3.addEventListener("change", function () {
        localStorage.setItem(CLOUD_L3_KEY, l3.checked ? "1" : "0");
      });
    }
  }

  let workspacePath = localStorage.getItem(WS_PATH_KEY) || "";
  let runId = "";
  let lastCost = "—";
  let lastTime = "—";
  let lastModel = localStorage.getItem(MODEL_KEY) || "gpt-4o";
  let lastRole = localStorage.getItem(ROLE_KEY) || "bulk";
  let modelCatalog = [];
  let roleCatalog = [];
  let opening = false;
  let forgeToken = sessionStorage.getItem("forge_local_token") || "";
  let lastQualityGate = null;
  let llmOnline = true;
  let gateDrawerOpen = false;
  let activeSessionId = "";
  let chatSessions = [];
  let recentWorkspaces = [];
  const EDITOR_W_KEY = "forge_ide_editor_w_v1";
  const EDITOR_H_KEY = "forge_ide_editor_h_v1";

  const qsBoot = new URLSearchParams(window.location.search);
  if (qsBoot.get("embed") === "1") {
    inChatUnifyShell = true;
    API = CU_IDE_API;
  }

  const MODEL_GUIDE_KEY = "cu_model_guide_collapsed_v1";

  function showCuServerOfflineBanner() {
    if (!inChatUnifyShell && qsBoot.get("embed") !== "1") return;
    let banner = $("cu-server-offline-banner");
    if (!banner) {
      banner = document.createElement("div");
      banner.id = "cu-server-offline-banner";
      banner.className = "cu-server-offline-banner";
      banner.setAttribute("role", "alert");
      banner.innerHTML =
        "Chat Unify server offline on :13023 — <strong>Cmd+Q</strong> then reopen <strong>Chat Unify.app</strong> from Desktop.";
      const editor = $("forge-editor-window");
      if (editor) editor.insertBefore(banner, editor.firstChild);
      else document.body.prepend(banner);
    }
    banner.hidden = false;
    setStatus("Server offline — reopen Chat Unify.app");
  }

  function hideCuServerOfflineBanner() {
    const banner = $("cu-server-offline-banner");
    if (banner) banner.hidden = true;
  }

  function setModelGuideCollapsed(collapsed) {
    const guide = $("forge-model-guide");
    const btn = $("btn-toggle-model-guide");
    const input = $("prompt-input");
    if (!guide) return;
    guide.classList.toggle("is-collapsed", collapsed);
    document.body.classList.toggle("forge-model-guide-collapsed", collapsed);
    if (btn) {
      btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
      btn.textContent = collapsed ? "Show guide" : "Hide guide";
      btn.title = collapsed
        ? "Show model guide and quick prompts"
        : "Hide model guide for more chat room";
    }
    if (input) {
      input.rows = collapsed ? 3 : 7;
      autoGrowPrompt();
    }
    try {
      localStorage.setItem(MODEL_GUIDE_KEY, collapsed ? "1" : "0");
    } catch (_) {
      /* ignore */
    }
    sizeEditorPanes();
    scheduleScrollToLatest();
  }

  function initModelGuideCollapse() {
    const btn = $("btn-toggle-model-guide");
    if (!btn || btn.dataset.wired === "1") return;
    btn.dataset.wired = "1";
    let collapsed = false;
    try {
      collapsed = localStorage.getItem(MODEL_GUIDE_KEY) === "1";
    } catch (_) {
      /* ignore */
    }
    setModelGuideCollapsed(collapsed);
    btn.addEventListener("click", function () {
      const guide = $("forge-model-guide");
      setModelGuideCollapsed(!(guide && guide.classList.contains("is-collapsed")));
    });
  }

  async function initEngineRoute() {
    try {
      const h = await fetchJsonWithTimeout(window.location.origin + "/health", { cache: "no-store" }, 5000);
      if (h.service === "chat-unify") {
        inChatUnifyShell = true;
        API = CU_IDE_API;
        document.documentElement.classList.add("cu-engine-active");
        if ($("forge-app")) $("forge-app").classList.add("cu-engine-active");
        applyChatUnifyShellBranding();
        hideCuServerOfflineBanner();
      }
    } catch (_) {
      if (inChatUnifyShell || qsBoot.get("embed") === "1") {
        showCuServerOfflineBanner();
      }
    }
  }

  function applyChatUnifyShellBranding() {
    if (!inChatUnifyShell) return;
    document.title = CU_IDE_LABEL;
    const chatTitle = document.querySelector(".forge-chat-title");
    if (chatTitle) chatTitle.textContent = CU_IDE_LABEL;
    const winTitle = document.querySelector(".forge-chat-window-title");
    if (winTitle) winTitle.textContent = "Message history";
    const ph = $("chat-placeholder");
    if (ph && inChatUnifyShell) ph.remove();
    if (ph && !inChatUnifyShell) {
      ph.textContent =
        "Chat inside the editor window below — scroll message history inside the window.";
    }
    const deckTitle = document.querySelector(".forge-tools-deck-title");
    if (deckTitle) deckTitle.textContent = "Chat Unify tools";
    const deckLead = document.querySelector(".forge-tools-deck-lead");
    if (deckLead) {
      deckLead.textContent =
        "Scroll the page for terminal + tools · scroll inside the editor window for chat history.";
    }
    const pillCu = $("pill-chat-unify");
    if (pillCu) pillCu.title = "Back to Chat Unify paste tab";
    applyChatUnifyCombinedLayout();
  }

  function initMovableEditorWindow() {
    if (!isEditorWindowMode() && !inChatUnifyShell) return;
    const win = $("forge-editor-window");
    const handle = document.querySelector(".forge-editor-toolbar");
    if (!win || !handle || handle.dataset.forgeDragWired === "1") return;
    handle.dataset.forgeDragWired = "1";
    win.classList.add("forge-movable-window");
    const KEY = inChatUnifyShell ? "cu_ide_window_pos_v1" : "forge_ide_window_pos_v1";
    let pos = { x: 0, y: 0 };
    try {
      pos = JSON.parse(localStorage.getItem(KEY) || "{}");
    } catch (_) {
      /* ignore */
    }
    function applyPos() {
      win.style.transform = "translate(" + (pos.x || 0) + "px," + (pos.y || 0) + "px)";
    }
    applyPos();
    let drag = null;
    handle.addEventListener("pointerdown", function (ev) {
      if (ev.target.closest("select,button,input,textarea,a,label")) return;
      drag = { sx: ev.clientX, sy: ev.clientY, ox: pos.x || 0, oy: pos.y || 0 };
      handle.setPointerCapture(ev.pointerId);
      handle.classList.add("forge-dragging");
    });
    handle.addEventListener("pointermove", function (ev) {
      if (!drag) return;
      pos.x = drag.ox + (ev.clientX - drag.sx);
      pos.y = drag.oy + (ev.clientY - drag.sy);
      applyPos();
    });
    function endDrag(ev) {
      if (!drag) return;
      drag = null;
      handle.classList.remove("forge-dragging");
      try {
        localStorage.setItem(KEY, JSON.stringify(pos));
      } catch (_) {
        /* ignore */
      }
      if (ev && ev.pointerId != null) {
        try {
          handle.releasePointerCapture(ev.pointerId);
        } catch (_) {
          /* ignore */
        }
      }
    }
    handle.addEventListener("pointerup", endDrag);
    handle.addEventListener("pointercancel", endDrag);
  }

  function applyChatUnifyCombinedLayout() {
    if (!inChatUnifyShell) return;
    if (document.documentElement.dataset.cuCombinedLayout === "1") return;
    document.documentElement.dataset.cuCombinedLayout = "1";
    document.documentElement.classList.add("forge-cu-combined", "forge-desktop-app", "forge-page-scroll");
    document.body.classList.add("forge-cu-combined", "forge-desktop-app", "forge-page-scroll");
    document.documentElement.classList.remove("forge-embed-root");
    document.body.classList.remove("forge-embed-root");
    const app = $("forge-app");
    if (app) {
      app.classList.add("forge-cu-combined", "forge-desktop-app");
    }
    forceScrollUnlock();
    enableEditorWindow();
    const embedStrip = $("embed-ws-strip");
    if (embedStrip) embedStrip.setAttribute("hidden", "");
    const scrollHint = $("composer-hint");
    if (scrollHint) {
      scrollHint.textContent = "Scroll message history inside the purple window ↑ · drag green toolbar to move";
    }
    initMovableEditorWindow();
    initComposerFollow();
    initModelGuideCollapse();
    sizeEditorPanes();
    scheduleScrollToLatest();
    syncSendButtonState();
    window.addEventListener("resize", function () {
      sizeEditorPanes();
      if (chatStickToBottom) scrollChatToBottom(true);
    });
  }

  function initComposerFollow() {
    if (!isEditorWindowMode() && !inChatUnifyShell) return;
    const input = $("prompt-input");
    if (!input || input.dataset.cuFollowWired === "1") return;
    input.dataset.cuFollowWired = "1";
    function syncComposeView() {
      const ph = $("chat-placeholder");
      if (ph) ph.remove();
      chatStickToBottom = true;
      if (isEditorWindowMode()) {
        enableEditorWindow();
        sizeEditorPanes();
      }
      scrollChatToBottom(true);
      updateJumpLatestButton();
    }
    input.addEventListener("focus", syncComposeView);
    input.addEventListener("input", syncComposeView);
    input.addEventListener("keydown", syncComposeView);
  }

  function openPeerUrl(url) {
    if (!url) return;
    if (inChatUnifyShell && window.parent !== window) {
      if (/13023|:13023|chat.unify|chat_unify/i.test(url) || url === window.location.origin + "/") {
        window.parent.postMessage({ type: "cu-goto-tab", tab: "home" }, "*");
        return;
      }
      if (/13027|:13027|cloud/i.test(url)) {
        window.parent.postMessage({ type: "sina-open-app", app: "cloud" }, "*");
        return;
      }
      return;
    }
    if (inChatUnifyShell && /127\.0\.0\.1:13023/.test(url)) return;
    try {
      window.open(url, "_blank", "noopener,noreferrer");
    } catch (_) {
      log("open " + url, "ok");
    }
  }

  function cuIdeStatus(suffix) {
    return CU_IDE_LABEL + (suffix ? " → " + suffix : "");
  }

  async function fetchJsonWithTimeout(url, init, timeoutMs) {
    const ms = timeoutMs || 90000;
    const ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
    const timer = ctrl
      ? setTimeout(function () {
          ctrl.abort();
        }, ms)
      : null;
    try {
      const res = await fetch(url, Object.assign({}, init || {}, ctrl ? { signal: ctrl.signal } : {}));
      const raw = await res.text();
      let row;
      try {
        row = JSON.parse(raw);
      } catch (_) {
        throw new Error(raw.slice(0, 200) || "Request failed");
      }
      if (!res.ok && row.ok === false) {
        throw new Error(row.message || row.error || "HTTP " + res.status);
      }
      return row;
    } catch (err) {
      if (ctrl && err && err.name === "AbortError") {
        throw new Error("Request timed out after " + Math.round(ms / 1000) + "s — retry or pick a faster model");
      }
      if (err && /Failed to fetch|NetworkError|Load failed|Connection refused/i.test(String(err.message || err))) {
        throw new Error("Chat Unify server not reachable — Cmd+Q and reopen Chat Unify.app from Desktop");
      }
      throw err;
    } finally {
      if (timer) clearTimeout(timer);
    }
  }

  async function pingServerHealth() {
    try {
      const row = await fetchJsonWithTimeout(window.location.origin + "/health", { cache: "no-store" }, 5000);
      return !!(row && row.ok && row.service === "chat-unify");
    } catch (_) {
      return false;
    }
  }

  async function cuEngineApi(body) {
    return fetchJsonWithTimeout(
      CU_ENGINE_API,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body || {}),
      },
      30000,
    );
  }

  function selectedAgentId() {
    const sel = $("agent-select");
    const v = (sel && sel.value) || localStorage.getItem(AGENT_KEY) || (inChatUnifyShell ? "auto" : "builder");
    return v;
  }

  function applySmartRoute(row) {
    const route = row.smart_route || row;
    if (!route || !route.machine_tab) return;
    const hint = $("composer-hint");
    if (hint && route.reasoning) {
      hint.textContent = "Smart route · " + route.reasoning;
    }
    if (route.machine_tab && route.machine_tab !== "living-chat" && window.parent !== window) {
      window.parent.postMessage({ type: "cu-goto-tab", tab: route.machine_tab }, "*");
    }
    setStatus(route.reasoning || "Routed");
  }

  async function loadAgentSelect() {
    const sel = $("agent-select");
    if (!sel) return;
    try {
      const row = inChatUnifyShell
        ? await cuEngineApi({ action: "list_agents" })
        : await api({ action: "list_agents" });
      const agents = row.agents || [];
      if (agents.length) {
        const autoOpt =
          '<option value="auto"' +
          (inChatUnifyShell ? " selected" : "") +
          '>Auto — smart router</option>';
        sel.innerHTML =
          autoOpt +
          agents
          .map(function (a) {
            const id = esc(a.id || a.role || "agent");
            const desc = esc(a.description || a.role || "");
            return '<option value="' + id + '">' + id + " — " + desc + "</option>";
          })
          .join("");
      }
      const saved = localStorage.getItem(AGENT_KEY) || (inChatUnifyShell ? "auto" : "builder");
      if (Array.from(sel.options).some(function (o) {
        return o.value === saved;
      })) {
        sel.value = saved;
      }
      renderAgents(agents);
    } catch (_) {
      renderAgents([]);
    }
    sel.addEventListener("change", function () {
      localStorage.setItem(AGENT_KEY, sel.value);
      document.querySelectorAll(".forge-agents li").forEach(function (li) {
        li.classList.toggle("is-active", li.getAttribute("data-agent") === sel.value);
      });
    });
  }

  function reloadUI() {
    const u = new URL(window.location.href);
    u.searchParams.set("ui", UI_VERSION);
    u.searchParams.set("t", String(Date.now()));
    window.location.replace(u.toString());
  }

  function renderThreadTabs() {
    renderWorkspaceHub(recentWorkspaces);
  }

  function renderWorkspaceHub(list) {
    if (list && list.length) recentWorkspaces = list;
    const hub = $("ws-hub");
    const nav = $("ws-list");
    const chips = $("embed-ws-chips");
    const rows = recentWorkspaces.slice();
    if (workspacePath && !rows.some(function (w) { return (w.path || "") === workspacePath; })) {
      rows.unshift({ path: workspacePath, name: folderLabel() });
    }
    if (hub) {
      if (!rows.length) {
        hub.innerHTML =
          '<p class="forge-ws-empty">No workspaces yet.<br/>Tap <strong>Open New Workspace</strong> above.</p>';
      } else {
        hub.innerHTML = rows
          .map(function (w) {
            const path = w.path || "";
            const name = esc(w.name || path.split("/").pop() || "Workspace");
            const isActive = path === workspacePath;
            let chatsHtml = "";
            if (isActive) {
              chatsHtml +=
                '<div class="forge-ws-chats"><button type="button" class="forge-ws-new-chat">+ New chat</button>';
              if (!chatSessions.length) {
                chatsHtml +=
                  '<button type="button" class="forge-ws-chat is-active" data-session="">Chat</button>';
              } else {
                chatsHtml += chatSessions
                  .map(function (s) {
                    const active = s.id === activeSessionId ? " is-active" : "";
                    const title = esc(s.title || "Chat");
                    const turns = s.turn_count ? " · " + s.turn_count : "";
                    return (
                      '<button type="button" class="forge-ws-chat' +
                      active +
                      '" data-session="' +
                      esc(s.id) +
                      '" title="' +
                      title +
                      '">' +
                      title +
                      '<span class="forge-ws-chat-meta">' +
                      turns +
                      "</span></button>"
                    );
                  })
                  .join("");
              }
              chatsHtml += "</div>";
            }
            return (
              '<div class="forge-ws-group' +
              (isActive ? " is-active" : "") +
              '"><button type="button" class="forge-ws-btn' +
              (isActive ? " is-active" : "") +
              '" data-path="' +
              esc(path) +
              '" title="' +
              esc(path) +
              '">' +
              name +
              "</button>" +
              chatsHtml +
              "</div>"
            );
          })
          .join("");
        hub.querySelectorAll(".forge-ws-btn").forEach(function (btn) {
          btn.addEventListener("click", function () {
            openFolder(btn.getAttribute("data-path") || "");
          });
        });
        hub.querySelectorAll(".forge-ws-chat").forEach(function (btn) {
          btn.addEventListener("click", function () {
            switchSession(btn.getAttribute("data-session") || "");
          });
        });
        hub.querySelectorAll(".forge-ws-new-chat").forEach(function (btn) {
          btn.addEventListener("click", function (ev) {
            ev.stopPropagation();
            newChatThread();
          });
        });
      }
    }
    if (nav) {
      nav.innerHTML = "";
    }
    if (chips) {
      if (!rows.length) {
        chips.innerHTML = '<span class="forge-muted" style="font-size:11px">—</span>';
      } else {
        chips.innerHTML = rows
          .slice(0, 6)
          .map(function (w) {
            const path = w.path || "";
            const active = path === workspacePath ? " is-active" : "";
            return (
              '<button type="button" class="forge-embed-ws-chip' +
              active +
              '" data-path="' +
              esc(path) +
              '" title="' +
              esc(path) +
              '">' +
              esc(w.name || path.split("/").pop()) +
              "</button>"
            );
          })
          .join("");
        chips.querySelectorAll(".forge-embed-ws-chip").forEach(function (btn) {
          btn.addEventListener("click", function () {
            openFolder(btn.getAttribute("data-path") || "");
          });
        });
      }
    }
  }

  function renderRecent(list) {
    renderWorkspaceHub(list || []);
  }

  async function loadChatSessions() {
    try {
      const row = await api({ action: "chat_sessions_list" });
      if (!row.ok) return;
      chatSessions = row.sessions || [];
      activeSessionId = row.active_session_id || (chatSessions[0] && chatSessions[0].id) || "";
      renderThreadTabs();
    } catch (_) { /* quiet */ }
  }

  async function switchSession(sessionId) {
    if (!sessionId || sessionId === activeSessionId) return;
    suppressThreadReload = false;
    chatClearGuardUntil = 0;
    activeSessionId = sessionId;
    renderThreadTabs();
    runId = "";
    $("run-id-label").textContent = "";
    $("exec-strip") && ($("exec-strip").hidden = true);
    gateDrawerOpen = false;
    $("decision-panel") && ($("decision-panel").hidden = true);
    await loadChatThread(true);
  }

  async function newChatThread() {
    try {
      const row = await api({ action: "chat_session_create", title: "New chat" });
      if (!row.ok) throw new Error(row.error || "create failed");
      suppressThreadReload = false;
      chatClearGuardUntil = 0;
      activeSessionId = row.active_session_id || (row.session && row.session.id) || "";
      await loadChatSessions();
      renderChatThread([]);
      log("new chat · " + activeSessionId, "ok");
      $("prompt-input") && $("prompt-input").focus();
    } catch (e) {
      log(String(e.message || e), "err");
    }
  }

  async function openFileInEditor(relPath) {
    if (!workspacePath || !relPath) return;
    try {
      const row = await api({ action: "workspace_read_file", path: relPath });
      if (!row.ok) throw new Error(row.error || "read failed");
      const pane = $("editor-pane");
      const resize = $("editor-resize");
      const body = $("editor-body");
      const pathEl = $("editor-path");
      if (pathEl) pathEl.textContent = row.rel || relPath;
      if (body) body.value = row.content || "";
      if (pane) pane.hidden = false;
      if (resize) resize.hidden = false;
      $("forge-main-split") && $("forge-main-split").classList.add("editor-open");
      const split = $("forge-main-split");
      const savedH = localStorage.getItem(EDITOR_H_KEY);
      if (split) split.style.setProperty("--editor-pane-h", savedH || "34vh");
      log("open file · " + (row.rel || relPath), "ok");
    } catch (e) {
      log(String(e.message || e), "err");
    }
  }

  function closeEditor() {
    $("editor-pane") && ($("editor-pane").hidden = true);
    $("editor-resize") && ($("editor-resize").hidden = true);
    $("forge-main-split") && $("forge-main-split").classList.remove("editor-open");
  }

  function initEditorResize() {
    const handle = $("editor-resize");
    const split = $("forge-main-split");
    if (!handle || !split) return;
    const saved = localStorage.getItem(EDITOR_W_KEY);
    if (saved) split.style.setProperty("--editor-w", saved);
    const savedH = localStorage.getItem(EDITOR_H_KEY);
    if (savedH) split.style.setProperty("--editor-pane-h", savedH);
    let dragging = false;
    handle.addEventListener("mousedown", function (ev) {
      if ($("editor-pane") && $("editor-pane").hidden) return;
      dragging = true;
      ev.preventDefault();
    });
    document.addEventListener("mousemove", function (ev) {
      if (!dragging || !split) return;
      const rect = split.getBoundingClientRect();
      const stacked = split.classList.contains("editor-open");
      if (stacked) {
        const h = Math.min(Math.max(ev.clientY - rect.top, 160), rect.height - 280);
        split.style.setProperty("--editor-pane-h", h + "px");
      } else {
        const w = Math.min(Math.max(ev.clientX - rect.left, 200), rect.width - 320);
        split.style.setProperty("--editor-w", w + "px");
      }
    });
    document.addEventListener("mouseup", function () {
      if (!dragging) return;
      dragging = false;
      const stacked = split.classList.contains("editor-open");
      if (stacked) {
        const h = split.style.getPropertyValue("--editor-pane-h");
        if (h) localStorage.setItem(EDITOR_H_KEY, h);
      } else {
        const w = split.style.getPropertyValue("--editor-w");
        if (w) localStorage.setItem(EDITOR_W_KEY, w);
      }
    });
  }

  function setSendEnabled(enabled) {
    const on = !!enabled;
    const runBtn = $("btn-run");
    const composerBtn = $("btn-run-composer");
    if (runBtn) runBtn.disabled = !on;
    if (composerBtn) {
      if (inChatUnifyShell) {
        composerBtn.disabled = false;
        composerBtn.classList.toggle("is-empty", !on);
        composerBtn.setAttribute("aria-disabled", on ? "false" : "true");
      } else {
        composerBtn.disabled = !on;
        composerBtn.classList.remove("is-empty");
      }
    }
  }

  function wireComposerSend() {
    const btn = $("btn-run-composer");
    const input = $("prompt-input");
    if (!btn || btn.dataset.cuSendWired === "1") return;
    btn.dataset.cuSendWired = "1";
    btn.disabled = false;
    function fireSend(ev) {
      if (ev) {
        ev.preventDefault();
        ev.stopPropagation();
      }
      onRun();
    }
    btn.addEventListener("click", fireSend);
    if (input) {
      input.addEventListener("input", function () {
        autoGrowPrompt();
        updateComposerChars();
      });
    }
  }

  function syncSendButtonState() {
    const raw = ($("prompt-input") && $("prompt-input").value) || "";
    const text = raw.trim();
    const mode = getForgeMode();
    let on = !opening && text.length > 0;
    if (mode === "chat") {
      if (chatSettings && chatSettings.require_workspace_for_chat && !inChatUnifyShell) {
        on = on && !!workspacePath;
      }
      if (inChatUnifyShell && text.length > 0) on = !opening;
    } else {
      on = on && !!workspacePath;
      if ($("opt-llm") && $("opt-llm").checked && !llmOnline) {
        on = false;
      }
    }
    setSendEnabled(on);
  }

  function autoGrowPrompt() {
    const el = $("prompt-input");
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 320) + "px";
  }

  function log(msg, kind) {
    const panel = $("tab-logs");
    if (!panel) return;
    const line = document.createElement("div");
    line.className = "forge-log-line" + (kind === "ok" ? " is-ok" : kind === "err" ? " is-err" : "");
    line.textContent = new Date().toLocaleTimeString() + " · " + msg;
    panel.prepend(line);
    while (panel.children.length > 200) panel.removeChild(panel.lastChild);
  }

  function setStatus(msg) {
    const el = $("sb-status");
    if (el) el.textContent = msg;
  }

  function folderLabel() {
    if (!workspacePath) return "No folder";
    const parts = workspacePath.split("/");
    return parts[parts.length - 1] || workspacePath;
  }

  function setStatusBar() {
    $("sb-workspace").textContent = "Folder · " + folderLabel();
    $("sb-model").textContent = "Model · " + lastModel;
    $("sb-time").textContent = "Time · " + lastTime;
    $("sb-cost").textContent = "Cost · " + lastCost;
  }

  function updateOnboardCard() {
    const card = $("forge-onboard-card");
    if (!card) return;
    card.hidden = !!workspacePath;
  }

  async function openPlatformWorkspace() {
    try {
      const sess = await api({ action: "platform_session_get" });
      const s = (sess && sess.session) || {};
      if (s.workspace_slug) {
        const row = await api({ action: "open_user_workspace", slug: s.workspace_slug });
        if (row.ok && row.path) {
          workspacePath = row.path;
          localStorage.setItem(WS_PATH_KEY, workspacePath);
          updateFolderUI();
          await loadSnapshot();
          loadChatThread();
          setStatus("Workspace open · " + folderLabel());
          log("platform workspace · " + row.path, "ok");
          return;
        }
      }
      if (s.project_name && s.email) {
        const prov = await api({
          action: "provision_user_workspace",
          email: s.email,
          name: s.name,
          org: s.org,
          project_name: s.project_name,
        });
        if (prov.ok && prov.path) {
          await openFolder(prov.path);
          return;
        }
      }
      if (window.parent === window) {
        window.open("https://sourcea.app/sourcea/forge/terminal/signin", "_blank");
      } else {
        log("Platform sign-in — use Chat Unify IDE tab when ready (no pop-up)", "warn");
      }
    } catch (e) {
      if (window.parent === window) {
        window.open("https://sourcea.app/sourcea/forge/terminal/signin", "_blank");
      }
      log("platform workspace: " + e, "err");
    }
  }

  async function maybeOpenPlatformWorkspaceFromUrl() {
    const slug = new URLSearchParams(window.location.search).get("workspace");
    if (slug) {
      try {
        const row = await api({ action: "open_user_workspace", slug: slug });
        if (row.ok && row.path) {
          await openFolder(row.path);
          return;
        }
      } catch (_) { /* fall through */ }
    }
    if (workspacePath) return;
    try {
      const sess = await api({ action: "platform_session_get" });
      const path = (sess.session && sess.session.workspace_path) || "";
      if (path) await openFolder(path);
    } catch (_) { /* quiet */ }
  }

  function updateFolderUI() {
    const pathEl = $("folder-path");
    const rootEl = $("ws-root-label");
    const openBtn = $("btn-open-folder");
    const editor = $("forge-main");

    if (rootEl) {
      rootEl.textContent = workspacePath ? folderLabel().toUpperCase() : "NO WORKSPACE";
    }
    if (pathEl) {
      if (workspacePath) {
        pathEl.textContent = workspacePath;
        pathEl.title = workspacePath;
        pathEl.classList.add("is-open");
      } else {
        pathEl.textContent = "Open a folder (⌘O)";
        pathEl.title = "";
        pathEl.classList.remove("is-open");
      }
    }
    if (openBtn) openBtn.disabled = opening;
    if (editor) {
      editor.classList.toggle("is-no-workspace", !workspacePath);
      editor.classList.remove("is-locked");
    }
    syncSendButtonState();
    updateOnboardCard();
    renderWorkspaceHub(recentWorkspaces);
  }

  function setDockOpen(open) {
    const col = $("forge-center-col");
    if (!col) return;
    col.classList.toggle("dock-collapsed", !open);
    localStorage.setItem(DOCK_KEY, open ? "1" : "0");
  }

  function toggleDock() {
    const col = $("forge-center-col");
    if (!col) return;
    setDockOpen(col.classList.contains("dock-collapsed"));
  }

  async function ensureForgeToken() {
    if (forgeToken) return forgeToken;
    try {
      const health = await fetch(window.location.origin + "/health").then(function (r) {
        return r.json();
      });
      if (health.forge_local_token) {
        forgeToken = health.forge_local_token;
        sessionStorage.setItem("forge_local_token", forgeToken);
      }
    } catch (_) { /* quiet */ }
    return forgeToken;
  }

  async function api(body) {
    await engineRouteReady;
    await ensureForgeToken();
    const payload = Object.assign({}, body || {});
    if (payload.living_chat) {
      delete payload.workspace_path;
    } else if (workspacePath && !(inChatUnifyShell && getForgeMode() === "chat")) {
      payload.workspace_path = workspacePath;
    }
    const t0 = performance.now();
    const headers = { "Content-Type": "application/json" };
    if (forgeToken) headers["X-Forge-Token"] = forgeToken;
    let row;
    const timeoutMs = payload.living_chat ? 60000 : 120000;
    try {
      row = await fetchJsonWithTimeout(
        API,
        { method: "POST", headers: headers, body: JSON.stringify(payload) },
        timeoutMs,
      );
    } catch (err) {
      if (forgeToken && /401|token/i.test(String(err.message || ""))) {
        forgeToken = "";
        sessionStorage.removeItem("forge_local_token");
        await ensureForgeToken();
        if (forgeToken) headers["X-Forge-Token"] = forgeToken;
        row = await fetchJsonWithTimeout(
          API,
          { method: "POST", headers: headers, body: JSON.stringify(payload) },
          timeoutMs,
        );
      } else {
        throw err;
      }
    }
    lastTime = ((performance.now() - t0) / 1000).toFixed(1) + "s";
    setStatusBar();
    return row;
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function looksLikeJsonBlob(text) {
    const s = String(text || "").trim();
    if (!s || (s[0] !== "{" && s[0] !== "[")) return false;
    try {
      JSON.parse(s);
      return true;
    } catch (_) {
      return false;
    }
  }

  function displayAssistantText(row) {
    const card = row.decision_card || {};
    const response = row.display_response || row.response || "";
    if (looksLikeJsonBlob(response)) {
      if (card.summary && !looksLikeJsonBlob(card.summary)) return card.summary;
      if (card.goal) return card.goal;
    }
    return response;
  }

  function renderFounderSections(text) {
    const names = ["Bottom line", "What this means for you", "Blockers", "Next step"];
    if (!names.some(function (n) { return String(text).indexOf(n) >= 0; })) return null;
    let html = '<div class="forge-founder-sections">';
    let rest = String(text || "");
    names.forEach(function (name, i) {
      const idx = rest.indexOf(name);
      if (idx < 0) return;
      let body = rest.slice(idx + name.length).trim();
      for (let j = i + 1; j < names.length; j++) {
        const nxt = body.indexOf(names[j]);
        if (nxt >= 0) {
          body = body.slice(0, nxt).trim();
          break;
        }
      }
      html +=
        '<section class="forge-founder-block"><h3 class="forge-founder-h">' +
        esc(name) +
        "</h3><p>" +
        esc(body).replace(/\n/g, "<br>") +
        "</p></section>";
    });
    html += "</div>";
    return html;
  }

  function renderMarkdown(text) {
    if (!text) return "";
    const founderHtml = renderFounderSections(text);
    if (founderHtml) return founderHtml;
    let html = esc(text);
    html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
    html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
    html = html.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");
    html = html.replace(/^[-*] (.+)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>\n?)+/g, function (m) { return "<ul>" + m + "</ul>"; });
    html = html.split(/\n\n+/).map(function (block) {
      if (/^<(h[123]|ul|pre)/.test(block.trim())) return block;
      return "<p>" + block.replace(/\n/g, "<br>") + "</p>";
    }).join("");
    return html;
  }

  function renderQualityChip(qg, container) {
    if (!qg || !container) return;
    const chip = document.createElement("div");
    chip.className = "forge-chat-quality-chip verdict-" + String(qg.verdict || "pending").toLowerCase();
    chip.innerHTML =
      "<strong>Quality " +
      esc(String(qg.verdict || "—")) +
      "</strong> · " +
      esc(String(qg.passed_layers || 0)) +
      "/" +
      esc(String(qg.total_layers || 11)) +
      " · score " +
      esc(String(qg.score || "—"));
    if (qg.eval_shadow && qg.eval_shadow.verdict) {
      const shadow = document.createElement("span");
      shadow.className = "forge-eval-shadow";
      shadow.textContent = "Eval: " + qg.eval_shadow.verdict;
      chip.appendChild(shadow);
    }
    container.appendChild(chip);
    lastQualityGate = qg;
    updateSelfHealVisibility();
    setExecButtonsEnabled(!!qg.execution_allowed);
  }

  function setDockHeight(px) {
    const col = $("forge-center-col");
    if (!col) return;
    const h = Math.max(120, Math.min(480, px));
    col.style.setProperty("--dock-h", h + "px");
    localStorage.setItem(DOCK_H_KEY, String(h));
  }

  function initDockResize() {
    const handle = $("dock-resize");
    const col = $("forge-center-col");
    if (!handle || !col) return;
    const saved = parseInt(localStorage.getItem(DOCK_H_KEY) || "200", 10);
    if (saved) setDockHeight(saved);
    let dragging = false;
    let startY = 0;
    let startH = 200;
    handle.addEventListener("mousedown", function (ev) {
      dragging = true;
      startY = ev.clientY;
      startH = parseInt(getComputedStyle(col).getPropertyValue("--dock-h") || "200", 10);
      document.body.style.cursor = "ns-resize";
      ev.preventDefault();
    });
    window.addEventListener("mousemove", function (ev) {
      if (!dragging) return;
      setDockHeight(startH - (ev.clientY - startY));
    });
    window.addEventListener("mouseup", function () {
      dragging = false;
      document.body.style.cursor = "";
    });
  }

  function initSidebarResize() {
    const handle = $("sidebar-resize");
    const bench = $("forge-workbench");
    if (!handle || !bench) return;
    const saved = parseInt(localStorage.getItem(SIDEBAR_W_KEY) || "240", 10);
    if (saved) bench.style.setProperty("--sidebar-w", saved + "px");
    let dragging = false;
    let startX = 0;
    let startW = 240;
    handle.addEventListener("mousedown", function (ev) {
      dragging = true;
      startX = ev.clientX;
      startW = parseInt(getComputedStyle(bench).getPropertyValue("--sidebar-w") || "240", 10);
      document.body.style.cursor = "ew-resize";
      ev.preventDefault();
    });
    window.addEventListener("mousemove", function (ev) {
      if (!dragging) return;
      const w = Math.max(160, Math.min(420, startW + (ev.clientX - startX)));
      bench.style.setProperty("--sidebar-w", w + "px");
      localStorage.setItem(SIDEBAR_W_KEY, String(w));
    });
    window.addEventListener("mouseup", function () {
      dragging = false;
      document.body.style.cursor = "";
    });
  }

  function setResponse(text, asMarkdown) {
    const body = $("response-body");
    const ph = $("response-placeholder");
    if (!body) return;
    if (ph) ph.hidden = true;
    if (asMarkdown) {
      body.innerHTML = renderMarkdown(text);
    } else {
      body.textContent = text;
    }
  }

  function renderFileTree(scan) {
    const tree = $("file-tree");
    if (!tree) return;
    const entries = (scan && scan.entries) || [];
    if (!entries.length) {
      tree.innerHTML = '<span class="forge-muted forge-tree-empty">Empty project</span>';
      return;
    }
    tree.innerHTML = entries
      .map(function (e) {
        const icon = e.dir ? "▸" : "·";
        return (
          '<div class="forge-tree-row' +
          (e.dir ? "" : " is-file") +
          '" data-path="' +
          esc(e.path || e.name) +
          '" title="' +
          esc(e.path) +
          '"><span class="forge-tree-icon">' +
          icon +
          "</span>" +
          esc(e.name) +
          "</div>"
        );
      })
      .join("");
    tree.querySelectorAll(".forge-tree-row.is-file").forEach(function (row) {
      row.addEventListener("click", function () {
        openFileInEditor(row.getAttribute("data-path") || "");
      });
    });
  }

  function renderAgents(agents) {
    const ul = $("agents-list");
    if (!ul) return;
    const list = agents && agents.length ? agents : [
      { id: "planner", description: "Plans missions" },
      { id: "builder", description: "Executes builds" },
      { id: "verifier", description: "Verifies output" },
    ];
    ul.innerHTML = list
      .map(function (a) {
        const id = (a.id || a.role || "agent").toLowerCase();
        const active = id === selectedAgentId() ? " is-active" : "";
        return (
          '<li class="' +
          active.trim() +
          '" data-agent="' +
          esc(id) +
          '" title="Select ' +
          esc(id) +
          ' agent"><span class="forge-agent-dot"></span><div><strong>' +
          esc(id) +
          "</strong><span>" +
          esc(a.description || "") +
          "</span></div></li>"
        );
      })
      .join("");
    ul.querySelectorAll("li").forEach(function (li) {
      li.addEventListener("click", function () {
        const id = li.getAttribute("data-agent") || "builder";
        localStorage.setItem(AGENT_KEY, id);
        const sel = $("agent-select");
        if (sel) sel.value = id;
        ul.querySelectorAll("li").forEach(function (x) {
          x.classList.toggle("is-active", x === li);
        });
      });
    });
  }

  function setEmbedSidebarCollapsed(collapsed) {
    const app = $("forge-app");
    const bench = $("forge-workbench");
    const sidebar = document.querySelector(".forge-sidebar");
    const resize = $("sidebar-resize");
    const toggle = $("embed-sidebar-toggle");
    if (sidebar) sidebar.classList.toggle("is-collapsed", collapsed);
    if (resize) resize.classList.toggle("is-collapsed", collapsed);
    if (bench) bench.classList.toggle("sidebar-collapsed", collapsed);
    if (toggle) {
      toggle.textContent = collapsed ? "Show workspaces" : "Hide workspaces";
      toggle.setAttribute("aria-pressed", collapsed ? "false" : "true");
    }
    if (app && app.classList.contains("forge-embed")) {
      localStorage.setItem(EMBED_SIDEBAR_KEY, collapsed ? "0" : "1");
    }
  }

  function applyPills(row) {
    const llm = row.llm || {};
    const llmOk = llm.openrouter_ready || llm.gemini_ready || llm.openai_ready || llm.anthropic_ready;
    const pillLlm = $("pill-llm");
    const pillAnthropic = $("pill-anthropic");
    const pillCloud = $("pill-cloud");
    const pillChat = $("pill-chat-unify");
    if (pillLlm) {
      pillLlm.textContent = llmOk ? "LLM live" : "LLM keys missing";
      pillLlm.classList.toggle("forge-pill-live", !!llmOk);
      pillLlm.classList.toggle("forge-pill-down", !llmOk);
    }
    if (pillAnthropic) {
      const on = !!llm.anthropic_ready;
      pillAnthropic.textContent = on ? "Anthropic ✓" : "Anthropic — add key";
      pillAnthropic.classList.toggle("forge-pill-live", on);
      pillAnthropic.classList.toggle("forge-pill-down", !on);
      pillAnthropic.title = on
        ? "ANTHROPIC_API_KEY loaded from ~/.sina/secrets.env"
        : "Add ANTHROPIC_API_KEY to ~/.sina/secrets.env (template: data/forge-secrets-env-template-v1.env)";
    }
    if (pillCloud) {
      const live = row.cloud_workers === "LIVE";
      pillCloud.textContent = "Cloud " + (row.cloud_workers || "…");
      pillCloud.classList.toggle("forge-pill-live", live);
      pillCloud.classList.toggle("forge-pill-down", !live);
    }
    if (pillChat && row.desktop_mesh) {
      const cu = row.desktop_mesh.chat_unify || "offline";
      pillChat.textContent = "Unify " + cu;
      pillChat.classList.toggle("forge-pill-live", cu === "live");
      pillChat.classList.toggle("forge-pill-down", cu === "offline");
    }
    if (row.desktop_mesh) applyMesh(row.desktop_mesh);
  }

  function applyMesh(mesh) {
    renderMeshList(mesh.peers || []);
    renderConnectPanel(mesh);
    renderForgeToolsDeck(mesh, null);
  }

  function renderMeshList(peers) {
    const el = $("mesh-list");
    if (!el) return;
    if (!peers.length) {
      el.innerHTML = '<span class="forge-muted" style="font-size:10px;padding:0 4px">Probing…</span>';
      return;
    }
    el.innerHTML = peers
      .filter(function (p) { return p.id !== "forge_terminal"; })
      .map(function (p) {
        const live = p.status === "live";
        return (
          '<button type="button" class="forge-mesh-row' +
          (live ? " is-live" : "") +
          '" data-peer="' +
          esc(p.id) +
          '" data-url="' +
          esc(p.url || "") +
          '" title="' +
          esc(p.role || "") +
          '"><span class="forge-mesh-dot"></span><span class="forge-mesh-label">' +
          esc(p.label) +
          '</span><span class="forge-mesh-port">:' +
          esc(String(p.port || "")) +
          "</span></button>"
        );
      })
      .join("");
    el.querySelectorAll(".forge-mesh-row").forEach(function (btn) {
      btn.addEventListener("click", function () {
        openPeerUrl(btn.getAttribute("data-url"));
      });
    });
  }

  function renderConnectPanel(mesh) {
    const panel = $("tab-connect");
    if (!panel) return;
    const peers = mesh.peers || [];
    const actions = inChatUnifyShell
      ? '<div class="forge-connect-actions">' +
        '<button type="button" class="forge-btn forge-btn-ghost forge-connect-btn" data-peer="cloud_workers">Cloud Workers · open</button>' +
        "</div>"
      : '<div class="forge-connect-actions">' +
        '<button type="button" class="forge-btn forge-btn-ghost forge-connect-btn" data-peer="chat_unify" data-dispatch="1">Chat Unify · ping</button>' +
        "</div>";
    panel.innerHTML =
      '<div class="forge-connect-head">Desktop mesh · ' +
      esc(String(mesh.live_peers || 0)) +
      "/" +
      esc(String(peers.length)) +
      (inChatUnifyShell ? " live · Chat Unify workspace" : " live · Forge Terminal") +
      "</div>" +
      actions +
      peers
        .map(function (p) {
          const live = p.status === "live";
          return (
            '<div class="forge-connect-row' +
            (live ? " is-live" : "") +
            '"><strong>' +
            esc(p.label) +
            "</strong> · " +
            esc(p.status) +
            (p.url
              ? ' · <button type="button" class="forge-link-btn" data-open-url="' +
                esc(p.url) +
                '">open</button>'
              : "") +
            "</div>"
          );
        })
        .join("");
    panel.querySelectorAll("[data-open-url]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        openPeerUrl(btn.getAttribute("data-open-url"));
      });
    });
    panel.querySelectorAll(".forge-connect-btn").forEach(function (btn) {
      btn.addEventListener("click", async function () {
        const peer = btn.getAttribute("data-peer") || "";
        const peerRow = peers.find(function (p) { return p.id === peer; });
        if (btn.getAttribute("data-dispatch") === "1") {
          setStatus("Pinging " + peer + "…");
          try {
            const row = await api({
              action: "peer_dispatch",
              peer: peer,
              text: ($("prompt-input") && $("prompt-input").value.trim()) || "forge terminal mesh ping",
              dry_run: true,
            });
            log(peer + " ping · " + (row.ok ? "ok" : row.error || "fail"), row.ok ? "ok" : "err");
            setStatus(row.ok ? peer + " live" : peer + " ping failed");
          } catch (e) {
            log(String(e.message || e), "err");
            setStatus(peer + " ping failed");
          }
          return;
        }
        openPeerUrl((peerRow && peerRow.url) || (peer === "chat_unify" ? "http://127.0.0.1:13023/" : "http://127.0.0.1:13027/"));
      });
    });
  }

  let settingsOpen = false;
  let lastSettingsRow = null;
  let chatSettings = null;

  function renderSettingsPanel(row) {
    const panel = $("settings-panel");
    if (!panel || !row || !row.ok) return;
    lastSettingsRow = row;
    const s = row.settings || {};
    const models = row.models || [];
    const modelList = $("settings-model-list");
    if (modelList) {
      modelList.innerHTML = models
        .slice(0, 24)
        .map(function (m) {
          const id = m.id || m.api_model || "";
          const label = m.label || id;
          const cost = m.cost_band || m.cost || "";
          return (
            '<div class="forge-settings-model"><code>' +
            id +
            "</code><span>" +
            label +
            (cost ? " · " + cost : "") +
            "</span></div>"
          );
        })
        .join("");
    }
    const set = function (id, val) {
      const el = $(id);
      if (el) el.value = val || "";
    };
    set("settings-default-model", s.default_model);
    set("settings-brain-url", s.brain_worker_url);
    set("settings-cloud-url", s.cloud_worker_url);
    set("settings-unify-url", s.chat_unify_url);
    const req = $("settings-require-ws");
    if (req) req.checked = !!s.require_workspace_for_chat;
    const fb = $("settings-fallback-or");
    if (fb) fb.checked = s.fallback_openrouter !== false;
    const pathEl = $("settings-path-label");
    if (pathEl) pathEl.textContent = row.path || "~/.sina/forge-chat-settings-v1.json";
    const brainPath = $("settings-brain-config-path");
    if (brainPath) brainPath.textContent = row.brain_config_path || "";
    const llm = (lastLightStatus && lastLightStatus.llm) || {};
    const liveEl = $("settings-llm-live");
    if (liveEl) {
      const bits = [];
      if (llm.gemini_ready) bits.push("Gemini");
      if (llm.openrouter_ready) bits.push("OpenRouter");
      if (llm.anthropic_ready) bits.push("Anthropic");
      if (llm.openai_ready) bits.push("OpenAI");
      liveEl.textContent = bits.length ? "Live: " + bits.join(" · ") : "LLM offline — check ~/.sina/secrets.env";
      liveEl.classList.toggle("is-live", bits.length > 0);
    }
  }

  let lastLightStatus = null;

  async function loadChatSettings() {
    try {
      const row = await api({ action: "chat_settings_get" });
      if (row && row.settings) chatSettings = row.settings;
      renderSettingsPanel(row);
      return row;
    } catch (e) {
      log("settings load failed: " + e, "err");
      return null;
    }
  }

  async function saveChatSettings() {
    const payload = {
      default_model: ($("settings-default-model") && $("settings-default-model").value) || "",
      brain_worker_url: ($("settings-brain-url") && $("settings-brain-url").value) || "",
      cloud_worker_url: ($("settings-cloud-url") && $("settings-cloud-url").value) || "",
      chat_unify_url: ($("settings-unify-url") && $("settings-unify-url").value) || "",
      require_workspace_for_chat: !!($("settings-require-ws") && $("settings-require-ws").checked),
      fallback_openrouter: !!($("settings-fallback-or") && $("settings-fallback-or").checked),
    };
    const sel = $("model-select");
    if (sel && payload.default_model) {
      if (Array.from(sel.options).some(function (o) { return o.value === payload.default_model; })) {
        sel.value = payload.default_model;
        lastModel = sel.value;
        localStorage.setItem(MODEL_KEY, lastModel);
        updateModelHint();
      }
    }
    try {
      const row = await api({ action: "chat_settings_save", settings: payload });
      if (row && row.settings) chatSettings = row.settings;
      renderSettingsPanel(row);
      setStatus("Chat settings saved");
      log("settings saved → " + (row.path || ""), "ok");
      syncSendButtonState();
    } catch (e) {
      setStatus("Settings save failed");
      log(String(e.message || e), "err");
    }
  }

  const LIVING_CHIPS = [
    { label: "Ship 48h MVP", text: "I need a 48-hour MVP — what's the intake path and what proof do I get?", accent: true },
    { label: "Pricing", text: "What would you charge for governed agent ops for a 12-person agency?" },
    { label: "See live receipt", text: "Show me what a client receives as proof after a job completes — no call needed." },
    { label: "Client QBR audit", text: "Audit my agency's AI deliverables before a client QBR next week" },
    { label: "I'm new here", text: "I'm new to agentic AI — what's the simplest path to learn and build on SourceA?" },
  ];

  function formatChatTime(d) {
    const dt = d || new Date();
    return dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function initLivingChips() {
    const row = $("forge-chat-chips");
    if (!row) return;
    row.innerHTML = "";
    LIVING_CHIPS.forEach(function (chip) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "forge-chat-chip" + (chip.accent ? " is-accent" : "");
      btn.textContent = chip.label;
      btn.addEventListener("click", function () {
        const input = $("prompt-input");
        if (input) {
          input.value = chip.text;
          autoGrowPrompt();
          updateComposerChars();
          input.focus();
        }
      });
      row.appendChild(btn);
    });
  }

  function updateComposerChars() {
    const input = $("prompt-input");
    const el = $("composer-chars");
    if (!input || !el) return;
    const n = (input.value || "").length;
    el.textContent = n > 0 ? n + " chars" : "";
    syncSendButtonState();
  }

  function isEmbedScrollMode() {
    const app = $("forge-app");
    return !!(app && app.classList.contains("forge-embed"));
  }

  function isDesktopApp() {
    return (
      window.__FORGE_DESKTOP_APP__ === true ||
      new URLSearchParams(window.location.search).get("desktop") === "1"
    );
  }

  function isEditorWindowMode() {
    const desktop =
      document.body.classList.contains("forge-desktop-app") ||
      document.documentElement.classList.contains("forge-desktop-app");
    return !!$("forge-editor-window") && (desktop || inChatUnifyShell);
  }

  function isWindowNearBottom() {
    const doc = document.documentElement;
    return doc.scrollHeight - window.scrollY - window.innerHeight < CHAT_SCROLL_THRESHOLD;
  }

  function chatScrollElement() {
    if (isEditorWindowMode()) return $("chat-thread");
    const root = embedScrollRoot();
    return root || $("chat-thread");
  }

  function enableEditorWindow() {
    const editor = $("forge-editor-window");
    if (editor) editor.classList.add("is-active");
    const live = $("forge-chat-live-window");
    if (live) live.classList.add("forge-editor-body");
    const thread = $("chat-thread");
    if (thread) thread.classList.add("forge-editor-scroll");
    const col = $("forge-main");
    if (col) {
      col.style.setProperty("overflow", "visible", "important");
      col.style.setProperty("height", "auto", "important");
    }
    sizeEditorPanes();
    if (typeof ResizeObserver !== "undefined") {
      const editor = $("forge-editor-window");
      if (editor && !editor.__forgePaneRo) {
        editor.__forgePaneRo = new ResizeObserver(function () {
          sizeEditorPanes();
          if (chatStickToBottom) scrollChatToBottom(true);
        });
        editor.__forgePaneRo.observe(editor);
      }
    }
    window.addEventListener(
      "resize",
      function () {
        sizeEditorPanes();
        if (chatStickToBottom) scrollChatToBottom(true);
      },
      { passive: true },
    );
  }

  function forceScrollUnlock() {
    document.documentElement.classList.add("forge-desktop-app", "forge-page-scroll", "forge-embed-root");
    document.body.classList.add("forge-desktop-app", "forge-page-scroll", "forge-embed-root");
    document.documentElement.style.setProperty("overflow-y", "scroll", "important");
    document.body.style.setProperty("overflow-y", "scroll", "important");
    document.body.style.setProperty("height", "auto", "important");
    const app = $("forge-app");
    if (app) {
      app.classList.add("forge-embed", "forge-desktop-app", "forge-page-scroll");
      app.style.setProperty("height", "auto", "important");
      app.style.setProperty("min-height", "100%", "important");
      app.style.setProperty("overflow", "visible", "important");
    }
    const bench = $("forge-workbench");
    if (bench) {
      bench.style.setProperty("height", "auto", "important");
      bench.style.setProperty("overflow", "visible", "important");
    }
    const col = $("forge-center-col");
    if (col) {
      col.style.setProperty("--dock-h", "340px");
      col.style.setProperty("overflow", "visible", "important");
      col.style.setProperty("height", "auto", "important");
    }
    const composer = $("forge-composer");
    if (composer) composer.style.setProperty("position", "static", "important");
    localStorage.setItem(DOCK_KEY, "1");
    setDockOpen(true);
    enableEditorWindow();
    if (lastThreadTurns && lastThreadTurns.length) scheduleScrollToLatest();
    reportEmbedHeight();
  }

  function reportEmbedHeight() {
    if (window.parent === window) return;
    const app = $("forge-app");
    const h = Math.max(
      document.documentElement.scrollHeight || 0,
      document.body.scrollHeight || 0,
      app ? app.offsetHeight : 0,
      window.innerHeight + (inChatUnifyShell ? 1400 : 600)
    );
    window.parent.postMessage({ type: "forge-ide-height", height: h }, "*");
  }

  function openGatePanel() {
    gateDrawerOpen = true;
    const panel = $("decision-panel");
    if (panel) {
      panel.hidden = false;
      panel.removeAttribute("hidden");
    }
    const btn = $("btn-toggle-gate");
    if (btn) btn.classList.add("is-active");
    settingsOpen = false;
    const sp = $("settings-panel");
    if (sp) sp.hidden = true;
    const sb = $("btn-forge-settings");
    if (sb) sb.classList.remove("is-active");
  }

  function openSettingsPanel() {
    settingsOpen = true;
    const panel = $("settings-panel");
    if (panel) {
      panel.hidden = false;
      panel.removeAttribute("hidden");
    }
    const btn = $("btn-forge-settings");
    if (btn) btn.classList.add("is-active");
    gateDrawerOpen = false;
    const dp = $("decision-panel");
    if (dp) dp.hidden = true;
    const gb = $("btn-toggle-gate");
    if (gb) gb.classList.remove("is-active");
    loadChatSettings();
  }

  function initForgeToolsDeck() {
    $("btn-deck-jump-gate") &&
      $("btn-deck-jump-gate").addEventListener("click", function () {
        openGatePanel();
        const gate = $("decision-panel");
        if (gate) gate.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    $("btn-deck-jump-settings") &&
      $("btn-deck-jump-settings").addEventListener("click", function () {
        openSettingsPanel();
        const panel = $("settings-panel");
        if (panel) panel.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    renderMachinesDeck(null);
  }

  function renderForgeConnectDeck(mesh) {
    const el = $("forge-tool-connect-deck");
    if (!el) return;
    const peers = (mesh && mesh.peers) || [];
    if (!peers.length) {
      el.innerHTML = '<span class="forge-muted">Probing execution mesh…</span>';
      return;
    }
    el.innerHTML = peers
      .map(function (p) {
        const live = p.status === "live";
        const separate = p.id === "chat_unify" ? ' <span class="forge-muted">· separate app</span>' : "";
        return (
          '<div class="forge-connect-row' +
          (live ? " is-live" : "") +
          '"><strong>' +
          esc(p.label) +
          "</strong> · " +
          esc(p.status) +
          separate +
          "</div>"
        );
      })
      .join("");
  }

  function renderForgeTasksDeck(tasks) {
    const el = $("forge-tool-tasks-deck");
    if (!el) return;
    el.innerHTML = (tasks || []).length
      ? tasks
          .slice(0, 8)
          .map(function (t) {
            return (
              "<div><strong>" +
              esc(t.task_id) +
              "</strong> " +
              esc(t.status) +
              " · " +
              esc((t.founder_text || "").slice(0, 80)) +
              "</div>"
            );
          })
          .join("")
      : '<span class="forge-muted">Open a workspace — tasks appear here</span>';
  }

  function renderForgeReceiptsDeck(recs) {
    const el = $("forge-tool-receipts-deck");
    if (!el) return;
    el.innerHTML = (recs || []).length
      ? recs
          .slice(0, 6)
          .map(function (r) {
            return "<div><strong>" + esc(r.run_id || r.file) + "</strong> · " + esc(r.at || "") + "</div>";
          })
          .join("")
      : '<span class="forge-muted">No receipts yet</span>';
  }

  function renderForgeQualityDeck() {
    const el = $("forge-tool-quality-deck");
    if (!el) return;
    const verdict = $("quality-verdict");
    const score = $("quality-score");
    el.innerHTML =
      "<div>Verdict: <strong>" +
      esc((verdict && verdict.textContent) || "—") +
      "</strong></div>" +
      "<div class='forge-muted'>" +
      esc((score && score.textContent) || "Send a message to run quality gate") +
      "</div>";
  }

  function renderForgeSettingsDeck() {
    const el = $("forge-tool-settings-deck");
    if (!el) return;
    const model = $("sb-model");
    const ws = $("sb-workspace");
    el.innerHTML =
      "<div>Workspace: " + esc((ws && ws.textContent) || "—") + "</div>" +
      "<div>Model: " + esc((model && model.textContent) || "—") + "</div>";
  }

  async function renderForgeOutboxDeck() {
    const el = $("forge-tool-outbox-deck");
    if (!el) return;
    if (!runId) {
      el.innerHTML = '<span class="forge-muted">No active run</span>';
      return;
    }
    try {
      const row = await api({ action: "poll_outbox", run_id: runId });
      el.textContent =
        row.outbox && row.outbox.payload ? JSON.stringify(row.outbox, null, 2).slice(0, 800) : "(empty)";
    } catch (_) {
      el.innerHTML = '<span class="forge-muted">Outbox unavailable</span>';
    }
  }

  function renderMachinesDeck(mesh) {
    const grid = $("forge-machines-grid");
    if (!grid) return;
    if (inChatUnifyShell && window.parent !== window) {
      const cuTiles = [
        { tab: "forge-ide", label: "Workspace", sub: "IDE · build", here: true },
        { tab: "home", label: "Chat", sub: "paste · unify" },
        { tab: "founder", label: "Verify & Act", sub: "PASS / BLOCK" },
        { tab: "ord", label: "Audit Trail", sub: "trace · disk" },
        { tab: "forge", label: "Mission builder", sub: "intent → mission" },
        { tab: "connect", label: "Connect", sub: "wire stack" },
        { tab: "form", label: "Decisions", sub: "approve scope" },
        { tab: "api", label: "Tasks", sub: "queue · dispatch" },
        { tab: "hubpro", label: "Operations", sub: "skills · log" },
        { tab: "proofpack", label: "Proof Pack", sub: "seal · deliver" },
        { tab: "vocab", label: "Vocabulary", sub: "scan · classify" },
        { tab: "start", label: "Start", sub: "guide" },
      ];
      grid.innerHTML = cuTiles
        .map(function (t) {
          return (
            '<article class="forge-machine-tile' +
            (t.here ? " is-here" : "") +
            ' is-live"><div class="forge-machine-top"><strong>' +
            esc(t.label) +
            '</strong><span class="forge-machine-port">' +
            esc(t.sub) +
            '</span></div><p class="forge-machine-note">Chat Unify machine · opens in app shell above</p><button type="button" class="forge-btn forge-btn-ghost forge-btn-sm forge-machine-open" data-cu-tab="' +
            esc(t.tab) +
            '"' +
            (t.here ? " disabled" : "") +
            ">" +
            (t.here ? "Current" : "Open") +
            "</button></article>"
          );
        })
        .join("");
      grid.querySelectorAll("[data-cu-tab]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          const tab = btn.getAttribute("data-cu-tab");
          if (tab) window.parent.postMessage({ type: "cu-goto-tab", tab: tab }, "*");
        });
      });
      reportEmbedHeight();
      return;
    }
    const peers = (mesh && mesh.peers) || [];
    const byId = {};
    peers.forEach(function (p) {
      byId[p.id] = p;
    });
    const tiles = [
      { id: "hub", label: "SourceA Hub", port: "13020", url: "http://127.0.0.1:13020/" },
      { id: "cloud_workers", label: "Cloud Workers", port: "13027", url: "http://127.0.0.1:13027/" },
      { id: "forge_terminal", label: "Forge Terminal", port: "13029", url: "http://127.0.0.1:13029/", here: true },
      { id: "chat_unify", label: "Chat Unify", port: "13023", url: "http://127.0.0.1:13023/", separate: true },
    ];
    grid.innerHTML = tiles
      .map(function (t) {
        const peer = byId[t.id] || byId[t.id.replace("_", "")] || null;
        const live = peer && peer.status === "live";
        return (
          '<article class="forge-machine-tile' +
          (t.here ? " is-here" : "") +
          (live ? " is-live" : "") +
          '"><div class="forge-machine-top"><strong>' +
          esc(t.label) +
          "</strong><span class=\"forge-machine-port\">:" +
          esc(t.port) +
          '</span></div><p class="forge-machine-note">' +
          (t.here ? "You are here · editor + chat" : t.separate ? "Separate app · not wired into this IDE" : "Forge Terminal machine") +
          (live ? " · live" : peer ? " · " + esc(peer.status) : "") +
          '</p><button type="button" class="forge-btn forge-btn-ghost forge-btn-sm forge-machine-open" data-open-url="' +
          esc(t.url) +
          '"' +
          (t.here ? " disabled" : "") +
          ">" +
          (t.here ? "Current" : "Open") +
          "</button></article>"
        );
      })
      .join("");
    grid.querySelectorAll(".forge-machine-open").forEach(function (btn) {
      btn.addEventListener("click", function () {
        openPeerUrl(btn.getAttribute("data-open-url"));
      });
    });
  }

  function renderForgeToolsDeck(mesh, snapshot) {
    renderMachinesDeck(mesh);
    renderForgeConnectDeck(mesh);
    if (snapshot) {
      renderForgeTasksDeck(snapshot.tasks);
      renderForgeReceiptsDeck(snapshot.receipts);
    }
    renderForgeQualityDeck();
    renderForgeSettingsDeck();
    renderForgeOutboxDeck();
  }

  function embedScrollRoot() {
    if (isEditorWindowMode()) return null;
    if (document.body.classList.contains("forge-desktop-app")) return document.body;
    if (document.body.classList.contains("forge-page-scroll")) return document.body;
    if (isEmbedScrollMode()) return $("forge-center-col");
    return null;
  }

  function isScrollNearBottom(el) {
    if (!el) return true;
    return el.scrollHeight - el.scrollTop - el.clientHeight < CHAT_SCROLL_THRESHOLD;
  }

  function isChatNearBottom(thread) {
    const el = chatScrollElement();
    return isScrollNearBottom(el || thread);
  }

  function ensureChatSpacer() {
    const thread = $("chat-thread");
    if (!thread) return null;
    if (isEditorWindowMode()) {
      const old = $("chat-thread-spacer");
      if (old) old.remove();
      return null;
    }
    let spacer = $("chat-thread-spacer");
    if (!spacer) {
      spacer = document.createElement("div");
      spacer.id = "chat-thread-spacer";
      spacer.className = "forge-chat-spacer";
      spacer.setAttribute("aria-hidden", "true");
      thread.insertBefore(spacer, thread.firstChild);
    } else if (thread.firstChild !== spacer) {
      thread.insertBefore(spacer, thread.firstChild);
    }
    return spacer;
  }

  let _sizingEditorPanes = false;

  function sizeEditorPanes() {
    if (_sizingEditorPanes) return;
    _sizingEditorPanes = true;
    try {
    const editor = $("forge-editor-window");
    const msgWin = $("forge-message-window");
    const thread = $("chat-thread");
    const live = $("forge-chat-live-window");
    if (!editor || !msgWin || !isEditorWindowMode()) return;

    if (inChatUnifyShell && document.body.classList.contains("forge-cu-combined")) {
      if (live) {
        live.style.setProperty("flex", "1 1 auto", "important");
        live.style.setProperty("min-height", "0", "important");
        live.style.setProperty("overflow", "hidden", "important");
        live.style.setProperty("display", "flex", "important");
        live.style.setProperty("flex-direction", "column", "important");
        live.style.removeProperty("height");
        live.style.removeProperty("max-height");
      }
      msgWin.style.setProperty("flex", "1 1 auto", "important");
      msgWin.style.setProperty("min-height", "200px", "important");
      msgWin.style.setProperty("overflow", "hidden", "important");
      msgWin.style.setProperty("display", "flex", "important");
      msgWin.style.setProperty("flex-direction", "column", "important");
      msgWin.style.removeProperty("height");
      msgWin.style.removeProperty("max-height");
      if (thread) {
        thread.style.setProperty("flex", "1 1 auto", "important");
        thread.style.setProperty("min-height", "120px", "important");
        thread.style.setProperty("overflow-y", "auto", "important");
        thread.style.setProperty("overflow-x", "hidden", "important");
        thread.style.setProperty("display", "block", "important");
        thread.style.removeProperty("height");
        thread.style.removeProperty("max-height");
      }
      reportEmbedHeight();
      return;
    }

    const toolbar = editor.querySelector(".forge-editor-toolbar");
    const composer = $("forge-composer");
    const strip = $("exec-strip");
    let used = 0;
    if (toolbar) used += toolbar.offsetHeight;
    if (composer) used += composer.offsetHeight;
    used += 20;
    const editorH = Math.max(inChatUnifyShell ? 960 : 480, editor.clientHeight || window.innerHeight - 80);
    const liveH = Math.max(inChatUnifyShell ? 560 : 280, editorH - used);
    if (live) {
      live.style.setProperty("height", liveH + "px", "important");
      live.style.setProperty("max-height", liveH + "px", "important");
      live.style.setProperty("flex", "1 1 auto", "important");
      live.style.setProperty("min-height", "0", "important");
      live.style.setProperty("overflow", "hidden", "important");
      live.style.setProperty("display", "flex", "important");
      live.style.setProperty("flex-direction", "column", "important");
    }
    const stripH = strip && !strip.hidden ? strip.offsetHeight : 0;
    const msgOuterH = Math.max(inChatUnifyShell ? 440 : 220, liveH - stripH - 12);
    msgWin.style.setProperty("height", msgOuterH + "px", "important");
    msgWin.style.setProperty("max-height", msgOuterH + "px", "important");
    msgWin.style.setProperty("min-height", (inChatUnifyShell ? "440px" : "220px"), "important");
    msgWin.style.setProperty("flex", "1 1 auto", "important");
    msgWin.style.setProperty("overflow", "hidden", "important");
    const head = msgWin.querySelector(".forge-message-window-head");
    const headH = head && head.offsetParent !== null ? head.offsetHeight : 0;
    if (thread) {
      const threadH = Math.max(inChatUnifyShell ? 320 : 160, msgOuterH - headH);
      thread.style.setProperty("height", threadH + "px", "important");
      thread.style.setProperty("max-height", threadH + "px", "important");
      thread.style.setProperty("min-height", "160px", "important");
      thread.style.setProperty("overflow-y", "scroll", "important");
      thread.style.setProperty("overflow-x", "hidden", "important");
      thread.style.setProperty("display", "block", "important");
      thread.style.removeProperty("justify-content");
    }
    } finally {
      _sizingEditorPanes = false;
    }
  }

  function ensureChatAnchor() {
    const thread = $("chat-thread");
    if (!thread) return null;
    let anchor = $("chat-thread-anchor");
    if (!anchor) {
      anchor = document.createElement("div");
      anchor.id = "chat-thread-anchor";
      anchor.className = "forge-chat-anchor";
      anchor.setAttribute("aria-hidden", "true");
      thread.appendChild(anchor);
    } else if (anchor.parentElement !== thread) {
      thread.appendChild(anchor);
    }
    return anchor;
  }

  function scheduleScrollToLatest() {
    chatStickToBottom = true;
    ensureChatAtLatest();
    [0, 40, 120, 280, 520, 900, 1400, 2200].forEach(function (ms) {
      setTimeout(ensureChatAtLatest, ms);
    });
  }

  function updateJumpLatestButton() {
    const btn = $("btn-jump-latest");
    if (!btn) return;
    if (chatStickToBottom) btn.setAttribute("hidden", "");
    else btn.removeAttribute("hidden");
  }

  function ensureChatAtLatest() {
    chatStickToBottom = true;
    const thread = $("chat-thread");
    if (thread) thread.classList.remove("is-user-scrolling");
    scrollChatToBottom(true);
    updateJumpLatestButton();
  }

  function scrollChatToBottom(force) {
    const scrollEl = chatScrollElement();
    if (!scrollEl) return;
    if (!force && !chatStickToBottom) return;
    if (isEditorWindowMode()) {
      const editor = $("forge-editor-window");
      if (editor && !editor.classList.contains("is-active")) enableEditorWindow();
      else sizeEditorPanes();
    } else {
      ensureChatSpacer();
    }
    const anchor = ensureChatAnchor();
    let frames = 0;
    function snap() {
      if (scrollEl.clientHeight < 48 && frames < 20) {
        frames += 1;
        requestAnimationFrame(snap);
        return;
      }
      const max = Math.max(0, scrollEl.scrollHeight - scrollEl.clientHeight);
      scrollEl.scrollTop = max;
      if (anchor) {
        const anchorBottom = anchor.offsetTop + anchor.offsetHeight;
        scrollEl.scrollTop = Math.max(max, anchorBottom - scrollEl.clientHeight);
      }
      frames += 1;
      if (frames < 14) requestAnimationFrame(snap);
    }
    snap();
  }

  function initSmartChatScroll() {
    const thread = $("chat-thread");
    const scrollEl = chatScrollElement();
    if (!scrollEl) return;
    scrollEl.addEventListener(
      "scroll",
      function () {
        chatStickToBottom = isScrollNearBottom(scrollEl);
        if (thread) thread.classList.toggle("is-user-scrolling", !chatStickToBottom);
        updateJumpLatestButton();
      },
      { passive: true },
    );
    if (typeof MutationObserver !== "undefined" && thread) {
      const mo = new MutationObserver(function () {
        if (chatStickToBottom) scrollChatToBottom(false);
        reportEmbedHeight();
      });
      mo.observe(thread, { childList: true, subtree: true, characterData: true });
    }
    if (typeof ResizeObserver !== "undefined") {
      const ro = new ResizeObserver(function () {
        if (chatStickToBottom) scrollChatToBottom(false);
        reportEmbedHeight();
      });
      ro.observe(thread || scrollEl);
      if (thread && scrollEl !== thread) ro.observe(scrollEl);
    }
  }

  function appendChatBubble(role, text, meta, opts) {
    opts = opts || {};
    const thread = $("chat-thread");
    const ph = $("chat-placeholder");
    if (!thread) return;
    if (ph) ph.remove();
    if (!isEditorWindowMode()) ensureChatSpacer();
    const anchor = ensureChatAnchor();
    const bubble = document.createElement("div");
    bubble.className = "forge-chat-bubble forge-chat-" + role + (role === "typing" ? " is-typing" : "");
    const timeEl = document.createElement("div");
    timeEl.className = "forge-chat-time";
    timeEl.textContent = formatChatTime();
    const inner = document.createElement("div");
    inner.className = "forge-chat-inner" + (role === "assistant" && meta !== "plain" ? " forge-markdown" : "");
    if (role === "typing") {
      inner.innerHTML = '<span class="forge-typing-dots" aria-label="Thinking"><span></span><span></span><span></span></span>';
    } else if (role === "assistant" && meta !== "plain") {
      inner.innerHTML = renderMarkdown(text);
    } else {
      inner.textContent = text;
    }
    if (role === "user") {
      bubble.appendChild(timeEl);
      bubble.appendChild(inner);
    } else {
      bubble.appendChild(inner);
      if (role !== "typing") bubble.appendChild(timeEl);
    }
    if (meta && meta !== "plain" && meta.run_id) {
      const foot = document.createElement("div");
      foot.className = "forge-chat-foot";
      foot.textContent = meta.run_id;
      bubble.appendChild(foot);
    }
    if (meta && meta.quality_gate) {
      renderQualityChip(meta.quality_gate, bubble);
    }
    if (anchor) thread.insertBefore(bubble, anchor);
    else thread.appendChild(bubble);
    ensureChatAnchor();
    if (!opts.silent) {
      if (role === "user" || role === "typing") chatStickToBottom = true;
      scrollChatToBottom(role === "user" || role === "typing");
      updateJumpLatestButton();
    }
    syncExecStripVisibility();
    return bubble;
  }

  function updateChatWindowMeta(turnCount) {
    const el = $("chat-window-meta");
    const meta = $("chat-meta");
    const n = turnCount || 0;
    const label = n ? n + " message" + (n === 1 ? "" : "s") + " · latest at bottom" : "Start a message below";
    if (el) el.textContent = label;
    if (meta && n) meta.textContent = n + " turns";
  }

  function renderChatThread(turns) {
    const thread = $("chat-thread");
    if (!thread) return;
    if (isEditorWindowMode()) enableEditorWindow();
    lastThreadTurns = turns || [];
    thread.innerHTML = "";
    ensureChatSpacer();
    if (!turns || !turns.length) {
      if (inChatUnifyShell) {
        thread.innerHTML =
          '<p class="forge-placeholder forge-cu-empty" id="chat-placeholder">Chat cleared — type below to start fresh.</p>';
        ensureChatAnchor();
      } else {
        const emptyPh = "Chat cleared — type below to start fresh.";
        thread.innerHTML =
          '<p class="forge-placeholder" id="chat-placeholder">' + emptyPh + "</p>";
        ensureChatSpacer();
        ensureChatAnchor();
      }
      updateChatWindowMeta(0);
      chatStickToBottom = true;
      updateJumpLatestButton();
      syncExecStripVisibility();
      return;
    }
    chatStickToBottom = true;
    turns.forEach(function (t) {
      const meta = t.meta || {};
      const text =
        t.role === "assistant" && meta.quality_gate
          ? displayAssistantText({ response: t.text, decision_card: { quality_gate: meta.quality_gate, summary: meta.summary, goal: meta.goal } })
          : t.text || "";
      appendChatBubble(t.role === "user" ? "user" : "assistant", text, meta, { silent: true });
    });
    ensureChatAnchor();
    updateChatWindowMeta(turns.length);
    sizeEditorPanes();
    scheduleScrollToLatest();
    syncExecStripVisibility();
  }

  function formatChatExportMarkdown(turns, title) {
    const lines = [
      "# " + (title || (inChatUnifyShell ? "Chat Unify workspace" : "Forge Terminal chat")),
      "",
      "_Exported " + new Date().toISOString() + "_",
      "",
    ];
    (turns || []).forEach(function (t) {
      const who = t.role === "user" ? "You" : inChatUnifyShell ? "Chat Unify" : "Forge";
      lines.push("## " + who);
      lines.push("");
      lines.push(t.text || "");
      lines.push("");
    });
    return lines.join("\n");
  }

  async function saveChatThread() {
    let turns = lastThreadTurns;
    let title = lastSessionTitle;
    try {
      const row = await api({
        action: "chat_thread",
        session_id: activeSessionId || undefined,
      });
      if (row.ok) {
        turns = row.turns || turns;
        title = row.session_title || title;
      }
    } catch (_) { /* use cache */ }
    if (!turns || !turns.length) {
      setStatus("Nothing to save — chat is empty");
      return;
    }
    const md = formatChatExportMarkdown(turns, title);
    const slug = (title || "forge-chat").replace(/[^\w.-]+/g, "-").slice(0, 48);
    const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = slug + "-" + new Date().toISOString().slice(0, 10) + ".md";
    a.click();
    URL.revokeObjectURL(url);
    setStatus("Chat saved · " + turns.length + " messages");
    log("chat saved · " + turns.length + " turns", "ok");
  }

  function clearChatNow() {
    lastThreadTurns = [];
    runId = "";
    if ($("run-id-label")) $("run-id-label").textContent = "";
    if ($("exec-strip")) $("exec-strip").hidden = true;
    if ($("decision-panel")) $("decision-panel").hidden = true;
    gateDrawerOpen = false;
    const thread = $("chat-thread");
    if (thread) {
      thread.querySelectorAll(".forge-chat-bubble").forEach(function (b) {
        b.remove();
      });
      thread.innerHTML = "";
    }
    renderChatThread([]);
    updateChatWindowMeta(0);
    chatStickToBottom = true;
    updateJumpLatestButton();
    scrollChatToBottom(true);
    sizeEditorPanes();
    localStorage.removeItem(DRAFT_KEY);
    if ($("prompt-input")) {
      $("prompt-input").value = "";
      autoGrowPrompt();
    }
    syncSendButtonState();
    setStatus("Chat cleared");
  }

  async function clearChatThread() {
    const desktop =
      isEditorWindowMode() ||
      isDesktopApp() ||
      window.__FORGE_DESKTOP_APP__ === true ||
      new URLSearchParams(window.location.search).get("embed") === "1";
    if (
      !desktop &&
      !window.__forgeClearSkipConfirm &&
      !confirm("Clear this chat thread? Save first if you need a copy.")
    ) {
      return;
    }
    suppressThreadReload = true;
    chatClearGuardUntil = Date.now() + 300000;
    clearChatNow();
    log("clear · wiping thread", "ok");

    try {
      const row = await api({ action: "chat_thread_clear", session_id: activeSessionId || undefined });
      if (!row.ok) throw new Error(row.error || "clear_failed");
      if (row.session_id) activeSessionId = row.session_id;
      lastThreadTurns = [];
      clearChatNow();
      log("chat thread cleared · " + (activeSessionId || "default"), "ok");
    } catch (err) {
      log("clear api: " + (err && err.message ? err.message : "failed") + " · kept UI empty", "err");
      setStatus("Chat cleared");
    }
  }

  async function loadChatThread(force) {
    if (Date.now() < chatClearGuardUntil) return;
    if (suppressThreadReload && !force) return;
    try {
      const row = await api({
        action: "chat_thread",
        session_id: activeSessionId || undefined,
      });
      if (row.ok) {
        if (row.session_id) activeSessionId = row.session_id;
        lastSessionTitle = row.session_title || "Chat";
        renderChatThread(row.turns || []);
        renderThreadTabs();
      }
    } catch (_) { /* quiet */ }
  }

  async function refreshMesh() {
    try {
      const row = await api({ action: "desktop_mesh_status" });
      if (row.ok) applyMesh(row);
    } catch (_) { /* quiet */ }
  }

  function modelMeta(id) {
    return modelCatalog.find(function (m) { return m.id === id; }) || null;
  }

  function updateModelHint() {
    const hint = $("model-hint");
    const sel = $("model-select");
    if (!hint || !sel) return;
    const meta = modelMeta(sel.value);
    const role = roleCatalog.find(function (r) { return r.id === lastRole; });
    const parts = [];
    if (role && role.hint) parts.push(role.hint);
    if (meta) {
      if (meta.subtitle) parts.push(meta.subtitle);
      if (meta.cost_band) parts.push(meta.cost_band);
      if (meta.available === false) parts.push("key missing");
    }
    hint.textContent = parts.join(" · ");
    const guideLead = $("forge-model-guide-lead");
    if (guideLead) {
      guideLead.textContent =
        parts.length > 0
          ? parts.join(" · ")
          : "Pick agent · tier · model above — quick prompts below.";
    }
  }

  function applyRoles(row) {
    const sel = $("role-select");
    const roles = row.model_roles || row.roles || [];
    if (!sel || !roles.length) return;
    roleCatalog = roles;
    const current = localStorage.getItem(ROLE_KEY) || row.default_role || "bulk";
    sel.innerHTML = roles
      .map(function (r) {
        return (
          '<option value="' +
          esc(r.id) +
          '">' +
          esc(r.label || r.id) +
          (r.available ? "" : " (needs key)") +
          "</option>"
        );
      })
      .join("");
    if (Array.from(sel.options).some(function (o) { return o.value === current; })) {
      sel.value = current;
    } else if (row.default_role) {
      sel.value = row.default_role;
    }
    lastRole = sel.value;
    localStorage.setItem(ROLE_KEY, lastRole);
  }

  function modelOptionAllowed(m, wantedId) {
    const id = m && m.id;
    if (!id) return false;
    if (HIDDEN_DEFAULT_MODELS.indexOf(id) >= 0 && wantedId !== id) return false;
    if (m.available === false && wantedId !== id) return false;
    return true;
  }

  function firstAllowedModelOption(sel) {
    if (!sel || !sel.options.length) return "gpt-4o";
    for (let i = 0; i < sel.options.length; i++) {
      const v = sel.options[i].value;
      if (v && HIDDEN_DEFAULT_MODELS.indexOf(v) < 0) return v;
    }
    return "gpt-4o";
  }

  function sanitizeSavedModel() {
    const saved = localStorage.getItem(MODEL_KEY);
    if (saved && HIDDEN_DEFAULT_MODELS.indexOf(saved) >= 0) {
      localStorage.setItem(MODEL_KEY, "gpt-4o");
      localStorage.removeItem(MODEL_LOCK_KEY);
      lastModel = "gpt-4o";
      const sel = $("model-select");
      if (sel && Array.from(sel.options).some(function (o) { return o.value === "gpt-4o"; })) {
        sel.value = "gpt-4o";
      }
    }
  }

  function restoreSavedModelSelect() {
    sanitizeSavedModel();
    const sel = $("model-select");
    const saved = localStorage.getItem(MODEL_KEY);
    if (!sel || !saved) return;
    if (HIDDEN_DEFAULT_MODELS.indexOf(saved) >= 0) return;
    if (Array.from(sel.options).some(function (o) { return o.value === saved; })) {
      sel.value = saved;
      lastModel = saved;
    }
  }

  function isUserModelLocked() {
    return localStorage.getItem(MODEL_LOCK_KEY) === "1";
  }

  function lockUserModel(modelId) {
    if (!modelId) return;
    localStorage.setItem(MODEL_KEY, modelId);
    localStorage.setItem(MODEL_LOCK_KEY, "1");
    lastModel = modelId;
  }

  function applyRolePick(roleId, row, force) {
    if (isUserModelLocked()) return;
    const role = (roleCatalog || []).find(function (r) { return r.id === roleId; });
    const pick = (role && role.default_model) || (row && row.default_model) || "gpt-4o";
    const sel = $("model-select");
    if (sel && Array.from(sel.options).some(function (o) { return o.value === pick; })) {
      sel.value = pick;
      lastModel = pick;
      localStorage.setItem(MODEL_KEY, pick);
    }
    updateModelHint();
  }

  function applyModels(row) {
    const sel = $("model-select");
    if (!sel || !row.models || !row.models.length) return;
    modelCatalog = row.models;
    const locked = isUserModelLocked();
    const saved = localStorage.getItem(MODEL_KEY);
    const wanted = (locked && saved) || saved || row.default_model || "gpt-4o";
    let html = "";
    if (row.model_groups && row.model_groups.length) {
      row.model_groups.forEach(function (g) {
        const models = (g.models || []).filter(function (m) {
          return modelOptionAllowed(m, wanted);
        });
        if (!models.length) return;
        html += '<optgroup label="' + esc(g.name) + '">';
        models.forEach(function (m) {
          const label = m.label + (m.subtitle ? " — " + m.subtitle : "") + (m.available === false ? " [no key]" : "");
          html += '<option value="' + esc(m.id) + '">' + esc(label) + "</option>";
        });
        html += "</optgroup>";
      });
    } else {
      row.models.filter(function (m) {
        return modelOptionAllowed(m, wanted);
      }).forEach(function (m) {
        html += '<option value="' + esc(m.id) + '">' + esc(m.label || m.id) + "</option>";
      });
    }
    if (!html) return;
    sel.innerHTML = html;
    let pick = wanted;
    if (!Array.from(sel.options).some(function (o) { return o.value === pick; })) {
      pick = row.default_model || "gpt-4o";
    }
    if (!Array.from(sel.options).some(function (o) { return o.value === pick; })) {
      pick = firstAllowedModelOption(sel);
    }
    sel.value = pick;
    lastModel = pick;
    if (locked || saved) {
      localStorage.setItem(MODEL_KEY, pick);
    }
    applyRoles(row);
    updateModelHint();
  }

  function applySnapshot(row) {
    if (row.scan) renderFileTree(row.scan);
    if (row.agents) renderAgents(row.agents);
    if (row.tasks) renderTasksPanel(row.tasks);
    if (row.receipts) renderReceiptsPanel(row.receipts);
    renderForgeToolsDeck(null, row);
  }

  async function loadSnapshot() {
    if (!workspacePath) return;
    const row = await api({ action: "workspace_snapshot" });
    if (row.ok) applySnapshot(row);
  }

  async function loadModelsFallback() {
    const urls = [
      window.location.origin + "/terminal/data/forge-terminal-models-public-v1.json",
      "/sourcea/data/forge-terminal-models-public-v1.json",
    ];
    for (let i = 0; i < urls.length; i++) {
      try {
        const row = await fetch(urls[i]).then(function (r) {
          return r.json();
        });
        if (row && row.models && row.models.length) {
          applyModels(row);
          return true;
        }
      } catch (_) { /* try next */ }
    }
    return false;
  }

  async function refreshLight() {
    try {
      const q = workspacePath
        ? "?status=1&light=1&workspace_path=" + encodeURIComponent(workspacePath)
        : "?status=1&light=1";
      const row = await fetch(API + q, { cache: "no-store" }).then(function (r) {
        return r.json();
      });
      if (!forgeToken) {
        try {
          const health = await fetch(window.location.origin + "/health").then(function (r) {
            return r.json();
          });
          if (health.forge_local_token) {
            forgeToken = health.forge_local_token;
            sessionStorage.setItem("forge_local_token", forgeToken);
          }
        } catch (_) { /* quiet */ }
      }
      applyPills(row);
      lastLightStatus = row;
      sanitizeSavedModel();
      if (row.models && row.models.length) {
        applyModels(row);
        restoreSavedModelSelect();
      } else {
        await loadModelsFallback();
      }
      renderRecent(row.recent_folders || []);
      const llm = row.llm || {};
      llmOnline = !!(llm.openrouter_ready || llm.gemini_ready || llm.anthropic_ready || llm.openai_ready);
      const banner = $("offline-banner");
      if (banner) {
        banner.hidden = llmOnline;
        if (!llmOnline && row.secrets_template) {
          banner.textContent =
            "LLM offline — add keys to ~/.sina/secrets.env (template: " + row.secrets_template + ")";
        }
      }
      if (!workspacePath && row.active_workspace_path) {
        workspacePath = row.active_workspace_path;
        localStorage.setItem(WS_PATH_KEY, workspacePath);
        updateFolderUI();
        await loadSnapshot();
      }
      syncSendButtonState();
      if (settingsOpen) renderSettingsPanel(lastSettingsRow);
    } catch (_) {
      await loadModelsFallback();
      syncSendButtonState();
    }
  }

  async function openFolder(path) {
    const p = (path || "").trim();
    if (!p || opening) return;
    opening = true;
    updateFolderUI();
    setStatus("Opening…");
    $("file-tree") && ($("file-tree").innerHTML = '<span class="forge-muted">Scanning…</span>');
    log("open " + p);
    try {
      const row = await api({ action: "open_folder", path: p });
      if (!row.ok) throw new Error(row.message || row.error || "Open failed");
      workspacePath = row.path || p;
      localStorage.setItem(WS_PATH_KEY, workspacePath);
      updateFolderUI();
      renderRecent(row.recent || []);
      if (row.scan) renderFileTree(row.scan);
      if (row.agents) renderAgents(row.agents);
      setStatus("Ready · " + folderLabel());
      log("workspace " + folderLabel() + (row.initialized ? " · init .sourcea" : ""), "ok");
      await loadSnapshot();
      await loadChatSessions();
      await loadChatThread(true);
    } catch (e) {
      setStatus("Open failed");
      log(String(e.message || e), "err");
      $("file-tree") && ($("file-tree").innerHTML = '<span class="forge-muted forge-tree-empty">Open failed</span>');
    } finally {
      opening = false;
      updateFolderUI();
    }
  }

  function requestOpenFolder() {
    if (opening) return;
    if (typeof window.forgeRequestNativeOpenFolder === "function") {
      window.forgeRequestNativeOpenFolder();
      return;
    }
    const path = window.prompt("Full folder path:");
    if (path) openFolder(path);
  }

  window.forgeOpenFolder = openFolder;
  window.forgeRequestOpenFolder = requestOpenFolder;

  function setExecButtonsEnabled(allowed) {
    ["btn-cloud", "btn-cursor", "btn-execute"].forEach(function (id) {
      const btn = $(id);
      if (!btn) return;
      btn.disabled = !allowed;
      btn.title = allowed ? "" : "Quality gate must PASS before execute";
    });
  }

  function syncExecStripVisibility() {
    const strip = $("exec-strip");
    if (!strip) return;
    const bubbles = document.querySelectorAll("#chat-thread .forge-chat-bubble").length;
    const embed = $("forge-app") && $("forge-app").classList.contains("forge-embed");
    const show = (inChatUnifyShell || embed) && bubbles > 0;
    if (show) {
      strip.hidden = false;
      strip.removeAttribute("hidden");
      strip.classList.add("is-live");
      if (!runId) setExecButtonsEnabled(false);
      sizeEditorPanes();
    } else if (inChatUnifyShell || embed) {
      strip.hidden = true;
      strip.classList.remove("is-live");
      sizeEditorPanes();
    }
  }

  function renderQualityGate(card) {
    const panel = $("quality-panel");
    const verdictEl = $("quality-verdict");
    const scoreEl = $("quality-score");
    const list = $("quality-layers");
    const qg = (card && card.quality_gate) || null;
    lastQualityGate = qg;
    updateSelfHealVisibility();
    if (!panel || !qg) {
      if (panel) panel.hidden = true;
      setExecButtonsEnabled(true);
      return;
    }
    panel.hidden = false;
    const verdict = (qg.verdict || "—").toLowerCase();
    if (verdictEl) {
      verdictEl.textContent = qg.verdict || "—";
      verdictEl.className = "forge-badge forge-quality-verdict " + verdict;
    }
    if (scoreEl) {
      scoreEl.textContent =
        (qg.passed_layers || 0) + "/" + (qg.total_layers || 11) + " · score " + (qg.score || 0);
    }
    const inlineEl = $("quality-score-inline");
    if (inlineEl) {
      inlineEl.textContent =
        (qg.passed_layers || 0) + "/" + (qg.total_layers || 11) + " · " + (qg.verdict || "—");
    }
    if (list) {
      list.innerHTML = (qg.layers || [])
        .map(function (ly) {
          const cls = ly.ok ? "pass" : "fail";
          return (
            '<li class="forge-q-layer ' +
            cls +
            '"><span class="forge-q-name">' +
            esc(ly.name || ly.id) +
            '</span><span class="forge-q-score">' +
            esc(String(ly.score || 0)) +
            '</span><span class="forge-q-note">' +
            esc(ly.note || "") +
            "</span></li>"
          );
        })
        .join("");
    }
    setExecButtonsEnabled(!!qg.execution_allowed);
  }

  function renderDecision(card) {
    const panel = $("decision-panel");
    const dl = $("decision-card");
    const badge = $("decision-badge");
    const execStrip = $("exec-strip");
    if (!card || !panel || !dl) return;
    if (execStrip) execStrip.hidden = false;
    panel.hidden = !gateDrawerOpen;
    if (badge) {
      badge.textContent = (card.decision || "pending").toLowerCase();
      badge.className = "forge-badge " + (card.decision || "pending").toLowerCase();
    }
    renderQualityGate(card);
    var qualityNote = card.quality_note ? "<dt>Quality</dt><dd>" + esc(card.quality_note) + "</dd>" : "";
    dl.innerHTML =
      qualityNote +
      "<dt>Goal</dt><dd>" +
      esc(card.goal || "—") +
      "</dd><dt>Risk</dt><dd>" +
      esc(card.risk || "low") +
      "</dd><dt>Cost</dt><dd>$" +
      esc(String(card.cost_usd ?? "—")) +
      "</dd><dt>Summary</dt><dd>" +
      esc(card.summary || "") +
      "</dd>";
    lastCost = "$" + String(card.cost_usd ?? "—");
    setStatusBar();
    log("decision gate · " + (card.decision || "pending"), "ok");
  }

  function showFeedback(msg, isError) {
    const el = $("action-feedback");
    if (!el) return;
    el.hidden = !msg;
    el.textContent = msg || "";
    el.classList.toggle("is-error", !!isError);
  }

  function updateSelfHealVisibility() {
    const btn = $("btn-self-heal");
    if (!btn) return;
    const fail =
      lastQualityGate &&
      !lastQualityGate.execution_allowed &&
      String(lastQualityGate.verdict || "").toUpperCase() !== "PASS";
    btn.hidden = !fail;
  }

  function activeTab(name) {
    return document.querySelector('.forge-tab-panel[data-tab="' + name + '"]') &&
      document.querySelector('.forge-tab-panel[data-tab="' + name + '"]').classList.contains("is-active");
  }

  function formatAgentSteps(row) {
    const lines = ["**Agent dev loop** · " + (row.run_id || "") + (row.done ? " · done" : "")];
    (row.steps || []).forEach(function (s) {
      if (s.done) {
        lines.push("- ✓ " + (s.summary || "complete"));
        return;
      }
      const act = s.action || {};
      const role = s.planner_role ? " [" + s.planner_role + "]" : "";
      lines.push(
        "- Step " +
          s.step +
          role +
          ": `" +
          (act.tool || "?") +
          "` — " +
          (s.summary || "") +
          (s.result && s.result.ok ? " ✓" : " ✗")
      );
    });
    return lines.join("\n");
  }

  function renderAdvisorTimeline(container, row) {
    if (!container) return;
    container.innerHTML = "";
    container.className = "forge-advisor-timeline";
    const steps = (row.agent && row.agent.steps) || row.steps || [];
    const rounds = row.repair_rounds || [];
    const compiled = row.compiled || {};
    if (compiled.ok) {
      const wrap = document.createElement("div");
      wrap.className = "forge-advisor-step is-open";
      const ft = compiled.forge_task || {};
      const routing = compiled.routing || {};
      const adaptiveTag = compiled.adaptive ? "adaptive" : "static";
      const learned = routing.adaptive_applied ? " · learned" : "";
      const runtimeTag = compiled.runtime_capable ? " · autonomous" : "";
      wrap.innerHTML =
        '<div class="forge-advisor-step-head"><span class="forge-advisor-role">compiler v3</span> ' +
        (compiled.stackLevel || "?") +
        " · " +
        (compiled.executionMode || ft.executionMode || "single") +
        " · cost=" +
        (compiled.estimatedCost || ft.estimatedCost || "?") +
        " · " +
        adaptiveTag +
        learned +
        runtimeTag +
        " · " +
        (compiled.intent || "") +
        "</div>";
      container.appendChild(wrap);
    }
    if (!steps.length && !rounds.length && !compiled.ok) {
      container.textContent = row.founder_summary || row.summary || "Advisor complete";
      return;
    }
    steps.forEach(function (s, idx) {
      const wrap = document.createElement("div");
      wrap.className = "forge-advisor-step" + (idx === steps.length - 1 ? " is-open" : "");
      const act = s.action || {};
      const head = document.createElement("div");
      head.className = "forge-advisor-step-head";
      head.innerHTML =
        '<span class="forge-advisor-tool">' +
        (act.tool || (s.done ? "done" : "?")) +
        "</span>" +
        (s.planner_role ? '<span class="forge-advisor-role">' + s.planner_role + "</span>" : "") +
        "<span>" +
        (s.summary || "") +
        "</span>" +
        (s.verify && s.verify.pass === false
          ? '<span class="forge-advisor-verify fail">✗</span>'
          : '<span class="forge-advisor-verify pass">✓</span>');
      const body = document.createElement("div");
      body.className = "forge-advisor-step-body";
      if (s.result && s.result.diff) body.textContent = String(s.result.diff).slice(0, 800);
      else if (s.result) body.textContent = JSON.stringify(s.result).slice(0, 400);
      head.addEventListener("click", function () {
        wrap.classList.toggle("is-open");
      });
      wrap.appendChild(head);
      wrap.appendChild(body);
      container.appendChild(wrap);
    });
    rounds.forEach(function (r) {
      const wrap = document.createElement("div");
      wrap.className = "forge-advisor-step is-open";
      const after = r.quality_after || {};
      wrap.innerHTML =
        '<div class="forge-advisor-step-head"><span class="forge-advisor-role">L2</span> Round ' +
        r.round +
        " · " +
        (r.quality_before || "?") +
        " → " +
        (after.verdict || "?") +
        " (" +
        (after.passed_layers || "?") +
        "/" +
        (after.total_layers || "?") +
        ")</div>";
      container.appendChild(wrap);
    });
    const swarmMeta = row.swarm_v3 || row;
    const swarmRuns = row.task_runs || (swarmMeta && swarmMeta.task_runs) || [];
    const replanRounds = swarmMeta.replan_rounds || row.replan_rounds || [];
    const criticAgg = swarmMeta.critic_aggregate || row.critic_aggregate;
    const bb = swarmMeta.blackboard || row.blackboard;
    const repairRuns = swarmMeta.repair_runs || row.repair_runs || [];
    const optimizerNotes = swarmMeta.optimizer_notes || row.optimizer_notes || {};
    const taskEconomy = (bb && bb.task_economy) || [];
    if (taskEconomy.length) {
      const wrap = document.createElement("div");
      wrap.className = "forge-advisor-step";
      wrap.innerHTML =
        '<div class="forge-advisor-step-head"><span class="forge-advisor-role">economy</span> Tasks=' +
        taskEconomy.length +
        " · bids=" +
        ((bb && bb.agent_bids && bb.agent_bids.length) || 0) +
        "</div>";
      container.appendChild(wrap);
    }
    if (optimizerNotes.notes || optimizerNotes.model_tier) {
      const wrap = document.createElement("div");
      wrap.className = "forge-advisor-step";
      wrap.innerHTML =
        '<div class="forge-advisor-step-head"><span class="forge-advisor-role">optimizer</span> ' +
        (optimizerNotes.model_tier || "build") +
        " · " +
        (optimizerNotes.notes || "roi check") +
        "</div>";
      container.appendChild(wrap);
    }
    repairRuns.forEach(function (rr) {
      const wrap = document.createElement("div");
      wrap.className = "forge-advisor-step is-open";
      const rep = rr.repair || {};
      wrap.innerHTML =
        '<div class="forge-advisor-step-head"><span class="forge-advisor-role">repair</span> Round ' +
        (rr.round || "?") +
        " · fixes=" +
        ((rep.fixes || []).length) +
        " · " +
        (rep.priority || "medium") +
        "</div>";
      container.appendChild(wrap);
    });
    if (swarmMeta.parallel || row.parallel) {
      const wrap = document.createElement("div");
      wrap.className = "forge-advisor-step is-open";
      wrap.innerHTML =
        '<div class="forge-advisor-step-head"><span class="forge-advisor-role">swarm</span> Parallel blackboard · planners=' +
        ((bb && bb.planner_votes && bb.planner_votes.length) || "?") +
        " · critics=" +
        ((bb && bb.critic_verdicts && bb.critic_verdicts.length) || "?") +
        (criticAgg ? " · score=" + (criticAgg.score != null ? criticAgg.score : "?") + " " + (criticAgg.approved ? "✓" : "✗") : "") +
        "</div>";
      container.appendChild(wrap);
    }
    replanRounds.forEach(function (rr) {
      const wrap = document.createElement("div");
      wrap.className = "forge-advisor-step";
      const c = rr.critic || {};
      wrap.innerHTML =
        '<div class="forge-advisor-step-head"><span class="forge-advisor-role">replan</span> Round ' +
        rr.round +
        " · tasks=" +
        (rr.tasks || "?") +
        " · critic " +
        (c.approved ? "✓" : "✗") +
        (c.score != null ? " (" + c.score + ")" : "") +
        "</div>";
      container.appendChild(wrap);
    });
    swarmRuns.forEach(function (tr, idx) {
      const wrap = document.createElement("div");
      wrap.className = "forge-advisor-step" + (idx === swarmRuns.length - 1 ? " is-open" : "");
      const b = tr.builder || {};
      const rev = tr.review || {};
      wrap.innerHTML =
        '<div class="forge-advisor-step-head"><span class="forge-advisor-role">swarm</span> ' +
        (tr.task || "task") +
        " · steps=" +
        ((b.steps || []).length) +
        " · review " +
        (rev.approved ? "✓" : "✗") +
        "</div>";
      container.appendChild(wrap);
    });
  }

  function appendAdvisorBubble(row) {
    const wrap = document.createElement("div");
    wrap.className = "forge-chat-bubble assistant";
    const inner = document.createElement("div");
    inner.className = "forge-chat-inner";
    const timeline = document.createElement("div");
    renderAdvisorTimeline(timeline, row);
    inner.appendChild(timeline);
    if (row.founder_summary) {
      const p = document.createElement("p");
      p.className = "forge-markdown";
      p.textContent = row.founder_summary;
      inner.appendChild(p);
    }
    wrap.appendChild(inner);
    const thread = $("chat-thread");
    if (thread) {
      const ph = $("chat-placeholder");
      if (ph) ph.remove();
      thread.appendChild(wrap);
      chatStickToBottom = true;
      scrollChatToBottom(true);
    }
    return wrap;
  }

  function formatSelfImproveResult(row) {
    if (row.skipped) return "L2 self-improve skipped — quality already PASS.";
    const lines = [
      "**L2 Self-improve** · " + (row.improved ? "PASS ✓" : "needs review"),
      "- Initial: **" + (row.initial_verdict || "?") + "** → Final: **" + (row.final_verdict || "?") + "**",
    ];
    (row.repair_rounds || []).forEach(function (r) {
      const after = r.quality_after || {};
      lines.push(
        "- Round " +
          r.round +
          ": agent steps=" +
          (r.agent_steps || 0) +
          " · gate **" +
          (r.quality_before || "?") +
          "** → **" +
          (after.verdict || "?") +
          "** (" +
          (after.passed_layers || "?") +
          "/" +
          (after.total_layers || "?") +
          ")"
      );
    });
    return lines.join("\n");
  }

  async function onSelfImprove(opts) {
    opts = opts || {};
    if (!workspacePath) {
      requestOpenFolder();
      return null;
    }
    if (!runId && !opts.quality_gate) {
      setStatus("Run a mission first");
      return null;
    }
    const model = ($("model-select") && $("model-select").value) || lastModel;
    setSendEnabled(false);
    setStatus("L2 self-improve…");
    const typing = appendChatBubble("typing", "Self-healing (patch-only)…", "plain");
    log("self_improve L2 · " + (runId || "inline") + " · " + model);
    try {
      const payload = {
        action: "agent_self_improve",
        run_id: runId || undefined,
        model: model,
        dry_run: !($("opt-llm") && $("opt-llm").checked),
        cloud_l3: !!($("opt-cloud-l3") && $("opt-cloud-l3").checked),
      };
      if (opts.quality_gate) payload.quality_gate = opts.quality_gate;
      if (opts.founder_text) payload.text = opts.founder_text;
      if (opts.response) payload.response = opts.response;
      const row = await api(payload);
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      if (!row.ok && !row.repair_rounds) throw new Error(row.error || row.message || "Self-improve failed");
      appendAdvisorBubble(row);
      appendChatBubble("assistant", formatSelfImproveResult(row), "plain");
      if (row.final_quality_gate) {
        lastQualityGate = row.final_quality_gate;
        if (row.decision_card) renderDecision(row.decision_card);
        renderQualityGate({ quality_gate: row.final_quality_gate });
      }
      setStatus(row.improved ? "L2 improved to PASS" : "L2 self-heal done · review gate");
      log("self_improve " + (row.improved ? "PASS" : row.final_verdict || "done"), row.improved ? "ok" : "err");
      loadSnapshot();
      return row;
    } catch (e) {
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      appendChatBubble("assistant", "Self-improve failed: " + String(e.message || e), "plain");
      setStatus("Self-improve failed");
      log(String(e.message || e), "err");
      return null;
    } finally {
      syncSendButtonState();
    }
  }

  function maybeAutoSelfImprove(row, founderText) {
    if (getForgeMode() !== "chat") return;
    const qg = row.quality_gate || (row.decision_card && row.decision_card.quality_gate);
    if (!qg || qg.execution_allowed) return;
    const verdict = String(qg.verdict || "").toUpperCase();
    if (verdict !== "REVISE" && verdict !== "REJECT") return;
    onSelfImprove({
      quality_gate: qg,
      founder_text: founderText,
      response: displayAssistantText(row),
    });
  }

  async function onMultiAgentRun(text) {
    setSendEnabled(false);
    setStatus("Multi-agent · planner → builder → verifier…");
    appendChatBubble("user", "[Multi-agent] " + text);
    const typing = appendChatBubble("typing", "Planner → Builder → Verifier…", "plain");
    try {
      const row = await cuEngineApi({
        action: "multi_agent_run",
        text: text,
        session_id: activeSessionId || undefined,
      });
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      if (!row.ok) throw new Error(row.error || "Multi-agent failed");
      const stages = row.stages || [];
      if (stages.length) {
        stages.forEach(function (s) {
          appendChatBubble(
            "assistant",
            "**" + (s.agent_id || "agent") + "**\n\n" + (s.response || ""),
            "plain",
          );
        });
      } else {
        appendChatBubble("assistant", displayAssistantText(row), "plain");
      }
      if (row.session_id) activeSessionId = row.session_id;
      setStatus("Multi-agent done · " + stages.length + " stages");
      log("multi_agent_run " + (row.run_id || ""), "ok");
    } catch (e) {
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      appendChatBubble("assistant", String(e.message || e), "plain");
      setStatus("Multi-agent failed");
      log(String(e.message || e), "err");
    } finally {
      syncSendButtonState();
    }
  }

  async function onAdvisorRun(text) {
    const model = ($("model-select") && $("model-select").value) || lastModel;
    setSendEnabled(false);
    setStatus("Advisor running…");
    appendChatBubble("user", "[Advisor] " + text);
    const typing = appendChatBubble("typing", "Plan → act → verify…", "plain");
    try {
      const row = await api({
        action: "advisor_run",
        goal: text,
        text: text,
        run_id: runId || undefined,
        model: model,
        locale: "en",
        swarm: true,
        compile: true,
        dry_run: !($("opt-llm") && $("opt-llm").checked),
        max_steps: 6,
      });
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      if (!row.ok && !row.agent) throw new Error(row.error || "Advisor failed");
      appendAdvisorBubble(row);
      if (row.founder_summary) appendChatBubble("assistant", row.founder_summary, "plain");
      setStatus("Advisor swarm · " + ((row.swarm_v3 && row.swarm_v3.state) || (row.quality_gate && row.quality_gate.verdict) || "done"));
      log("advisor_run " + (row.advisor_id || ""), "ok");
      loadChatSessions();
    } catch (e) {
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      appendChatBubble("assistant", String(e.message || e), "plain");
      setStatus("Advisor failed");
    } finally {
      syncSendButtonState();
    }
  }

  async function onAgentDev(text) {
    const model = ($("model-select") && $("model-select").value) || lastModel;
    setSendEnabled(false);
    setStatus("Agent dev loop…");
    appendChatBubble("user", "[Agent] " + text);
    const typing = appendChatBubble("typing", "Agent planning…", "plain");
    log("agent_dev · " + model);
    try {
      const row = await api({
        action: "agent_dev_loop",
        goal: text,
        model: model,
        max_steps: 6,
        dry_run: !($("opt-llm") && $("opt-llm").checked),
      });
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      if (!row.ok && !row.steps) throw new Error(row.error || row.message || "Agent failed");
      appendChatBubble("assistant", formatAgentSteps(row), "plain");
      setStatus(row.done ? "Agent done" : "Agent paused");
      log("agent_dev " + (row.run_id || "") + " steps=" + ((row.steps || []).length), row.done ? "ok" : "err");
      loadChatSessions();
    } catch (e) {
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      appendChatBubble("assistant", String(e.message || e), "plain");
      setStatus("Agent failed");
      log(String(e.message || e), "err");
    } finally {
      syncSendButtonState();
    }
  }

  async function onRun() {
    const text = ($("prompt-input") && $("prompt-input").value.trim()) || "";
    if (!text) {
      setStatus("Type a message first");
      if ($("prompt-input")) $("prompt-input").focus();
      return;
    }
    if (opening) {
      opening = false;
      updateFolderUI();
    }
    const mode = getForgeMode();
    if (!workspacePath && mode !== "chat") {
      requestOpenFolder();
      return;
    }
    if (!workspacePath && mode === "chat") {
      setStatus("Living chat · no folder — open one for Execute/Cursor");
    }
    if (getForgeMode() === "selfheal") {
      await onSelfImprove({ founder_text: text, text: text });
      if ($("prompt-input")) {
        $("prompt-input").value = "";
        autoGrowPrompt();
      }
      return;
    }
    if (getForgeMode() === "advisor") {
      await onAdvisorRun(text);
      if ($("prompt-input")) {
        $("prompt-input").value = "";
        autoGrowPrompt();
      }
      return;
    }
    appendChatBubble("user", text);
    if ($("prompt-input")) {
      $("prompt-input").value = "";
      autoGrowPrompt();
      syncSendButtonState();
    }
    if (!llmOnline && $("opt-llm") && $("opt-llm").checked && !inChatUnifyShell) {
      appendChatBubble(
        "assistant",
        "LLM offline — uncheck Live LLM for draft-only or add API keys in ~/.sina/secrets.env",
        "plain",
      );
      setStatus("LLM offline");
      return;
    }
    if (!llmOnline && !inChatUnifyShell) {
      localStorage.setItem(DRAFT_KEY, text);
      setStatus("Draft saved — LLM offline");
      log("draft saved (offline)", "ok");
      return;
    }
    let model = ($("model-select") && $("model-select").value) || lastModel || "gpt-4o";
    const agentId = selectedAgentId();
    if (inChatUnifyShell && agentId === "auto" && text.length > 80) {
      try {
        const route = await cuEngineApi({ action: "smart_route", text: text });
        if (route.ok) {
          applySmartRoute(route);
          if (route.use_multi_agent) {
            if ($("prompt-input")) {
              $("prompt-input").value = "";
              autoGrowPrompt();
              syncSendButtonState();
            }
            await onMultiAgentRun(text);
            return;
          }
        }
      } catch (e) {
        log("smart_route: " + e, "err");
      }
    }
    lockUserModel(model);
    lastModel = model;
    setSendEnabled(false);
    setStatus(inChatUnifyShell ? cuIdeStatus("LLM") : "Forge IDE → LLM…");
    showFeedback("", false);
    let typing = null;
    try {
      if (!(await pingServerHealth())) {
        throw new Error("Chat Unify server not running — Cmd+Q and reopen Chat Unify.app from Desktop");
      }
      typing = appendChatBubble(
        "typing",
        inChatUnifyShell
          ? agentId === "auto"
            ? "Chat Unify router → agents…"
            : cuIdeStatus("model")
          : agentId === "auto"
            ? "Smart route → Forge engine…"
            : "Forge IDE → model…",
        "plain",
      );
      log(
        (inChatUnifyShell ? "chat · Chat Unify workspace · " : "chat · desktop IDE · ") +
          agentId +
          " · " +
          model +
          " · " +
          folderLabel(),
      );
      const row = await api({
        action: "chat_turn",
        text: text,
        full_llm: $("opt-llm") && $("opt-llm").checked,
        fast: inChatUnifyShell || getForgeMode() === "chat",
        living_chat: inChatUnifyShell && getForgeMode() === "chat",
        model: model,
        session_id: activeSessionId || undefined,
      });
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      typing = null;
      if (!row.ok) throw new Error(row.message || row.error || "Run failed");
      if (row.smart_route || row.routing_reason) applySmartRoute(row);
      runId = row.run_id || "";
      $("run-id-label").textContent = runId;
      appendChatBubble("assistant", displayAssistantText(row), {
        run_id: runId,
        quality_gate: row.quality_gate || (row.decision_card && row.decision_card.quality_gate),
      });
      const meta = $("chat-meta");
      if (meta) meta.textContent = ((row.llm && row.llm.model) || model) + " · " + lastTime;
      renderDecision(row.decision_card);
      if (row.quality_gate && row.decision_card) {
        row.decision_card.quality_gate = row.decision_card.quality_gate || {
          verdict: row.quality_gate.verdict,
          passed_layers: row.quality_gate.passed_layers,
          total_layers: row.quality_gate.total_layers,
          score: row.quality_gate.score,
          execution_allowed: row.quality_gate.execution_allowed,
          layers: row.quality_gate.layers,
        };
        renderQualityGate(row.decision_card);
      }
      setStatus(
        row.quality_gate && !row.quality_gate.execution_allowed
          ? "Review quality gate · " + (row.quality_gate.verdict || "")
          : "Review decision gate",
      );
      log("chat ok · " + runId, "ok");
      loadSnapshot();
      refreshMesh();
      loadChatSessions();
    } catch (e) {
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      appendChatBubble("assistant", String(e.message || e), "plain");
      setStatus("Chat failed");
      log(String(e.message || e), "err");
    } finally {
      syncSendButtonState();
    }
  }

  async function onDecide(dec) {
    if (!runId) {
      showFeedback("Send a message first — then Approve / Revise", true);
      setStatus("No run yet — send a message");
      return;
    }
    setStatus(dec + "…");
    log("decide · " + dec);
    try {
      const row = await api({ action: "decide", run_id: runId, decision: dec });
      if (row.decision_card) renderDecision(row.decision_card);
      setStatus("Decision: " + dec);
    } catch (e) {
      setStatus("Decision failed");
      log(String(e.message || e), "err");
    }
  }

  async function onRerun() {
    if (!runId) {
      showFeedback("Send a message first — then Re-run quality", true);
      return;
    }
    const text = ($("prompt-input") && $("prompt-input").value.trim()) || "";
    setStatus("Re-running quality gate…");
    try {
      const row = await api({ action: "quality_rerun", run_id: runId, text: text, full_llm: false });
      if (row.decision_card) renderDecision(row.decision_card);
      setStatus("Quality · " + ((row.quality_gate && row.quality_gate.verdict) || "done"));
    } catch (e) {
      setStatus("Quality re-run failed");
      log(String(e.message || e), "err");
    }
  }

  async function onCursor() {
    if (!runId) {
      showFeedback("Send a message first — then Cursor", true);
      return;
    }
    setExecButtonsEnabled(false);
    setStatus("Cursor INBOX…");
    log("cursor · " + runId);
    try {
      const row = await api({ action: "send_cursor", run_id: runId });
      if (row.decision_card) renderDecision(row.decision_card);
      const msg = (row.for_founder && row.for_founder.show_this) || (row.ok ? "Cursor OK" : row.error);
      showFeedback(msg, !row.ok);
      setStatus(row.ok ? "Sent to Cursor" : "Cursor blocked");
    } catch (e) {
      showFeedback(String(e.message || e), true);
      setStatus("Cursor failed");
    } finally {
      setExecButtonsEnabled(lastQualityGate ? !!lastQualityGate.execution_allowed : true);
    }
  }

  async function onExecute() {
    if (!runId) {
      showFeedback("Send a message first — then Execute", true);
      return;
    }
    setExecButtonsEnabled(false);
    setStatus("Execute…");
    log("execute · " + runId);
    try {
      const row = await api({ action: "execute", run_id: runId, prefer: "auto" });
      if (row.decision_card) renderDecision(row.decision_card);
      const msg = (row.for_founder && row.for_founder.show_this) || (row.ok ? "Execute OK" : row.error);
      showFeedback(msg, !row.ok);
      setStatus(row.ok ? "Executed" : "Execute blocked");
      if (activeTab("outbox")) pollOutbox();
    } catch (e) {
      showFeedback(String(e.message || e), true);
      setStatus("Execute failed");
    } finally {
      setExecButtonsEnabled(lastQualityGate ? !!lastQualityGate.execution_allowed : true);
    }
  }

  async function onCloud() {
    if (!runId) {
      showFeedback("Send a message first — then Cloud", true);
      return;
    }
    setExecButtonsEnabled(false);
    setStatus("Cloud execute…");
    log("cloud · " + runId);
    try {
      const row = await api({ action: "send_cloud", run_id: runId });
      if (row.decision_card) renderDecision(row.decision_card);
      const msg = (row.for_founder && row.for_founder.show_this) || (row.ok ? "Cloud OK" : row.error);
      showFeedback(msg, !row.ok);
      setStatus(row.ok ? "Cloud complete" : "Cloud blocked");
      log(row.ok ? "cloud ok" : "cloud fail · " + (row.error || ""), row.ok ? "ok" : "err");
      if (activeTab("outbox")) pollOutbox();
      loadSnapshot();
    } catch (e) {
      showFeedback(String(e.message || e), true);
      setStatus("Cloud failed");
      log(String(e.message || e), "err");
    } finally {
      setExecButtonsEnabled(lastQualityGate ? !!lastQualityGate.execution_allowed : true);
    }
  }

  async function pollOutbox() {
    if (!runId) return;
    const row = await api({ action: "poll_outbox", run_id: runId });
    const panel = $("tab-outbox");
    if (!panel) return;
    panel.textContent = row.outbox && row.outbox.payload ? JSON.stringify(row.outbox, null, 2) : "(empty)";
  }

  function renderTasksPanel(tasks) {
    const panel = $("tab-tasks");
    if (!panel) return;
    panel.innerHTML = (tasks || []).length
      ? tasks
          .map(function (t) {
            return (
              '<div class="forge-list-item"><strong>' +
              esc(t.task_id) +
              "</strong> " +
              esc(t.status) +
              " · " +
              esc(t.type || "") +
              "<br><span class='forge-muted'>" +
              esc((t.founder_text || "").slice(0, 100)) +
              "</span></div>"
            );
          })
          .join("")
      : '<span class="forge-muted">No tasks</span>';
  }

  function renderReceiptsPanel(recs) {
    const panel = $("tab-receipts");
    if (!panel) return;
    panel.innerHTML = (recs || []).length
      ? recs
          .map(function (r) {
            return (
              '<div class="forge-list-item"><strong>' +
              esc(r.run_id || r.file) +
              "</strong> " +
              esc(r.at || "") +
              "<br><span class='forge-muted'>" +
              esc(r.preview || "") +
              "</span></div>"
            );
          })
          .join("")
      : '<span class="forge-muted">No receipts</span>';
  }

  function initTabs() {
    document.querySelectorAll(".forge-tab").forEach(function (tab) {
      tab.addEventListener("click", function () {
        const name = tab.getAttribute("data-tab");
        document.querySelectorAll(".forge-tab").forEach(function (t) {
          t.classList.toggle("is-active", t.getAttribute("data-tab") === name);
        });
        document.querySelectorAll(".forge-tab-panel").forEach(function (p) {
          p.classList.toggle("is-active", p.getAttribute("data-tab") === name);
        });
        if (name === "outbox" && runId) pollOutbox();
        if (name === "connect") refreshMesh();
        if (name === "tasks" && workspacePath) loadSnapshot();
        if (name === "receipts" && workspacePath) loadSnapshot();
      });
    });
  }

  $("btn-open-platform-ws") && $("btn-open-platform-ws").addEventListener("click", openPlatformWorkspace);
  $("btn-open-folder") && $("btn-open-folder").addEventListener("click", requestOpenFolder);
  $("btn-run") && $("btn-run").addEventListener("click", onRun);
  wireComposerSend();
  $("btn-toggle-gate") &&
    $("btn-toggle-gate").addEventListener("click", function () {
      gateDrawerOpen = !gateDrawerOpen;
      if (gateDrawerOpen) openGatePanel();
      else {
        gateDrawerOpen = false;
        const panel = $("decision-panel");
        if (panel) panel.hidden = true;
        $("btn-toggle-gate") && $("btn-toggle-gate").classList.remove("is-active");
      }
    });
  $("btn-forge-settings") &&
    $("btn-forge-settings").addEventListener("click", async function () {
      if (settingsOpen) {
        settingsOpen = false;
        const panel = $("settings-panel");
        if (panel) panel.hidden = true;
        $("btn-forge-settings") && $("btn-forge-settings").classList.remove("is-active");
        return;
      }
      openSettingsPanel();
    });
  $("btn-settings-save") && $("btn-settings-save").addEventListener("click", saveChatSettings);
  $("btn-settings-site") &&
    $("btn-settings-site").addEventListener("click", function () {
      openPeerUrl("https://sourcea.app/sourcea/brain-chat-settings");
    });
  $("btn-approve") && $("btn-approve").addEventListener("click", function () { onDecide("approved"); });
  $("btn-revise") && $("btn-revise").addEventListener("click", function () { onDecide("revise"); });
  $("btn-rerun") && $("btn-rerun").addEventListener("click", onRerun);
  $("btn-self-heal") && $("btn-self-heal").addEventListener("click", function () { onSelfImprove(); });
  $("btn-reject") && $("btn-reject").addEventListener("click", function () { onDecide("rejected"); });
  $("btn-cursor") && $("btn-cursor").addEventListener("click", onCursor);
  $("btn-execute") && $("btn-execute").addEventListener("click", onExecute);
  $("btn-cloud") && $("btn-cloud").addEventListener("click", onCloud);
  $("pill-chat-unify") &&
    $("pill-chat-unify").addEventListener("click", function () {
      openPeerUrl("http://127.0.0.1:13023/");
    });
  $("pill-cloud") &&
    $("pill-cloud").addEventListener("click", function () {
      openPeerUrl("http://127.0.0.1:13027/");
    });
  document.addEventListener("click", function (ev) {
    const t = ev.target && ev.target.closest ? ev.target.closest("#btn-clear-chat, #btn-clear-chat-toolbar") : null;
    if (!t) return;
    ev.preventDefault();
    ev.stopPropagation();
    clearChatThread();
  }, true);
  window.forgeClearChat = clearChatThread;
  $("btn-save-chat") && $("btn-save-chat").addEventListener("click", saveChatThread);
  $("btn-save-chat-toolbar") && $("btn-save-chat-toolbar").addEventListener("click", saveChatThread);
  $("btn-jump-latest") && $("btn-jump-latest").addEventListener("click", ensureChatAtLatest);
  $("btn-new-thread") && $("btn-new-thread").addEventListener("click", newChatThread);
  $("btn-reload-ui") && $("btn-reload-ui").addEventListener("click", reloadUI);
  $("btn-close-editor") && $("btn-close-editor").addEventListener("click", closeEditor);
  $("btn-toggle-terminal") && $("btn-toggle-terminal").addEventListener("click", toggleDock);

  $("role-select") &&
    $("role-select").addEventListener("change", function () {
      lastRole = $("role-select").value || "bulk";
      localStorage.setItem(ROLE_KEY, lastRole);
      if (!isUserModelLocked()) {
        applyRolePick(lastRole, { default_model: rowDefaultModel() }, true);
      }
      updateModelHint();
    });

  function rowDefaultModel() {
    const roleRow = roleCatalog.find(function (r) { return r.id === lastRole; });
    return (roleRow && roleRow.default_model) || "gpt-4o";
  }

  $("model-select") &&
    $("model-select").addEventListener("change", function () {
      lockUserModel($("model-select").value || lastModel);
      updateModelHint();
    });

  $("prompt-input") &&
    $("prompt-input").addEventListener("keydown", function (ev) {
      if (ev.key !== "Enter") return;
      if (ev.shiftKey) return;
      ev.preventDefault();
      ev.stopPropagation();
      onRun();
    });

  initLivingChips();
  updateComposerChars();
  sanitizeSavedModel();
  restoreSavedModelSelect();
  if (isDesktopApp() && !isUserModelLocked()) {
    const sel = $("model-select");
    const pick = (sel && sel.value) || localStorage.getItem(MODEL_KEY) || "gpt-4o";
    if (pick && HIDDEN_DEFAULT_MODELS.indexOf(pick) < 0) lockUserModel(pick);
  }

  document.addEventListener("keydown", function (ev) {
    if ((ev.metaKey || ev.ctrlKey) && ev.key === "o") {
      ev.preventDefault();
      requestOpenFolder();
    }
    if ((ev.metaKey || ev.ctrlKey) && ev.key === "j") {
      ev.preventDefault();
      toggleDock();
    }
    if ((ev.metaKey || ev.ctrlKey) && ev.key === "n") {
      ev.preventDefault();
      newChatThread();
    }
    if ((ev.metaKey || ev.ctrlKey) && ev.key === "r") {
      ev.preventDefault();
      reloadUI();
    }
  });

  initTabs();
  initDockResize();
  initSidebarResize();
  initEditorResize();
  if (document.documentElement.classList.contains("forge-desktop-app")) {
    forceScrollUnlock();
    enableEditorWindow();
    initMovableEditorWindow();
    initComposerFollow();
  }
  initSmartChatScroll();
  initForgeToolsDeck();
  const urlEmbed = new URLSearchParams(window.location.search).get("embed") === "1";
  const inEmbed = window.parent !== window || urlEmbed;
  if (inEmbed) {
    $("forge-app") && $("forge-app").classList.add("forge-embed");
    document.documentElement.classList.add("forge-embed-root");
    document.body.classList.add("forge-embed-root");
    if (urlEmbed) applyChatUnifyShellBranding();
    const sidebarOpen = localStorage.getItem(EMBED_SIDEBAR_KEY) !== "0";
    setEmbedSidebarCollapsed(!sidebarOpen);
    $("embed-btn-open-folder") &&
      $("embed-btn-open-folder").addEventListener("click", requestOpenFolder);
    $("embed-sidebar-toggle") &&
      $("embed-sidebar-toggle").addEventListener("click", function () {
        const bench = $("forge-workbench");
        setEmbedSidebarCollapsed(!bench || !bench.classList.contains("sidebar-collapsed"));
      });
    const scrollHint = $("composer-hint");
    if (scrollHint) {
      scrollHint.textContent = "Scroll message history inside Editor ↑ · page scroll right edge for Terminal below";
    }
    if (window.parent !== window && typeof ResizeObserver !== "undefined") {
      new ResizeObserver(function () {
        reportEmbedHeight();
      }).observe(document.body);
    }
  } else if (isDesktopApp()) {
    forceScrollUnlock();
    enableEditorWindow();
    initMovableEditorWindow();
    initComposerFollow();
    initModelGuideCollapse();
  }
  if (!inEmbed && !isDesktopApp() && localStorage.getItem(DOCK_KEY) === null) {
    setDockOpen(false);
  } else if (!inEmbed && !isDesktopApp()) {
    setDockOpen(localStorage.getItem(DOCK_KEY) !== "0");
  }
  renderAgents([]);
  updateFolderUI();
  setStatusBar();
  engineRouteReady = initEngineRoute().then(function () {
    loadAgentSelect();
    const msg = inChatUnifyShell
      ? CU_IDE_LABEL + " v" + UI_VERSION + " · combined Chat Unify upgrade"
      : "Desktop IDE v" + UI_VERSION + " · editor · terminal · composer";
    log(msg, "ok");
    refreshLight();
    refreshMesh();
    setInterval(refreshLight, 15000);
    setInterval(refreshMesh, 15000);
    return loadChatSessions().then(function () {
      return loadChatThread(true).then(function () {
        sizeEditorPanes();
        scheduleScrollToLatest();
      });
    });
  });
  initModePills();
  window.addEventListener("message", function (ev) {
    if (ev.data && ev.data.type === "forge-parent-ready") {
      reportEmbedHeight();
      return;
    }
    if (!ev.data || ev.data.type !== "forge-token") return;
    if (ev.data.token) {
      forgeToken = ev.data.token;
      sessionStorage.setItem("forge_local_token", forgeToken);
    }
  });
  if (window.parent !== window) {
    ensureForgeToken().then(function () {
      if (forgeToken) {
        window.parent.postMessage({ type: "forge-token-ready", token: forgeToken }, "*");
      }
    });
  }
  const draft = localStorage.getItem(DRAFT_KEY);
  if (draft && $("prompt-input") && !$("prompt-input").value) $("prompt-input").value = draft;
  window.addEventListener("load", function () {
    engineRouteReady.then(function () {
      sizeEditorPanes();
      scheduleScrollToLatest();
    });
  }, { once: true });
  loadChatSettings();
  maybeOpenPlatformWorkspaceFromUrl();
  updateOnboardCard();
  if (workspacePath) openFolder(workspacePath);
})();

/**
 * SourceA Platform workspace — provision + living chat (signed-in project context).
 */
(function (global) {
  "use strict";

  const VERSION = "1.4.0";
  const PRODUCT = "forge_terminal";
  const CONFIG_URL = "/sourcea/data/sourcea-brain-chat-config-v1.json";
  const DEFAULT_API =
    "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/api/brain/chat/v1";
  const MODELS_PUBLIC_URL = "/sourcea/data/forge-terminal-models-public-v1.json";
  const MODEL_KEY = "sourcea-platform-workspace-model-v1";
  const STATUS_TIMEOUT_MS = 12000;

  function isAiReady(data) {
    if (!data || typeof data !== "object") return false;
    return Boolean(data.ai_model_ready ?? data.openrouter_ready);
  }

  const $ = (id) => document.getElementById(id);
  let session = null;
  let apiUrl = DEFAULT_API;
  let history = [];
  let busy = false;
  let selectedModel = "google/gemini-2.5-flash";

  function escHtml(s) {
    const d = document.createElement("div");
    d.textContent = String(s || "");
    return d.innerHTML;
  }

  function isSectionLine(line) {
    const t = line.trim();
    if (!t) return false;
    if (/^#{1,3}\s/.test(t)) return true;
    if (/^\d+\)\s/.test(t)) return true;
    if (/^(BOTTOM LINE|WHAT THIS MEANS|BLOCKERS|RISKS|SUGGESTED NEXT|IF BLOCKED)/i.test(t)) return true;
    if (/^[A-Z][A-Z0-9\s/&'’-]{4,}$/.test(t) && t.length < 72) return true;
    return false;
  }

  function sectionTitle(line) {
    return line.trim().replace(/^#{1,3}\s*/, "").replace(/^\d+\)\s*/, "");
  }

  function renderSections(reply) {
    if (!reply) return "";
    const lines = String(reply).split(/\n/);
    let html = "";
    let buf = [];
    function flushBuf() {
      if (!buf.length) return;
      const para = buf.join(" ").trim();
      if (!para) return;
      const body = escHtml(para).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
      html += '<p class="sa-ws-body">' + body + "</p>";
      buf = [];
    }
    lines.forEach(function (line) {
      const trimmed = line.trim();
      if (!trimmed) {
        flushBuf();
        return;
      }
      if (isSectionLine(trimmed)) {
        flushBuf();
        html += '<div class="sa-ws-section">' + escHtml(sectionTitle(trimmed)) + "</div>";
        return;
      }
      buf.push(trimmed);
    });
    flushBuf();
    if (!html) {
      return (
        '<div class="sa-ws-answer">' +
        escHtml(reply).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/\n/g, "<br>") +
        "</div>"
      );
    }
    return '<div class="sa-ws-answer">' + html + "</div>";
  }

  function appendBubble(role, html, plain) {
    const thread = $("sa-ws-thread");
    if (!thread) return;
    const ph = $("sa-ws-placeholder");
    if (ph) ph.remove();
    const el = document.createElement("div");
    el.className = "sa-ws-bubble " + role;
    if (role === "assistant" && html) {
      el.innerHTML = html;
    } else {
      el.textContent = plain || html || "";
    }
    thread.appendChild(el);
    thread.scrollTop = thread.scrollHeight;
    return el;
  }

  function forgeMission(text) {
    const raw = (text || "").trim();
    const goal = raw.split(/[.!?\n]/)[0].trim() || raw;
    const s = session || {};
    const ctx = [];
    if (s.project_name) ctx.push("PROJECT: " + s.project_name);
    if (s.org) ctx.push("ORG: " + s.org);
    if (s.goal) ctx.push("SHIPPING: " + s.goal);
    if (s.workspace_path) ctx.push("WORKSPACE_PATH: " + s.workspace_path);
    if (s.email) ctx.push("FOUNDER: " + s.name + " <" + s.email + ">");
    return [
      "GOAL: " + goal.slice(0, 280),
      ctx.length ? "WORKSPACE CONTEXT:\n" + ctx.join("\n") : "",
      "CONTEXT: Signed-in Forge Terminal workspace on sourcea.app — controlled agent execution with receipts.",
      "VERIFY: Reply in plain English with four short sections:",
      "  1) Bottom line",
      "  2) What this means for their business",
      "  3) Blockers or risks",
      "  4) Suggested next step (Mac Forge IDE when disk receipts needed)",
      "",
      "Founder input:",
      raw.slice(0, 1200),
    ]
      .filter(Boolean)
      .join("\n");
  }

  function setLive(text, on) {
    const el = $("sa-ws-live");
    if (!el) return;
    el.textContent = text;
    el.classList.toggle("is-on", !!on);
  }

  function fetchJson(url, body, timeoutMs) {
    const ctrl = new AbortController();
    const timer = setTimeout(function () {
      ctrl.abort();
    }, timeoutMs || STATUS_TIMEOUT_MS);
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: ctrl.signal,
    })
      .then(function (res) {
        clearTimeout(timer);
        return res.json();
      })
      .catch(function (err) {
        clearTimeout(timer);
        throw err;
      });
  }

  function applyModels(models, defaultModel) {
    const sel = $("sa-ws-model");
    if (!sel || !models || !models.length) return;
    const groups = {};
    models.forEach(function (m) {
      const g = m.group || m.provider || "Models";
      if (!groups[g]) groups[g] = [];
      groups[g].push(m);
    });
    let html = "";
    Object.keys(groups).forEach(function (g) {
      html += '<optgroup label="' + g.replace(/"/g, "") + '">';
      groups[g].forEach(function (m) {
        const id = m.id || m.api_model;
        const label = (m.label || id) + (m.cost || m.cost_band ? " · " + (m.cost || m.cost_band) : "");
        html += '<option value="' + id.replace(/"/g, "") + '">' + label.replace(/</g, "") + "</option>";
      });
      html += "</optgroup>";
    });
    sel.innerHTML = html;
    const saved = localStorage.getItem(MODEL_KEY);
    const pick = saved || defaultModel || selectedModel;
    if (Array.from(sel.options).some(function (o) { return o.value === pick; })) {
      sel.value = pick;
    }
    selectedModel = sel.value;
  }

  async function loadChatConfig() {
    try {
      const res = await fetch(CONFIG_URL);
      if (res.ok) {
        const row = await res.json();
        if (row.api_worker_url) apiUrl = row.api_worker_url;
      }
    } catch (_) {
      /* default */
    }
    try {
      const st = await fetchJson(apiUrl, { action: "status", product: PRODUCT }, STATUS_TIMEOUT_MS);
      if (st.models && st.models.length) {
        applyModels(st.models, st.default_model || st.model);
      } else {
        const pub = await fetch(MODELS_PUBLIC_URL).then(function (r) { return r.json(); });
        const orOnly = (pub.models || []).filter(function (m) {
          return m.provider === "openrouter" || String(m.api_model || m.id || "").includes("/");
        }).map(function (m) {
          return { id: m.api_model || m.id, label: m.label, group: m.group, cost: m.cost_band };
        });
        if (orOnly.length) applyModels(orOnly, pub.default_model);
      }
      setLive(isAiReady(st) ? "Live · prompt forge on send" : "Offline — book a walkthrough", isAiReady(st));
    } catch (_) {
      setLive("Offline — book a walkthrough", false);
    }
  }

  async function sendChat(forged) {
    const model = ($("sa-ws-model") && $("sa-ws-model").value) || selectedModel;
    const row = await fetchJson(
      apiUrl,
      { action: "chat", product: PRODUCT, message: forged, model: model, history: history },
      90000,
    );
    if (!row.ok && !row.reply) throw new Error(row.error || row.message || "Chat failed");
    return row.reply || row.message || "No reply";
  }

  async function onSend() {
    if (busy) return;
    const input = $("sa-ws-input");
    const text = ((input && input.value) || "").trim();
    if (!text) return;
    busy = true;
    $("sa-ws-send") && ($("sa-ws-send").disabled = true);
    appendBubble("user", "", text);
    history.push({ role: "user", content: text });
    const typing = appendBubble("typing", "", "Thinking…");
    setLive("Prompt forge → model…", true);
    try {
      const reply = await sendChat(forgeMission(text));
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      history.push({ role: "assistant", content: reply });
      appendBubble("assistant", renderSections(reply), reply);
      setLive("Live · prompt forge on send", true);
      if (input) {
        input.value = "";
        input.focus();
      }
    } catch (e) {
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      appendBubble("assistant", "", String(e.message || e));
      setLive("Send failed", false);
    } finally {
      busy = false;
      $("sa-ws-send") && ($("sa-ws-send").disabled = false);
    }
  }

  function paintSidebar(s) {
    $("sa-ws-project-title") && ($("sa-ws-project-title").textContent = s.project_name || "Your project");
    $("sa-ws-org") && ($("sa-ws-org").textContent = s.org || s.name || s.email || "");
    $("sa-ws-goal-text") && ($("sa-ws-goal-text").textContent = s.goal || "Add a goal in profile to seed your first session.");
    const pill = $("sa-ws-provision-pill");
    const pathEl = $("sa-ws-path");
    if (s.workspace_path) {
      if (pill) {
        pill.textContent = "Workspace ready";
        pill.className = "sa-ws-status-pill is-ready";
      }
      if (pathEl) {
        pathEl.textContent = s.workspace_path;
        pathEl.hidden = false;
      }
      const mac = $("sa-ws-open-mac");
      if (mac && s.workspace_slug) {
        mac.href = "http://127.0.0.1:13029/terminal/?workspace=" + encodeURIComponent(s.workspace_slug);
        mac.hidden = false;
      }
    } else if (pill) {
      pill.textContent = "Cloud workspace";
      pill.className = "sa-ws-status-pill is-pending";
    }
    const input = $("sa-ws-input");
    if (input && s.goal && !input.value) input.value = s.goal;
  }

  async function provision(s) {
    const S = global.SourceAPlatformSession;
    const statusEl = $("sa-ws-provision-status");
    if (s.workspace_path && s.workspace_slug) {
      paintSidebar(s);
      if (statusEl) statusEl.textContent = "Workspace linked · chat uses your project context";
      return s;
    }
    if (statusEl) statusEl.textContent = "Provisioning workspace on Mac (if app is running)…";
    const row = await S.provisionOnMac(s);
    if (row.ok) {
      const merged = S.write(
        Object.assign({}, s, {
          workspace_path: row.path,
          workspace_slug: row.slug,
          workspace_ready: !!row.workspace_ready,
          provisioned_at: new Date().toISOString(),
          step: "workspace",
        }),
      );
      paintSidebar(merged);
      if (statusEl) {
        statusEl.textContent = row.workspace_ready
          ? ".sourcea kernel initialized logged"
          : "Folder created — open Mac app to finish init";
      }
      return merged;
    }
    if (statusEl) {
      statusEl.textContent = "Browser workspace active — install Mac app for disk receipts";
    }
    paintSidebar(s);
    return s;
  }

  function bindChips() {
    document.querySelectorAll(".sa-ws-chip").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const input = $("sa-ws-input");
        if (input) {
          input.value = btn.getAttribute("data-prompt") || "";
          input.focus();
        }
      });
    });
  }

  function bind(sessionRow) {
    session = sessionRow;
    $("sa-ws-send") && $("sa-ws-send").addEventListener("click", onSend);
    $("sa-ws-input") &&
      $("sa-ws-input").addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
          ev.preventDefault();
          onSend();
        }
      });
    const modelSel = $("sa-ws-model");
    if (modelSel) {
      modelSel.addEventListener("change", function () {
        selectedModel = modelSel.value;
        localStorage.setItem(MODEL_KEY, selectedModel);
      });
    }
    $("sa-po-signout") &&
      $("sa-po-signout").addEventListener("click", function () {
        global.SourceAPlatformSession.signOut();
      });
    bindChips();
    paintSidebar(sessionRow);
    loadChatConfig();
  }

  async function init() {
    const S = global.SourceAPlatformSession;
    const cur = await S.routeGuardAsync("workspace");
    if (!S.canAccess("workspace", cur)) return;
    session = await provision(cur);
    bind(session);
  }

  global.SourceAPlatformWorkspace = { init: init, VERSION: VERSION };
})(typeof window !== "undefined" ? window : globalThis);

/**
 * Forge Terminal public demo — client prompt forge + cloud brain chat.
 * Law: no Mac body · no new kernel · uses sourcea-brain-chat-config-v1 worker URL.
 */
(function () {
  "use strict";

  const DEMO_VERSION = "1.4.1";
  const PRODUCT = "forge_terminal";
  const CONFIG_URL = "/sourcea/data/sourcea-brain-chat-config-v1.json";
  const DEFAULT_API =
    "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/api/brain/chat/v1";
  const FEEDBACK_KEY = "sourcea-forge-terminal-demo-feedback-v1";
  const MODEL_KEY = "sourcea-forge-terminal-demo-model-v1";
  const MODELS_PUBLIC_URL = "/sourcea/data/forge-terminal-models-public-v1.json";
  const STATUS_TIMEOUT_MS = 12000;

  function isAiReady(data) {
    if (!data || typeof data !== "object") return false;
    return Boolean(data.ai_model_ready ?? data.openrouter_ready);
  }

  const $ = (id) => document.getElementById(id);
  let apiUrl = DEFAULT_API;
  let history = [];
  let turnCount = 0;
  let busy = false;
  let selectedModel = "google/gemini-2.5-flash";
  let modelCatalog = [];

  const COMPOSER_CHIPS = [
    { label: "Ship 48h MVP", text: "I need a 48-hour MVP — what's the intake path and what proof do I get?" },
    { label: "Pricing", text: "What would you charge for controlled agent ops for a 12-person agency?" },
    { label: "See live receipt", text: "Show me what a client receives as proof after a job completes." },
  ];

  function forgeMission(text) {
    const raw = (text || "").trim();
    const goal = raw.split(/[.!?\n]/)[0].trim() || raw;
    return [
      "GOAL: " + goal.slice(0, 280),
      "CONTEXT: Forge Terminal on sourcea.app — founder evaluating controlled agent execution.",
      "VERIFY: Reply in plain English with four short sections:",
      "  1) Bottom line",
      "  2) What this means for their business",
      "  3) Blockers or risks",
      "  4) Suggested next step (include the signed-in workspace if they need saved project proof)",
      "IF BLOCKED: Say what you need from them in one sentence.",
      "",
      "Founder input:",
      raw.slice(0, 1200),
    ].join("\n");
  }

  function escHtml(s) {
    const d = document.createElement("div");
    d.textContent = String(s || "");
    return d.innerHTML;
  }

  function isSectionLine(line) {
    const t = line.trim().replace(/^\*\*/, "").replace(/\*\*$/, "");
    if (!t) return false;
    if (/^#{1,3}\s/.test(t)) return true;
    if (/^\d+\)\s/.test(t)) return true;
    if (/^(BOTTOM LINE|WHAT THIS MEANS|BLOCKERS|RISKS|SUGGESTED NEXT|IF BLOCKED)/i.test(t)) return true;
    if (/^[A-Z][A-Z0-9\s/&'’-]{4,}$/.test(t) && t.length < 72) return true;
    return false;
  }

  function sectionTitle(line) {
    return line
      .trim()
      .replace(/^\*\*/, "")
      .replace(/\*\*$/, "")
      .replace(/^#{1,3}\s*/, "")
      .replace(/^\d+\)\s*/, "");
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
      html += '<p class="sa-ft-body">' + body + "</p>";
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
        html += '<div class="sa-ft-section">' + escHtml(sectionTitle(trimmed)) + "</div>";
        return;
      }
      buf.push(trimmed);
    });
    flushBuf();
    if (!html) {
      return (
        '<div class="sa-ft-answer">' +
        escHtml(reply).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/\n/g, "<br>") +
        "</div>"
      );
    }
    return '<div class="sa-ft-answer">' + html + "</div>";
  }

  function appendBubble(role, html, plain) {
    const thread = $("sa-ft-thread");
    if (!thread) return;
    const ph = $("sa-ft-placeholder");
    if (ph) ph.remove();
    const el = document.createElement("div");
    el.className = "sa-ft-bubble " + role;
    if (role === "assistant" && html) {
      el.innerHTML = html;
    } else {
      el.textContent = plain || html || "";
    }
    thread.appendChild(el);
    thread.scrollTop = thread.scrollHeight;
    return el;
  }

  function initComposerChips() {
    const row = $("sa-ft-composer-chips");
    if (!row) return;
    row.innerHTML = "";
    COMPOSER_CHIPS.forEach(function (chip) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "sa-ft-chip";
      btn.textContent = chip.label;
      btn.addEventListener("click", function () {
        const input = $("sa-ft-input");
        if (input) {
          input.value = chip.text;
          input.focus();
        }
      });
      row.appendChild(btn);
    });
  }

  function setStatus(text, live) {
    const el = $("sa-ft-status");
    if (!el) return;
    el.textContent = text;
    el.classList.toggle("is-live", !!live);
    const banner = $("sa-ft-offline-banner");
    if (banner) {
      const offline = /offline|failed/i.test(text);
      banner.hidden = !offline;
    }
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

  function applyDemoModels(models, defaultModel) {
    const sel = $("sa-ft-model");
    if (!sel || !models || !models.length) return;
    modelCatalog = models;
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

  async function loadConfig() {
    try {
      const res = await fetch(CONFIG_URL);
      if (res.ok) {
        const row = await res.json();
        if (row.api_worker_url) apiUrl = row.api_worker_url;
        if (row.model) selectedModel = row.model;
      }
    } catch (_) {
      /* default worker */
    }
    try {
      const st = await fetchJson(
        apiUrl,
        { action: "status", product: PRODUCT },
        STATUS_TIMEOUT_MS,
      );
      if (st.models && st.models.length) {
        applyDemoModels(st.models, st.default_model || st.model);
      } else {
        const pub = await fetch(MODELS_PUBLIC_URL).then(function (r) { return r.json(); });
        const orOnly = (pub.models || []).filter(function (m) {
          return m.provider === "openrouter" || String(m.api_model || m.id || "").includes("/");
        }).map(function (m) {
          return { id: m.api_model || m.id, label: m.label, group: m.group, cost: m.cost_band };
        });
        if (orOnly.length) applyDemoModels(orOnly, pub.default_model);
      }
      setStatus(
        isAiReady(st) ? "Live · prompt forge on send" : "Demo offline — email forge@sourcea.app",
        isAiReady(st),
      );
    } catch (_) {
      setStatus("Demo offline — email forge@sourcea.app", false);
    }
  }

  async function sendChat(forged) {
    const model = ($("sa-ft-model") && $("sa-ft-model").value) || selectedModel;
    const row = await fetchJson(
      apiUrl,
      {
        action: "chat",
        product: PRODUCT,
        message: forged,
        model: model,
        history: history,
        page_path: window.location.pathname || "/sourcea/forge/terminal",
        page_lane: "developer",
        sa_page: "forge-terminal-demo",
      },
      90000,
    );
    if (!row.ok && !row.reply) {
      throw new Error(row.error || row.message || "Chat failed");
    }
    if (row.model_fallback) {
      setStatus("Live · used fallback model", true);
    }
    return row.reply || row.message || "No reply";
  }

  function maybeShowFeedback() {
    if (turnCount < 2) return;
    const panel = $("sa-ft-feedback");
    if (panel) panel.hidden = false;
  }

  function saveFeedback() {
    const row = {
      at: new Date().toISOString(),
      name: ($("sa-ft-fb-name") || {}).value || "",
      call_it: ($("sa-ft-fb-call") || {}).value || "",
      would_pay: ($("sa-ft-fb-pay") || {}).value || "",
      confused: ($("sa-ft-fb-confused") || {}).value || "",
    };
    try {
      const prev = JSON.parse(localStorage.getItem(FEEDBACK_KEY) || "[]");
      prev.push(row);
      localStorage.setItem(FEEDBACK_KEY, JSON.stringify(prev.slice(-20)));
    } catch (_) {
      /* quiet */
    }
    const subject = encodeURIComponent("Forge Terminal demo feedback");
    const body = encodeURIComponent(
      "Name: " +
        row.name +
        "\nWould call it: " +
        row.call_it +
        "\nWould pay: " +
        row.would_pay +
        "\nConfused by: " +
        row.confused +
        "\n\n(Sent from sourcea.app/forge/terminal demo v" +
        DEMO_VERSION +
        ")",
    );
    window.location.href = "mailto:forge@sourcea.app?subject=" + subject + "&body=" + body;
  }

  async function onSend() {
    if (busy) return;
    const input = $("sa-ft-input");
    const text = ((input && input.value) || "").trim();
    if (!text) return;
    busy = true;
    $("sa-ft-send") && ($("sa-ft-send").disabled = true);
    appendBubble("user", "", text);
    history.push({ role: "user", content: text });
    const forged = forgeMission(text);
    appendBubble(
      "system",
      "",
      "Prompt forge shaped your message into a bounded mission — then the model replies.",
    );
    const typing = appendBubble("typing", "", "Thinking…");
    setStatus("Prompt forge → model…", true);
    try {
      const reply = await sendChat(forged);
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      history.push({ role: "assistant", content: reply });
      appendBubble("assistant", renderSections(reply), reply);
      turnCount += 1;
      maybeShowFeedback();
      setStatus("Live · prompt forge on send", true);
      if (input) {
        input.value = "";
        input.focus();
      }
    } catch (e) {
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      appendBubble("assistant", "", String(e.message || e));
      setStatus("Send failed — try again or book a call", false);
    } finally {
      busy = false;
      $("sa-ft-send") && ($("sa-ft-send").disabled = false);
    }
  }

  function bindChips() {
    document.querySelectorAll(".sa-ft-chip").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const input = $("sa-ft-input");
        if (input) {
          input.value = btn.getAttribute("data-prompt") || "";
          input.focus();
        }
      });
    });
  }

  function bind() {
    $("sa-ft-send") && $("sa-ft-send").addEventListener("click", onSend);
    $("sa-ft-input") &&
      $("sa-ft-input").addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
          ev.preventDefault();
          onSend();
        }
      });
    $("sa-ft-fb-save") && $("sa-ft-fb-save").addEventListener("click", saveFeedback);
    const modelSel = $("sa-ft-model");
    if (modelSel) {
      modelSel.addEventListener("change", function () {
        selectedModel = modelSel.value;
        localStorage.setItem(MODEL_KEY, selectedModel);
      });
    }
    bindChips();
    initComposerChips();
    loadConfig();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();

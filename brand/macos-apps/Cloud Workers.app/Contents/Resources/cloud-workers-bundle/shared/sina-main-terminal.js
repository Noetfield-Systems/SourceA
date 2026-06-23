(function () {
  "use strict";

  var PLAIN = {
    hub: "Opens Worker Hub — your task queue, cloud proceed, and form picks on :13020.",
    cloud: "Opens Cloud Workers — Railway queue, CLOUD-SEC drain, deploy commands on :13027.",
    mail: "Opens Portfolio Mail — inbox wiring and mail hub on Hub :13020/mail-hub.",
    chat: "Opens Chat Unify — merges Cursor chats and fires n8n webhook on :13023.",
    n8n: "Opens N8N Integration — automation spine, validators, n8n workflows on :13026.",
    "mac-law": "Opens Mac Law routing panel — Mac control plane rules on :8781.",
    "ag-routing": "Opens AG Routing Panel — agent cost intelligence and brand routes on :8782.",
    capture_intelligence:
      "Scans n8n + Hub + cloud queue on disk, writes intelligence brief to ~/.sina/n8n-intelligence/ — takes 1–3 min; terminal shows each step.",
    start: "Starts local n8n process on :5678 if stopped.",
    validate_chain: "Runs fast parallel living-chain probes — all links in terminal.",
    validator_run: "Probe N8N Integration health + disk receipts.",
    force_auto_tick: "Forces cloud drain auto-tick (skips 15m rate limit) — advances CLOUD-SEC queue.",
    wire_chat_unify: "Wires Chat Unify merge pipeline to n8n webhook.",
    wire_portfolio_mail: "Wires Portfolio Mail + Chat + N8N glue.",
    refresh: "Reloads fast disk snapshot — not a full validator run.",
  };

  var lines = [];
  var running = false;

  function ts() {
    return new Date().toISOString().replace("T", " ").slice(0, 19) + "Z";
  }

  function mount() {
    if (document.getElementById("sina-main-terminal-dock")) return;
    document.body.classList.add("sina-has-main-terminal");
    var dock = document.createElement("div");
    dock.id = "sina-main-terminal-dock";
    dock.className = "sina-main-terminal-dock";
    dock.innerHTML =
      '<div class="sina-main-terminal-head">' +
      "<span><strong>Main terminal</strong> · concrete output only · status tiles are glance hints</span>" +
      '<span id="sina-main-terminal-badge" class="sina-main-terminal-badge">idle</span>' +
      "</div>" +
      '<div id="sina-main-terminal-hint" class="sina-main-terminal-hint">Tap any action — plain English + live lines appear here.</div>' +
      '<pre id="sina-main-terminal-body" class="sina-main-terminal-body">Ready.</pre>';
    document.body.appendChild(dock);
  }

  function render() {
    var body = document.getElementById("sina-main-terminal-body");
    var badge = document.getElementById("sina-main-terminal-badge");
    if (body) {
      body.textContent = lines.length ? lines.join("\n") : "Ready.";
      body.classList.toggle("running", running);
      body.scrollTop = body.scrollHeight;
    }
    if (badge) {
      badge.textContent = running ? "running" : lines.length > 2 ? "ready" : "idle";
      badge.className = "sina-main-terminal-badge" + (running ? " running" : "");
    }
  }

  function log(msg) {
    lines.push("[" + ts() + "] " + msg);
    if (lines.length > 400) lines = lines.slice(-350);
    render();
  }

  function hint(text) {
    var el = document.getElementById("sina-main-terminal-hint");
    if (el) el.textContent = text;
  }

  function plain(key) {
    return PLAIN[key] || "Runs " + key + " — watch terminal for concrete output.";
  }

  function start(action, label) {
    running = true;
    var desc = plain(action);
    hint(desc);
    log("═══ " + (label || action) + " ═══");
    log("→ " + desc);
    render();
  }

  function finish(ok, summary) {
    running = false;
    if (summary) log(summary);
    log("═══ " + (ok ? "PASS" : "FAIL") + " · finished ═══");
    var badge = document.getElementById("sina-main-terminal-badge");
    if (badge) {
      badge.textContent = ok ? "pass" : "fail";
      badge.className = "sina-main-terminal-badge " + (ok ? "pass" : "fail");
    }
    render();
  }

  function setRunning(isRunning) {
    running = !!isRunning;
    render();
  }

  function appendBlock(blockLines) {
    (blockLines || []).forEach(function (ln) {
      lines.push(ln);
    });
    render();
  }

  window.SinaMainTerminal = {
    mount: mount,
    log: log,
    hint: hint,
    plain: plain,
    start: start,
    finish: finish,
    setRunning: setRunning,
    appendBlock: appendBlock,
    lines: function () {
      return lines.slice();
    },
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();

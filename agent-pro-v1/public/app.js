/**
 * Agent Pro v1 — Composer, Inbox, Session surfaces.
 * No legacy hub. SSE pushes every state change to the UI.
 */
(function () {
  "use strict";

  const API = location.origin;
  let view = "inbox";
  let state = null;
  let sessionTab = "plan";
  let es = null;

  const $ = (id) => document.getElementById(id);

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function activeSession() {
    const id = state?.active_session_id;
    return (state?.sessions || []).find((s) => s.id === id) || (state?.sessions || [])[0];
  }

  function paintTop() {
    const s = activeSession();
    const running = s?.status === "running";
    $("chips").innerHTML = `
      <span class="chip ${running ? "chip--run" : "chip--ok"}">${running ? "Agent running" : "Idle"}</span>
      <span class="chip">${(state?.inbox || []).filter((t) => t.status === "needs_approval").length} need approval</span>`;
    $("title").textContent =
      view === "inbox" ? "Inbox" : view === "session" ? "Agent session" : "Inbox";
  }

  function renderInbox() {
    $("workspace").className = "body single";
    const items = state?.inbox || [];
    $("main").innerHTML = `<div class="inbox">${items
      .map(
        (t) => `<article class="card">
        <h3>${esc(t.title)}</h3>
        <p class="meta">Owner: ${esc(t.owner)} · Delegate: ${esc(t.delegate)} · ${esc(t.status)}</p>
        <p>Delegate work — you stay accountable while the agent executes.</p>
        ${
          t.status === "needs_approval"
            ? `<button type="button" class="btn btn--primary" data-approve="${esc(t.id)}">Approve & run</button>`
            : `<span class="meta">Approved</span>`
        }
      </article>`
      )
      .join("")}</div>`;
    document.querySelectorAll("[data-approve]").forEach((btn) => {
      btn.onclick = () => approveInbox(btn.dataset.approve);
    });
  }

  function renderSession() {
    $("workspace").className = "body";
    const s = activeSession();
    const log = s?.log || [];
    const planLines = log.filter((l) => l.phase === "plan");
    const actLines = log.filter((l) => l.phase === "act" || l.phase === "done");

    $("main").innerHTML = `
      <section class="chat">
        <div class="messages" id="messages">
          <div class="msg user"><strong>You</strong><br>${esc(s?.prompt || "Start a session below.")}</div>
          <div class="msg agent"><strong>Agent</strong><br>${esc(s?.status || "idle")} · phase ${esc(s?.phase || "—")}</div>
        </div>
        <form class="composer" id="composer">
          <input type="text" placeholder="Delegate a task to the agent…" autocomplete="off" />
          <button type="submit" class="btn btn--primary">Run</button>
        </form>
      </section>
      <section class="session">
        <div class="tabs">
          <button type="button" data-stab="plan" class="${sessionTab === "plan" ? "active" : ""}">Planner</button>
          <button type="button" data-stab="log" class="${sessionTab === "log" ? "active" : ""}">Output</button>
        </div>
        <div class="panel" id="panel">
          ${
            sessionTab === "plan"
              ? planLines.map((l) => `<div class="plan-step ${s?.phase === "plan" ? "running" : "done"}">${esc(l.line)}</div>`).join("") || "<p class='meta'>Plan appears when session runs.</p>"
              : actLines.map((l) => `<div class="log-line">[${esc(l.phase)}] ${esc(l.line)}</div>`).join("") || "<p class='meta'>Output streams here live.</p>"
          }
        </div>
      </section>`;

    $("composer").onsubmit = async (e) => {
      e.preventDefault();
      const input = e.target.querySelector("input");
      const prompt = input.value.trim();
      if (!prompt) return;
      input.value = "";
      await startSession(prompt);
    };
    document.querySelectorAll("[data-stab]").forEach((b) => {
      b.onclick = () => {
        sessionTab = b.dataset.stab;
        renderSession();
      };
    });
  }

  function render() {
    paintTop();
    document.querySelectorAll(".rail [data-view]").forEach((b) => {
      b.classList.toggle("active", b.dataset.view === view);
    });
    if (view === "inbox") renderInbox();
    else renderSession();
  }

  async function fetchState() {
    const res = await fetch(`${API}/api/state`, { cache: "no-store" });
    const json = await res.json();
    if (json.ok !== false) {
      state = json;
      render();
    }
  }

  async function approveInbox(id) {
    await fetch(`${API}/api/inbox/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
  }

  async function startSession(prompt) {
    await fetch(`${API}/api/session/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    view = "session";
  }

  function connectSSE() {
    if (es) es.close();
    es = new EventSource(`${API}/api/events`);
    $("live").textContent = "Live · connecting…";
    es.onopen = () => {
      $("live").textContent = "Live · connected";
      $("live").classList.add("on");
    };
    es.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.data && (msg.event === "state" || msg.event === "session.update" || msg.event === "connected")) {
          state = msg.data;
          render();
        }
      } catch { /* ignore */ }
    };
    es.onerror = () => {
      $("live").textContent = "Live · reconnecting…";
      $("live").classList.remove("on");
      es.close();
      setTimeout(connectSSE, 2000);
    };
  }

  function bindNav() {
    document.querySelectorAll(".rail [data-view]").forEach((b) => {
      b.onclick = () => {
        view = b.dataset.view;
        render();
      };
    });
  }

  bindNav();
  fetchState();
  connectSSE();
})();

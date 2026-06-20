/**
 * Founder Light v1 — one store, one poll, three tabs.
 * Pattern: Stripe (few destinations) + Linear (instant tap feedback).
 */
(function () {
  "use strict";

  const API = `${location.protocol}//${location.host}`;
  const POLL_MS = 3000;

  let state = null;
  let tab = "home";
  let gid = 0;
  let output = "";
  let pollTimer = null;

  const $ = (id) => document.getElementById(id);

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function setOutput(text, pulse) {
    output = text;
    const el = $("output");
    if (!el) return;
    el.textContent = text || "Tap an action — result appears here.";
    if (pulse) {
      el.classList.add("pulse");
      setTimeout(() => el.classList.remove("pulse"), 1200);
      el.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }

  function paintChips() {
    const ctx = state?.context || {};
    const home = state?.home || {};
    const frozen = ctx.frozen;
    const q = ctx.queue_pos != null ? `Task ${ctx.queue_pos}` : "Queue";
    const pct = home.progress_pct != null ? `${Number(home.progress_pct).toFixed(1)}%` : "—";
    $("chips").innerHTML = `
      <span class="chip ${frozen ? "chip--warn" : "chip--ok"}">${frozen ? "Paused" : "Running"}</span>
      <span class="chip">${esc(q)}</span>
      <span class="chip">${esc(pct)} done</span>
      <span class="chip ${ctx.worker_ok ? "chip--ok" : "chip--warn"}">${ctx.worker_ok ? "Worker online" : "Worker …"}</span>`;
    $("live").textContent = state?.generation_id
      ? `Live · gen ${state.generation_id}`
      : "Connecting…";
  }

  function renderHome() {
    const h = state?.home || {};
    const pct = Math.max(0, Math.min(100, Number(h.progress_pct) || 0));
    const needs = (state?.needs_you || [])
      .map((n) => `<li>${esc(n.label)}</li>`)
      .join("");
    $("view").innerHTML = `
      <section class="hero">
        <p class="meta">${esc(h.goal_title)}</p>
        <h2>${esc(h.headline)}</h2>
        <p>${esc(h.subline)}</p>
        <div class="progress" aria-label="Progress"><span style="width:${pct}%"></span></div>
        <p class="meta">${esc(h.progress_label)}</p>
      </section>
      ${
        needs
          ? `<section class="panel"><h3>Needs you</h3><ul class="list">${needs}</ul></section>`
          : ""
      }`;
  }

  function renderRun() {
    const r = state?.run || {};
    $("view").innerHTML = `
      <section class="hero">
        <h2>${r.busy ? "Working" : "Ready"}</h2>
        <p>${esc(r.message || "Open Actions for Safety check or Stop factory.")}</p>
        <div class="actions">
          <button type="button" class="btn btn--danger" data-action="founder-goal1-autorun-stop">Stop factory</button>
          <button type="button" class="btn" data-action="founder-ecosystem-safety">Safety check</button>
        </div>
      </section>`;
  }

  function renderActions() {
    const acts = state?.actions || [];
    const btns = acts
      .map((a) => {
        const cls = a.danger ? "btn btn--danger" : "btn";
        return `<button type="button" class="${cls}" data-action="${esc(a.id)}">${esc(a.label)}</button>`;
      })
      .join("");
    $("view").innerHTML = `
      <section class="hero">
        <h2>Actions</h2>
        <p>Six essentials. Results update below and live every ${POLL_MS / 1000}s.</p>
        <div class="actions">${btns}</div>
      </section>
      <section class="panel"><h3>Output</h3><pre class="empty" id="output">${esc(output || "Tap an action — result appears here.")}</pre></section>`;
  }

  function render() {
    paintChips();
    $("title").textContent = tab === "home" ? "Home" : tab === "run" ? "Run" : "Actions";
    document.querySelectorAll(".nav button[data-tab]").forEach((b) => {
      b.classList.toggle("active", b.dataset.tab === tab);
    });
    if (tab === "home") renderHome();
    else if (tab === "run") renderRun();
    else renderActions();
    bindActions();
  }

  async function fetchState() {
    const res = await fetch(`${API}/api/state`, { cache: "no-store" });
    const json = await res.json();
    if (!json.ok) return;
    const newGid = Number(json.generation_id) || 0;
    const changed = !state || newGid !== gid || JSON.stringify(json.home) !== JSON.stringify(state?.home);
    state = json;
    gid = newGid;
    if (changed) render();
    else paintChips();
  }

  async function runAction(id, btn) {
    if (btn) btn.disabled = true;
    const label = btn?.textContent?.trim() || id;
    setOutput(`Running ${label}…`, true);
    try {
      const res = await fetch(`${API}/api/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      const json = await res.json();
      const lines = [
        json.ok ? "OK" : "FAIL",
        json.message || "",
        json.output || json.stdout || "",
        json.error || json.stderr || "",
      ].filter(Boolean);
      setOutput(lines.join("\n"), true);
      if (json.state) {
        state = json.state;
        gid = Number(state.generation_id) || gid;
        render();
      } else {
        await fetchState();
      }
    } catch (e) {
      setOutput(`Error: ${e.message}`, true);
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  function bindActions() {
    document.querySelectorAll("[data-action]").forEach((btn) => {
      btn.onclick = () => runAction(btn.dataset.action, btn);
    });
  }

  function go(t) {
    tab = t;
    render();
  }

  function startPoll() {
    clearInterval(pollTimer);
    pollTimer = setInterval(() => fetchState().catch(() => {}), POLL_MS);
  }

  function bindNav() {
    document.querySelectorAll(".nav button[data-tab]").forEach((b) => {
      b.onclick = () => go(b.dataset.tab);
    });
  }

  async function boot() {
    bindNav();
    await fetchState();
    startPoll();
  }

  boot().catch((e) => {
    $("view").innerHTML = `<p class="meta">Failed to start: ${esc(e.message)}</p>`;
  });
})();

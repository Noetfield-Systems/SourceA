/**
 * sourcea-founder-gates-v1 — daily founder interrupt surface (/gates)
 * E2E v3: create → telegram callback → resolve → Governor ACCEPTED observe
 * Amber Telegram callbacks: signed packets + webhook. Red: view/defer (+ notify).
 * ASK keeps gate OPEN. Never writes Goal Contracts or DecisionRecords.
 */

import { DurableObject } from "cloudflare:workers";

export interface Env {
  GATES: DurableObjectNamespace;
  ASSETS?: Fetcher;
  GATES_SIGNING_SECRET?: string;
  TELEGRAM_BOT_TOKEN?: string;
  TELEGRAM_CHAT_ID_AMBER?: string;
  TELEGRAM_CHAT_ID_RED?: string;
  SOURCEA_GOVERNOR_URL?: string;
}

type GateAction = "APPROVE" | "REJECT" | "DEFER" | "ASK";
type Lane = "AMBER" | "RED";

type GateItem = {
  gate_id: string;
  title: string;
  summary: string;
  lane: Lane;
  correlation_id: string;
  created_at: string;
  status: "OPEN" | "RESOLVED";
  resolution?: GateAction;
  resolved_at?: string;
  ask_count?: number;
  last_ask_at?: string;
  telegram_notified?: boolean;
  e2e?: boolean;
  governor_notify?: {
    at: string;
    http_status: number;
    terminal?: string;
    run_id?: string;
  };
};

type GateEvent = {
  at: string;
  type: string;
  gate_id?: string;
  detail?: Record<string, unknown>;
};

type CallbackPacket = {
  v: 1;
  gate_id: string;
  action: GateAction;
  lane: Lane;
  exp: number;
  nonce: string;
  idempotency_key: string;
};

type E2eStep = {
  step: string;
  ok: boolean;
  detail?: Record<string, unknown>;
  error?: string;
};

function cors(res: Response): Response {
  const h = new Headers(res.headers);
  h.set("access-control-allow-origin", "*");
  h.set("access-control-allow-methods", "GET,POST,OPTIONS");
  h.set("access-control-allow-headers", "content-type,x-gates-signature,authorization,x-gates-e2e");
  return new Response(res.body, { status: res.status, headers: h });
}

async function hmacHex(secret: string, body: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function signPacket(secret: string, packet: CallbackPacket): Promise<string> {
  const payload = JSON.stringify(packet);
  const sig = await hmacHex(secret, payload);
  return btoa(JSON.stringify({ packet, sig }));
}

async function verifyPacket(
  secret: string,
  token: string,
): Promise<{ ok: true; packet: CallbackPacket } | { ok: false; reason: string }> {
  try {
    const parsed = JSON.parse(atob(token)) as { packet: CallbackPacket; sig: string };
    const expect = await hmacHex(secret, JSON.stringify(parsed.packet));
    if (expect !== parsed.sig) return { ok: false, reason: "bad_signature" };
    if (Date.now() / 1000 > parsed.packet.exp) return { ok: false, reason: "expired" };
    return { ok: true, packet: parsed.packet };
  } catch {
    return { ok: false, reason: "malformed" };
  }
}

const GATES_HTML = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta name="color-scheme" content="dark"/>
<title>SourceA Gates</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet"/>
<style>
  :root {
    --bg0:#0b1016; --bg1:#121a24; --fg:#e8eef4; --muted:#8a98a8; --line:#2a3848;
    --amber:#e0a21a; --amber-dim:rgba(224,162,26,.14);
    --red:#d45a5a; --red-dim:rgba(212,90,90,.14);
    --ok:#3fae74; --ok-dim:rgba(63,174,116,.14);
    --panel:rgba(18,26,36,.88); --glow:rgba(224,162,26,.08);
  }
  * { box-sizing:border-box; }
  body {
    margin:0; font-family:"IBM Plex Sans", ui-sans-serif, sans-serif; color:var(--fg); min-height:100vh;
    background:
      radial-gradient(900px 420px at 12% -10%, var(--glow), transparent 55%),
      radial-gradient(700px 360px at 100% 0%, rgba(61,120,160,.12), transparent 50%),
      linear-gradient(165deg, var(--bg0), var(--bg1) 55%, #0e1620);
  }
  main { max-width:760px; margin:0 auto; padding:1.75rem 1.2rem 3.5rem; }
  .brand { font-family:Syne, sans-serif; font-weight:800; font-size:clamp(1.85rem, 4.5vw, 2.35rem); letter-spacing:-0.03em; line-height:1.05; margin:0 0 .4rem; }
  .brand span { color:var(--amber); }
  .lead { color:var(--muted); margin:0 0 1.25rem; font-size:.98rem; max-width:38rem; }
  .pulse-row { display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:.55rem; margin-bottom:1rem; }
  @media (max-width:560px) { .pulse-row { grid-template-columns:repeat(2, minmax(0,1fr)); } }
  .stat { background:var(--panel); border:1px solid var(--line); padding:.7rem .8rem; border-radius:2px; }
  .stat .k { font-size:.68rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
  .stat .v { font-family:Syne, sans-serif; font-weight:700; font-size:1.35rem; margin-top:.15rem; }
  .stat.amber .v { color:var(--amber); } .stat.red .v { color:var(--red); }
  .toolbar { display:flex; flex-wrap:wrap; align-items:center; gap:.5rem; margin-bottom:1rem; }
  .filters { display:flex; gap:.35rem; flex-wrap:wrap; flex:1; }
  .chip, button { font:inherit; cursor:pointer; background:#172231; color:var(--fg); border:1px solid var(--line); padding:.42rem .75rem; border-radius:2px; }
  .chip.active { border-color:var(--amber); background:var(--amber-dim); color:#f3d58a; }
  button:hover, .chip:hover { border-color:#4d647c; }
  button:disabled { opacity:.45; cursor:not-allowed; }
  button.primary { border-color:var(--ok); background:var(--ok-dim); }
  button.danger { border-color:var(--red); background:var(--red-dim); }
  button.ghost { background:transparent; }
  #status { min-height:1.25rem; font-size:.85rem; color:var(--muted); margin-bottom:.75rem; }
  #status.ok { color:var(--ok); } #status.err { color:var(--red); }
  .gate { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--line); padding:1rem 1rem .95rem; margin:0 0 .65rem; }
  .gate.AMBER { border-left-color:var(--amber); } .gate.RED { border-left-color:var(--red); } .gate.RESOLVED { opacity:.72; }
  .row { display:flex; flex-wrap:wrap; gap:.4rem .65rem; align-items:center; margin-bottom:.45rem; }
  .lane { font-size:.68rem; letter-spacing:.07em; font-weight:600; padding:.18rem .45rem; border:1px solid var(--line); }
  .lane.AMBER { color:var(--amber); border-color:var(--amber); background:var(--amber-dim); }
  .lane.RED { color:var(--red); border-color:var(--red); background:var(--red-dim); }
  .badge { font-size:.68rem; letter-spacing:.04em; color:var(--muted); border:1px solid var(--line); padding:.15rem .4rem; }
  .badge.OPEN { color:#9fd6b8; border-color:#3d6a55; }
  .badge.ACCEPTED { color:var(--ok); border-color:var(--ok); }
  .title { font-family:Syne, sans-serif; font-weight:700; font-size:1.08rem; margin:.15rem 0 .35rem; }
  .summary { color:var(--muted); font-size:.92rem; margin:0 0 .65rem; line-height:1.45; }
  .meta { font-size:.75rem; color:var(--muted); display:flex; flex-wrap:wrap; gap:.35rem .75rem; }
  .meta code { font-family:ui-monospace, SFMono-Regular, Menlo, monospace; font-size:.72rem; }
  .actions { display:flex; flex-wrap:wrap; gap:.45rem; margin-top:.8rem; }
  .empty { border:1px dashed var(--line); padding:1.5rem 1rem; color:var(--muted); text-align:center; }
  .empty strong { display:block; color:var(--fg); font-family:Syne, sans-serif; margin-bottom:.35rem; }
  #e2e { margin:1rem 0; padding:.85rem 1rem; border:1px solid var(--line); background:var(--panel); font-size:.82rem; color:var(--muted); }
  #e2e.pass { border-color:var(--ok); color:#9fd6b8; }
  #e2e.fail { border-color:var(--red); color:#f0a0a0; }
  footer.law { margin-top:1.75rem; padding-top:1rem; border-top:1px solid var(--line); font-size:.75rem; color:var(--muted); line-height:1.5; }
</style>
</head>
<body>
<main>
  <h1 class="brand">SourceA <span>Gates</span></h1>
  <p class="lead">Daily founder interrupt surface. Amber decisions · Telegram callbacks · Governor observe. Canvas stays forensic.</p>
  <div class="pulse-row" id="pulse">
    <div class="stat"><div class="k">Open</div><div class="v" id="p-open">—</div></div>
    <div class="stat amber"><div class="k">Amber</div><div class="v" id="p-amber">—</div></div>
    <div class="stat red"><div class="k">Red</div><div class="v" id="p-red">—</div></div>
    <div class="stat"><div class="k">Updated</div><div class="v" id="p-at" style="font-size:.85rem;font-family:IBM Plex Sans,sans-serif;font-weight:500">—</div></div>
  </div>
  <div id="e2e">E2E · loading…</div>
  <div class="toolbar">
    <div class="filters" role="tablist" aria-label="Filter gates">
      <button type="button" class="chip active" data-filter="OPEN">Open</button>
      <button type="button" class="chip" data-filter="RESOLVED">Resolved</button>
      <button type="button" class="chip" data-filter="ALL">All</button>
    </div>
    <button type="button" class="ghost" id="btn-refresh">Refresh</button>
  </div>
  <div id="status" aria-live="polite"></div>
  <div id="list"></div>
  <footer class="law">
    Amber: APPROVE · REJECT · DEFER · ASK (ASK keeps open) &nbsp;·&nbsp; Red: DEFER only<br/>
    Mac observes · Railway/cloud owns · Governor ACCEPTED = observe only · no DecisionRecords
  </footer>
</main>
<script>
(function () {
  let filter = 'OPEN';
  let busy = false;
  const statusEl = document.getElementById('status');
  const listEl = document.getElementById('list');
  const e2eEl = document.getElementById('e2e');

  function esc(s) {
    return String(s ?? '').replace(/[&<>"']/g, function (c) {
      return ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' })[c];
    });
  }
  function rel(iso) {
    if (!iso) return '';
    const t = Date.parse(iso);
    if (!t) return esc(iso);
    const sec = Math.max(0, Math.round((Date.now() - t) / 1000));
    if (sec < 60) return sec + 's ago';
    if (sec < 3600) return Math.floor(sec / 60) + 'm ago';
    if (sec < 86400) return Math.floor(sec / 3600) + 'h ago';
    return Math.floor(sec / 86400) + 'd ago';
  }
  function setStatus(msg, kind) {
    statusEl.textContent = msg || '';
    statusEl.className = kind || '';
  }
  function actionsFor(g) {
    if (g.status !== 'OPEN') return [];
    if (g.lane === 'AMBER') return ['APPROVE','REJECT','DEFER','ASK'];
    if (g.lane === 'RED') return ['DEFER'];
    return [];
  }
  function render(gates, pulse, e2e) {
    document.getElementById('p-open').textContent = String(pulse.open_count ?? 0);
    document.getElementById('p-amber').textContent = String(pulse.amber_open ?? 0);
    document.getElementById('p-red').textContent = String(pulse.red_open ?? 0);
    document.getElementById('p-at').textContent = rel(pulse.at) || 'now';
    if (e2e && e2e.at) {
      e2eEl.className = e2e.ok ? 'pass' : 'fail';
      e2eEl.textContent = 'E2E ' + (e2e.ok ? 'PASS' : 'FAIL') + ' · ' + rel(e2e.at) +
        (e2e.receipt_id ? ' · ' + e2e.receipt_id : '');
    } else {
      e2eEl.className = '';
      e2eEl.textContent = 'E2E · no cloud receipt yet · POST /v1/e2e/run';
    }
    const items = (gates.items || []).filter(function (g) {
      if (filter === 'ALL') return true;
      return g.status === filter;
    });
    listEl.innerHTML = '';
    if (!items.length) {
      listEl.innerHTML = '<div class="empty"><strong>No ' + (filter === 'ALL' ? '' : filter.toLowerCase() + ' ') + 'gates</strong>Pulse stays live — new interrupts appear here.</div>';
      return;
    }
    for (const g of items) {
      const el = document.createElement('article');
      el.className = 'gate ' + g.lane + ' ' + g.status;
      const acts = actionsFor(g);
      const gov = g.governor_notify && g.governor_notify.terminal
        ? '<span class="badge ACCEPTED">' + esc(g.governor_notify.terminal) + '</span>'
        : '';
      const ask = g.ask_count ? '<span class="badge">ASK×' + esc(g.ask_count) + '</span>' : '';
      el.innerHTML =
        '<div class="row">' +
          '<span class="lane ' + esc(g.lane) + '">' + esc(g.lane) + '</span>' +
          '<span class="badge ' + esc(g.status) + '">' + esc(g.status) +
            (g.resolution ? ' · ' + esc(g.resolution) : '') + '</span>' +
          ask + gov +
          '<span class="badge">' + esc(rel(g.created_at)) + '</span>' +
        '</div>' +
        '<div class="title">' + esc(g.title) + '</div>' +
        '<p class="summary">' + esc(g.summary || '') + '</p>' +
        '<div class="meta">' +
          '<span><code>' + esc(g.gate_id) + '</code></span>' +
          '<span>corr <code>' + esc(g.correlation_id) + '</code></span>' +
        '</div>' +
        '<div class="actions"></div>';
      const box = el.querySelector('.actions');
      for (const a of acts) {
        const b = document.createElement('button');
        b.type = 'button';
        b.textContent = a;
        if (a === 'APPROVE') b.className = 'primary';
        if (a === 'REJECT') b.className = 'danger';
        b.onclick = function () { resolve(g.gate_id, a); };
        box.appendChild(b);
      }
      listEl.appendChild(el);
    }
  }
  async function load(quiet) {
    if (!quiet) setStatus('Loading…');
    try {
      const [gates, pulse, e2e] = await Promise.all([
        fetch('/v1/gates').then(function (r) { return r.json(); }),
        fetch('/v1/pulse').then(function (r) { return r.json(); }),
        fetch('/v1/e2e/last').then(function (r) { return r.json(); }).catch(function () { return {}; }),
      ]);
      render(gates, pulse, e2e);
      if (!quiet) setStatus('Synced · ' + (pulse.at || ''), '');
    } catch (e) {
      setStatus('Load failed — retrying', 'err');
    }
  }
  async function resolve(gateId, action) {
    if (busy) return;
    busy = true;
    listEl.querySelectorAll('button').forEach(function (b) { b.disabled = true; });
    setStatus('Resolving ' + action + '…');
    try {
      const res = await fetch('/v1/gates/' + encodeURIComponent(gateId) + '/resolve', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ action: action }),
      });
      const j = await res.json();
      if (j.ok) {
        setStatus(action + ' · ' + gateId, 'ok');
        await load(true);
      } else {
        setStatus('Failed: ' + (j.error || res.status), 'err');
        listEl.querySelectorAll('button').forEach(function (b) { b.disabled = false; });
      }
    } catch (e) {
      setStatus('Network error', 'err');
      listEl.querySelectorAll('button').forEach(function (b) { b.disabled = false; });
    }
    busy = false;
  }
  document.querySelectorAll('[data-filter]').forEach(function (chip) {
    chip.addEventListener('click', function () {
      filter = chip.getAttribute('data-filter');
      document.querySelectorAll('[data-filter]').forEach(function (c) {
        c.classList.toggle('active', c === chip);
      });
      load(true);
    });
  });
  document.getElementById('btn-refresh').onclick = function () { load(false); };
  load(false);
  setInterval(function () { if (!busy) load(true); }, 20000);
})();
</script>
</body>
</html>`;

export class FounderGatesDO extends DurableObject<Env> {
  private async emit(type: string, gate_id?: string, detail?: Record<string, unknown>): Promise<void> {
    const events = (await this.ctx.storage.get<GateEvent[]>("events")) || [];
    events.unshift({ at: new Date().toISOString(), type, gate_id, detail });
    await this.ctx.storage.put("events", events.slice(0, 100));
  }

  private e2eAuthorized(request: Request): boolean {
    const secret = this.env.GATES_SIGNING_SECRET || "";
    if (secret.length < 32) return false;
    const auth = request.headers.get("authorization") || "";
    const hdr = request.headers.get("x-gates-e2e") || "";
    if (auth === `Bearer ${secret}`) return true;
    if (hdr === secret) return true;
    return false;
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method === "OPTIONS") return cors(new Response(null, { status: 204 }));

    if (request.method === "GET" && path === "/health") {
      return cors(
        Response.json({
          ok: true,
          worker: "sourcea-founder-gates-v1",
          ui: "v3",
          e2e: "v1",
          governor_wired: Boolean(this.env.SOURCEA_GOVERNOR_URL),
          telegram_amber: Boolean(this.env.TELEGRAM_BOT_TOKEN && this.env.TELEGRAM_CHAT_ID_AMBER),
          telegram_red: Boolean(this.env.TELEGRAM_BOT_TOKEN && this.env.TELEGRAM_CHAT_ID_RED),
          decision_id: "NF-SOURCEA-N8N-ORCHESTRATOR-V1",
        }),
      );
    }

    if (request.method === "GET" && (path === "/" || path === "/gates")) {
      return cors(
        new Response(GATES_HTML, {
          headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" },
        }),
      );
    }

    if (request.method === "GET" && path === "/v1/pulse") {
      const items = (await this.ctx.storage.get<GateItem[]>("gates")) || [];
      const open = items.filter((g) => g.status === "OPEN");
      const lastE2e = await this.ctx.storage.get<{ ok?: boolean; at?: string }>("e2e_last");
      return cors(
        Response.json({
          schema: "sourcea_gates_pulse_v1",
          at: new Date().toISOString(),
          open_count: open.length,
          amber_open: open.filter((g) => g.lane === "AMBER").length,
          red_open: open.filter((g) => g.lane === "RED").length,
          resolved_count: items.filter((g) => g.status === "RESOLVED").length,
          e2e_last_ok: lastE2e?.ok ?? null,
          e2e_last_at: lastE2e?.at ?? null,
        }),
      );
    }

    if (request.method === "GET" && path === "/v1/events") {
      const events = (await this.ctx.storage.get<GateEvent[]>("events")) || [];
      return cors(Response.json({ schema: "sourcea_gates_events_v1", items: events.slice(0, 50) }));
    }

    if (request.method === "GET" && path === "/v1/e2e/last") {
      const last = (await this.ctx.storage.get<Record<string, unknown>>("e2e_last")) || {};
      return cors(Response.json(last));
    }

    if (request.method === "GET" && path === "/v1/gates") {
      const items = (await this.ctx.storage.get<GateItem[]>("gates")) || [];
      const status = url.searchParams.get("status");
      const filtered =
        status === "OPEN" || status === "RESOLVED"
          ? items.filter((g) => g.status === status)
          : items;
      return cors(Response.json({ schema: "sourcea_gates_list_v1", items: filtered, ui: "v3" }));
    }

    if (request.method === "POST" && path === "/v1/gates") {
      const body = (await request.json()) as Partial<GateItem> & { e2e?: boolean };
      const items = (await this.ctx.storage.get<GateItem[]>("gates")) || [];
      const gate: GateItem = {
        gate_id: String(body.gate_id || `gate_${crypto.randomUUID()}`),
        title: String(body.title || "Untitled gate"),
        summary: String(body.summary || ""),
        lane: body.lane === "RED" ? "RED" : "AMBER",
        correlation_id: String(body.correlation_id || crypto.randomUUID()),
        created_at: new Date().toISOString(),
        status: "OPEN",
        e2e: Boolean(body.e2e),
      };
      items.unshift(gate);
      await this.ctx.storage.put("gates", items.slice(0, 200));
      await this.emit("GATE_CREATED", gate.gate_id, { lane: gate.lane, e2e: gate.e2e });
      if (!gate.e2e) {
        if (gate.lane === "AMBER") {
          gate.telegram_notified = await this.notifyTelegram(gate, "AMBER");
        } else {
          gate.telegram_notified = await this.notifyTelegram(gate, "RED");
        }
        const items2 = (await this.ctx.storage.get<GateItem[]>("gates")) || [];
        const i = items2.findIndex((g) => g.gate_id === gate.gate_id);
        if (i >= 0) {
          items2[i].telegram_notified = gate.telegram_notified;
          await this.ctx.storage.put("gates", items2);
        }
      }
      return cors(Response.json({ ok: true, gate }, { status: 201 }));
    }

    if (request.method === "POST" && path.startsWith("/v1/gates/") && path.endsWith("/resolve")) {
      const gateId = path.split("/")[3];
      const body = (await request.json()) as { action?: GateAction };
      return cors(await this.resolve(gateId, body.action || "DEFER", "ui", true));
    }

    if (request.method === "POST" && path === "/v1/telegram/webhook") {
      return cors(await this.handleTelegramWebhook(request));
    }

    if (request.method === "POST" && path === "/v1/telegram/callback") {
      return cors(await this.handleSignedCallback(await request.json()));
    }

    if (request.method === "POST" && path === "/v1/telegram/mint") {
      const secret = this.env.GATES_SIGNING_SECRET || "";
      if (secret.length < 32) {
        return cors(Response.json({ ok: false, error: "signing_secret_missing" }, { status: 503 }));
      }
      const body = (await request.json()) as Partial<CallbackPacket>;
      if (body.lane === "RED" && body.action && body.action !== "DEFER") {
        return cors(Response.json({ ok: false, error: "red_lane_view_defer_only" }, { status: 403 }));
      }
      const packet: CallbackPacket = {
        v: 1,
        gate_id: String(body.gate_id || ""),
        action: (body.action as GateAction) || "DEFER",
        lane: body.lane === "RED" ? "RED" : "AMBER",
        exp: Math.floor(Date.now() / 1000) + Number(body.exp || 900),
        nonce: crypto.randomUUID(),
        idempotency_key: String(body.idempotency_key || `tg_${crypto.randomUUID()}`),
      };
      const token = await signPacket(secret, packet);
      return cors(Response.json({ ok: true, token, packet }));
    }

    if (request.method === "POST" && path === "/v1/e2e/run") {
      if (!this.e2eAuthorized(request)) {
        return cors(Response.json({ ok: false, error: "unauthorized_e2e" }, { status: 401 }));
      }
      return cors(await this.runE2e());
    }

    return cors(Response.json({ error: "not_found" }, { status: 404 }));
  }

  private async handleTelegramWebhook(request: Request): Promise<Response> {
    const update = (await request.json().catch(() => ({}))) as {
      callback_query?: { id?: string; data?: string };
    };
    const cq = update.callback_query;
    if (!cq?.data) {
      return Response.json({ ok: true, ignored: true });
    }
    const result = await this.handleSignedCallback({ callback_data: cq.data });
    const token = this.env.TELEGRAM_BOT_TOKEN;
    if (token && cq.id) {
      const data = (await result.clone().json().catch(() => ({}))) as { ok?: boolean; error?: string };
      await fetch(`https://api.telegram.org/bot${token}/answerCallbackQuery`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          callback_query_id: cq.id,
          text: data.ok ? "Recorded" : String(data.error || "Failed").slice(0, 180),
          show_alert: !data.ok,
        }),
      }).catch(() => undefined);
    }
    return result;
  }

  private async handleSignedCallback(body: {
    token?: string;
    callback_data?: string;
  }): Promise<Response> {
    const secret = this.env.GATES_SIGNING_SECRET || "";
    if (secret.length < 32) {
      return Response.json({ ok: false, error: "signing_secret_missing" }, { status: 503 });
    }
    let token = String(body.token || "");
    const cb = String(body.callback_data || "");
    if (!token && cb.startsWith("g:")) {
      const stored = await this.ctx.storage.get<string>(`tgcb:${cb.slice(2)}`);
      if (!stored) return Response.json({ ok: false, error: "unknown_callback" }, { status: 404 });
      token = stored;
    }
    const verified = await verifyPacket(secret, token);
    if (!verified.ok) return Response.json({ ok: false, error: verified.reason }, { status: 401 });
    const { packet } = verified;
    if (packet.lane === "RED" && packet.action !== "DEFER") {
      return Response.json({ ok: false, error: "red_lane_view_defer_only" }, { status: 403 });
    }
    const seen = await this.ctx.storage.get<string>(`idem:${packet.idempotency_key}`);
    if (seen) return Response.json({ ok: true, idempotent: true, gate_id: seen });
    const res = await this.resolve(packet.gate_id, packet.action, "telegram", true);
    const data = (await res.json()) as { ok?: boolean };
    if (data.ok) await this.ctx.storage.put(`idem:${packet.idempotency_key}`, packet.gate_id);
    return Response.json({ ...(data as object), nonce: packet.nonce });
  }

  private async resolve(
    gateId: string,
    action: GateAction,
    source: string,
    awaitGovernor: boolean,
  ): Promise<Response> {
    const items = (await this.ctx.storage.get<GateItem[]>("gates")) || [];
    const idx = items.findIndex((g) => g.gate_id === gateId);
    if (idx < 0) return Response.json({ ok: false, error: "not_found" }, { status: 404 });
    const gate = items[idx];
    if (gate.status !== "OPEN") {
      return Response.json({ ok: true, idempotent: true, gate });
    }
    if (gate.lane === "RED" && action !== "DEFER") {
      return Response.json({ ok: false, error: "red_lane_view_defer_only" }, { status: 403 });
    }

    // ASK keeps the interrupt open — founder needs more context
    if (action === "ASK") {
      gate.ask_count = (gate.ask_count || 0) + 1;
      gate.last_ask_at = new Date().toISOString();
      items[idx] = gate;
      await this.ctx.storage.put("gates", items);
      await this.emit("GATE_ASKED", gate.gate_id, { source, ask_count: gate.ask_count });
      return Response.json({ ok: true, gate, source, kept_open: true });
    }

    gate.status = "RESOLVED";
    gate.resolution = action;
    gate.resolved_at = new Date().toISOString();
    items[idx] = gate;
    await this.ctx.storage.put("gates", items);
    await this.emit("GATE_RESOLVED", gate.gate_id, { action, source, lane: gate.lane });

    if (awaitGovernor) {
      await this.notifyGovernor(gate, action, source);
      const refreshed = ((await this.ctx.storage.get<GateItem[]>("gates")) || []).find(
        (g) => g.gate_id === gateId,
      );
      return Response.json({ ok: true, gate: refreshed || gate, source });
    }
    this.ctx.waitUntil(this.notifyGovernor(gate, action, source));
    return Response.json({ ok: true, gate, source });
  }

  private async notifyGovernor(
    gate: GateItem,
    action: GateAction,
    source: string,
  ): Promise<void> {
    const base = (this.env.SOURCEA_GOVERNOR_URL || "").replace(/\/$/, "");
    if (!base) return;
    const idempotency_key = `founder_gate_resolved:${gate.gate_id}:${action}:${gate.resolved_at}`;
    const event_id = `gate_resolve_${gate.gate_id}_${action}`;
    try {
      const res = await fetch(`${base}/v1/executive/runs?org=sourcea`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          event_id,
          idempotency_key,
          event_type: "founder.gate.resolved",
          payload: {
            task_type: "founder_gate_resolved",
            gate_id: gate.gate_id,
            action,
            lane: gate.lane,
            correlation_id: gate.correlation_id,
            source,
            title: gate.title,
            summary: gate.summary,
          },
        }),
      });
      const body = (await res.json().catch(() => ({}))) as {
        terminal?: string;
        run_id?: string;
      };
      const items = (await this.ctx.storage.get<GateItem[]>("gates")) || [];
      const i = items.findIndex((g) => g.gate_id === gate.gate_id);
      if (i >= 0) {
        items[i].governor_notify = {
          at: new Date().toISOString(),
          http_status: res.status,
          terminal: body.terminal,
          run_id: body.run_id,
        };
        await this.ctx.storage.put("gates", items);
      }
      await this.emit("GATE_GOVERNOR_NOTIFIED", gate.gate_id, {
        terminal: body.terminal,
        http_status: res.status,
        run_id: body.run_id,
      });
    } catch (exc) {
      await this.emit("GATE_GOVERNOR_NOTIFY_FAILED", gate.gate_id, {
        error: String(exc).slice(0, 160),
      });
    }
  }

  private async notifyTelegram(gate: GateItem, lane: Lane): Promise<boolean> {
    const secret = this.env.GATES_SIGNING_SECRET;
    const token = this.env.TELEGRAM_BOT_TOKEN;
    const chat =
      lane === "RED" ? this.env.TELEGRAM_CHAT_ID_RED : this.env.TELEGRAM_CHAT_ID_AMBER;
    if (!secret || secret.length < 32 || !token || !chat) return false;
    const actions: GateAction[] =
      lane === "RED" ? ["DEFER"] : ["APPROVE", "REJECT", "DEFER", "ASK"];
    const buttons = [];
    for (const action of actions) {
      const packet: CallbackPacket = {
        v: 1,
        gate_id: gate.gate_id,
        action,
        lane,
        exp: Math.floor(Date.now() / 1000) + 900,
        nonce: crypto.randomUUID(),
        idempotency_key: `tg_${gate.gate_id}_${action}`,
      };
      const signed = await signPacket(secret, packet);
      const shortId = crypto.randomUUID().replace(/-/g, "").slice(0, 24);
      await this.ctx.storage.put(`tgcb:${shortId}`, signed);
      buttons.push([{ text: action, callback_data: `g:${shortId}` }]);
    }
    try {
      const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          chat_id: chat,
          text: `${lane} gate\n${gate.title}\n${gate.summary}\n${gate.gate_id}`,
          reply_markup: { inline_keyboard: buttons },
        }),
      });
      const ok = res.ok;
      await this.emit(ok ? "GATE_TELEGRAM_SENT" : "GATE_TELEGRAM_FAILED", gate.gate_id, {
        lane,
        http_status: res.status,
      });
      return ok;
    } catch {
      await this.emit("GATE_TELEGRAM_FAILED", gate.gate_id, { lane });
      return false;
    }
  }

  private async runE2e(): Promise<Response> {
    const receipt_id = `e2e_${crypto.randomUUID().slice(0, 8)}`;
    const steps: E2eStep[] = [];
    const started = Date.now();

    const push = (step: string, ok: boolean, detail?: Record<string, unknown>, error?: string) => {
      steps.push({ step, ok, detail, error });
    };

    // 1) health preconditions
    const healthOk =
      Boolean(this.env.SOURCEA_GOVERNOR_URL) &&
      Boolean(this.env.GATES_SIGNING_SECRET && this.env.GATES_SIGNING_SECRET.length >= 32);
    push("preconditions", healthOk, {
      governor_wired: Boolean(this.env.SOURCEA_GOVERNOR_URL),
      signing_secret: Boolean(this.env.GATES_SIGNING_SECRET),
      telegram_amber: Boolean(this.env.TELEGRAM_BOT_TOKEN && this.env.TELEGRAM_CHAT_ID_AMBER),
    });

    // 2) create amber + telegram callback resolve + governor ACCEPTED
    const amberId = `gate_e2e_amber_${crypto.randomUUID().slice(0, 8)}`;
    const createAmber = await this.fetch(
      new Request("https://gates.internal/v1/gates", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          gate_id: amberId,
          title: "E2E amber",
          summary: receipt_id,
          lane: "AMBER",
          correlation_id: receipt_id,
          e2e: true,
        }),
      }),
    );
    const amberBody = (await createAmber.json()) as { ok?: boolean; gate?: GateItem };
    push("create_amber", Boolean(amberBody.ok), { gate_id: amberId });

    const secret = this.env.GATES_SIGNING_SECRET!;
    const packet: CallbackPacket = {
      v: 1,
      gate_id: amberId,
      action: "APPROVE",
      lane: "AMBER",
      exp: Math.floor(Date.now() / 1000) + 900,
      nonce: crypto.randomUUID(),
      idempotency_key: `e2e_${amberId}_APPROVE`,
    };
    const token = await signPacket(secret, packet);
    const cb = await this.handleSignedCallback({ token });
    const cbBody = (await cb.json()) as {
      ok?: boolean;
      gate?: GateItem;
    };
    const govTerminal = cbBody.gate?.governor_notify?.terminal;
    const govOk = Boolean(cbBody.ok) && govTerminal === "ACCEPTED";
    push("telegram_callback_approve_governor", govOk, {
      terminal: govTerminal,
      run_id: cbBody.gate?.governor_notify?.run_id,
      http_status: cbBody.gate?.governor_notify?.http_status,
    });

    // 3) RED lane: APPROVE forbidden, DEFER + governor
    const redId = `gate_e2e_red_${crypto.randomUUID().slice(0, 8)}`;
    await this.fetch(
      new Request("https://gates.internal/v1/gates", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          gate_id: redId,
          title: "E2E red",
          summary: receipt_id,
          lane: "RED",
          correlation_id: receipt_id,
          e2e: true,
        }),
      }),
    );
    const redBad = await this.resolve(redId, "APPROVE", "e2e", false);
    const redBadBody = (await redBad.json()) as { ok?: boolean; error?: string };
    push("red_approve_forbidden", redBad.status === 403 && !redBadBody.ok, {
      error: redBadBody.error,
    });
    const redOkRes = await this.resolve(redId, "DEFER", "e2e", true);
    const redOkBody = (await redOkRes.json()) as { ok?: boolean; gate?: GateItem };
    push(
      "red_defer_governor",
      Boolean(redOkBody.ok) && redOkBody.gate?.governor_notify?.terminal === "ACCEPTED",
      { terminal: redOkBody.gate?.governor_notify?.terminal },
    );

    // 4) ASK keeps open
    const askId = `gate_e2e_ask_${crypto.randomUUID().slice(0, 8)}`;
    await this.fetch(
      new Request("https://gates.internal/v1/gates", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          gate_id: askId,
          title: "E2E ask",
          summary: receipt_id,
          lane: "AMBER",
          correlation_id: receipt_id,
          e2e: true,
        }),
      }),
    );
    const askRes = await this.resolve(askId, "ASK", "e2e", false);
    const askBody = (await askRes.json()) as {
      ok?: boolean;
      kept_open?: boolean;
      gate?: GateItem;
    };
    push(
      "ask_keeps_open",
      Boolean(askBody.ok && askBody.kept_open && askBody.gate?.status === "OPEN"),
      { ask_count: askBody.gate?.ask_count },
    );
    await this.resolve(askId, "DEFER", "e2e", true);

    const ok = steps.every((s) => s.ok);
    const receipt = {
      schema: "sourcea_founder_gates_e2e_receipt_v1",
      receipt_id,
      ok,
      at: new Date().toISOString(),
      ms: Date.now() - started,
      ui: "v3",
      steps,
    };
    await this.ctx.storage.put("e2e_last", receipt);
    await this.emit(ok ? "E2E_PASS" : "E2E_FAIL", undefined, { receipt_id, ms: receipt.ms });
    return Response.json(receipt, { status: ok ? 200 : 422 });
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const id = env.GATES.idFromName("founder");
    const stub = env.GATES.get(id);
    return stub.fetch(request);
  },
};

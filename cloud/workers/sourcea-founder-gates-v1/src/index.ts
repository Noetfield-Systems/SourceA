/**
 * sourcea-founder-gates-v1 — daily founder interrupt surface (/gates)
 * Amber Telegram callbacks: signed packets (expiry, nonce, idempotency).
 * Red: view / defer only. Never writes Goal Contracts or DecisionRecords.
 *
 * UI v2: founder glance — pulse strip, open-first filters, inline status (no alert),
 * XSS-safe render, auto-refresh. API contracts preserved.
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
  governor_notify?: {
    at: string;
    http_status: number;
    terminal?: string;
    run_id?: string;
  };
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

function cors(res: Response): Response {
  const h = new Headers(res.headers);
  h.set("access-control-allow-origin", "*");
  h.set("access-control-allow-methods", "GET,POST,OPTIONS");
  h.set("access-control-allow-headers", "content-type,x-gates-signature");
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
    --bg0:#0b1016;
    --bg1:#121a24;
    --fg:#e8eef4;
    --muted:#8a98a8;
    --line:#2a3848;
    --amber:#e0a21a;
    --amber-dim:rgba(224,162,26,.14);
    --red:#d45a5a;
    --red-dim:rgba(212,90,90,.14);
    --ok:#3fae74;
    --ok-dim:rgba(63,174,116,.14);
    --panel:rgba(18,26,36,.88);
    --glow:rgba(224,162,26,.08);
  }
  * { box-sizing:border-box; }
  body {
    margin:0;
    font-family:"IBM Plex Sans", ui-sans-serif, sans-serif;
    color:var(--fg);
    min-height:100vh;
    background:
      radial-gradient(900px 420px at 12% -10%, var(--glow), transparent 55%),
      radial-gradient(700px 360px at 100% 0%, rgba(61,120,160,.12), transparent 50%),
      linear-gradient(165deg, var(--bg0), var(--bg1) 55%, #0e1620);
  }
  main { max-width:760px; margin:0 auto; padding:1.75rem 1.2rem 3.5rem; }
  .brand {
    font-family:Syne, sans-serif;
    font-weight:800;
    font-size:clamp(1.85rem, 4.5vw, 2.35rem);
    letter-spacing:-0.03em;
    line-height:1.05;
    margin:0 0 .4rem;
  }
  .brand span { color:var(--amber); }
  .lead { color:var(--muted); margin:0 0 1.25rem; font-size:.98rem; max-width:38rem; }
  .pulse-row {
    display:grid;
    grid-template-columns:repeat(4, minmax(0,1fr));
    gap:.55rem;
    margin-bottom:1rem;
  }
  @media (max-width:560px) { .pulse-row { grid-template-columns:repeat(2, minmax(0,1fr)); } }
  .stat {
    background:var(--panel);
    border:1px solid var(--line);
    padding:.7rem .8rem;
    border-radius:2px;
  }
  .stat .k { font-size:.68rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
  .stat .v { font-family:Syne, sans-serif; font-weight:700; font-size:1.35rem; margin-top:.15rem; }
  .stat.amber .v { color:var(--amber); }
  .stat.red .v { color:var(--red); }
  .toolbar {
    display:flex; flex-wrap:wrap; align-items:center; gap:.5rem;
    margin-bottom:1rem;
  }
  .filters { display:flex; gap:.35rem; flex-wrap:wrap; flex:1; }
  .chip, button {
    font:inherit; cursor:pointer;
    background:#172231; color:var(--fg);
    border:1px solid var(--line);
    padding:.42rem .75rem;
    border-radius:2px;
  }
  .chip.active { border-color:var(--amber); background:var(--amber-dim); color:#f3d58a; }
  button:hover, .chip:hover { border-color:#4d647c; }
  button:disabled { opacity:.45; cursor:not-allowed; }
  button.primary { border-color:var(--ok); background:var(--ok-dim); }
  button.danger { border-color:var(--red); background:var(--red-dim); }
  button.ghost { background:transparent; }
  #status {
    min-height:1.25rem;
    font-size:.85rem;
    color:var(--muted);
    margin-bottom:.75rem;
  }
  #status.ok { color:var(--ok); }
  #status.err { color:var(--red); }
  .gate {
    background:var(--panel);
    border:1px solid var(--line);
    border-left:3px solid var(--line);
    padding:1rem 1rem .95rem;
    margin:0 0 .65rem;
  }
  .gate.AMBER { border-left-color:var(--amber); }
  .gate.RED { border-left-color:var(--red); }
  .gate.RESOLVED { opacity:.72; }
  .row { display:flex; flex-wrap:wrap; gap:.4rem .65rem; align-items:center; margin-bottom:.45rem; }
  .lane {
    font-size:.68rem; letter-spacing:.07em; font-weight:600;
    padding:.18rem .45rem; border:1px solid var(--line);
  }
  .lane.AMBER { color:var(--amber); border-color:var(--amber); background:var(--amber-dim); }
  .lane.RED { color:var(--red); border-color:var(--red); background:var(--red-dim); }
  .badge {
    font-size:.68rem; letter-spacing:.04em; color:var(--muted);
    border:1px solid var(--line); padding:.15rem .4rem;
  }
  .badge.OPEN { color:#9fd6b8; border-color:#3d6a55; }
  .title { font-family:Syne, sans-serif; font-weight:700; font-size:1.08rem; margin:.15rem 0 .35rem; }
  .summary { color:var(--muted); font-size:.92rem; margin:0 0 .65rem; line-height:1.45; }
  .meta { font-size:.75rem; color:var(--muted); display:flex; flex-wrap:wrap; gap:.35rem .75rem; }
  .meta code { font-family:ui-monospace, SFMono-Regular, Menlo, monospace; font-size:.72rem; }
  .actions { display:flex; flex-wrap:wrap; gap:.45rem; margin-top:.8rem; }
  .empty {
    border:1px dashed var(--line);
    padding:1.5rem 1rem;
    color:var(--muted);
    text-align:center;
  }
  .empty strong { display:block; color:var(--fg); font-family:Syne, sans-serif; margin-bottom:.35rem; }
  footer.law {
    margin-top:1.75rem;
    padding-top:1rem;
    border-top:1px solid var(--line);
    font-size:.75rem;
    color:var(--muted);
    line-height:1.5;
  }
</style>
</head>
<body>
<main>
  <h1 class="brand">SourceA <span>Gates</span></h1>
  <p class="lead">Daily founder interrupt surface. Approve amber decisions here — Canvas stays forensic, not daily ops.</p>
  <div class="pulse-row" id="pulse">
    <div class="stat"><div class="k">Open</div><div class="v" id="p-open">—</div></div>
    <div class="stat amber"><div class="k">Amber</div><div class="v" id="p-amber">—</div></div>
    <div class="stat red"><div class="k">Red</div><div class="v" id="p-red">—</div></div>
    <div class="stat"><div class="k">Updated</div><div class="v" id="p-at" style="font-size:.85rem;font-family:IBM Plex Sans,sans-serif;font-weight:500">—</div></div>
  </div>
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
    Amber: APPROVE · REJECT · DEFER · ASK &nbsp;·&nbsp; Red: DEFER only<br/>
    Mac observes · Railway / cloud owns execution · Gates never write Goal Contracts or DecisionRecords
  </footer>
</main>
<script>
(function () {
  let filter = 'OPEN';
  let busy = false;
  let timer = null;
  const statusEl = document.getElementById('status');
  const listEl = document.getElementById('list');

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

  function render(gates, pulse) {
    document.getElementById('p-open').textContent = String(pulse.open_count ?? 0);
    document.getElementById('p-amber').textContent = String(pulse.amber_open ?? 0);
    document.getElementById('p-red').textContent = String(pulse.red_open ?? 0);
    document.getElementById('p-at').textContent = rel(pulse.at) || 'now';

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
      el.innerHTML =
        '<div class="row">' +
          '<span class="lane ' + esc(g.lane) + '">' + esc(g.lane) + '</span>' +
          '<span class="badge ' + esc(g.status) + '">' + esc(g.status) +
            (g.resolution ? ' · ' + esc(g.resolution) : '') + '</span>' +
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
        b.onclick = function () { resolve(g.gate_id, a, b); };
        box.appendChild(b);
      }
      if (!acts.length && g.status === 'RESOLVED') {
        const note = document.createElement('span');
        note.className = 'badge';
        note.textContent = 'Closed' + (g.resolved_at ? ' · ' + rel(g.resolved_at) : '');
        box.appendChild(note);
      }
      listEl.appendChild(el);
    }
  }

  async function load(quiet) {
    if (!quiet) setStatus('Loading…');
    try {
      const [gates, pulse] = await Promise.all([
        fetch('/v1/gates').then(function (r) { return r.json(); }),
        fetch('/v1/pulse').then(function (r) { return r.json(); }),
      ]);
      render(gates, pulse);
      if (!quiet) setStatus('Synced · ' + (pulse.at || ''), '');
    } catch (e) {
      setStatus('Load failed — retrying', 'err');
    }
  }

  async function resolve(gateId, action, btn) {
    if (busy) return;
    busy = true;
    const buttons = listEl.querySelectorAll('button');
    buttons.forEach(function (b) { b.disabled = true; });
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
        buttons.forEach(function (b) { b.disabled = false; });
      }
    } catch (e) {
      setStatus('Network error', 'err');
      buttons.forEach(function (b) { b.disabled = false; });
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
  timer = setInterval(function () { if (!busy) load(true); }, 20000);
})();
</script>
</body>
</html>`;

export class FounderGatesDO extends DurableObject<Env> {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method === "OPTIONS") return cors(new Response(null, { status: 204 }));

    if (request.method === "GET" && path === "/health") {
      return cors(
        Response.json({
          ok: true,
          worker: "sourcea-founder-gates-v1",
          ui: "v2",
          governor_wired: Boolean(this.env.SOURCEA_GOVERNOR_URL),
          telegram_amber: Boolean(this.env.TELEGRAM_BOT_TOKEN && this.env.TELEGRAM_CHAT_ID_AMBER),
          decision_id: "NF-SOURCEA-N8N-ORCHESTRATOR-V1",
        }),
      );
    }

    if (request.method === "GET" && (path === "/" || path === "/gates")) {
      return cors(
        new Response(GATES_HTML, {
          headers: {
            "content-type": "text/html; charset=utf-8",
            "cache-control": "no-store",
          },
        }),
      );
    }

    if (request.method === "GET" && path === "/v1/pulse") {
      const items = (await this.ctx.storage.get<GateItem[]>("gates")) || [];
      const open = items.filter((g) => g.status === "OPEN");
      return cors(
        Response.json({
          schema: "sourcea_gates_pulse_v1",
          at: new Date().toISOString(),
          open_count: open.length,
          amber_open: open.filter((g) => g.lane === "AMBER").length,
          red_open: open.filter((g) => g.lane === "RED").length,
          resolved_count: items.filter((g) => g.status === "RESOLVED").length,
        }),
      );
    }

    if (request.method === "GET" && path === "/v1/gates") {
      const items = (await this.ctx.storage.get<GateItem[]>("gates")) || [];
      const status = url.searchParams.get("status");
      const filtered =
        status === "OPEN" || status === "RESOLVED"
          ? items.filter((g) => g.status === status)
          : items;
      return cors(
        Response.json({
          schema: "sourcea_gates_list_v1",
          items: filtered,
          ui: "v2",
        }),
      );
    }

    if (request.method === "POST" && path === "/v1/gates") {
      const body = (await request.json()) as Partial<GateItem>;
      const items = (await this.ctx.storage.get<GateItem[]>("gates")) || [];
      const gate: GateItem = {
        gate_id: String(body.gate_id || `gate_${crypto.randomUUID()}`),
        title: String(body.title || "Untitled gate"),
        summary: String(body.summary || ""),
        lane: body.lane === "RED" ? "RED" : "AMBER",
        correlation_id: String(body.correlation_id || crypto.randomUUID()),
        created_at: new Date().toISOString(),
        status: "OPEN",
      };
      items.unshift(gate);
      await this.ctx.storage.put("gates", items.slice(0, 200));
      if (gate.lane === "AMBER" && this.env.GATES_SIGNING_SECRET) {
        await this.notifyAmber(gate);
      }
      return cors(Response.json({ ok: true, gate }, { status: 201 }));
    }

    if (request.method === "POST" && path.startsWith("/v1/gates/") && path.endsWith("/resolve")) {
      const gateId = path.split("/")[3];
      const body = (await request.json()) as { action?: GateAction };
      return cors(await this.resolve(gateId, body.action || "DEFER", "ui"));
    }

    if (request.method === "POST" && path === "/v1/telegram/callback") {
      const secret = this.env.GATES_SIGNING_SECRET || "";
      if (secret.length < 32) {
        return cors(Response.json({ ok: false, error: "signing_secret_missing" }, { status: 503 }));
      }
      const body = (await request.json()) as { token?: string; callback_data?: string };
      let token = String(body.token || "");
      const cb = String(body.callback_data || "");
      if (!token && cb.startsWith("g:")) {
        const stored = await this.ctx.storage.get<string>(`tgcb:${cb.slice(2)}`);
        if (!stored) {
          return cors(Response.json({ ok: false, error: "unknown_callback" }, { status: 404 }));
        }
        token = stored;
      }
      const verified = await verifyPacket(secret, token);
      if (!verified.ok) {
        return cors(Response.json({ ok: false, error: verified.reason }, { status: 401 }));
      }
      const { packet } = verified;
      if (packet.lane === "RED" && packet.action !== "DEFER") {
        return cors(Response.json({ ok: false, error: "red_lane_view_defer_only" }, { status: 403 }));
      }
      const seen = await this.ctx.storage.get<string>(`idem:${packet.idempotency_key}`);
      if (seen) {
        return cors(Response.json({ ok: true, idempotent: true, gate_id: seen }));
      }
      const res = await this.resolve(packet.gate_id, packet.action, "telegram");
      const data = (await res.json()) as { ok?: boolean };
      if (data.ok) {
        await this.ctx.storage.put(`idem:${packet.idempotency_key}`, packet.gate_id);
      }
      return cors(Response.json({ ...(data as object), nonce: packet.nonce }));
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

    return cors(Response.json({ error: "not_found" }, { status: 404 }));
  }

  private async resolve(
    gateId: string,
    action: GateAction,
    source: string,
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
    gate.status = "RESOLVED";
    gate.resolution = action;
    gate.resolved_at = new Date().toISOString();
    items[idx] = gate;
    await this.ctx.storage.put("gates", items);
    this.ctx.waitUntil(this.notifyGovernor(gate, action, source));
    return Response.json({ ok: true, gate, source });
  }

  /**
   * Fire-and-forget ingress to Executive Governor.
   * Non-repair events currently land as DEFERRED_BY_POLICY (no DecisionRecord write).
   * Resolve never fails if Governor is down.
   */
  private async notifyGovernor(
    gate: GateItem,
    action: GateAction,
    source: string,
  ): Promise<void> {
    const base = (this.env.SOURCEA_GOVERNOR_URL || "").replace(/\/$/, "");
    if (!base) return;
    const idempotency_key = `founder_gate_resolved:${gate.gate_id}:${action}:${gate.resolved_at}`;
    const event_id = `gate_resolve_${gate.gate_id}`;
    try {
      const res = await fetch(`${base}/v1/executive/runs?org=sourcea`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          event_id,
          idempotency_key,
          event_type: "founder.gate.resolved",
          // omit canonical_state_version → Governor uses live DO version (avoids STALE_EVENT_VERSION)
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
    } catch {
      /* Mac/UI observe path — never block resolve */
    }
  }

  private async notifyAmber(gate: GateItem): Promise<void> {
    const secret = this.env.GATES_SIGNING_SECRET!;
    const token = this.env.TELEGRAM_BOT_TOKEN;
    const chat = this.env.TELEGRAM_CHAT_ID_AMBER;
    if (!token || !chat) return;
    const actions: GateAction[] = ["APPROVE", "REJECT", "DEFER", "ASK"];
    const buttons = [];
    for (const action of actions) {
      const packet: CallbackPacket = {
        v: 1,
        gate_id: gate.gate_id,
        action,
        lane: "AMBER",
        exp: Math.floor(Date.now() / 1000) + 900,
        nonce: crypto.randomUUID(),
        idempotency_key: `tg_${gate.gate_id}_${action}`,
      };
      const signed = await signPacket(secret, packet);
      const shortId = crypto.randomUUID().replace(/-/g, "").slice(0, 24);
      await this.ctx.storage.put(`tgcb:${shortId}`, signed);
      buttons.push([{ text: action, callback_data: `g:${shortId}` }]);
    }
    await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        chat_id: chat,
        text: `AMBER gate\n${gate.title}\n${gate.summary}\n${gate.gate_id}`,
        reply_markup: { inline_keyboard: buttons },
      }),
    }).catch(() => undefined);
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const id = env.GATES.idFromName("founder");
    const stub = env.GATES.get(id);
    return stub.fetch(request);
  },
};

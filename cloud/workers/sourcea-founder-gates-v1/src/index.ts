/**
 * sourcea-founder-gates-v1 — daily founder interrupt surface (/gates)
 * Amber Telegram callbacks: signed packets (expiry, nonce, idempotency).
 * Red: view / defer only. Never writes Goal Contracts or DecisionRecords.
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
<title>SourceA Gates</title>
<style>
  :root { --bg:#0f1419; --fg:#e7ecf1; --muted:#8b98a5; --line:#243040; --amber:#d4a017; --ok:#3d9a6a; }
  body { margin:0; font-family: ui-sans-serif, system-ui, sans-serif; background:linear-gradient(160deg,#0f1419,#1a2430); color:var(--fg); min-height:100vh; }
  main { max-width:720px; margin:0 auto; padding:2rem 1.25rem 4rem; }
  h1 { font-size:1.75rem; letter-spacing:-0.02em; margin:0 0 .35rem; }
  p.lead { color:var(--muted); margin:0 0 1.5rem; }
  .gate { border-top:1px solid var(--line); padding:1rem 0; }
  .meta { font-size:.8rem; color:var(--muted); }
  .lane { display:inline-block; font-size:.7rem; letter-spacing:.06em; padding:.15rem .45rem; border:1px solid var(--line); }
  .lane.AMBER { color:var(--amber); border-color:var(--amber); }
  .lane.RED { color:#c45; border-color:#c45; }
  .actions { display:flex; flex-wrap:wrap; gap:.5rem; margin-top:.75rem; }
  button { background:#1c2836; color:var(--fg); border:1px solid var(--line); padding:.45rem .8rem; cursor:pointer; }
  button:hover { border-color:#4a6078; }
  button.primary { border-color:var(--ok); }
  #pulse { font-size:.85rem; color:var(--muted); margin-bottom:1rem; }
</style>
</head>
<body>
<main>
  <h1>Gates</h1>
  <p class="lead">Daily founder interrupt surface. Canvas is forensic — not daily ops.</p>
  <div id="pulse">Loading pulse…</div>
  <div id="list"></div>
</main>
<script>
async function load() {
  const [gates, pulse] = await Promise.all([
    fetch('/v1/gates').then(r => r.json()),
    fetch('/v1/pulse').then(r => r.json()),
  ]);
  document.getElementById('pulse').textContent =
    'Pulse · open=' + (pulse.open_count ?? 0) + ' · ' + (pulse.at || '');
  const root = document.getElementById('list');
  root.innerHTML = '';
  for (const g of (gates.items || [])) {
    const el = document.createElement('div');
    el.className = 'gate';
    const canAct = g.lane === 'AMBER' && g.status === 'OPEN';
    el.innerHTML = '<div class="meta"><span class="lane ' + g.lane + '">' + g.lane + '</span> · ' +
      g.gate_id + ' · ' + g.status + '</div><strong>' + g.title + '</strong><p class="meta">' +
      g.summary + '</p><div class="actions"></div>';
    const actions = el.querySelector('.actions');
    const acts = canAct ? ['APPROVE','REJECT','DEFER','ASK'] : (g.lane === 'RED' && g.status === 'OPEN' ? ['DEFER'] : []);
    for (const a of acts) {
      const b = document.createElement('button');
      b.textContent = a;
      if (a === 'APPROVE') b.className = 'primary';
      b.onclick = async () => {
        const res = await fetch('/v1/gates/' + encodeURIComponent(g.gate_id) + '/resolve', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ action: a }),
        });
        const j = await res.json();
        alert(j.ok ? ('Resolved: ' + a) : ('Failed: ' + (j.error || res.status)));
        load();
      };
      actions.appendChild(b);
    }
    root.appendChild(el);
  }
  if (!(gates.items || []).length) {
    root.innerHTML = '<p class="meta">No open gates.</p>';
  }
}
load();
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
          decision_id: "NF-SOURCEA-N8N-ORCHESTRATOR-V1",
        }),
      );
    }

    if (request.method === "GET" && (path === "/" || path === "/gates")) {
      return cors(
        new Response(GATES_HTML, {
          headers: { "content-type": "text/html; charset=utf-8" },
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
        }),
      );
    }

    if (request.method === "GET" && path === "/v1/gates") {
      const items = (await this.ctx.storage.get<GateItem[]>("gates")) || [];
      return cors(Response.json({ schema: "sourcea_gates_list_v1", items }));
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
    return Response.json({ ok: true, gate, source });
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
      // Telegram callback_data max 64 bytes — store signed token server-side
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

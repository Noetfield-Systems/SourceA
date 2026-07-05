/**
 * SourceA Loop Specialist — Cloudflare cron
 * */15 loop + SF tick + nerve + triage
 * hourly gmail sweep · 07:00 UTC heartbeat · 03:00 UTC kaizen nightly
 */
import { handleIntakePost, probeSsot } from "./nerve-probe/probes.js";
import { runNerveProbeCycle } from "./nerve-probe/cycle.js";

export default {
  async scheduled(event, env, ctx) {
    const cron = event?.cron || "*/15 * * * *";
    const jobs = [
      () => runTick(env, { dispatch: env.LOOP_AUTO_DISPATCH === "true" }),
      () => runSignalFactoryTick(env),
      () => runNerveProbeCycle(env),
      () => postFbe(env, "/api/fbe/signal-factory/triage/v1", { max_batch: 10 }),
    ];
    if (cron === "0 * * * *") {
      jobs.push(() => postFbe(env, "/api/fbe/gmail-sweep/v1", { max_per_mailbox: 25 }));
    }
    if (cron === "0 7 * * *") {
      jobs.push(() => postFbe(env, "/api/fbe/ops/heartbeat/v1", {}));
    }
    if (cron === "0 3 * * *") {
      jobs.push(() => postFbe(env, "/api/fbe/kaizen/nightly/v1", {}));
    }
    ctx.waitUntil(Promise.all(jobs.map((fn) => fn())));
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }
    if (url.pathname === "/health") {
      return Response.json({
        ok: true,
        service: "loop-specialist-cron-v1",
        crons: ["*/15 * * * *", "0 * * * *", "0 7 * * *", "0 3 * * *"],
        nerve_probe: true,
        ops_motors: ["gmail-sweep", "signal-triage", "kaizen-nightly", "ops-heartbeat"],
        supabase_ready: Boolean(env.SUPABASE_URL && env.SUPABASE_SERVICE_ROLE_KEY),
        telegram_ready: Boolean(
          env.TELEGRAM_BOT_TOKEN && (env.TELEGRAM_ALERT_CHAT_ID || env.TELEGRAM_ALLOWED_CHAT_ID),
        ),
      });
    }
    if (url.pathname === "/api/noetfield/intake/v1" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const row = await handleIntakePost(env, body, { origin: "sourcea_loop_specialist" });
      return Response.json(row, { status: row.status || (row.ok ? 200 : 422) });
    }
    if (url.pathname === "/nerve/run" && request.method === "POST") {
      const row = await runNerveProbeCycle(env);
      return Response.json(row, { status: row.ok ? 200 : 422 });
    }
    if (url.pathname === "/nerve/ssot" && request.method === "GET") {
      return Response.json({ ok: true, ssot: probeSsot() });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const row = await runTick(env, { dispatch: Boolean(body.dispatch) });
      return Response.json(row, { status: row.ok ? 200 : 422 });
    }
    return Response.json({ ok: false, error: "not_found" }, { status: 404 });
  },
};

async function postFbe(env, path, body) {
  const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
  if (!base) {
    return { ok: false, error: "missing_FBE_CLOUD_WORKER_URL", path };
  }
  const headers = { "Content-Type": "application/json" };
  if (env.FBE_INTERNAL_SECRET) {
    headers.Authorization = `Bearer ${env.FBE_INTERNAL_SECRET}`;
  }
  const resp = await fetch(`${base}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      ...body,
      trigger_source: "cloudflare_cron_loop_specialist",
      execution_mode: "CLOUD_ONLY",
    }),
  });
  let row = {};
  try {
    row = await resp.json();
  } catch {
    row = { ok: false, error: "invalid_json", status: resp.status };
  }
  return { ok: Boolean(row.ok), path, proxied_status: resp.status, row };
}

async function runTick(env, { dispatch }) {
  const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
  if (!base) {
    return { ok: false, error: "missing_FBE_CLOUD_WORKER_URL" };
  }
  const autoOn = env.LOOP_AUTO_DISPATCH !== "false";
  const doDispatch = dispatch !== undefined ? dispatch : autoOn;
  const target = `${base}/api/fbe/loop-specialist/tick/v1`;
  const payload = {
    job_id: crypto.randomUUID(),
    factory_id: "comprehension-loop-factory-v1",
    bay_slug: "noetfield-freemium-bay",
    tenant: "sourcea",
    execution_mode: "CLOUD_ONLY",
    founder_message: "Auto Runtime · Cloudflare cron · read chat not disk · Hub glance only",
    draft: "Cloud loop tick — Mac control plane glance only · no RUN INBOX",
    dispatch: doDispatch,
    loop_auto_dispatch_enabled: autoOn,
  };
  const headers = { "Content-Type": "application/json" };
  if (env.FBE_INTERNAL_SECRET) {
    headers.Authorization = `Bearer ${env.FBE_INTERNAL_SECRET}`;
  }
  const resp = await fetch(target, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  let row = {};
  try {
    row = await resp.json();
  } catch {
    row = { ok: false, error: "invalid_json", status: resp.status };
  }
  return {
    ok: Boolean(row.ok),
    at: new Date().toISOString(),
    execution_plane: "cloudflare_cron",
    tick_decision: row.tick_decision,
    loop_specialist_line: row.loop_specialist_line,
    proxied_status: resp.status,
    cloud_target: target,
  };
}

async function runSignalFactoryTick(env) {
  const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
  if (!base) {
    return { ok: false, error: "missing_FBE_CLOUD_WORKER_URL" };
  }
  const target = `${base}/api/fbe/signal-factory/tick/v1`;
  const headers = { "Content-Type": "application/json" };
  if (env.FBE_INTERNAL_SECRET) {
    headers.Authorization = `Bearer ${env.FBE_INTERNAL_SECRET}`;
  }
  const resp = await fetch(target, {
    method: "POST",
    headers,
    body: JSON.stringify({
      job_id: crypto.randomUUID(),
      factory_id: "signal-factory-v1",
      tenant: "sourcea",
      execution_mode: "CLOUD_ONLY",
      max_batch: 5,
      trigger_source: "cloudflare_cron_loop_specialist",
    }),
  });
  let row = {};
  try {
    row = await resp.json();
  } catch {
    row = { ok: false, error: "invalid_json", status: resp.status };
  }
  return {
    ok: Boolean(row.ok),
    at: new Date().toISOString(),
    execution_plane: "cloudflare_cron_loop_specialist",
    decision: row.decision,
    signal_factory_line: row.signal_factory_line,
    proxied_status: resp.status,
    cloud_target: target,
  };
}

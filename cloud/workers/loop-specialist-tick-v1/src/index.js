/**
 * SourceA Loop Specialist — Cloudflare cron (phase 2b · FREE tier)
 * POST Railway FBE loop tick + signal factory + nerve probes (15-minute cron)
 */
import { handleIntakePost, probeSsot } from "./nerve-probe/probes.js";
import { runNerveProbeCycle } from "./nerve-probe/cycle.js";

export default {
  async scheduled(_event, env, ctx) {
    ctx.waitUntil(
      Promise.all([
        runTick(env, { dispatch: env.LOOP_AUTO_DISPATCH === "true" }),
        runSignalFactoryTick(env),
        runNerveProbeCycle(env),
      ]),
    );
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
        cron: "*/15 * * * *",
        nerve_probe: true,
        probes: ["nf_intake_e2e", "greeting", "drift", "uptime"],
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

/**
 * SourceA Loop Specialist — CF cron dispatch → Railway FBE
 */
import { handleIntakePost, probeSsot } from "./nerve-probe/probes.js";
import { runNerveProbeCycle } from "./nerve-probe/cycle.js";
import { runGatewayWatchdog, runGatewayHeartbeat } from "./gateway-probe/cycle.js";
import { dispatchMeta, jobsForCron, runDispatchJobs, runDueDispatch, smokeAllJobs } from "./dispatch.js";

const HANDLERS = {
  loop_specialist_tick: (env) => runTick(env, { dispatch: env.LOOP_AUTO_DISPATCH === "true" }),
  signal_factory_tick: (env) => runSignalFactoryTick(env),
  nerve_probe: (env) => runNerveProbeCycle(env),
  gateway_watchdog: (env) => runGatewayWatchdog(env),
  gateway_heartbeat: (env) => runGatewayHeartbeat(env),
  n8n_pulse: (env) => runN8nPulse(env),
};

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(
      runDueDispatch(env, HANDLERS, { trigger: "cloudflare_cron_loop_specialist" }),
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
      const meta = dispatchMeta();
      return Response.json({
        ok: true,
        service: "loop-specialist-cron-v1",
        crons: meta.crons,
        dispatch: meta,
        nerve_probe: true,
        ops_motors: ["gmail-sweep", "signal-triage", "kaizen-nightly", "ops-heartbeat", "sg-gateway-watchdog", "sg-gateway-heartbeat", "n8n-pulse"],
        scheduled_loops: [
          "repo-health-daily",
          "security-sweep-weekly",
          "determinism-gate-6h",
        ],
        supabase_ready: Boolean(env.SUPABASE_URL && env.SUPABASE_SERVICE_ROLE_KEY),
        telegram_ready: Boolean(
          env.TELEGRAM_BOT_TOKEN && (env.TELEGRAM_ALERT_CHAT_ID || env.TELEGRAM_ALLOWED_CHAT_ID),
        ),
      });
    }
    if (url.pathname === "/dispatch/smoke" && request.method === "POST") {
      const row = await smokeAllJobs(env, HANDLERS);
      return Response.json(row, { status: row.ok ? 200 : 422 });
    }
    if (url.pathname === "/dispatch/run" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const cron = String(body.cron || "*/15 * * * *");
      const row = await runDispatchJobs(env, cron, HANDLERS, {
        trigger: body.trigger || "manual_dispatch_run",
      });
      return Response.json(row, { status: row.ok ? 200 : 422 });
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

/** NF-SOURCEA-N8N-ORCHESTRATOR-V1 — cloud pulse for Railway n8n + founder gates */
async function runN8nPulse(env) {
  const n8nUrl = String(
    env.SOURCEA_N8N_HEALTH_URL || "https://n8n-main-production-bfdc.up.railway.app/healthz",
  );
  const gatesUrl = String(
    env.SOURCEA_GATES_URL || "https://sourcea-founder-gates-v1.sina-kazemnezhad-ca.workers.dev",
  ).replace(/\/$/, "");
  const started = Date.now();
  let n8nOk = false;
  let gatesOk = false;
  let n8nDetail = "";
  let gatesDetail = "";
  try {
    const res = await fetch(n8nUrl, { method: "GET" });
    n8nOk = res.status === 200;
    n8nDetail = `http_${res.status}`;
  } catch (exc) {
    n8nDetail = String(exc).slice(0, 120);
  }
  try {
    const res = await fetch(`${gatesUrl}/health`, { method: "GET" });
    gatesOk = res.status === 200;
    gatesDetail = `http_${res.status}`;
  } catch (exc) {
    gatesDetail = String(exc).slice(0, 120);
  }
  return {
    ok: n8nOk && gatesOk,
    schema: "sourcea_n8n_pulse_v1",
    loop_id: "sourcea_n8n_pulse_v1",
    deadman: "sourcea-deadman-v1",
    trigger_host: "cloud",
    at: new Date().toISOString(),
    ms: Date.now() - started,
    n8n: { ok: n8nOk, detail: n8nDetail, url: n8nUrl },
    gates: { ok: gatesOk, detail: gatesDetail, url: gatesUrl },
  };
}

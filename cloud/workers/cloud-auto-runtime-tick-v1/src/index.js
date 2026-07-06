/**
 * SourceA Cloud Auto Runtime — Cloudflare cron (scheduler only · motor stays Railway FBE)
 * POST Railway /api/cloud-forge-run/auto-tick/v1 — server-side PROVE → contract → SHIP
 */
import { writeCronFired } from "./truth_log.js";
import { upsertLoopLiveness } from "./loop_liveness.js";

const DEFAULT_VERIFIER_BASE_URL =
  "https://sina-governance-ssot-advisory.kazemnezhadsina144.workers.dev";
const DEFAULT_CANDIDATE_REPO = "noetfield-systems/sourcea";
const DEFAULT_CANDIDATE_REF = "main";
const DEFAULT_CANDIDATE_PATH = "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json";

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "no-store",
    },
  });
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(
      (async () => {
        const armed =
          env.CLOUD_FORGE_RUN_AUTO_PROCEED === "true" || env.CLOUD_DRAIN_AUTO_PROCEED === "true";
        const tick = await runTick(env, { proceed: armed });
        const brain = await runBrainVerifierTick(env);
        await writeCronFired(env, {
          deployment_id: event?.cron || "*/10 * * * *",
          queue_head: tick?.motor?.head || tick?.pack?.head_now || null,
          receipt_id: tick?.motor?.cycle_receipt_path || null,
          tick_decision: tick?.decision || null,
          brain_verifier_result: brain?.run_result || null,
          brain_receipt_id: brain?.receipt_id || null,
          cycle_verdict:
            tick?.decision === "IDLE_NO_WORK" || tick?.auto_stop
              ? "IDLE_NO_WORK"
              : tick?.motor?.pack?.idle_batch && !(tick?.motor?.pack?.shipped || tick?.motor?.pack?.advanced)
                ? "IDLE_NO_WORK"
                : tick?.motor?.decision || tick?.decision || null,
          motor_invoked: tick?.motor_invoked !== false,
        });
        await upsertLoopLiveness(env, {
          loop_id: "sourcea-cloud-auto-runtime-tick-v1",
          trigger_host: "cloudflare",
          schedule_cron: "*/10 * * * *",
          interval_minutes: 10,
          last_ok: Boolean(tick?.ok),
          last_receipt: {
            decision: tick?.decision || null,
            motor_invoked: tick?.motor_invoked !== false,
          },
        });
        return tick;
      })(),
    );
  },

  async fetch(request, env) {
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
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return json({
        ok: true,
        schema: "sourcea-auto-runtime-health-v1",
        service: "cloud-auto-runtime-tick-v1",
        cron: "*/10 * * * *",
        brain_verifier_cron: "bundled_each_tick",
        auto_proceed_ready:
          env.CLOUD_FORGE_RUN_AUTO_PROCEED === "true" || env.CLOUD_DRAIN_AUTO_PROCEED === "true",
        railway_upstream_ready: Boolean(env.FBE_CLOUD_WORKER_URL),
        internal_secret_ready: Boolean(env.FBE_INTERNAL_SECRET),
        verifier_base_url: env.VERIFIER_BASE_URL || DEFAULT_VERIFIER_BASE_URL,
      });
    }
    if (url.pathname === "/status" && request.method === "GET") {
      const [queue, observer] = await Promise.all([
        fetchRailwayJson(env, "/api/cloud-forge-run/queue/v1"),
        fetchRailwayJson(env, "/api/cloud-forge-run/observer/v1"),
      ]);
      return json({
        ok: queue.ok && observer.ok,
        schema: "sourcea-auto-runtime-status-v1",
        service: "cloud-auto-runtime-tick-v1",
        cron: "*/10 * * * *",
        auto_proceed_ready:
          env.CLOUD_FORGE_RUN_AUTO_PROCEED === "true" || env.CLOUD_DRAIN_AUTO_PROCEED === "true",
        railway_upstream_ready: Boolean(env.FBE_CLOUD_WORKER_URL),
        internal_secret_ready: Boolean(env.FBE_INTERNAL_SECRET),
        queue,
        observer,
        at: new Date().toISOString(),
      });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const row = await runTick(env, { proceed: Boolean(body.proceed) });
      return json(row, row.ok ? 200 : 422);
    }
    if (url.pathname === "/brain-tick" && request.method === "POST") {
      const row = await runBrainVerifierTick(env);
      return json(row, row.ok ? 200 : 422);
    }
  if (url.pathname === "/observer" && request.method === "GET") {
    const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
    if (!base) {
      return json({ ok: false, error: "missing_FBE_CLOUD_WORKER_URL" }, 503);
    }
    const resp = await fetch(`${base}/observer`, { headers: { Accept: "text/html" } });
    return new Response(await resp.text(), {
      status: resp.status,
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  }
  if (url.pathname === "/observer-json" && request.method === "GET") {
    const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
    if (!base) {
      return json({ ok: false, error: "missing_FBE_CLOUD_WORKER_URL" }, 503);
    }
    const resp = await fetch(`${base}/api/cloud-forge-run/observer/v1`, {
      headers: { Accept: "application/json" },
    });
    const text = await resp.text();
    return new Response(text, {
      status: resp.status,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }
  if (url.pathname === "/queue" && request.method === "GET") {
    const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
    if (!base) {
      return json({ ok: false, error: "missing_FBE_CLOUD_WORKER_URL" }, 503);
    }
    const headers = { Accept: "application/json" };
    if (env.FBE_INTERNAL_SECRET) {
      headers.Authorization = `Bearer ${env.FBE_INTERNAL_SECRET}`;
    }
    const resp = await fetch(`${base}/api/cloud-forge-run/queue/v1`, { headers });
    const text = await resp.text();
    return new Response(text, {
      status: resp.status,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }
    if (url.pathname === "/plan-registry" && request.method === "GET") {
      return proxyPlanRegistry(url, env);
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};

async function fetchRailwayJson(env, path) {
  const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
  if (!base) {
    return { ok: false, error: "missing_FBE_CLOUD_WORKER_URL" };
  }
  const headers = { Accept: "application/json" };
  if (env.FBE_INTERNAL_SECRET) {
    headers.Authorization = `Bearer ${env.FBE_INTERNAL_SECRET}`;
  }
  try {
    const resp = await fetch(`${base}${path}`, { headers });
    const text = await resp.text();
    let body = {};
    try {
      body = JSON.parse(text);
    } catch {
      body = { ok: false, error: "invalid_json", body_prefix: text.slice(0, 120) };
    }
    return {
      ok: resp.ok && body.ok !== false,
      status: resp.status,
      body,
    };
  } catch (err) {
    return { ok: false, error: "fetch_failed", message: String(err && err.message ? err.message : err).slice(0, 160) };
  }
}

async function proxyPlanRegistry(url, env) {
  const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
  if (!base) {
    return Response.json({ ok: false, error: "missing_FBE_CLOUD_WORKER_URL" }, { status: 503 });
  }
  const headers = { Accept: "application/json" };
  if (env.FBE_INTERNAL_SECRET) {
    headers.Authorization = `Bearer ${env.FBE_INTERNAL_SECRET}`;
  }
  const upstream = new URL(`${base}/api/sourcea/plan-registry/v1`);
  for (const [key, value] of url.searchParams.entries()) {
    upstream.searchParams.append(key, value);
  }
  try {
    const resp = await fetch(upstream, { headers });
    const text = await resp.text();
    return new Response(text, {
      status: resp.status,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-store",
      },
    });
  } catch (err) {
    return Response.json(
      {
        ok: false,
        error: "plan_registry_proxy_failed",
        message: String(err && err.message ? err.message : err).slice(0, 160),
      },
      { status: 502, headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" } },
    );
  }
}

async function runBrainVerifierTick(env) {
  const verifier = (env.VERIFIER_BASE_URL || DEFAULT_VERIFIER_BASE_URL).replace(/\/$/, "");
  const payload = {
    candidate_repo: env.CANDIDATE_REPO || DEFAULT_CANDIDATE_REPO,
    candidate_ref: env.CANDIDATE_REF || DEFAULT_CANDIDATE_REF,
    candidate_path: env.CANDIDATE_PATH || DEFAULT_CANDIDATE_PATH,
  };
  const runResp = await fetch(`${verifier}/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      "User-Agent": "cloud-auto-runtime-tick-v1/brain",
    },
    body: JSON.stringify(payload),
  });
  let receipt = {};
  try {
    receipt = await runResp.json();
  } catch {
    receipt = { ok: false, error: "invalid_json", status: runResp.status };
  }
  const pass = receipt.result === "PASS" || receipt.status === "PASS";
  return {
    ok: pass && runResp.ok,
    schema: "sourcea-brain-verifier-cloud-tick-v1",
    at: new Date().toISOString(),
    verifier_base_url: verifier,
    candidate_ref: payload.candidate_ref,
    run_status: receipt.status,
    run_result: receipt.result,
    receipt_id: receipt.receipt_id,
    candidate_sha256: receipt.candidate_sha256,
    proxied_status: runResp.status,
  };
}

function registryExhaustedFromObserver(body) {
  if (!body || typeof body !== "object") {
    return { exhausted: false, head: null, batch_id: null };
  }
  const hb = body.daily_heartbeat;
  const batch = (hb && hb.batch_state) || {};
  if (batch.registry_exhausted && batch.queue_batch_complete) {
    return {
      exhausted: true,
      head: body.queue_head || hb.queue_head || null,
      batch_id: batch.batch_id || null,
      source: "daily_heartbeat",
    };
  }
  const cycles = Array.isArray(body.cycles) ? body.cycles : [];
  const latest = cycles[0];
  const pack = latest && latest.pack;
  if (pack && pack.registry_exhausted && pack.idle_batch) {
    return {
      exhausted: true,
      head: body.queue_head || null,
      batch_id: pack.batch_id || null,
      source: "latest_cycle",
    };
  }
  return { exhausted: false, head: body.queue_head || null, batch_id: null };
}

function edgeIdleReceipt(env, precheck) {
  const at = new Date().toISOString();
  const head = precheck.head || null;
  return {
    ok: true,
    schema: "autorun-edge-idle-receipt-v1",
    at,
    execution_plane: "cloudflare_cron",
    trigger_source: "cloudflare_cron",
    decision: "IDLE_NO_WORK",
    auto_stop: true,
    auto_stop_reason: "registry_exhausted",
    motor_invoked: false,
    precheck_source: precheck.source,
    queue_head: head,
    batch_id: precheck.batch_id,
    pack: {
      ok: true,
      idle_batch: true,
      registry_exhausted: true,
      schema: "cloud-forge-run-pack-v1",
      advanced: 0,
      skipped: 0,
      processed: 0,
      shipped: 0,
      mandatory_quota: maxAdvanceCap(env),
      max_advance: maxAdvanceCap(env),
      batch_complete: true,
      batch_id: precheck.batch_id,
      head_now: head,
    },
    cost: {
      provider: "cloudflare",
      model: "workers-cron",
      tokens_in: 0,
      tokens_out: 0,
      unit_cost_usd: 0,
      total_usd: 0,
    },
    value_class: "hygiene",
    law: "Tier0 auto-stop — skip Railway POST when registry_exhausted",
    cf_version: env.CF_VERSION_METADATA || null,
    pending_auto_note: "see observer.pending or receipts/cloud/autorun-pending/pending-latest-v1.json",
  };
}

function maxAdvanceCap(env) {
  const n = parseInt(env.MAX_ADVANCE_PER_TICK || "10", 10);
  return Number.isFinite(n) && n > 0 ? n : 10;
}

async function runTick(env, { proceed }) {
  const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
  if (!base) {
    return { ok: false, error: "missing_FBE_CLOUD_WORKER_URL" };
  }
  const autoOn =
    env.CLOUD_FORGE_RUN_AUTO_PROCEED === "true" || env.CLOUD_DRAIN_AUTO_PROCEED === "true";
  const doProceed = proceed !== undefined ? proceed : autoOn;

  const headers = { "Content-Type": "application/json" };
  if (env.FBE_INTERNAL_SECRET) {
    headers.Authorization = `Bearer ${env.FBE_INTERNAL_SECRET}`;
  }

  if (!doProceed) {
    return {
      ok: true,
      at: new Date().toISOString(),
      execution_plane: "cloudflare_cron",
      decision: "observe_only",
      auto_proceed: false,
    };
  }

  const observer = await fetchRailwayJson(env, "/api/cloud-forge-run/observer/v1");
  if (observer.ok) {
    const precheck = registryExhaustedFromObserver(observer.body);
    if (precheck.exhausted) {
      return edgeIdleReceipt(env, precheck);
    }
  }

  const tickPaths = [
    `${base}/api/cloud-forge-run/auto-tick/v1`,
    `${base}/api/cloud-drain/auto-tick/v1`,
  ];
  let resp = null;
  let row = {};
  for (const tickUrl of tickPaths) {
    resp = await fetch(tickUrl, {
      method: "POST",
      headers,
      body: JSON.stringify({
        trigger_source: "cloudflare_cron",
        full_pack: true,
        max_advance: maxAdvanceCap(env),
        auto_tick: true,
      }),
    });
    if (resp.status !== 404) {
      break;
    }
  }
  if (!resp) {
    return { ok: false, error: "tick_fetch_failed" };
  }
  try {
    row = await resp.json();
  } catch {
    row = { ok: false, error: "invalid_json", status: resp.status };
  }

  return {
    ok: Boolean(row.ok),
    at: new Date().toISOString(),
    execution_plane: "cloudflare_cron",
    trigger_source: "cloudflare_cron",
    decision: row.decision || (row.ok ? "proceed_ok" : "proceed_fail"),
    auto_proceed: doProceed,
    motor_invoked: true,
    pack: row.pack || (row.motor && row.motor.pack) || null,
    processed: (row.pack && row.pack.processed) || (row.motor && row.motor.pack && row.motor.pack.processed) || null,
    motor: row,
    proxied_status: resp.status,
  };
}

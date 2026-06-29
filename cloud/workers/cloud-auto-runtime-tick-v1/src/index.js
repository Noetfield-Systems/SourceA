/**
 * SourceA Cloud Auto Runtime — Cloudflare cron (scheduler only · motor stays Railway FBE)
 * POST Railway /api/cloud-forge-run/auto-tick/v1 — server-side PROVE → contract → SHIP
 */
import { writeCronFired } from "./truth_log.js";

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
      writeCronFired(env, {
        deployment_id: event?.cron || "*/10 * * * *",
      }),
    );
    const armed =
      env.CLOUD_FORGE_RUN_AUTO_PROCEED === "true" || env.CLOUD_DRAIN_AUTO_PROCEED === "true";
    ctx.waitUntil(runTick(env, { proceed: armed }));
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
        auto_proceed_ready:
          env.CLOUD_FORGE_RUN_AUTO_PROCEED === "true" || env.CLOUD_DRAIN_AUTO_PROCEED === "true",
        railway_upstream_ready: Boolean(env.FBE_CLOUD_WORKER_URL),
        internal_secret_ready: Boolean(env.FBE_INTERNAL_SECRET),
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
      { ok: false, error: "plan_registry_proxy_failed", message: String(err && err.message ? err.message : err).slice(0, 160) },
      { status: 502, headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" } },
    );
  }
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
        max_advance: 100,
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
    pack: row.pack || (row.motor && row.motor.pack) || null,
    processed: (row.pack && row.pack.processed) || (row.motor && row.motor.pack && row.motor.pack.processed) || null,
    motor: row,
    proxied_status: resp.status,
  };
}

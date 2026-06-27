/**
 * SourceA Cloud Auto Runtime — Cloudflare cron (scheduler only · motor stays Railway FBE)
 * POST Railway /api/cloud-forge-run/auto-tick/v1 — server-side PROVE → contract → SHIP
 */
import { writeCronFired } from "./truth_log.js";

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
      return Response.json({ ok: true, service: "cloud-auto-runtime-tick-v1", cron: "*/10 * * * *" });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const row = await runTick(env, { proceed: Boolean(body.proceed) });
      return Response.json(row, {
        status: row.ok ? 200 : 422,
        headers: { "Access-Control-Allow-Origin": "*" },
      });
    }
  if (url.pathname === "/observer" && request.method === "GET") {
    const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
    if (!base) {
      return Response.json({ ok: false, error: "missing_FBE_CLOUD_WORKER_URL" }, { status: 503 });
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
      return Response.json({ ok: false, error: "missing_FBE_CLOUD_WORKER_URL" }, { status: 503 });
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
      return Response.json({ ok: false, error: "missing_FBE_CLOUD_WORKER_URL" }, { status: 503 });
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
    return Response.json({ ok: false, error: "not_found" }, { status: 404 });
  },
};

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

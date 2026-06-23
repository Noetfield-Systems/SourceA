/**
 * SourceA Cloud Drain Auto-Runtime — Cloudflare cron (scheduler only · motor stays Railway FBE)
 * POST Railway /api/cloud-drain/auto-tick/v1 — server-side PROVE → contract → SHIP
 */
import { writeCronFired } from "./truth_log.js";

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(
      writeCronFired(env, {
        deployment_id: event?.cron || "*/10 * * * *",
      }),
    );
    const armed = env.CLOUD_DRAIN_AUTO_PROCEED === "true";
    ctx.waitUntil(runTick(env, { proceed: armed }));
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return Response.json({ ok: true, service: "cloud-drain-tick-v1", cron: "*/10 * * * *" });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const row = await runTick(env, { proceed: Boolean(body.proceed) });
      return Response.json(row, { status: row.ok ? 200 : 422 });
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
    return Response.json({ ok: false, error: "not_found" }, { status: 404 });
  },
};

async function runTick(env, { proceed }) {
  const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
  if (!base) {
    return { ok: false, error: "missing_FBE_CLOUD_WORKER_URL" };
  }
  const autoOn = env.CLOUD_DRAIN_AUTO_PROCEED === "true";
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

  const resp = await fetch(`${base}/api/cloud-drain/proceed/v1`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      trigger_source: "cloudflare_cron",
      llm_provider: "openrouter",
      full_motor: true,
      auto_tick: true,
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
    execution_plane: "cloudflare_cron",
    trigger_source: "cloudflare_cron",
    decision: row.decision || (row.ok ? "proceed_ok" : "proceed_fail"),
    auto_proceed: doProceed,
    motor: row,
    proxied_status: resp.status,
  };
}

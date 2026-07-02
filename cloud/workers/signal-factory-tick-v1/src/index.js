/**
 * SourceA Signal Factory v1 — Cloudflare cron (synthetic disk queue · no Gmail)
 * POST Railway FBE signal-factory tick every 15m
 */
export default {
  async scheduled(_event, env, ctx) {
    ctx.waitUntil(runTick(env));
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return Response.json({ ok: true, service: "signal-factory-cron-v1" });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const row = await runTick(env, body);
      return Response.json(row, { status: row.ok ? 200 : 422 });
    }
    return Response.json({ ok: false, error: "not_found" }, { status: 404 });
  },
};

async function runTick(env, body = {}) {
  const base = (env.FBE_CLOUD_WORKER_URL || "").replace(/\/$/, "");
  if (!base) {
    return { ok: false, error: "missing_FBE_CLOUD_WORKER_URL" };
  }
  const target = `${base}/api/fbe/signal-factory/tick/v1`;
  const payload = {
    job_id: crypto.randomUUID(),
    factory_id: "signal-factory-v1",
    tenant: "sourcea",
    execution_mode: "CLOUD_ONLY",
    max_batch: Number(body.max_batch || 5),
    trigger_source: "cloudflare_cron",
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
    decision: row.decision,
    signal_factory_line: row.signal_factory_line,
    proxied_status: resp.status,
    cloud_target: target,
  };
}

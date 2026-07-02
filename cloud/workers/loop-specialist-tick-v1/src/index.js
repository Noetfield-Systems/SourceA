/**
 * SourceA Auto Runtime specialist — Cloudflare cron (phase 2b · FREE tier)
 * POST Railway FBE loop tick — zero Mac Terminal · zero Mac execution
 */
export default {
  async scheduled(_event, env, ctx) {
    ctx.waitUntil(
      Promise.all([
        runTick(env, { dispatch: env.LOOP_AUTO_DISPATCH === "true" }),
        runSignalFactoryTick(env),
      ]),
    );
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return Response.json({ ok: true, service: "loop-specialist-cron-v1" });
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

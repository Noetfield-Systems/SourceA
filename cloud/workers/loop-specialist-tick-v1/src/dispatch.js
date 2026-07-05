/**
 * CF cron dispatch table → Railway FBE + inline handlers.
 * SSOT: data/loop-specialist-cron-dispatch-v1.json (copied to dispatch-table.json before deploy).
 */
import DISPATCH from "./dispatch-table.json";

export function dispatchMeta() {
  return {
    schema: DISPATCH.schema,
    version: DISPATCH.version,
    crons: (DISPATCH.crons || []).map((row) => row.cron),
    job_count: (DISPATCH.crons || []).reduce((n, row) => n + (row.jobs || []).length, 0),
  };
}

export function jobsForCron(cron) {
  const row = (DISPATCH.crons || []).find((entry) => entry.cron === cron);
  return row ? { ...row, jobs: row.jobs || [] } : { cron, jobs: [] };
}

export function allCronRows() {
  return DISPATCH.crons || [];
}

export async function runDispatchJobs(env, cron, handlers, { trigger = "cloudflare_cron" } = {}) {
  const row = jobsForCron(cron);
  const results = [];
  for (const job of row.jobs) {
    const started = Date.now();
    try {
      let result;
      if (job.kind === "handler") {
        const fn = handlers[job.handler];
        if (!fn) {
          result = { ok: false, error: "unknown_handler", handler: job.handler };
        } else {
          result = await fn(env);
        }
      } else if (job.kind === "railway") {
        result = await postFbe(env, job.path, job.body || {}, { trigger });
      } else {
        result = { ok: false, error: "unknown_job_kind", kind: job.kind };
      }
      results.push({
        id: job.id,
        kind: job.kind,
        handler: job.handler || null,
        path: job.path || null,
        ok: Boolean(result?.ok),
        ms: Date.now() - started,
        result,
      });
    } catch (exc) {
      results.push({
        id: job.id,
        kind: job.kind,
        ok: false,
        ms: Date.now() - started,
        error: String(exc).slice(0, 200),
      });
    }
  }
  return {
    ok: results.every((r) => r.ok),
    schema: "loop-specialist-cron-dispatch-run-v1",
    at: new Date().toISOString(),
    cron,
    trigger_id: row.trigger_id || null,
    label: row.label || null,
    results,
  };
}

export async function smokeAllJobs(env, handlers) {
  const seen = new Set();
  const jobs = [];
  for (const row of allCronRows()) {
    for (const job of row.jobs || []) {
      const key = job.kind === "railway" ? `r:${job.path}` : `h:${job.handler}`;
      if (seen.has(key)) continue;
      seen.add(key);
      jobs.push({ ...job, cron: row.cron, trigger_id: row.trigger_id });
    }
  }
  const results = [];
  for (const job of jobs) {
    let result;
    if (job.kind === "handler") {
      const fn = handlers[job.handler];
      result = fn ? await fn(env) : { ok: false, error: "unknown_handler" };
    } else {
      result = await postFbe(env, job.path, { ...(job.body || {}), smoke: true }, {
        trigger: "dispatch_smoke",
      });
    }
    results.push({
      id: job.id,
      cron: job.cron,
      trigger_id: job.trigger_id,
      kind: job.kind,
      path: job.path || null,
      handler: job.handler || null,
      ok: Boolean(result?.ok),
      result,
    });
  }
  return {
    ok: results.every((r) => r.ok),
    schema: "loop-specialist-cron-dispatch-smoke-v1",
    at: new Date().toISOString(),
    unique_jobs: results.length,
    results,
  };
}

async function postFbe(env, path, body, { trigger }) {
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
      trigger_source: trigger || "cloudflare_cron_loop_specialist",
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

/**
 * Upsert loop_registry liveness (portfolio-spine Supabase).
 */
const TABLE = "loop_registry";

export async function upsertLoopLiveness(env, row) {
  const url = (env.SUPABASE_URL || "").replace(/\/$/, "");
  const key = env.SUPABASE_SERVICE_ROLE_KEY || "";
  if (!url || !key) {
    return { ok: false, skipped: true, reason: "supabase_not_configured" };
  }

  const payload = {
    loop_id: row.loop_id,
    trigger_host: row.trigger_host || "cloudflare",
    schedule_cron: row.schedule_cron || null,
    interval_minutes: row.interval_minutes,
    last_fired_at: row.last_fired_at || new Date().toISOString(),
    last_ok: Boolean(row.last_ok),
    last_error: row.last_error || null,
    last_receipt: row.last_receipt || {},
    updated_at: new Date().toISOString(),
  };

  const resp = await fetch(`${url}/rest/v1/${TABLE}?on_conflict=loop_id`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      apikey: key,
      Authorization: `Bearer ${key}`,
      Prefer: "resolution=merge-duplicates,return=representation",
    },
    body: JSON.stringify(payload),
  });

  let body = {};
  try {
    body = await resp.json();
  } catch {
    body = {};
  }
  const inserted = Array.isArray(body) ? body[0] : body;
  return {
    ok: resp.ok,
    loop_id: row.loop_id,
    loop_registry_id: inserted?.loop_id || row.loop_id,
    status: resp.status,
  };
}

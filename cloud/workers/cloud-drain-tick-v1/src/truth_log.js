/**
 * Truth Layer v2 — CRON_FIRED to Supabase (cloudflare_cron only).
 * Secrets: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
 */

const TRUTH_TABLE = "truth_log";

export async function writeCronFired(env, extra = {}) {
  const url = (env.SUPABASE_URL || "").replace(/\/$/, "");
  const key = env.SUPABASE_SERVICE_ROLE_KEY || "";
  if (!url || !key) {
    return { ok: false, error: "supabase_not_configured" };
  }

  const row = {
    source: "cloudflare_cron",
    event: "CRON_FIRED",
    deployment_id: extra.deployment_id || env.CF_VERSION_METADATA || null,
    queue_head: extra.queue_head || null,
    receipt_id: extra.receipt_id || null,
  };

  const resp = await fetch(`${url}/rest/v1/${TRUTH_TABLE}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      apikey: key,
      Authorization: `Bearer ${key}`,
      Prefer: "return=representation",
    },
    body: JSON.stringify(row),
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
    truth_log_id: inserted?.id || null,
    status: resp.status,
  };
}

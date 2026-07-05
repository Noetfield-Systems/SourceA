/**
 * Supabase REST — portfolio-spine (SourceA nerve probes).
 */

export async function supabaseInsert(env, table, row) {
  const base = supabaseBase(env);
  if (!base.ok) return base;
  const resp = await fetch(`${base.url}/rest/v1/${table}`, {
    method: "POST",
    headers: supabaseHeaders(env, { prefer: "return=representation" }),
    body: JSON.stringify(row),
  });
  let body = {};
  try {
    body = await resp.json();
  } catch {
    body = {};
  }
  const inserted = Array.isArray(body) ? body[0] : body;
  return { ok: resp.ok, status: resp.status, row: inserted, error: resp.ok ? null : JSON.stringify(body).slice(0, 240) };
}

export async function supabaseSelectOne(env, table, filters) {
  const base = supabaseBase(env);
  if (!base.ok) return base;
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters || {})) {
    params.set(k, `eq.${v}`);
  }
  params.set("limit", "1");
  const resp = await fetch(`${base.url}/rest/v1/${table}?${params}`, {
    headers: supabaseHeaders(env),
  });
  let rows = [];
  try {
    rows = await resp.json();
  } catch {
    rows = [];
  }
  return { ok: resp.ok, row: Array.isArray(rows) ? rows[0] || null : null, status: resp.status };
}

export async function supabasePatch(env, table, filters, patch) {
  const base = supabaseBase(env);
  if (!base.ok) return base;
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters || {})) {
    params.set(k, `eq.${v}`);
  }
  const resp = await fetch(`${base.url}/rest/v1/${table}?${params}`, {
    method: "PATCH",
    headers: supabaseHeaders(env, { prefer: "return=representation" }),
    body: JSON.stringify(patch),
  });
  let body = {};
  try {
    body = await resp.json();
  } catch {
    body = {};
  }
  const updated = Array.isArray(body) ? body[0] : body;
  return { ok: resp.ok, row: updated, status: resp.status };
}

function supabaseBase(env) {
  const url = (env.SUPABASE_URL || "").replace(/\/$/, "");
  const key = env.SUPABASE_SERVICE_ROLE_KEY || "";
  if (!url || !key) {
    return { ok: false, error: "supabase_not_configured" };
  }
  return { ok: true, url };
}

function supabaseHeaders(env, { prefer } = {}) {
  const key = env.SUPABASE_SERVICE_ROLE_KEY || "";
  const headers = {
    "Content-Type": "application/json",
    apikey: key,
    Authorization: `Bearer ${key}`,
  };
  if (prefer) headers.Prefer = prefer;
  return headers;
}

export async function writeProbeReceipt(env, { runId, probeId, verdict, evidence, telegramSent }) {
  return supabaseInsert(env, "nerve_probe_receipts", {
    run_id: runId,
    probe_id: probeId,
    verdict,
    execution_plane: "cloudflare_cron",
    evidence: evidence || {},
    telegram_sent: Boolean(telegramSent),
  });
}

export async function fileImprovement(env, { finding, source, expectedRoi, machineSafe }) {
  return supabaseInsert(env, "improvement_queue", {
    finding,
    source,
    expected_roi: expectedRoi ?? null,
    machine_safe: Boolean(machineSafe),
    status: machineSafe ? "open" : "founder_gated",
  });
}

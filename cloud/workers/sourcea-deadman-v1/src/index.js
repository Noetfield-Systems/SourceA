/**
 * sourcea-deadman-v1 — independent watcher for loop_registry staleness.
 * Law: data/loop-registry-v1.json · Observe → alert → one restart attempt → receipt.
 */
import REGISTRY from "./loop-registry.json";
import { sendTelegramAlert } from "./telegram.js";

const TABLE = "loop_registry";

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runDeadmanCheck(env));
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return Response.json({
        ok: true,
        service: "sourcea-deadman-v1",
        cron: REGISTRY.deadman_cron || "*/30 * * * *",
        watches: (REGISTRY.loops || []).map((r) => r.loop_id),
        stale_multiplier: REGISTRY.stale_multiplier || 2,
      });
    }
    if (url.pathname === "/check" && request.method === "POST") {
      const row = await runDeadmanCheck(env);
      return Response.json(row, { status: row.ok ? 200 : 422 });
    }
    return Response.json({ ok: false, error: "not_found" }, { status: 404 });
  },
};

export async function runDeadmanCheck(env) {
  const mult = Number(REGISTRY.stale_multiplier || 2);
  const loops = REGISTRY.loops || [];
  const live = await fetchRegistry(env);
  const now = Date.now();
  const results = [];

  for (const spec of loops) {
    const row = live.find((r) => r.loop_id === spec.loop_id) || null;
    const intervalMs = Number(spec.interval_minutes || 15) * 60 * 1000;
    const staleMs = intervalMs * mult;
    let stale = true;
    let ageMin = null;
    if (row?.last_fired_at) {
      const age = now - Date.parse(row.last_fired_at);
      ageMin = Math.round(age / 60000);
      stale = age > staleMs;
    }
    let restart = null;
    if (stale) {
      restart = await attemptRestart(spec);
      const text =
        `<b>DEADMAN stale</b> · ${spec.loop_id}\n` +
        `age=${ageMin ?? "never"}m · limit=${Math.round(staleMs / 60000)}m\n` +
        `restart=${restart?.ok ? "OK" : "FAIL"}`;
      await sendTelegramAlert(env, text);
    }
    results.push({
      loop_id: spec.loop_id,
      stale,
      age_minutes: ageMin,
      last_fired_at: row?.last_fired_at || null,
      last_ok: row?.last_ok ?? null,
      restart,
    });
  }

  const staleCount = results.filter((r) => r.stale).length;
  await upsertDeadmanPulse(env, { stale_count: staleCount, results });

  return {
    ok: staleCount === 0,
    schema: "sourcea-deadman-check-v1",
    at: new Date().toISOString(),
    stale_count: staleCount,
    results,
  };
}

async function fetchRegistry(env) {
  const url = (env.SUPABASE_URL || "").replace(/\/$/, "");
  const key = env.SUPABASE_SERVICE_ROLE_KEY || "";
  if (!url || !key) return [];
  const resp = await fetch(`${url}/rest/v1/${TABLE}?select=loop_id,last_fired_at,last_ok,interval_minutes`, {
    headers: { apikey: key, Authorization: `Bearer ${key}` },
  });
  try {
    return await resp.json();
  } catch {
    return [];
  }
}

async function attemptRestart(spec) {
  const restart = spec.restart;
  if (!restart?.url) return { ok: false, skipped: true, reason: "no_restart_url" };
  try {
    const resp = await fetch(restart.url, {
      method: restart.method || "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(restart.body || {}),
    });
    let row = {};
    try {
      row = await resp.json();
    } catch {
      row = {};
    }
    return { ok: resp.ok && row.ok !== false, status: resp.status, row };
  } catch (exc) {
    return { ok: false, error: String(exc).slice(0, 200) };
  }
}

async function upsertDeadmanPulse(env, receipt) {
  const url = (env.SUPABASE_URL || "").replace(/\/$/, "");
  const key = env.SUPABASE_SERVICE_ROLE_KEY || "";
  if (!url || !key) return { ok: false };
  const payload = {
    loop_id: "sourcea-deadman-v1",
    trigger_host: "cloudflare",
    schedule_cron: REGISTRY.deadman_cron || "*/30 * * * *",
    interval_minutes: 30,
    last_fired_at: new Date().toISOString(),
    last_ok: receipt.stale_count === 0,
    last_receipt: receipt,
  };
  await fetch(`${url}/rest/v1/${TABLE}?on_conflict=loop_id`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      apikey: key,
      Authorization: `Bearer ${key}`,
      Prefer: "resolution=merge-duplicates",
    },
    body: JSON.stringify(payload),
  });
  return { ok: true };
}

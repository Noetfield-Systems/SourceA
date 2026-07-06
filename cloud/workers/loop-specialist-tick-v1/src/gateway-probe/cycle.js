/**
 * Sina Gateway chain probes — piggyback loop-specialist 15m CF cron (zero new slots).
 * LAW: HTTP probes + JSON receipts only. ZERO Telegram — @Gateway_A is NOT this lane.
 * External alerts: UptimeRobot per data/noos-external-monitors-v1.json
 */
const DEFAULT_BASE = "https://sina-gateway-production.up.railway.app";

export async function runGatewayWatchdog(env) {
  const baseUrl = (env.SINA_GATEWAY_BASE_URL || DEFAULT_BASE).replace(/\/$/, "");
  const checks = [];

  if (!baseUrl) {
    return { ok: false, checks, error: "SINA_GATEWAY_BASE_URL not set" };
  }

  checks.push(await probe(`${baseUrl}/health`, "health"));
  checks.push(await probeReady(`${baseUrl}/ready`));
  checks.push(await probeConfig(`${baseUrl}/api/config`));

  const ok = checks.every((check) => check.ok);

  return {
    ok,
    schema: "sina-gateway-watchdog-v1",
    checks,
    telegram: { ok: true, skipped: true, reason: "gateway_lane_no_telegram" },
    at: new Date().toISOString(),
    execution_plane: "cloudflare_cron_loop_specialist",
  };
}

export async function runGatewayHeartbeat(env) {
  const baseUrl = (env.SINA_GATEWAY_BASE_URL || DEFAULT_BASE).replace(/\/$/, "");
  const gateway = { health: "FAIL", ready: "FAIL", supabase_table: "FAIL", capture_mode: "unknown" };

  if (!baseUrl) {
    return verdictPayload({ gateway, error: "SINA_GATEWAY_BASE_URL not set" });
  }

  try {
    const health = await fetch(`${baseUrl}/health`);
    gateway.health = health.ok ? "PASS" : "FAIL";
  } catch {
    gateway.health = "FAIL";
  }

  try {
    const readyRes = await fetch(`${baseUrl}/ready`);
    const ready = await readyRes.json();
    gateway.ready = readyRes.ok && ready.ok !== false ? "PASS" : "FAIL";
    gateway.supabase_table = ready.supabaseTableReady ? "PASS" : "FAIL";
    gateway.capture_mode = ready.captureMode || "unknown";
  } catch {
    gateway.ready = "FAIL";
  }

  const commercial = {
    offers_sent: Number(env.SG_OFFERS_SENT || 0),
    replies: Number(env.SG_REPLIES || 0),
    L2_receipts: Number(env.SG_L2_RECEIPTS || 0),
  };

  const infraRed = Object.values(gateway).includes("FAIL");
  const commercialRed = commercial.offers_sent === 0;
  const verdict = infraRed || commercialRed ? "RED" : "GREEN";

  const payload = verdictPayload({ gateway, commercial, verdict });

  return {
    ...payload,
    telegram: { ok: true, skipped: true, reason: "gateway_lane_no_telegram" },
    execution_plane: "cloudflare_cron_loop_specialist",
  };
}

async function probe(url, name) {
  try {
    const response = await fetch(url);
    return { name, ok: response.ok, status: response.status };
  } catch (error) {
    return { name, ok: false, error: error.message };
  }
}

async function probeReady(url) {
  try {
    const response = await fetch(url);
    const body = await response.json();
    const ok = response.ok && body.ok !== false && body.supabaseTableReady !== false;
    return {
      name: "ready",
      ok,
      status: response.status,
      captureMode: body.captureMode,
      supabaseTableReady: body.supabaseTableReady,
      error: body.supabaseTableError || "",
    };
  } catch (error) {
    return { name: "ready", ok: false, error: error.message };
  }
}

async function probeConfig(url) {
  try {
    const response = await fetch(url);
    const body = await response.json();
    const ok = response.ok && body.captureMode === "supabase";
    return { name: "config", ok, status: response.status, captureMode: body.captureMode };
  } catch (error) {
    return { name: "config", ok: false, error: error.message };
  }
}

function verdictPayload({ gateway, commercial = defaultCommercial(), verdict = "RED", error = "" }) {
  return {
    schema: "sina-gateway-heartbeat-v1",
    at: new Date().toISOString(),
    gateway,
    commercial,
    verdict,
    error,
  };
}

function defaultCommercial() {
  return { offers_sent: 0, replies: 0, L2_receipts: 0 };
}

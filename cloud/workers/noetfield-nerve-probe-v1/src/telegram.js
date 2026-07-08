/**
 * Telegram alert on probe FAIL — SourceA ops lane only.
 * NEVER @Gateway_A · see data/sourcea-telegram-lane-v1.json
 */

const FORBIDDEN_USERNAMES = ["gateway_a", "@gateway_a"];

function resolveOpsTelegram(env) {
  const token = (env.TELEGRAM_PRIMARY_BOT_TOKEN || env.TELEGRAM_BOT_TOKEN || "").trim();
  const chatId = (env.TELEGRAM_OPS_CHAT_ID || "").trim();
  if (!token || !chatId) {
    return {
      ok: false,
      skipped: true,
      reason: "telegram_ops_not_configured",
      hint: "Set TELEGRAM_OPS_CHAT_ID + TELEGRAM_PRIMARY_BOT_TOKEN only",
    };
  }
  return { ok: true, token, chatId };
}

function assertOutboundLane(text) {
  const lower = String(text || "").toLowerCase();
  for (const name of FORBIDDEN_USERNAMES) {
    if (lower.includes(name)) {
      return { ok: false, reason: "forbidden_telegram_target", target: name };
    }
  }
  return { ok: true };
}

export async function sendTelegramAlert(env, text) {
  const lane = resolveOpsTelegram(env);
  if (!lane.ok) {
    return { ok: false, skipped: true, reason: lane.reason, hint: lane.hint };
  }
  const guard = assertOutboundLane(text);
  if (!guard.ok) {
    return { ok: false, skipped: true, reason: guard.reason, target: guard.target };
  }
  const resp = await fetch(`https://api.telegram.org/bot${lane.token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: lane.chatId,
      text: String(text).slice(0, 3900),
      parse_mode: "HTML",
      disable_web_page_preview: true,
    }),
  });
  let body = {};
  try {
    body = await resp.json();
  } catch {
    body = {};
  }
  return {
    ok: Boolean(body.ok),
    message_id: body.result?.message_id || null,
    status: resp.status,
    lane: "sourcea_ops_trustfield",
    error: body.ok ? null : JSON.stringify(body).slice(0, 200),
  };
}

export async function sendIntakeTelegram(env, { intakeId, probe, company, email }) {
  const label = probe ? "NF intake probe" : "NF intake lead";
  const text = probe
    ? `<b>${label}</b> · ${intakeId}\nDB+Telegram path OK`
    : `<b>${label}</b> · ${intakeId}\n${company || "—"}\n${email || "—"}`;
  return sendTelegramAlert(env, text);
}

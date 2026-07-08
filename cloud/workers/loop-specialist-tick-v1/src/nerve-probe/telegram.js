/**
 * Telegram alert on probe FAIL — SourceA ops lane only (TrustFieldBot → TELEGRAM_OPS_CHAT_ID).
 * NEVER @Gateway_A · NEVER Sina Gateway lane · see data/sourcea-telegram-lane-v1.json
 */
import { assertOutboundLane, resolveOpsTelegram } from "./telegram-lane.js";

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

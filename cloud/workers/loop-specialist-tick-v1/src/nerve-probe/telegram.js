/**
 * Telegram alert on probe FAIL (SourceA loop-specialist nerve channel).
 */

export async function sendTelegramAlert(env, text) {
  const token = env.TELEGRAM_BOT_TOKEN || "";
  const chatId = env.TELEGRAM_ALERT_CHAT_ID || env.TELEGRAM_ALLOWED_CHAT_ID || "";
  if (!token || !chatId) {
    return { ok: false, skipped: true, reason: "telegram_not_configured" };
  }
  const resp = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
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

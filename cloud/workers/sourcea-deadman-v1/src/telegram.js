/** Ops Telegram only — see data/sourcea-telegram-lane-v1.json */
const FORBIDDEN = ["gateway_a", "@gateway_a"];

export async function sendTelegramAlert(env, text) {
  const token = (env.TELEGRAM_PRIMARY_BOT_TOKEN || env.TELEGRAM_BOT_TOKEN || "").trim();
  const chatId = (env.TELEGRAM_OPS_CHAT_ID || "").trim();
  if (!token || !chatId) {
    return { ok: false, skipped: true, reason: "telegram_ops_not_configured" };
  }
  const lower = String(text || "").toLowerCase();
  for (const name of FORBIDDEN) {
    if (lower.includes(name)) {
      return { ok: false, skipped: true, reason: "forbidden_telegram_target" };
    }
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
  return { ok: Boolean(body.ok), lane: "sourcea_ops_trustfield" };
}

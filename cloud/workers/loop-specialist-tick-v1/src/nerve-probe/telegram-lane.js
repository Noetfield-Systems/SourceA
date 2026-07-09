/**
 * SourceA Telegram lane guard — ops channel only.
 * @Gateway_A / Sina Gateway lane: NEVER send (see data/sourcea-telegram-lane-v1.json).
 */

const FORBIDDEN_USERNAMES = ["gateway_a", "@gateway_a"];

/**
 * Resolve TrustField ops Telegram only. No fallbacks to ALERT/ALLOWED chat IDs.
 */
export function resolveOpsTelegram(env) {
  const token = (env.TELEGRAM_PRIMARY_BOT_TOKEN || env.TELEGRAM_BOT_TOKEN || "").trim();
  const chatId = (env.TELEGRAM_OPS_CHAT_ID || "").trim();
  if (!token || !chatId) {
    return {
      ok: false,
      skipped: true,
      reason: "telegram_ops_not_configured",
      hint: "Set TELEGRAM_OPS_CHAT_ID + TELEGRAM_PRIMARY_BOT_TOKEN on loop-specialist only",
    };
  }
  return { ok: true, token, chatId };
}

/** Block @mentions of forbidden accounts in outbound text (belt-and-suspenders). */
export function assertOutboundLane(text) {
  const lower = String(text || "").toLowerCase();
  for (const name of FORBIDDEN_USERNAMES) {
    if (lower.includes(name)) {
      return { ok: false, reason: "forbidden_telegram_target", target: name };
    }
  }
  return { ok: true };
}

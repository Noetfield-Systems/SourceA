#!/usr/bin/env bash
# Arm loop-specialist-tick-v1 nerve probes (Supabase + SourceA ops Telegram only).
# NEVER @Gateway_A · NEVER TELEGRAM_ALERT_CHAT_ID / ALLOWED fallbacks.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WF="$ROOT/cloud/workers/loop-specialist-tick-v1"
SPINE="${HOME}/.sourcea-secrets/portfolio-spine.env"
SECRETS="${HOME}/.sina/secrets.env"
LANE="$ROOT/data/sourcea-telegram-lane-v1.json"

[[ -f "$LANE" ]] || { echo "FAIL: missing $LANE" >&2; exit 1; }
for f in "$SPINE" "$SECRETS"; do
  if [[ ! -f "$f" ]]; then
    echo "FAIL: missing $f" >&2
    exit 1
  fi
done
set -a
# shellcheck disable=SC1090
source "$SPINE"
# shellcheck disable=SC1090
source "$SECRETS"
set +a

OPS_CHAT="${TELEGRAM_OPS_CHAT_ID:-}"
TOKEN="${TELEGRAM_PRIMARY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-}}"
if [[ -z "$OPS_CHAT" ]]; then
  echo "FAIL: TELEGRAM_OPS_CHAT_ID required — never use @Gateway_A or other Telegram lanes" >&2
  exit 1
fi
if [[ -z "$TOKEN" ]]; then
  echo "FAIL: TELEGRAM_PRIMARY_BOT_TOKEN or TELEGRAM_BOT_TOKEN required" >&2
  exit 1
fi

unset CF_API_TOKEN CLOUDFLARE_API_TOKEN 2>/dev/null || true
cd "$WF"

echo "→ SUPABASE_URL"
printf '%s' "${SUPABASE_URL}" | npx wrangler secret put SUPABASE_URL
echo "→ SUPABASE_SERVICE_ROLE_KEY"
printf '%s' "${SUPABASE_SERVICE_ROLE_KEY}" | npx wrangler secret put SUPABASE_SERVICE_ROLE_KEY

echo "→ TELEGRAM_PRIMARY_BOT_TOKEN (TrustFieldBot ops lane only)"
printf '%s' "$TOKEN" | npx wrangler secret put TELEGRAM_PRIMARY_BOT_TOKEN
echo "→ TELEGRAM_OPS_CHAT_ID (never @Gateway_A)"
printf '%s' "$OPS_CHAT" | npx wrangler secret put TELEGRAM_OPS_CHAT_ID

echo ""
echo "OK — ops Telegram lane on loop-specialist. Gateway probes: HTTP only, zero Telegram."
echo "  bash scripts/validate-sourcea-telegram-lane-v1.sh"
echo "  curl -s https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev/health"

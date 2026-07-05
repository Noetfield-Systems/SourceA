#!/usr/bin/env bash
# Arm loop-specialist-tick-v1 nerve probes (Supabase + Telegram).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WF="$ROOT/cloud/workers/loop-specialist-tick-v1"
SPINE="${HOME}/.sourcea-secrets/portfolio-spine.env"
SECRETS="${HOME}/.sina/secrets.env"

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

unset CF_API_TOKEN CLOUDFLARE_API_TOKEN 2>/dev/null || true
cd "$WF"

echo "→ SUPABASE_URL"
printf '%s' "${SUPABASE_URL}" | npx wrangler secret put SUPABASE_URL
echo "→ SUPABASE_SERVICE_ROLE_KEY"
printf '%s' "${SUPABASE_SERVICE_ROLE_KEY}" | npx wrangler secret put SUPABASE_SERVICE_ROLE_KEY

if [[ -n "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  echo "→ TELEGRAM_BOT_TOKEN"
  printf '%s' "${TELEGRAM_BOT_TOKEN}" | npx wrangler secret put TELEGRAM_BOT_TOKEN
fi
CHAT="${TELEGRAM_ALERT_CHAT_ID:-${TELEGRAM_ALLOWED_CHAT_ID:-}}"
if [[ -n "$CHAT" ]]; then
  echo "→ TELEGRAM_ALERT_CHAT_ID"
  printf '%s' "$CHAT" | npx wrangler secret put TELEGRAM_ALERT_CHAT_ID
fi

echo ""
echo "OK — nerve probe secrets on loop-specialist. Test:"
echo "  curl -s https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
echo "  curl -s -X POST https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev/nerve/run"

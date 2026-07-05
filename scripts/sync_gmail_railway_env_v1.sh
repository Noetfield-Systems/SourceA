#!/usr/bin/env bash
# Sync Gmail + ops secrets to Railway FBE runner (from disk — never echoes values).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE="${RAILWAY_SERVICE:-sourcea-fbe-runner}"

command -v railway >/dev/null || { echo "FAIL: railway CLI required" >&2; exit 1; }

load_env() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  set -a
  # shellcheck disable=SC1090
  source "$f"
  set +a
}

load_env "${HOME}/.sourcea-secrets/portfolio-spine.env"
load_env "${HOME}/.sina/secrets.env"

SA_FILE="${GMAIL_SERVICE_ACCOUNT_PATH:-${HOME}/.sourcea-secrets/gmail-service-account.json}"
if [[ -z "${GOOGLE_SERVICE_ACCOUNT_JSON:-}" && -f "$SA_FILE" ]]; then
  export GOOGLE_SERVICE_ACCOUNT_JSON="$(python3 -c "import json; print(json.dumps(json.load(open('$SA_FILE'))))")"
fi

args=("railway" "variables" "set")
[[ -n "${SUPABASE_URL:-}" ]] && args+=("SUPABASE_URL=${SUPABASE_URL}")
[[ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]] && args+=("SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}")
[[ -n "${GOOGLE_SERVICE_ACCOUNT_JSON:-}" ]] && args+=("GOOGLE_SERVICE_ACCOUNT_JSON=${GOOGLE_SERVICE_ACCOUNT_JSON}")
[[ -n "${GMAIL_DELEGATED_USER:-}" ]] && args+=("GMAIL_DELEGATED_USER=${GMAIL_DELEGATED_USER}")
[[ -n "${TELEGRAM_BOT_TOKEN:-}" ]] && args+=("TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}")
[[ -n "${TELEGRAM_ALERT_CHAT_ID:-}" ]] && args+=("TELEGRAM_ALERT_CHAT_ID=${TELEGRAM_ALERT_CHAT_ID}")
[[ -n "${TELEGRAM_ALLOWED_CHAT_ID:-}" ]] && args+=("TELEGRAM_ALLOWED_CHAT_ID=${TELEGRAM_ALLOWED_CHAT_ID}")

args+=("-s" "$SERVICE")
echo "Syncing Gmail/ops env → Railway service ${SERVICE}"
"${args[@]}"
echo "OK: sync_gmail_railway_env_v1"

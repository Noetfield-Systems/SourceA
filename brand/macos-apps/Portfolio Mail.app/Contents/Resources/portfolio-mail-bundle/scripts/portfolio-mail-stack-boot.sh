#!/usr/bin/env bash
# Portfolio Mail stack — Chat Unify + N8N + standalone mail server (no Worker Hub).
set -uo pipefail
SA="${SINA_SOURCE_A:-$HOME/Desktop/SourceA}"
CU_PORT="${CHAT_UNIFY_PORT:-13023}"
N8_PORT="${N8N_INTEGRATION_PORT:-13026}"
MAIL_PORT="${PORTFOLIO_MAIL_PORT:-13028}"
CURL="${CURL:-/usr/bin/curl}"
LOG="${HOME}/.sina/portfolio-mail-stack-boot.log"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:/usr/bin:/bin:/usr/sbin:/sbin"

mkdir -p "${HOME}/.sina"
{
  echo "=== portfolio-mail-stack-boot $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  if [[ ! -d "$SA" ]]; then
    echo "FAIL missing SourceA at $SA"
    exit 1
  fi
  if ! "$CURL" -sf "http://127.0.0.1:${CU_PORT}/health" >/dev/null 2>&1; then
    echo "starting Chat Unify…"
    python3 "$SA/scripts/chat-unify-server.py" >>"$LOG" 2>&1 &
  fi
  if ! "$CURL" -sf "http://127.0.0.1:${N8_PORT}/health" >/dev/null 2>&1; then
    echo "starting N8N Integration…"
    bash "$SA/scripts/serve-n8n-integration.sh" >>"$LOG" 2>&1 || true
  fi
  if ! "$CURL" -sf "http://127.0.0.1:${MAIL_PORT}/health" >/dev/null 2>&1; then
    echo "starting Portfolio Mail server :${MAIL_PORT}…"
    PORTFOLIO_MAIL_PORT="$MAIL_PORT" python3 "$SA/scripts/portfolio-mail-server.py" >>"$LOG" 2>&1 &
  fi
  for _ in {1..40}; do
    "$CURL" -sf "http://127.0.0.1:${MAIL_PORT}/health" >/dev/null 2>&1 \
      && "$CURL" -sf "http://127.0.0.1:${CU_PORT}/health" >/dev/null 2>&1 \
      && "$CURL" -sf "http://127.0.0.1:${N8_PORT}/health" >/dev/null 2>&1 && break
    sleep 0.25
  done
  python3 "$SA/scripts/portfolio_mail_integration_wire_v1.py" --wire --json >>"$LOG" 2>&1 || true
  echo "done mail_port=${MAIL_PORT}"
} >>"$LOG" 2>&1

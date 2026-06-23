#!/usr/bin/env bash
# Portfolio Mail stack — start Hub + Chat Unify + N8N Integration + wire (no browser).
set -uo pipefail
SA="${SINA_SOURCE_A:-$HOME/Desktop/SourceA}"
PORT="${SINA_COMMAND_PORT:-13020}"
CU_PORT="${CHAT_UNIFY_PORT:-13023}"
N8_PORT="${N8N_INTEGRATION_PORT:-13026}"
CURL="${CURL:-/usr/bin/curl}"
LOG="${HOME}/.sina/portfolio-mail-stack-boot.log"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:/usr/bin:/bin:/usr/sbin:/sbin"

mkdir -p "${HOME}/.sina"
{
  echo "=== portfolio-mail-stack-boot $(date) ==="
  if [[ ! -d "$SA" ]]; then
    echo "FAIL missing SourceA at $SA"
    exit 1
  fi
  if ! "$CURL" -sf "http://127.0.0.1:${CU_PORT}/health" >/dev/null 2>&1; then
    echo "starting Chat Unify…"
    bash "$SA/scripts/serve-chat-unify.sh" >>"$LOG" 2>&1 || true
  fi
  if ! "$CURL" -sf "http://127.0.0.1:${N8_PORT}/health" >/dev/null 2>&1; then
    echo "starting N8N Integration…"
    bash "$SA/scripts/serve-n8n-integration.sh" >>"$LOG" 2>&1 || true
  fi
  if ! "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    echo "starting Worker Hub…"
    bash "$SA/scripts/serve-sina-command.sh" >>"$LOG" 2>&1 || true
  fi
  for _ in {1..40}; do
    "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 \
      && "$CURL" -sf "http://127.0.0.1:${CU_PORT}/health" >/dev/null 2>&1 \
      && "$CURL" -sf "http://127.0.0.1:${N8_PORT}/health" >/dev/null 2>&1 && break
    sleep 0.25
  done
  python3 "$SA/scripts/portfolio_mail_integration_wire_v1.py" --wire --json >>"$LOG" 2>&1 || true
  if ! "$CURL" -sf "http://127.0.0.1:8781/api/mac-law/health" >/dev/null 2>&1; then
    echo "starting Mac Law surfaces…"
    bash "$SA/scripts/mac_law_surfaces_boot_v1.sh" >>"$LOG" 2>&1 || true
  fi
  echo "done"
} >>"$LOG" 2>&1

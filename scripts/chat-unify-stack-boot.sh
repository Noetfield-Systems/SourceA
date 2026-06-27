#!/usr/bin/env bash
# Chat Unify stack boot — keep :13023 alive for app + browser (no Worker Hub).
set -euo pipefail
SA="${SINA_SOURCE_A:-$HOME/Desktop/SourceA}"
CU_PORT="${CHAT_UNIFY_PORT:-13023}"
CURL="${CURL:-/usr/bin/curl}"
LOG="${HOME}/.sina/chat-unify-stack-boot.log"
RECEIPT="${HOME}/.sina/chat-unify-stack-boot-receipt-v1.json"
PID_FILE="${HOME}/.sina/chat-unify-server.pid"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

pick_bundle() {
  for app in \
    "$HOME/Desktop/Chat Unify.app" \
    "$HOME/Applications/Chat Unify.app" \
    "$SA/brand/macos-apps/Chat Unify.app"; do
    local b="$app/Contents/Resources/chat-unify-bundle"
    if [[ -f "$b/scripts/chat-unify-server.py" && -f "$b/app/index.html" ]]; then
      echo "$b"
      return 0
    fi
  done
  return 1
}

mkdir -p "${HOME}/.sina"
{
  echo "=== chat-unify-stack-boot $(date -u +%Y-%m-%dT%H:%M:%SZ) port=${CU_PORT} ==="
  if [[ ! -d "$SA" ]]; then
    echo "FAIL missing SourceA at $SA"
    exit 1
  fi

  if "$CURL" -sf "http://127.0.0.1:${CU_PORT}/health" >/dev/null 2>&1; then
    health=$("$CURL" -sf "http://127.0.0.1:${CU_PORT}/health")
    stale=$(
      echo "$health" | python3 -c "
import sys, json
d = json.load(sys.stdin)
feats = d.get('features') or []
sys.exit(0 if 'platform_home' in feats else 1)
" 2>/dev/null || echo 1
    )
    if [[ "${CHAT_UNIFY_FORCE_BOOT:-}" == "1" || "$stale" == "1" ]]; then
      echo "recycling stale chat-unify (missing platform_home or force boot)"
      lsof -ti:"${CU_PORT}" | xargs kill -9 2>/dev/null || true
      sleep 0.35
    else
      echo "already_up ui=$(echo "$health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ui_version','?'))" 2>/dev/null || echo '?')"
    fi
  fi
  if ! "$CURL" -sf "http://127.0.0.1:${CU_PORT}/health" >/dev/null 2>&1; then
    BUNDLE="$(pick_bundle)" || {
      echo "FAIL no Chat Unify.app bundle found (Desktop, Applications, or brand)"
      exit 1
    }
    echo "starting from bundle $BUNDLE"
    export CHAT_UNIFY_BUNDLE_ROOT="$BUNDLE"
    export CHAT_UNIFY_STANDALONE=1
    export CHAT_UNIFY_PORT="$CU_PORT"
    export SINA_SOURCE_A="$SA"
    nohup python3 "$BUNDLE/scripts/chat-unify-server.py" >>"${HOME}/.sina/chat-unify-server.log" 2>&1 &
    echo $! >"$PID_FILE"
    echo "started pid=$(cat "$PID_FILE")"
  fi

  ok=0
  for _ in {1..40}; do
    if "$CURL" -sf "http://127.0.0.1:${CU_PORT}/health" >/dev/null 2>&1 \
      && "$CURL" -sf "http://127.0.0.1:${CU_PORT}/" -o /dev/null; then
      ok=1
      break
    fi
    sleep 0.25
  done
  health=$("$CURL" -sf "http://127.0.0.1:${CU_PORT}/health" 2>/dev/null || echo '{}')
  ui_ver=$(echo "$health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('ui_version','?'))" 2>/dev/null || echo "?")
  features=$(echo "$health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(','.join(d.get('features') or []))" 2>/dev/null || echo "")
  if [[ "$ok" != "1" ]]; then
    echo "FAIL health timeout — tail chat-unify-server.log"
    tail -5 "${HOME}/.sina/chat-unify-server.log" 2>/dev/null || true
    exit 1
  fi
  python3 - <<PY
import json, datetime
from pathlib import Path
Path("$RECEIPT").write_text(json.dumps({
  "schema": "chat-unify-stack-boot-receipt-v1",
  "ok": True,
  "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "port": int("$CU_PORT"),
  "url": f"http://127.0.0.1:{int('$CU_PORT')}/",
  "ui_version": "$ui_ver",
  "features": "$features".split(",") if "$features" else [],
  "registry": "data/validator-machine-registry-v1.json#chat_unify",
}, indent=2) + "\\n")
PY
  echo "PASS ui=${ui_ver} url=http://127.0.0.1:${CU_PORT}/"
} >>"$LOG" 2>&1

cat "$RECEIPT" 2>/dev/null || tail -3 "$LOG"

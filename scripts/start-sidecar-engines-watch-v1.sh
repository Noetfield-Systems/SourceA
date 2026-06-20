#!/usr/bin/env bash
# Phase 1 — keep API scout + CLI prep running while Worker drains INBOX.
# NOT the overnight boss-queue dispatcher (that is arm-sleep only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PIDFILE="$HOME/.sina/sidecar-engines-watch-v1.pid"
LOG="$HOME/.sina/sidecar-engines-watch-v1.log"
INTERVAL="${SINA_SIDECAR_INTERVAL_SEC:-180}"

if [[ -f "$PIDFILE" ]]; then
  old=$(cat "$PIDFILE" 2>/dev/null || true)
  if [[ -n "$old" ]] && kill -0 "$old" 2>/dev/null; then
    echo "Sidecar watch already running pid=$old"
    exit 0
  fi
fi

# Overnight boss loop owns the queue — no parallel sidecar watch
if ! python3 "$ROOT/scripts/single_boss_loop_v1.py" check --mode sidecar; then
  echo "ABORT: overnight boss loop active — sidecar watch forbidden (ONE LOOP law)"
  exit 0
fi
python3 "$ROOT/scripts/single_boss_loop_v1.py" claim --mode sidecar --pid $$ 2>/dev/null || true

# One immediate pass
bash "$ROOT/scripts/start-sidecar-engines-v1.sh"

(
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] sidecar watch start interval=${INTERVAL}s"
  while true; do
    if [[ -f "$HOME/.sina/auto-run-disabled-v1.flag" ]]; then
      # Awake phase — sidecars still run (Worker lane uses kill flag for dispatcher only)
      :
    fi
    sleep "$INTERVAL"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] sidecar tick"
    python3 "$ROOT/scripts/sidecar_scout_api_v1.py" --json >>"$LOG" 2>&1 || true
    python3 "$ROOT/scripts/sidecar_prep_cli_v1.py" --json >>"$LOG" 2>&1 || true
  done
) >>"$LOG" 2>&1 &

echo $! >"$PIDFILE"
echo "Sidecar watch ON pid=$(cat "$PIDFILE") interval=${INTERVAL}s log=$LOG"

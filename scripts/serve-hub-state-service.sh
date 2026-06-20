#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${HUB_STATE_SERVICE_PORT:-13031}"
PIDFILE="${HOME}/.sina/hub-state-service.pid"
LOGFILE="${HOME}/.sina/hub-state-service.log"
cd "$ROOT"

if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  if [[ "${SINA_FORCE_RESTART:-}" == "1" ]]; then
    pkill -f "hub_state_service_v1.py" 2>/dev/null || true
    sleep 0.5
  else
    curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null && exit 0
  fi
fi

nohup python3 "$ROOT/scripts/hub_state_service_v1.py" >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"
sleep 1
curl -sf "http://127.0.0.1:${PORT}/health"
echo "Hub state service → http://127.0.0.1:${PORT}/health"

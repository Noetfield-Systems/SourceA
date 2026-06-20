#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${HUB_AGENT_RUNTIME_PORT:-13032}"
PIDFILE="${HOME}/.sina/hub-agent-runtime.pid"
LOGFILE="${HOME}/.sina/hub-agent-runtime.log"
cd "$ROOT"

if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  if [[ "${SINA_FORCE_RESTART:-}" == "1" ]]; then
    pkill -f "hub_agent_runtime_v1.py" 2>/dev/null || true
    sleep 0.5
  else
    curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null && exit 0
  fi
fi

nohup python3 "$ROOT/scripts/hub_agent_runtime_v1.py" >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"
sleep 1
curl -sf "http://127.0.0.1:${PORT}/health"
echo "Hub agent runtime → http://127.0.0.1:${PORT}/health"

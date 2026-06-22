#!/usr/bin/env bash
# N8N Integration — standalone mini app (:13026). Does NOT start Sina Command hub.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${N8N_INTEGRATION_PORT:-13026}"
PIDFILE="${HOME}/.sina/n8n-integration-server.pid"
LOGFILE="${HOME}/.sina/n8n-integration-server.log"

export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}"
export SINA_SOURCE_A="${SINA_SOURCE_A:-$ROOT}"
export N8N_INTEGRATION_STANDALONE=1
export N8N_INTEGRATION_PORT="$PORT"
unset N8N_INTEGRATION_BUNDLE_ROOT

mkdir -p "${HOME}/.sina"

LOSF="${LOSF:-/usr/sbin/lsof}"
CURL="$(command -v curl 2>/dev/null || echo /usr/bin/curl)"

port_up() {
  if [[ -x "$LOSF" ]]; then
    "$LOSF" -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1 && return 0
  fi
  python3 -c "import socket; s=socket.socket(); s.settimeout(0.3); exit(0 if s.connect_ex(('127.0.0.1',${PORT}))==0 else 1)" 2>/dev/null
}

health_ok() {
  "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1
}

stop_stale_port() {
  if [[ -x "$LOSF" ]]; then
    "$LOSF" -t -iTCP:"${PORT}" 2>/dev/null | xargs kill 2>/dev/null || true
    sleep 0.3
    return
  fi
  if [[ -f "$PIDFILE" ]]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null || true
  fi
}

if port_up && ! health_ok; then
  echo "Port ${PORT} stale — restarting N8N Integration…"
  stop_stale_port
elif health_ok; then
  echo "N8N Integration already running → http://127.0.0.1:${PORT}/"
  exit 0
fi

if port_up; then
  echo "Port ${PORT} busy but not healthy — restarting…"
  stop_stale_port
fi

echo "Starting N8N Integration → http://127.0.0.1:${PORT}/"
echo "=== start $(date) ===" >>"$LOGFILE"
nohup python3 "$ROOT/scripts/n8n-integration-server.py" >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"

for _ in {1..80}; do
  if health_ok; then
    echo "Ready."
    exit 0
  fi
  sleep 0.25
done

echo "FAIL: N8N Integration did not become healthy on :${PORT} — see ${LOGFILE}"
tail -20 "$LOGFILE" 2>/dev/null || true
exit 1

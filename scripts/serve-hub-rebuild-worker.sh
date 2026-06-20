#!/usr/bin/env bash
# Hub rebuild worker — standalone queue consumer on :13030
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${HUB_REBUILD_WORKER_PORT:-13030}"
PIDFILE="${HOME}/.sina/hub-rebuild-worker.pid"
LOGFILE="${HOME}/.sina/hub-rebuild-worker.log"

export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}"

mkdir -p "${HOME}/.sina"
cd "$ROOT"

LOSF="${LOSF:-/usr/sbin/lsof}"
if [[ -z "${CURL:-}" ]]; then
  CURL="$(command -v curl 2>/dev/null || true)"
  CURL="${CURL:-/usr/bin/curl}"
fi

port_up() {
  if [[ -x "$LOSF" ]]; then
    "$LOSF" -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1 && return 0
  fi
  python3 -c "import socket; s=socket.socket(); s.settimeout(0.3); exit(0 if s.connect_ex(('127.0.0.1',${PORT}))==0 else 1)" 2>/dev/null
}

health_ok() { "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; }

stop_stale_port() {
  bash "$ROOT/scripts/kill-hub-rebuild-worker.sh" || true
  sleep 0.5
}

if health_ok; then
  if [[ "${SINA_FORCE_RESTART:-}" == "1" ]]; then
    echo "Restarting hub rebuild worker (founder force restart)…"
    stop_stale_port
    sleep 0.5
  else
    echo "Hub rebuild worker already running → http://127.0.0.1:${PORT}/health"
    exit 0
  fi
fi

if port_up; then
  echo "Port ${PORT} busy but not healthy — restarting…"
  stop_stale_port
fi

echo "Starting hub rebuild worker → http://127.0.0.1:${PORT}/health"
: >"$LOGFILE"
nohup env HUB_REBUILD_WORKER_PORT="${PORT}" python3 "$ROOT/scripts/hub_rebuild_worker_v1.py" >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"

for _ in {1..40}; do
  if health_ok; then
    echo "Ready."
    exit 0
  fi
  sleep 0.25
done

stop_stale_port
nohup env HUB_REBUILD_WORKER_PORT="${PORT}" python3 "$ROOT/scripts/hub_rebuild_worker_v1.py" >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"
for _ in {1..20}; do
  if health_ok; then
    echo "Ready (after retry)."
    exit 0
  fi
  sleep 0.25
done

echo "Failed to start hub rebuild worker. Log: $LOGFILE"
tail -20 "$LOGFILE" 2>/dev/null || true
exit 1

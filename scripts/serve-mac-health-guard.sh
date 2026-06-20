#!/usr/bin/env bash
# Mac Health Guard — standalone mini app (:13024). Does NOT start Sina Command hub.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${MAC_HEALTH_PORT:-13024}"
PIDFILE="${HOME}/.sina/mac-health-guard-server.pid"
LOGFILE="${HOME}/.sina/mac-health-guard-server.log"

export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}"
export MAC_HEALTH_PORT="$PORT"
export MAC_HEALTH_STANDALONE=1

mkdir -p "${HOME}/.sina"

LOSF="${LOSF:-/usr/sbin/lsof}"
CURL="$(command -v curl 2>/dev/null || echo /usr/bin/curl)"

port_up() {
  if [[ -x "$LOSF" ]]; then
    "$LOSF" -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1 && return 0
  fi
  python3 -c "import socket; s=socket.socket(); s.settimeout(0.3); exit(0 if s.connect_ex(('127.0.0.1',${PORT}))==0 else 1)" 2>/dev/null
}

health_ok() { "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; }

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

if health_ok; then
  echo "Mac Health Guard already running → http://127.0.0.1:${PORT}/"
  exit 0
fi

if port_up; then
  echo "Port ${PORT} busy but not healthy — restarting…"
  stop_stale_port
fi

echo "Starting Mac Health Guard → http://127.0.0.1:${PORT}/"
: >"$LOGFILE"
nohup python3 "$ROOT/scripts/mac-health-guard-server.py" >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"

for _ in {1..80}; do
  if health_ok; then
    echo "Ready."
    exit 0
  fi
  sleep 0.25
done

stop_stale_port
nohup python3 "$ROOT/scripts/mac-health-guard-server.py" >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"
for _ in {1..40}; do
  if health_ok; then
    echo "Ready (after retry)."
    exit 0
  fi
  sleep 0.25
done

echo "Failed to start. Log: $LOGFILE"
exit 1

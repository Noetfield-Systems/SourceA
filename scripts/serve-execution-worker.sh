#!/usr/bin/env bash
# Start execution spine worker (background) — polls ~/.sina/execution-queue.db
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIDFILE="${HOME}/.sina/execution-worker.pid"
LOGFILE="${HOME}/.sina/execution-worker.log"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

mkdir -p "${HOME}/.sina"

if [[ -f "$PIDFILE" ]]; then
  old_pid="$(cat "$PIDFILE" 2>/dev/null || true)"
  if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
    echo "Execution worker already running (pid $old_pid)"
    exit 0
  fi
fi

: >"$LOGFILE"
nohup python3 "$ROOT/scripts/execution_spine/worker.py" --poll 1.0 >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"
echo "Execution worker started → pid $(cat "$PIDFILE") · log $LOGFILE"

#!/usr/bin/env bash
# Stop hub rebuild worker on :13030 (queue consumer).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${HUB_REBUILD_WORKER_PORT:-13030}"
PIDFILE="${HOME}/.sina/hub-rebuild-worker.pid"
LOCKFILE="${HOME}/.sina/hub-rebuild-worker-v1.lock"

pkill -f 'hub_rebuild_worker_v1.py' 2>/dev/null || true
if command -v lsof >/dev/null 2>&1; then
  lsof -tiTCP:"${PORT}" 2>/dev/null | xargs kill -9 2>/dev/null || true
fi
if [[ -f "$PIDFILE" ]]; then
  kill -9 "$(cat "$PIDFILE")" 2>/dev/null || true
  rm -f "$PIDFILE"
fi
rm -f "$LOCKFILE"
sleep 0.5
echo "OK: hub rebuild worker stopped (:${PORT})"

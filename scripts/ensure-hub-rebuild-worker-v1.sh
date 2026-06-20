#!/usr/bin/env bash
# Ensure rebuild worker :13030 healthy; auto-start if down.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${HUB_REBUILD_WORKER_PORT:-13030}"
SERVE="$ROOT/scripts/serve-hub-rebuild-worker.sh"

_worker_ok() {
  curl -sf "http://127.0.0.1:${PORT}/health" 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
sys.exit(0 if d.get('ok') and d.get('service') == 'hub-rebuild-worker' else 1)
" 2>/dev/null
}

if _worker_ok; then
  echo "OK: rebuild worker :${PORT}/health"
  exit 0
fi

echo "WARN: rebuild worker :${PORT} down — running serve-hub-rebuild-worker.sh"
bash "$SERVE" || true

if _worker_ok; then
  echo "OK: rebuild worker :${PORT}/health (after serve)"
  exit 0
fi

echo "FAIL: rebuild worker :${PORT} not up — run serve-hub-rebuild-worker.sh or serve-sina-command.sh"
exit 1

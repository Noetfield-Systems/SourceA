#!/usr/bin/env bash
# Verify com.sourcea.hub launchd supervisor + health endpoint.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_DST="${HOME}/Library/LaunchAgents/com.sourcea.hub.plist"
LABEL="com.sourcea.hub"
PORT="${SINA_COMMAND_PORT:-13020}"
UID_NUM="$(id -u)"
DOMAIN="gui/${UID_NUM}"

test -f "$ROOT/launch/com.sourcea.hub.plist"
test -f "$PLIST_DST"
grep -q "KeepAlive" "$PLIST_DST"
grep -q "RunAtLoad" "$PLIST_DST"
grep -q "sina-command-server.py" "$PLIST_DST"

launchctl print "$DOMAIN/${LABEL}" >/dev/null 2>&1 || {
  echo "FAIL: launchd job ${LABEL} not loaded" >&2
  exit 1
}

curl -sf "http://127.0.0.1:${PORT}/health" | python3 -c "
import json, sys
b = json.load(sys.stdin)
assert b.get('ok') is True, b
print('health_ok')
"

echo "OK: validate-hub-launchd-v1"

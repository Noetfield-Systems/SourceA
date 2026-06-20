#!/usr/bin/env bash
# validate-mac-law-surfaces-launchd-v1.sh — :8781 + :8780 launchd + health
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UID_NUM="$(id -u)"
DOMAIN="gui/${UID_NUM}"

for label in com.sourcea.mac-law com.sourcea.routing-panel; do
  test -f "$ROOT/launch/${label}.plist"
  test -f "${HOME}/Library/LaunchAgents/${label}.plist"
  launchctl print "$DOMAIN/${label}" >/dev/null 2>&1 || {
    echo "FAIL: launchd ${label} not loaded — bash scripts/install-mac-law-surfaces-launchd-v1.sh" >&2
    exit 1
  }
done

curl -sf "http://127.0.0.1:8781/api/mac-law/health" | python3 -c "import json,sys; b=json.load(sys.stdin); assert b.get('status')=='ok', b"
curl -sf "http://127.0.0.1:8780/api/panel/health" | python3 -c "import json,sys; b=json.load(sys.stdin); assert b.get('status')=='ok', b"

echo "OK: validate-mac-law-surfaces-launchd-v1"

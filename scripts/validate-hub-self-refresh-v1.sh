#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f scripts/hub_self_refresh_v1.py
curl -sf "http://127.0.0.1:13020/api/hub-sync" >/dev/null || {
  echo "FAIL: /api/hub-sync unreachable — run serve-sina-command.sh"
  exit 1
}
python3 scripts/hub_self_refresh_v1.py --json | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('ok'), d
print('PASS: hub_self_refresh_v1')
"
echo "OK: validate-hub-self-refresh-v1"

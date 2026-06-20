#!/usr/bin/env bash
# U0 — hub-sync flat contract: server fields + app.js merge path.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

curl -sf "http://127.0.0.1:13020/health" >/dev/null || {
  echo "FAIL: hub not up"
  exit 1
}

python3 - <<'PY'
import json
import sys
import urllib.request

with urllib.request.urlopen("http://127.0.0.1:13020/api/hub-sync", timeout=10) as r:
    data = json.loads(r.read().decode("utf-8"))

if not data.get("ok"):
    print("FAIL: hub-sync ok=false", file=sys.stderr)
    sys.exit(1)
if "home_founder_view" not in data:
    print("FAIL: home_founder_view missing from hub-sync", file=sys.stderr)
    sys.exit(1)
if data.get("data"):
    print("FAIL: hub-sync still returns legacy data wrapper", file=sys.stderr)
    sys.exit(1)
print(f"OK: hub-sync contract fields present generation_id={data.get('generation_id')}")
PY

APP_JS="$ROOT/agent-control-panel/assets/app.js"
grep -q "shellFieldsFromHubSync" "$APP_JS" || {
  echo "FAIL: app.js missing shellFieldsFromHubSync"
  exit 1
}
grep -q "home_founder_view" "$APP_JS" || {
  echo "FAIL: app.js missing home_founder_view in merge path"
  exit 1
}
grep -qE "45000|120000|connectHubLive" "$APP_JS" || {
  echo "FAIL: app.js missing hubAutoSync fallback or SSE connectHubLive"
  exit 1
}

echo "OK: validate-hub-sync-ui-contract-v1"

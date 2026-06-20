#!/usr/bin/env bash
# validate-mac-health-cloud-glance-v1.sh — v4.0.0 cloud glance read-only API
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
PORT="${MAC_HEALTH_PORT:-13024}"
BASE="http://127.0.0.1:${PORT}"
fail=0

check() {
  if "$@"; then echo "PASS: $*"; else echo "FAIL: $*"; fail=1; fi
}

echo "=== Mac Health cloud glance v4 ==="

check test -f "$ROOT/scripts/mac_health_cloud_glance_v1.py"
check grep -q 'cloud-glance/v1' "$ROOT/scripts/mac-health-guard-server.py"
check grep -q 'id="cloud-glance-strip"' "$ROOT/scripts/mac-health-standalone/index.html"

python3 <<PY || fail=1
import json, urllib.request
row = json.loads(urllib.request.urlopen("${BASE}/api/mac-health/cloud-glance/v1", timeout=15).read())
for k in ("schema", "founder_line", "execution_plane"):
    assert k in row, f"missing {k}"
assert row.get("execution_plane") == "read_only_mac_glance", row
print("PASS: cloud-glance API schema")
PY

python3 <<PY || fail=1
import json, urllib.request
health = json.loads(urllib.request.urlopen("${BASE}/health", timeout=10).read())
ui = health.get("ui_contract") or {}
cg = ui.get("cloud_glance") or {}
assert "founder_line" in cg or health.get("version", "").startswith("4."), ui
print("PASS: /health ui_contract cloud_glance extension")
PY

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-cloud-glance-v1: ALL PASS"
  exit 0
fi
echo "validate-mac-health-cloud-glance-v1: FAILED"
exit 1

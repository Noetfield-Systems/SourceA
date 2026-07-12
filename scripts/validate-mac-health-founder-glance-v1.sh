#!/usr/bin/env bash
# validate-mac-health-founder-glance-v1.sh — SSOT gate for Founder Glance UI v3.3+
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
PORT="${MAC_HEALTH_PORT:-13024}"
BASE="http://127.0.0.1:${PORT}"
CONTRACT="$ROOT/data/mac-health-founder-glance-ui-contract-v1.json"
fail=0

check() {
  if "$@"; then echo "PASS: $*"; else echo "FAIL: $*"; fail=1; fi
}

echo "=== Mac Health Founder Glance SSOT ==="

check test -f "$CONTRACT"
check test -f "$ROOT/brain-os/law/enforcement/SINA_MAC_HEALTH_FOUNDER_GLANCE_UI_LOCKED_v1.md"
check node --check "$ROOT/scripts/mac-health-standalone/app.js"

python3 <<'PY' || fail=1
from mac_health_version_v1 import CSS_CACHE_BUSTER, MAC_HEALTH_VERSION, UI_SURFACE_ID
assert CSS_CACHE_BUSTER == MAC_HEALTH_VERSION, (CSS_CACHE_BUSTER, MAC_HEALTH_VERSION)
assert UI_SURFACE_ID == "founder_glance", UI_SURFACE_ID
print(f"PASS: version SSOT {MAC_HEALTH_VERSION} founder_glance")
PY

python3 <<PY || fail=1
from pathlib import Path
ROOT = Path("$ROOT")
src = (ROOT / "scripts/mac-health-standalone/index.html").read_text(encoding="utf-8")
assert "mhg-founder-glance" in src, "source index missing founder-glance — UI was downgraded on disk"
for bad in ("mhg-seg-nav", "tab-cooldown-btn", "founder-poem", "Brain heal"):
    assert bad not in src, f"source index still has old UI: {bad!r}"
print("PASS: source index not downgraded (anti-regression)")
PY

python3 <<PY || fail=1
import json, urllib.error, urllib.request
from pathlib import Path

from mac_health_version_v1 import MAC_HEALTH_VERSION

ROOT = Path("$ROOT")
CONTRACT = ROOT / "data/mac-health-founder-glance-ui-contract-v1.json"
BASE = "$BASE"
contract = json.loads(CONTRACT.read_text())
html = urllib.request.urlopen(f"{BASE}/", timeout=10).read().decode()
for needle in contract.get("dom_must_contain") or []:
    assert needle in html, f"missing dom: {needle!r}"
for bad in contract.get("dom_must_not_contain") or []:
    assert bad not in html, f"forbidden dom present: {bad!r}"
print("PASS: served HTML matches machine contract")

health = json.loads(urllib.request.urlopen(f"{BASE}/health", timeout=10).read())
v = health.get("version", "")
assert v == MAC_HEALTH_VERSION, f"health version={v!r} expected {MAC_HEALTH_VERSION!r}"
ui = health.get("ui_contract") or {}
assert ui.get("ui_mode") == "founder_glance", ui
assert ui.get("primary_cta") == "Relieve pressure", ui
assert ui.get("tab_count") == 0, ui
print("PASS: /health ui_contract wired")
# Report ui_contract is embedded on every build_report; health contract is SSOT for UI gate.
PY

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-founder-glance-v1: ALL PASS"
  exit 0
fi
echo "validate-mac-health-founder-glance-v1: FAILED"
exit 1

#!/usr/bin/env bash
# validate-sourcea-ui-pro-444-v1.sh — UI Pro 444 plan integrity (light; Mac-founder-safe)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PLAN="data/sourcea-ui-pro-444-upgrade-plan-v1.json"
DOC="docs/SOURCEA_UI_PRO_444_UPGRADE_PLAN_LOCKED_v1.md"
REG="brain-os/plan-registry/sourcea-ui-pro-444-v1/REGISTRY.json"

test -f "$PLAN" || { echo "FAIL: missing $PLAN"; exit 1; }
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }
test -f "$REG" || { echo "FAIL: missing $REG"; exit 1; }
test -f scripts/generate_sourcea_ui_pro_444_plan_v1.py || { echo "FAIL: missing generator"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path
plan = json.loads(Path("data/sourcea-ui-pro-444-upgrade-plan-v1.json").read_text())
steps = plan.get("steps") or []
assert len(steps) == 444, len(steps)
ids = [s["id"] for s in steps]
assert ids[0] == "UP-UI-001" and ids[-1] == "UP-UI-444", (ids[0], ids[-1])
assert len(set(ids)) == 444, "duplicate step ids"
ws = plan.get("workstreams") or []
assert len(ws) == 37, len(ws)
for w in ws:
    assert len(w.get("steps") or []) == 12, w["id"]
print(f"OK plan integrity · 444 steps · 37 workstreams · locked={plan.get('locked')}")
PY

python3 scripts/sourcea_ui_pro_444_pulse_v1.py >/tmp/ui-444-pulse.json
python3 -c "import json; r=json.load(open('/tmp/ui-444-pulse.json')); assert r.get('ok'), r"

echo "validate-sourcea-ui-pro-444-v1.sh: ALL PASS"

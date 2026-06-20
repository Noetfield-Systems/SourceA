#!/usr/bin/env bash
# validate-plans-unified-upgrade-v1.sh — unified plan SSOT sync + cross-ref
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f scripts/plans_unified_upgrade_v1.py || { echo "FAIL missing orchestrator"; exit 1; }
test -f data/outbound-factory-100-upgrade-plan-v1.json || { echo "FAIL missing outbound plan"; exit 1; }
test -f data/sourcea-full-stack-100-fix-plan-v1.json || { echo "FAIL missing full-stack plan"; exit 1; }
test -f data/brain-cloud-reasoning-1000-upgrade-plan-v1.json || { echo "FAIL missing brain plan"; exit 1; }

grep -q 'tool_pick_two_phase' scripts/plans_unified_upgrade_v1.py || { echo "FAIL cross_ref tool_pick"; exit 1; }
grep -q '/api/plans-unified/tick/v1' scripts/sina-command-server.py || { echo "FAIL hub API missing"; exit 1; }
grep -q 'plans-unified-card' agent-control-panel/worker-hub/index.html || { echo "FAIL hub card missing"; exit 1; }
grep -q 'plans_unified_upgrade' scripts/disk_live_wire_sync_v1.py || { echo "FAIL disk_live_wire missing"; exit 1; }
grep -q 'world_model_plan_check' scripts/disk_live_wire_sync_v1.py || { echo "FAIL disk_live_wire missing WTM"; exit 1; }
grep -q 'world_model_check' scripts/plans_unified_upgrade_v1.py || { echo "FAIL plans_unified missing WTM"; exit 1; }

python3 scripts/plans_unified_upgrade_v1.py --json >/dev/null
test -f "${SINA}/plans-unified-upgrade-receipt-v1.json" || { echo "FAIL missing receipt"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path
r = json.loads((Path.home() / ".sina/plans-unified-upgrade-receipt-v1.json").read_text())
assert r.get("schema") == "plans-unified-upgrade-receipt-v1"
assert r.get("outbound", {}).get("total") >= 100
assert r.get("full_stack", {}).get("total") == 100
assert r.get("brain_cloud", {}).get("total") == 1000
assert "Phase 1 free-tier" in (r.get("one_law") or "")
wm = r.get("world_model_check") or {}
assert wm.get("ok") is True, wm
print("OK:", r.get("plans_unified_line", "")[:96])
print("OK: WTM", (wm.get("line") or "")[:72])
PY

echo "PASS: validate-plans-unified-upgrade-v1"

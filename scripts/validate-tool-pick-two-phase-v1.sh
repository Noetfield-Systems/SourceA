#!/usr/bin/env bash
# validate-tool-pick-two-phase-v1.sh — two-phase free-first · founder approval gate
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/tool-pick-two-phase-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/tool_pick_two_phase_v1.py || { echo "FAIL missing script"; exit 1; }

grep -q 'pending_founder_approval' data/tool-pick-two-phase-v1.json || { echo "FAIL missing approval gate"; exit 1; }
grep -q 'phase_2_affordable_ai' data/tool-pick-two-phase-v1.json || { echo "FAIL missing phase 2"; exit 1; }
python3 - <<'PY' || { echo "FAIL phase 2 auto_wire"; exit 1; }
import json
from pathlib import Path
j = json.loads(Path("data/tool-pick-two-phase-v1.json").read_text())
assert j.get("phase_2_affordable_ai", {}).get("auto_wire") is False
assert j.get("phase_2_affordable_ai", {}).get("founder_approval_required") is True
print("OK: phase 2 founder approval gate")
PY
grep -q 'tool_pick_two_phase' scripts/disk_live_wire_sync_v1.py || { echo "FAIL disk_live_wire missing tool_pick"; exit 1; }
grep -q '/api/tool-pick/tick/v1' scripts/sina-command-server.py || { echo "FAIL hub API missing"; exit 1; }
grep -q 'tool-pick-card' agent-control-panel/worker-hub/index.html || { echo "FAIL hub card missing"; exit 1; }

python3 scripts/tool_pick_two_phase_v1.py --json >/dev/null
test -f "${SINA}/tool-pick-two-phase-receipt-v1.json" || { echo "FAIL missing receipt"; exit 1; }
test -f "${SINA}/tool-pick-phase2-founder-approval-v1.json" || { echo "FAIL missing approval receipt"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path
r = json.loads((Path.home() / ".sina/tool-pick-two-phase-receipt-v1.json").read_text())
assert r.get("schema") == "tool-pick-two-phase-receipt-v1"
assert r.get("phase_2", {}).get("auto_wire") is False
assert r.get("phase_2", {}).get("founder_approval_required") is True
pending = r.get("phase_2", {}).get("pending_founder_approval") or []
assert len(pending) >= 5
print("OK:", r.get("tool_pick_line", "")[:72])
PY

echo "PASS: validate-tool-pick-two-phase-v1"

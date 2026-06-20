#!/usr/bin/env bash
# UI FIRST CHECK mandatory for ALL agents — nerves · rules · pre-write · conduct · behavior
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-ui-first-check-mandatory-all-agents-v1 — $*" >&2; exit 1; }

# Rules (alwaysApply)
for rule in 024-ui-upgrade-mandatory-checklist.mdc 025-ui-upgrade-first-check-live-wire.mdc 026-ui-first-check-zero-exception.mdc; do
  [[ -f ".cursor/rules/$rule" ]] || fail "missing rule $rule"
done

# Core scripts
for s in ui_upgrade_first_check_v1.py ui_upgrade_path_classifier_v1.py ui_upgrade_mandatory_gate_v1.py pre_write_guard_v1.py agentic_conduct_gate_v1.py; do
  [[ -f "scripts/$s" ]] || fail "missing script $s"
done

bash scripts/validate-ui-upgrade-first-check-live-wire-v1.sh || fail "live wire"
bash scripts/validate-ui-upgrade-mandatory-v1.sh || fail "mandatory ledgers"

[[ -f ~/.sina/ui-upgrade-first-check-receipt-v1.json ]] || fail "wire receipt missing"
python3 - <<'PY' || fail "wire receipt wire_ok"
import json
from pathlib import Path
row = json.loads((Path.home() / ".sina/ui-upgrade-first-check-receipt-v1.json").read_text())
assert row.get("wire_ok") is True, row
print("OK: wire_ok=True")
PY

# Nerves + mirror + surfaces
grep -q 'ui_upgrade_first_check' scripts/agent_nerve_system_v1.py || fail "nerve missing ui_fc"
grep -q 'ui_upgrade_first_check' scripts/agent_memory_mirror_v1.py || fail "mirror missing ui_fc"
grep -q 'ui_upgrade_first_check' scripts/agent_session_gate_run_v1.py || fail "session gate missing ui_fc"
grep -q 'ui_upgrade_first_check' scripts/disk_live_wire_sync_v1.py || fail "disk sync missing ui_fc"
grep -q 'ui_upgrade_first_check' scripts/pre_write_guard_v1.py || fail "pre_write missing ui_fc"

python3 - <<'PY' || fail "surfaces line"
import json
from pathlib import Path
s = json.loads((Path.home() / ".sina/agent-live-surfaces-v1.json").read_text())
line = str(s.get("ui_upgrade_first_check_line") or "")
assert "UI-FIRST-CHECK" in line and "ack_before_edit" in line, line
print(f"OK: surfaces · {line[:80]}")
PY

# Behavior settings wire
grep -q 'ui_first_check_mandatory' data/agent-behavior-settings-v1.json || fail "behavior SSOT missing ui_first_check"
grep -q 'ui_edit_without_first_check' scripts/agentic_conduct_gate_v1.py || fail "conduct gate missing ui scan"

# Conduct gate — UI edit without ack = violation
python3 scripts/agentic_conduct_gate_v1.py --role worker --task-text "I will edit agent-control-panel/form/index.html now" --json 2>/dev/null > /tmp/ui-conduct-test.json || true
python3 - <<'PY' || fail "conduct ui scan"
import json
from pathlib import Path
d = json.loads(Path("/tmp/ui-conduct-test.json").read_text())
v = [x for x in (d.get("violations") or []) if "ui_edit_without_first_check" in x]
assert v, d
print("OK: conduct blocks UI edit claim without first check")
PY

# Multi-surface classify
python3 - <<'PY' || fail "surface classify"
import json, subprocess, sys
from pathlib import Path
root = Path.cwd()
checks = [
    ("agent-control-panel/form/index.html", "hub_form"),
    ("witnessbc-site/content/toolkits.html", "witnessbc_commercial"),
    ("SourceA-landing/green-unified/index.html", "sourcea_landing"),
    ("agent-control-panel/worker-hub/index.html", "worker_hub"),
]
for rel, expect in checks:
    proc = subprocess.run(
        [sys.executable, "scripts/ui_upgrade_path_classifier_v1.py", "--path", rel, "--json"],
        cwd=str(root), capture_output=True, text=True,
    )
    row = json.loads(proc.stdout)
    assert row.get("is_ui") is True, (rel, row)
    assert row.get("surface_id") == expect, (rel, row.get("surface_id"), expect)
print("OK: classify hub_form · witnessbc_commercial · sourcea_landing · worker_hub")
PY

[[ -f scripts/wbc-ui-first-check.sh ]] || fail "missing wbc-ui-first-check.sh"

[[ -f ~/.sina/founder-zero-ui-drift-v1.flag ]] || fail "founder-zero-ui-drift-v1.flag missing"
[[ -f scripts/validate-ui-zero-drift-v1.sh ]] || fail "missing validate-ui-zero-drift-v1.sh"
grep -q 'founder_zero_ui_drift' data/agent-behavior-settings-v1.json || fail "behavior SSOT missing founder_zero_ui_drift"

echo "PASS: validate-ui-first-check-mandatory-all-agents-v1"

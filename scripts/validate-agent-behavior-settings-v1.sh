#!/usr/bin/env bash
# validate-agent-behavior-settings-v1.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-agent-behavior-settings-v1 — $*" >&2; exit 1; }

test -f data/agent-behavior-settings-v1.json || fail "missing SSOT"
test -f scripts/agent_behavior_settings_v1.py || fail "missing script"
test -f .cursor/rules/agent-founder-intent-first.mdc || fail "missing cursor rule"
grep -q 'founder_intent_first' scripts/agent_memory_mirror_v1.py || fail "memory mirror not wired"
grep -q 'agent_behavior_settings' scripts/governance_gate_cart_v1.py || fail "gate cart not wired"
grep -q 'behavior_line' scripts/disk_live_wire_sync_v1.py || fail "disk_live_wire not wired"
grep -q 'behavior_line' scripts/worker_live_context_v1.py || fail "worker live context not wired"
grep -q 'behavior_line' scripts/brain_live_context_v1.py || fail "brain live context not wired"
grep -q 'founder_intent_behavior' scripts/agent_nerve_system_v1.py || fail "nerve not wired"
grep -q 'ui_upgrade_first_check' scripts/agent_nerve_system_v1.py || fail "nerve ui_fc not wired"
grep -q 'ui_edit_without_first_check' scripts/agentic_conduct_gate_v1.py || fail "conduct ui scan missing"
grep -q 'agent_report_language' scripts/agentic_conduct_gate_v1.py || fail "conduct report language missing"
test -f data/agent-report-language-standard-v1.json || fail "report language SSOT missing"
bash scripts/validate-agent-report-language-v1.sh >/dev/null || fail "report language validator"
test -f .cursor/rules/026-ui-first-check-zero-exception.mdc || fail "rule 026 missing"

python3 scripts/agent_memory_mirror_v1.py --sync --json >/dev/null || fail "mirror sync"
python3 scripts/agent_behavior_settings_v1.py --wire --json >/dev/null || fail "behavior wire"

test -f "${SINA}/agent-behavior-settings-receipt-v1.json" || fail "missing receipt"

python3 - <<'PY' || fail "mirror inject"
import json
from pathlib import Path
m = json.loads((Path.home() / ".sina/agent-memory-mirror-v1.json").read_text())
inj = m.get("inject") or {}
if not inj.get("founder_intent_first"):
    raise SystemExit("missing founder_intent_first in inject")
if not (inj.get("founder_intent_first_detail") or {}).get("one_law"):
    raise SystemExit("missing founder_intent_first_detail")
print("OK: mirror inject")
PY

python3 scripts/agent_behavior_settings_v1.py --validate --json >/dev/null || fail "validate after wire"

echo "PASS: validate-agent-behavior-settings-v1"

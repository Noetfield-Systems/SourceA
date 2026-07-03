#!/usr/bin/env bash
# validate-github-automation-governance-v1.sh — living system lane + conflict governance (light)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-github-automation-governance-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/data/github-automation-governance-v1.json" ]] || fail "missing governance SSOT"
[[ -f "$ROOT/data/automation-lane-registry-v1.json" ]] || fail "missing lane registry"
[[ -f "$ROOT/data/automation-conflict-matrix-v1.json" ]] || fail "missing conflict matrix"
[[ -f "$ROOT/docs/GITHUB_AUTOMATION_LIVING_SYSTEM_GOVERNANCE_LOCKED_v1.md" ]] || fail "missing governance doc"

PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"

"$PY" -c "
import json
from pathlib import Path
root = Path('$ROOT')
gov = json.loads((root / 'data/github-automation-governance-v1.json').read_text())
lanes = json.loads((root / 'data/automation-lane-registry-v1.json').read_text())
conflicts = json.loads((root / 'data/automation-conflict-matrix-v1.json').read_text())
triggers = json.loads((root / 'data/trigger-registry-v1.json').read_text())

assert gov.get('schema') == 'github-automation-governance-v1'
assert len(gov.get('executors', [])) >= 10
assert len(lanes.get('lanes', [])) >= 10
assert len(conflicts.get('conflicts', [])) >= 8

exec_ids = {e['id'] for e in gov['executors']}
for lane in lanes['lanes']:
    assert lane['owner_executor'] in exec_ids, lane['lane_id']

trigger_ids = {t['trigger_id'] for t in triggers['triggers']}
assert 'SA-T-brain-loop' not in trigger_ids
assert 'SA-T-signal-factory-dedicated' not in trigger_ids

sf = [t for t in triggers['triggers'] if t['trigger_id'] == 'SA-T-signal-factory'][0]
assert sf.get('kind') == 'piggyback'

copilot = gov.get('copilot', {})
assert 'forbidden' in copilot
assert any('Railway' in str(x) or 'motor' in str(x).lower() for x in copilot['forbidden'])

agents = gov.get('github_agents', {})
assert 'op_key' in str(agents.get('payload_schema', {}))

print(f\"OK governance: {len(gov['executors'])} executors · {len(lanes['lanes'])} lanes · {len(conflicts['conflicts'])} conflicts\")
"

mkdir -p "$ROOT/receipts/proof"
"$PY" "$ROOT/scripts/sandbox_health_sweep_v1.py" --json > "$ROOT/receipts/proof/trigger-sweep-latest-v1.json" 2>/dev/null || true
if [[ -f "$ROOT/receipts/proof/trigger-sweep-latest-v1.json" ]]; then
  "$PY" -c "import json; d=json.load(open('$ROOT/receipts/proof/trigger-sweep-latest-v1.json')); print(d.get('report_line',''))"
fi

echo "PASS: validate-github-automation-governance-v1.sh"

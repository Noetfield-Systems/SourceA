#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

test -f brain-os/scripts/brain_enforcement_audit_v1.py
test -f brain-os/enforcement/BRAIN_ENFORCEMENT_AUDIT_PROMPT_LOCKED_v1.md

python3 brain-os/scripts/brain_enforcement_audit_v1.py --json --write 2>/dev/null | python3 -c "
import json, sys
from pathlib import Path
d = json.load(sys.stdin)
assert d.get('status') == 'BRAIN_ENFORCEMENT_AUDIT', d.get('status')
assert len(d.get('steps', [])) >= 14, len(d.get('steps', []))
assert Path.home().joinpath('.sina/brain-enforcement-audit-v1.json').is_file()
ids = [s['step_id'] for s in d['steps']]
for need in ('S07_inbox_status', 'S10_brain_validate_goal1', 'S08_one_sa_gate_status'):
    assert need in ids, ids
print('PASS: brain_enforcement_audit_v1 steps', len(d['steps']))
"

echo "OK: validate-brain-enforcement-audit-v1"

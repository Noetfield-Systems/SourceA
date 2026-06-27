#!/usr/bin/env bash
# Validate SourceA Brain chatbot 100-plan SSOT — exactly 100 plans, 10 per phase.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLAN="${ROOT}/data/brain-chatbot-100-plans-v1.json"

[[ -f "$PLAN" ]] || { echo "FAIL: missing $PLAN — run python3 scripts/generate_brain_chatbot_100_plans_v1.py"; exit 1; }

python3 -c "
import json, sys
from pathlib import Path
p = Path('$PLAN')
doc = json.loads(p.read_text(encoding='utf-8'))
assert doc.get('schema') == 'sourcea-brain-chatbot-100-plans-v1', doc.get('schema')
plans = doc.get('plans') or []
assert len(plans) == 100, f'expected 100 plans, got {len(plans)}'
ids = [x['id'] for x in plans]
assert len(ids) == len(set(ids)), 'duplicate plan ids'
for phase in range(1, 11):
    phase_plans = [x for x in plans if x.get('phase') == phase]
    assert len(phase_plans) == 10, f'phase {phase} has {len(phase_plans)} plans'
    for seq in range(1, 11):
        pid = f'BRAIN-P{phase}-{seq:02d}'
        assert pid in ids, f'missing {pid}'
required = {'id', 'phase', 'title', 'summary', 'paths', 'status', 'priority', 'acceptance'}
for plan in plans:
    missing = required - set(plan.keys())
    assert not missing, f\"{plan.get('id')} missing {missing}\"
progress = doc.get('progress') or {}
assert progress.get('total') == 100
print('OK schema', doc.get('schema'))
print('OK plans', len(plans))
print('OK progress', progress.get('done'), 'done', progress.get('pct'), '%')
print('OK critical_path', len(doc.get('critical_path') or []), 'P0 remaining')
"

echo "validate-brain-chatbot-100-plans-v1.sh: ALL PASS"

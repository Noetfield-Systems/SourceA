#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from execution_intelligence.decision_memory.api import decisions_v1_payload, run_decision_pipeline

r = run_decision_pipeline(force=True)
assert r.get('ok'), r
p = decisions_v1_payload()
assert p.get('ok'), p
assert p.get('schema') == 'execution-decisions-v1'
required = {
    'decision_id','task_id','pattern_id','cause_type',
    'why_summary','cause_signal','effect_signal','confidence',
}
if p.get('decisions'):
    assert required.issubset(p['decisions'][0].keys()), p['decisions'][0]
assert 'cause_effect_mappings' in p
assert 'fix_relationships' in p
print('PASS decision memory v1', 'count', p['confidence_summary']['count'], 'types', p.get('by_cause_type'))
"

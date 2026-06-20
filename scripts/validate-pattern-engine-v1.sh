#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from execution_intelligence.pattern_engine.api import patterns_v1_payload, run_extraction

r = run_extraction(force=True)
assert r.get('ok'), r
p = patterns_v1_payload()
assert p.get('ok'), p
required = {'pattern_id','type','frequency','signature','related_task_ids','input_pattern','output_pattern','confidence'}
for pat in (p.get('top_success_patterns') or [])[:1]:
    assert required.issubset(pat.keys()), pat
print('PASS pattern engine v1', 'count', p.get('pattern_count'), 'fix', len(p.get('fix_mappings') or []))
"

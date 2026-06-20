#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from execution_intelligence.context_intelligence.api import execution_context_payload

p = execution_context_payload(action_id='pos-status')
assert p.get('ok'), p
ctx = p.get('context') or {}
required = {
    'task_id','system_state_summary','recent_executions','relevant_patterns',
    'decision_context','risk_context','recommended_focus_areas','active_constraints',
}
assert required.issubset(ctx.keys()), ctx.keys()
assert p.get('matters_now'), p
print('PASS execution context', ctx.get('task_id'), 'execs', len(ctx.get('recent_executions', [])))
"

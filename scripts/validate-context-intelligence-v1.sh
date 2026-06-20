#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from pathlib import Path

from execution_intelligence.context_intelligence.api import context_intelligence_v1_payload, run_context_intelligence
from execution_intelligence.context_intelligence.context_store import CONTEXT_SSOT_PATH

result = run_context_intelligence(force=True)
assert result.get('ok'), result
assert CONTEXT_SSOT_PATH.is_file(), 'snapshot missing'

sys_state = result.get('system_state') or {}
assert {'active_tasks', 'recent_successes', 'recent_failures', 'system_health'}.issubset(sys_state.keys())

repo = result.get('repo_state') or {}
assert 'active_projects' in repo and 'progress_summary' in repo and 'critical_paths' in repo

behavior = result.get('behavior_state') or {}
assert behavior.get('dominant_patterns') is not None
assert behavior.get('dominant_decisions') is not None
assert 'behavioral_risks' in behavior

assert result.get('planner_state') is not None
assert result.get('context_summary'), 'context_summary empty'

api = context_intelligence_v1_payload()
assert api.get('ok'), api
assert api.get('schema') == 'context-intelligence-v1'
assert api.get('system_state')
assert api.get('repo_state')
assert api.get('behavior_state')
assert api.get('planner_state')
assert api.get('context_summary')

print(
    'PASS context intelligence v1',
    'health', sys_state.get('system_health'),
    'active_projects', len(repo.get('active_projects', [])),
    'patterns', len(behavior.get('dominant_patterns', [])),
)
"

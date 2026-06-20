#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from pathlib import Path

from execution_intelligence.context_intelligence.api import run_context_intelligence
from execution_intelligence.feedback_loop.loop_engine import run_feedback_loop
from execution_intelligence.planner_upgrade.api import run_planner_upgrade
from execution_intelligence.self_optimization.api import self_optimization_v1_payload, run_self_optimization
from execution_intelligence.self_optimization.optimization_memory import SSOT_PATH

# Ensure upstream snapshots exist
run_feedback_loop(force=True)
run_planner_upgrade(force=True)
run_context_intelligence(force=True)

result = run_self_optimization(force=True)
assert result.get('ok'), result
assert SSOT_PATH.is_file(), 'self_optimization_v1.json missing'

perf = result.get('performance') or []
assert perf, 'performance metrics missing'
assert {'action_id', 'success_rate', 'failure_rate', 'stability_score'}.issubset(perf[0].keys())

strategies = result.get('strategies') or []
assert strategies, 'strategy analysis missing'
assert {'strategy_id', 'trend', 'confidence'}.issubset(strategies[0].keys())

trends = result.get('trends') or []
assert trends, 'trends missing'
assert {'trend_type', 'direction', 'strength'}.issubset(trends[0].keys())

recs = result.get('recommendations') or []
assert recs, 'recommendations missing'
assert {'recommendation_id', 'recommendation_type', 'target', 'reason', 'confidence'}.issubset(recs[0].keys())
assert recs[0].get('executed') is False, 'must not auto-execute'

api = self_optimization_v1_payload()
assert api.get('ok'), api
assert api.get('schema') == 'self-optimization-v1'
assert api.get('performance_summary')
assert api.get('trend_summary')
assert api.get('strategy_summary')
assert api.get('optimization_recommendations')

print(
    'PASS self-optimization v1',
    'actions', len(perf),
    'recommendations', len(recs),
    'top', api['performance_summary'].get('best_action'),
)
"

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from pathlib import Path

from execution_intelligence.feedback_loop.loop_engine import run_feedback_loop
from execution_intelligence.planner_upgrade.api import PLANNER_CONTEXT_PATH, planner_upgrade_v1_payload, run_planner_upgrade
from execution_intelligence.planner_influence import influence_task_priority

# Ensure upstream signals exist
run_feedback_loop(force=True)

candidates = ['pos-status', 'pos-dispatch', 'pos-run', 'spine-smoke-echo']
result = run_planner_upgrade(force=True, candidate_actions=candidates)
assert result.get('ok'), result
assert result.get('signals_consumed', result.get('planner_context_summary', {}).get('signals_consumed', 0)) > 0
assert PLANNER_CONTEXT_PATH.is_file(), 'planner_context_v1.json missing'

rec = result.get('recommendation') or {}
assert rec.get('ranked_actions'), 'rankings missing'
assert rec.get('recommended_actions'), 'recommendations missing'
# avoid list key exists (may be empty when no failures)
assert 'avoid_actions' in rec

ranked = influence_task_priority(candidates)
assert ranked, 'planner influence ranking empty'
top = ranked[0]['action_id']
# History must change order: spine-smoke-echo has prefer+reinforce signals
assert top == 'spine-smoke-echo', f'expected history-aware top spine-smoke-echo got {top}'
scores = [r['score'] for r in ranked]
assert len(set(scores)) > 1, 'scores must differ based on history'

outcome = result.get('outcome_evaluations') or []
assert outcome and {'action_id', 'historical_score', 'risk_score', 'confidence'}.issubset(outcome[0].keys())

api = planner_upgrade_v1_payload(candidate_actions=candidates)
assert api.get('ok'), api
assert api.get('schema') == 'planner-upgrade-v1'
assert api.get('ranked_actions')
assert api.get('recommended_actions')
assert api.get('planner_context_summary')

print('PASS planner upgrade v1', 'top', top, 'recommended', api['recommended_actions'], 'signals', api['planner_context_summary'].get('signals_consumed'))
"

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from runtime.tool_graph.api import build_tool_graph
from runtime.tool_graph_verification.validation_engine import verify_tool_graph
from runtime.execution_router.api import execution_router_v1_payload
from runtime.execution_router.router_engine import route_execution
from runtime.execution_router.router_store import ROUTER_SSOT_PATH
from runtime.execution_router.step_selector import dependencies_satisfied, select_candidates
from runtime.execution_router.policy_engine import evaluate_step, policy_context
from runtime.execution_router.priority_resolver import resolve_priority

TASK = 'router-smoke-1'
GOAL = 'pos-run'

build_tool_graph(goal_tool_id=GOAL, task_id=TASK, force=True)
verify_tool_graph(goal_tool_id=GOAL, task_id=TASK, force=True)

# Live route (may block if verification needs_fix — correct behavior)
live = route_execution(goal_tool_id=GOAL, task_id=TASK)
assert live.get('ok'), live
assert live.get('routing_decision') in ('allow', 'block', 'wait')
assert live.get('next_step'), live
assert ROUTER_SSOT_PATH.is_file(), 'execution_router_v1.json missing'

required = {'step', 'tool_id', 'title', 'status'}
assert required.issubset(live['next_step'].keys())
assert live.get('execution_state') and 'completed' in live['execution_state']

# Deterministic selection + dependency compliance (synthetic approve path)
mock_verified = {
    'ok': True,
    'is_valid': True,
    'recommendation': 'approve',
    'cycle_detected': False,
    'safety_score': 0.92,
    'context_alignment_score': 0.5,
    'plan_score': 0.8,
    'execution_path_verified': [
        {'step': 1, 'tool_id': 'pos-dispatch'},
        {'step': 2, 'tool_id': 'pos-decide'},
        {'step': 3, 'tool_id': 'pos-run'},
    ],
}
from runtime.execution_router.router_store import load_graph_entry, load_memory, load_planner, load_context
graph = load_graph_entry(goal_tool_id=GOAL, task_id=TASK)
assert graph, 'graph entry required'
path = graph.get('execution_path') or []
cands = select_candidates(execution_path=path, completed=[], graph_entry=graph)
assert cands, 'expected candidates'
assert cands[0] == 'pos-dispatch', f'first candidate should be dispatch got {cands}'
assert dependencies_satisfied('pos-decide', completed=['pos-dispatch'], graph_entry=graph)

policy = policy_context(verified=mock_verified, planner=load_planner(), context=load_context())
pol = evaluate_step(tool_id='pos-dispatch', policy=policy, dependencies_satisfied=True)
assert pol['allowed'], pol

# Safety filter: avoid list blocks
policy_bad = {**policy, 'avoid_actions': ['pos-dispatch']}
pol_bad = evaluate_step(tool_id='pos-dispatch', policy=policy_bad, dependencies_satisfied=True)
assert pol_bad['blocked'], 'avoid should block'

winner = resolve_priority(candidates=cands, policy=policy, memory=load_memory())
assert winner and winner['tool_id'] == 'pos-dispatch'
assert winner.get('breakdown'), 'score breakdown required'

api = execution_router_v1_payload(goal_tool_id=GOAL, task_id=TASK)
assert api.get('ok'), api
assert api.get('schema') == 'execution-router-v1'

print(
    'PASS execution router v1',
    'live_decision', live.get('routing_decision'),
    'first_candidate', cands[0],
    'priority', winner['tool_id'],
)
"

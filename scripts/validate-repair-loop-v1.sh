#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from runtime.tool_graph.api import build_tool_graph
from runtime.tool_graph_verification.validation_engine import verify_tool_graph
from runtime.execution_router.router_engine import route_execution
from runtime.repair_loop.api import repair_loop_v1_payload
from runtime.repair_loop.repair_engine import run_repair_loop
from runtime.repair_loop.failure_classifier import classify_failure, FAILURE_CLASSES
from runtime.repair_loop.recovery_graph import build_recovery_suggestions
from runtime.repair_loop.repair_loop_store import REPAIR_SSOT_PATH, load_router_route
from runtime.execution_router.router_store import load_verified_entry

TASK = 'repair-smoke-1'
GOAL = 'pos-run'

build_tool_graph(goal_tool_id=GOAL, task_id=TASK, force=True)
verify_tool_graph(goal_tool_id=GOAL, task_id=TASK, force=True)
route = route_execution(goal_tool_id=GOAL, task_id=TASK)
assert route.get('ok'), route

verified = load_verified_entry(goal_tool_id=GOAL, task_id=TASK)
failure = classify_failure(route=route, verified=verified, task_id=TASK)
assert failure.get('failure_class') in FAILURE_CLASSES, failure
assert 'links' in failure

suggestions = build_recovery_suggestions(
    failure=failure, route=route, goal_tool_id=GOAL, task_id=TASK,
)
# healthy path may have zero suggestions — still valid
for s in suggestions:
    assert s.get('path_id') and s.get('steps'), s

live = run_repair_loop(goal_tool_id=GOAL, task_id=TASK, force_refresh=True)
assert live.get('ok'), live
assert live.get('schema') == 'repair-loop-v1'
assert live.get('failure_class'), live
assert live.get('dispatch_ready') is False, 'repair must not auto-dispatch'
assert REPAIR_SSOT_PATH.is_file(), 'repair_loop_v1.json missing'

api = repair_loop_v1_payload(goal_tool_id=GOAL, task_id=TASK)
assert api.get('ok'), api
assert api.get('schema') == 'repair-loop-v1'
assert api.get('dispatch_ready') is False

# Blocked route still produces repair output
mock_route = {
    'ok': True,
    'routing_decision': 'block',
    'reason': 'verification recommendation is needs_fix (requires approve)',
    'next_step': {'tool_id': 'pos-run', 'status': 'blocked', 'step': 1, 'title': ''},
}
mock_verified = {'recommendation': 'needs_fix', 'is_valid': False}
bf = classify_failure(route=mock_route, verified=mock_verified, task_id='mock-block')
assert bf.get('failure_class') == 'verification_needs_fix', bf
bs = build_recovery_suggestions(failure=bf, route=mock_route, goal_tool_id=GOAL, task_id='mock-block')
assert bs, 'expected recovery path for verification failure'

print(
    'PASS repair loop v1',
    'failure_class', live.get('failure_class'),
    'suggestions', len(live.get('recovery_suggestions') or []),
)
"

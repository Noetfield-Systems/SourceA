#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from runtime.tool_graph.api import build_tool_graph
from runtime.tool_graph_verification.validation_engine import verify_tool_graph
from runtime.repair_loop.repair_engine import run_repair_loop
from runtime.multi_step_planner.api import multi_step_planner_v1_payload
from runtime.multi_step_planner.planner_engine import plan_multi_step_execution, PLANNING_AUTHORITY
from runtime.multi_step_planner.chain_builder import build_primary_chain, spine_sequence_from_chain
from runtime.multi_step_planner.planner_store import PLANNER_SSOT_PATH, load_graph_entry, load_verified_entry

TASK = 'planner-smoke-1'
GOAL = 'pos-run'

build_tool_graph(goal_tool_id=GOAL, task_id=TASK, force=True)
verify_tool_graph(goal_tool_id=GOAL, task_id=TASK, force=True)
run_repair_loop(goal_tool_id=GOAL, task_id=TASK, force_refresh=True)

verified = load_verified_entry(goal_tool_id=GOAL, task_id=TASK)
graph = load_graph_entry(goal_tool_id=GOAL, task_id=TASK)
assert verified and graph, 'graph substrate required'

chain = build_primary_chain(
    execution_path=graph.get('execution_path') or [],
    graph_entry=graph,
    verified=verified,
)
assert chain, chain
assert all('tool_id' in s and 'order' in s for s in chain)

spine = spine_sequence_from_chain(chain)
assert spine.get('action_ids'), spine
assert spine.get('dispatch_ready') is False

live = plan_multi_step_execution(goal_tool_id=GOAL, task_id=TASK)
assert live.get('ok'), live
assert live.get('schema') == 'multi-step-planner-v1'
assert PLANNING_AUTHORITY in (live.get('planning_authority') or '')
assert live.get('dispatch_ready') is False
assert live.get('primary_chain'), live
assert PLANNER_SSOT_PATH.is_file(), 'multi_step_planner_v1.json missing'

api = multi_step_planner_v1_payload(goal_tool_id=GOAL, task_id=TASK)
assert api.get('ok'), api
assert api.get('schema') == 'multi-step-planner-v1'
assert 'D10' in (api.get('planning_authority') or '')

print(
    'PASS multi-step planner v1',
    'chain_len', len(live.get('primary_chain') or []),
    'fallbacks', len(live.get('fallback_paths') or []),
    'plan_status', live.get('plan_status'),
)
"

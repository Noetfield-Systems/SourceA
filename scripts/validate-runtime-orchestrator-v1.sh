#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from runtime.orchestrator.api import runtime_orchestrator_v1_payload
from runtime.orchestrator.orchestrator_engine import run_runtime_orchestration, PIPELINE_STAGES, SCHEMA
from runtime.orchestrator.orchestrator_store import ORCHESTRATOR_SSOT_PATH
from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready

TASK = 'orchestrator-smoke-1'
GOAL = 'pos-run'
exp_ready, exp_blockers, _ = orchestrator_dispatch_ready()

assert len(PIPELINE_STAGES) == 6, PIPELINE_STAGES

live = run_runtime_orchestration(goal_tool_id=GOAL, task_id=TASK)
assert live.get('ok'), live
assert live.get('schema') == SCHEMA
assert live.get('runtime_stack_complete') is True
assert bool(live.get('dispatch_ready')) == exp_ready, (live.get('dispatch_ready'), exp_blockers)
assert live.get('founder_confirm_required') is True
assert ORCHESTRATOR_SSOT_PATH.is_file(), 'runtime_orchestrator_v1.json missing'

pipe = live.get('pipeline') or []
assert len(pipe) == 6, pipe
steps = [p['step'] for p in pipe]
assert steps == ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'], steps
assert all('ok' in p for p in pipe)

api = runtime_orchestrator_v1_payload(goal_tool_id=GOAL, task_id=TASK)
assert api.get('ok'), api
assert api.get('schema') == 'runtime-orchestrator-v1'
assert bool(api.get('dispatch_ready')) == exp_ready, api

decision = live.get('dispatch_decision') or api.get('dispatch_decision') or {}
assert decision.get('schema') == 'dispatch-policy-v1', decision
assert decision.get('dry_run') is True, decision
assert live.get('task_class'), live

print(
    'PASS runtime orchestrator v1',
    'overall', live.get('overall_status'),
    'pipeline_ok', sum(1 for p in pipe if p.get('ok')),
)
"

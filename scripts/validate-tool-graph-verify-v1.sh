#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from pathlib import Path

from runtime.tool_graph.api import build_tool_graph
from runtime.tool_graph_verification.api import tool_graph_verify_v1_payload
from runtime.tool_graph_verification.validation_engine import verify_tool_graph
from runtime.tool_graph_verification.verify_store import VERIFIED_PATH

# Ensure graph exists
build_tool_graph(goal_tool_id='pos-run', task_id='verify-smoke-1', force=True)

result = verify_tool_graph(goal_tool_id='pos-run', task_id='verify-smoke-1', force=True)
assert result.get('ok'), result
assert VERIFIED_PATH.is_file(), 'tool_graph_verified_v1.json missing'

# Cycle check
assert result.get('cycle_detected') is False, 'cycle should not be detected on valid graph'

# Dependency validation
assert result.get('invalid_tools') == [], result.get('invalid_tools')
assert result.get('execution_path_verified'), 'verified path missing'
assert result['execution_path_verified'][-1]['tool_id'] == 'pos-run'

# Scoring
assert result.get('plan_score') is not None and result['plan_score'] > 0
assert result.get('score_breakdown'), 'score breakdown missing'
assert result.get('context_alignment_score') is not None
assert result.get('safety_score') is not None
assert result.get('recommendation') in ('approve', 'reject', 'needs_fix')

api = tool_graph_verify_v1_payload(goal_tool_id='pos-run', task_id='verify-smoke-1')
assert api.get('ok'), api
assert api.get('schema') == 'tool-graph-verified-v1'
assert api.get('plan_score') is not None
assert api.get('recommendation')

print(
    'PASS tool graph verify v1',
    'valid', result.get('is_valid'),
    'plan_score', result.get('plan_score'),
    'recommendation', result.get('recommendation'),
)
"

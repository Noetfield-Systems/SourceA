#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from pathlib import Path

from runtime.tool_graph.api import build_tool_graph, tool_graph_v1_payload
from runtime.tool_graph.graph_store import GRAPH_SSOT_PATH

result = build_tool_graph(goal_tool_id='pos-run', task_id='runtime-smoke-1', force=True)
assert result.get('ok'), result
assert GRAPH_SSOT_PATH.is_file(), 'tool_graph_v1.json missing'

assert result.get('estimated_steps', 0) >= 2, 'graph must be multi-step not single tool'
assert len(result.get('execution_path') or []) >= 2
assert result.get('required_tools'), 'required_tools missing'
assert result.get('dependencies'), 'dependencies missing'

path = result['execution_path']
assert path[-1]['tool_id'] == 'pos-run', 'goal must be last step'
assert 'pos-dispatch' in result['required_tools'], 'dispatch prerequisite expected'

api = tool_graph_v1_payload(goal_tool_id='pos-run', task_id='runtime-smoke-1')
assert api.get('ok'), api
assert api.get('schema') == 'tool-graph-v1'
assert api.get('execution_path')
assert api.get('dependencies')
assert api.get('graph_summary', {}).get('node_count', 0) >= 2

print(
    'PASS tool graph v1',
    'steps', api['estimated_steps'],
    'path', [s['tool_id'] for s in api['execution_path']],
)
"

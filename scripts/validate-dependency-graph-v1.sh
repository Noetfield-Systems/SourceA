#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
import inspect
from pre_llm.dependency_graph.api import dependency_graph_v1_payload
from pre_llm.dependency_graph.graph_engine import run_dependency_graph
from pre_llm.dependency_graph.store import DEP_GRAPH_SSOT_PATH, SCHEMA

import pre_llm.dependency_graph.graph_engine as ge
src = inspect.getsource(ge)
for forbidden in ('openai', 'embeddings', 'pgvector', 'def rank', 'def retrieve'):
    assert forbidden not in src, f'forbidden in D3: {forbidden}'

TASK = 'dependency-graph-smoke-1'
live = run_dependency_graph(task_id=TASK, force_refresh=True)
assert live.get('ok'), live
assert live.get('schema') == SCHEMA
assert DEP_GRAPH_SSOT_PATH.is_file(), 'dependency_graph_v1.json missing'
assert live.get('dependency_ready') is True

stats = live.get('graph_stats') or {}
assert stats.get('module_edges', 0) > 0, 'module edges required'
assert stats.get('file_edges', 0) > 0, 'file edges required'
assert stats.get('call_edges', 0) > 0, 'call edges required'

d2_ref = live.get('d2_ref') or {}
assert d2_ref.get('schema') == 'graph-fusion-v1', 'must reference D2'

mg = live.get('module_graph') or []
sample_mod = mg[0]['to']
api = dependency_graph_v1_payload(
    task_id=TASK,
    query_type='impact',
    query_arg=sample_mod,
    target_type='module',
)
assert api.get('ok'), api
qr = api.get('query_result') or {}
assert qr.get('ok') is True, qr
assert 'direct_dependents' in qr

sym_api = dependency_graph_v1_payload(
    task_id=TASK,
    query_type='impact',
    query_arg='run_full_index',
    target_type='symbol',
)
assert sym_api.get('query_result', {}).get('ok') is True

print(
    'PASS dependency graph v1',
    'module_edges', stats.get('module_edges'),
    'file_edges', stats.get('file_edges'),
    'call_edges', stats.get('call_edges'),
)
"

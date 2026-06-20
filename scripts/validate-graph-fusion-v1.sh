#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
import inspect
from pre_llm.graph_fusion.api import graph_fusion_v1_payload
from pre_llm.graph_fusion.fusion_builder import run_fusion
from pre_llm.graph_fusion.store import FUSION_SSOT_PATH, SCHEMA

# Law: D2 must not embed forbidden semantic layers
import pre_llm.graph_fusion.fusion_builder as fb
src = inspect.getsource(fb)
for forbidden in ('openai', 'embeddings', 'pgvector', 'def rank', 'def retrieve'):
    assert forbidden not in src, f'forbidden in D2: {forbidden}'

TASK = 'graph-fusion-smoke-1'
live = run_fusion(task_id=TASK, force_refresh=True)
assert live.get('ok'), live
assert live.get('schema') == SCHEMA
assert FUSION_SSOT_PATH.is_file(), 'graph_fusion_v1.json missing'
assert live.get('fusion_ready') is True

stats = live.get('fusion_stats') or {}
assert stats.get('nodes', 0) > 0, 'nodes > 0 required'
assert stats.get('edges', 0) > 0, 'edges > 0 required'
by_type = stats.get('edges_by_type') or {}
assert 'import' in by_type, 'import edges required'
assert 'defines' in by_type or 'call' in by_type, 'symbol edges required'

d1_ref = live.get('d1_ref') or {}
assert d1_ref.get('schema') == 'code-intelligence-v1', 'must reference D1'

api = graph_fusion_v1_payload(task_id=TASK, query_type='find_symbol', query_arg='run_full_index')
assert api.get('ok'), api
assert api.get('fusion_ready') is True
qr = api.get('query_result') or {}
assert qr.get('found') is True, qr

print(
    'PASS graph fusion v1',
    'nodes', stats.get('nodes'),
    'edges', stats.get('edges'),
    'edge_types', list(by_type.keys()),
)
"

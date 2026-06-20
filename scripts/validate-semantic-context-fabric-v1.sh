#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
import inspect
from runtime.context_fabric.api import semantic_context_fabric_v1_payload
from runtime.context_fabric.fabric_engine import build_context_fabric, SCHEMA, BRIDGE_LAW
from runtime.context_fabric.fabric_store import FABRIC_SSOT_PATH, PRE_LLM_ARTIFACTS

# Law: pre-LLM handle bridge — D1 + D4–D12 SSOT pointers only (no inference; D2/D3 wired via schema hydrate)
EXPECTED_PRE_LLM = {
    'd1_code_intelligence', 'd4_intent_engine', 'd5_vector_retrieval',
    'd6_memory_git_bridge', 'd7_query_expansion', 'd8_graph_reasoning',
    'd9_context_ranking', 'd10_planning_engine', 'd11_tool_router', 'd12_validation_layer',
    'd13_diff_intelligence', 'd14_context_compression',
}
assert set(PRE_LLM_ARTIFACTS.keys()) == EXPECTED_PRE_LLM

# No heavy semantic modules imported in fabric package
import runtime.context_fabric.fabric_engine as fe
import runtime.context_fabric.fabric_store as fs
for mod in (fe, fs):
    src = inspect.getsource(mod)
    for forbidden in ('import ast', 'openai', 'embeddings', 'def rank', 'def retrieve'):
        assert forbidden not in src, f'forbidden in context_fabric: {forbidden}'

live = build_context_fabric(task_id='fabric-smoke-1')
assert live.get('ok'), live
assert live.get('schema') == SCHEMA
assert live.get('stateless') is True
assert BRIDGE_LAW in (live.get('bridge_law') or '')
assert FABRIC_SSOT_PATH.is_file(), 'semantic_context_fabric_v1.json missing'

pre = live.get('pre_llm_handles') or {}
assert set(pre.keys()) == EXPECTED_PRE_LLM
for h in pre.values():
    assert h.get('path') and h.get('owner_step') in ('D1', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14')
    assert 'exists' in h and 'ready' in h

runtime = live.get('runtime_handles') or {}
assert len(runtime) >= 4, runtime
assert all(r.get('owner_step', '').startswith('C') for r in runtime.values())

hooks = live.get('packet_hooks') or {}
assert hooks.get('llm_packet_fields'), hooks

api = semantic_context_fabric_v1_payload(task_id='fabric-smoke-1')
assert api.get('ok'), api
assert api.get('schema') == 'semantic-context-fabric-v1'
assert api.get('stateless') is True

print(
    'PASS semantic context fabric v1',
    'd1_ready', pre['d1_code_intelligence']['ready'],
    'd5_ready', pre['d5_vector_retrieval']['ready'],
    'runtime_handles', len(runtime),
)
"

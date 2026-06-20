#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
import inspect

from pre_llm.intent_engine.api import intent_engine_v1_payload
from pre_llm.intent_engine.intent_engine import run_intent_engine
from pre_llm.intent_engine.store import INTENT_SSOT_PATH, SCHEMA

import pre_llm.intent_engine.intent_engine as ie
src = inspect.getsource(ie)
for forbidden in ('openai', 'openrouter', 'anthropic', 'embeddings', 'pgvector', 'requests.post'):
    assert forbidden not in src.lower(), f'forbidden in D4: {forbidden}'

TASK = 'intent-engine-smoke-1'
FIX_TEXT = 'fix the dependency graph validator failing on file_edges'
BUILD_TEXT = 'build D4 intent engine with goal classification'
VAGUE_TEXT = 'it'

live = run_intent_engine(text=BUILD_TEXT, task_id=TASK, force_refresh=True)
assert live.get('ok'), live
assert live.get('schema') == SCHEMA
assert INTENT_SSOT_PATH.is_file(), 'intent_engine_v1.json missing'
assert live.get('intent_ready') is True, live
assert live.get('goal_class') == 'build', live

fix = run_intent_engine(text=FIX_TEXT, task_id=TASK + '-fix', force_refresh=True)
assert fix.get('goal_class') == 'fix', fix
assert fix.get('decomposition_tree'), 'decomposition tree required'
assert any(s.get('id') == 'assess_impact' for s in fix['decomposition_tree'])

vague = run_intent_engine(text=VAGUE_TEXT, task_id=TASK + '-vague', force_refresh=True)
assert vague.get('needs_clarification') is True, vague
assert vague.get('goal_class') == 'other', vague

api = intent_engine_v1_payload(text=BUILD_TEXT, task_id=TASK, query_type='tree')
assert api.get('ok'), api
qr = api.get('query_result') or {}
assert qr.get('decomposition_tree'), qr
pkt = api.get('packet_intent') or {}
assert pkt.get('goal_class') == 'build'
assert pkt.get('producer') == 'D4'

d3_ref = live.get('d3_ref') or {}
assert d3_ref.get('schema') == 'dependency-graph-v1', 'must reference D3 substrate'

print('PASS intent engine v1', 'goal_class', live.get('goal_class'), 'confidence', live.get('confidence'))
"

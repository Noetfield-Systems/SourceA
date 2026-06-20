#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
import inspect
from pre_llm.code_intelligence.api import code_intelligence_v1_payload
from pre_llm.code_intelligence.index_builder import run_full_index
from pre_llm.code_intelligence.store import CODE_INTEL_SSOT_PATH, SCHEMA, MANDATORY_EXTENSIONS
from pre_llm.code_intelligence.query_engine import run_query

# Law: no forbidden semantic layers in D1 package surface
import pre_llm.code_intelligence.index_builder as ib
import pre_llm.code_intelligence.store as st
for mod in (ib, st):
    src = inspect.getsource(mod)
    for forbidden in ('openai', 'embeddings', 'pgvector', 'def rank', 'def retrieve'):
        assert forbidden not in src, f'forbidden in D1: {forbidden}'

assert '.py' in MANDATORY_EXTENSIONS

TASK = 'code-intel-smoke-1'
live = run_full_index(task_id=TASK, force_refresh=True)
assert live.get('ok'), live
assert live.get('schema') == SCHEMA
assert CODE_INTEL_SSOT_PATH.is_file(), 'code_intelligence_v1.json missing'

stats = live.get('index_stats') or {}
assert stats.get('files', 0) > 0, 'files > 0 required'
assert stats.get('symbols', 0) > 0, 'symbols > 0 required'
assert stats.get('edges', 0) > 0, 'import graph edges required'
assert live.get('query_layer_ready') is True

files = live.get('files') or []
py_files = [f for f in files if f.get('language') == 'python']
assert py_files, 'python files required'
assert any(f.get('ast_hash') for f in py_files), 'AST parsed (ast_hash) required'

ig = live.get('imports_graph') or []
assert ig and all('from' in e and 'to' in e and 'type' in e for e in ig[:5])

symbols = live.get('symbols') or {}
assert symbols and all('type' in v and 'file' in v for v in list(symbols.values())[:5])

who = run_query(query_type='who_calls', arg='run_full_index', canonical=live)
assert who.get('query') == 'who_calls'

api = code_intelligence_v1_payload(task_id=TASK, query_type='find_symbol', query_arg='run_full_index')
assert api.get('ok'), api
assert api.get('schema') == SCHEMA
assert api.get('query_layer_ready') is True
assert api.get('index_stats', {}).get('symbols', 0) > 0
assert api.get('query_result', {}).get('hit_count', 0) >= 1

print(
    'PASS code intelligence v1',
    'files', stats.get('files'),
    'symbols', stats.get('symbols'),
    'edges', stats.get('edges'),
)
"

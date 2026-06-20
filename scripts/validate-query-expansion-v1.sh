#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import inspect

from pre_llm.query_expansion.api import query_expansion_v1_payload
from pre_llm.query_expansion.expansion_engine import run_query_expansion
from pre_llm.query_expansion.store import EXPANSION_SSOT_PATH, SCHEMA

import pre_llm.query_expansion.expansion_engine as ee
src = inspect.getsource(ee)
for forbidden in ("openai", "openrouter", "anthropic", "embeddings", "requests.post"):
    assert forbidden not in src.lower(), f"forbidden in D7: {forbidden}"

BUILD = "ship D7 query expansion intent retrieval plan symbols validate_packet"
live = run_query_expansion(text=BUILD, task_id="validate-d7", force_refresh=True)
assert live.get("ok"), live
assert live.get("schema") == SCHEMA
assert EXPANSION_SSOT_PATH.is_file(), "query_expansion_v1.json missing"
assert live.get("expansion_ready"), live
assert live.get("query_count", 0) >= 3, f"too few queries: {live.get('query_count')}"
assert live.get("goal_class") == "build", live

plan = live.get("retrieval_plan") or {}
assert plan.get("schema") == "retrieval-plan-v1"
assert plan.get("fuse", {}).get("method") == "rrf"
assert len(plan.get("stages") or []) >= 2

queries = live.get("queries") or []
modes = {q.get("mode") for q in queries}
assert "hybrid" in modes or "dense" in modes
assert any(q.get("source") == "goal_template" for q in queries)
assert any(q.get("source") == "d4_decomposition" for q in queries)

api = query_expansion_v1_payload(text=BUILD, task_id="validate-d7-api")
assert api.get("ok"), api
pr = api.get("packet_retrieval") or {}
assert len(pr.get("queries") or []) >= 3
assert pr.get("retrieval_plan")

print(
    "PASS query expansion v1",
    "queries",
    live.get("query_count"),
    "symbols",
    live.get("symbol_count"),
    "goal",
    live.get("goal_class"),
)
PY

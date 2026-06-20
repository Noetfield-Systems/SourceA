#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import inspect

from pre_llm.context_ranking.api import context_ranking_v1_payload
from pre_llm.context_ranking.ranking_engine import run_context_ranking
from pre_llm.context_ranking.store import RANKING_SSOT_PATH, SCHEMA

import pre_llm.context_ranking.ranking_engine as re_mod
src = inspect.getsource(re_mod)
for forbidden in ("openai", "openrouter", "anthropic", "requests.post"):
    assert forbidden not in src.lower(), f"forbidden in D9: {forbidden}"

QUERY = "ship D9 context ranking pre-LLM gate ranked evidence validate_packet"
live = run_context_ranking(text=QUERY, task_id="validate-d9", force_refresh=True, top_k=12)
assert live.get("ok"), live
assert live.get("schema") == SCHEMA
assert RANKING_SSOT_PATH.is_file(), "context_ranking_v1.json missing"
assert live.get("ranking_ready"), live
assert live.get("ranked_count", 0) >= 3, f"too few ranked: {live.get('ranked_count')}"

ranked = live.get("ranked_evidence") or []
assert ranked[0].get("rank") == 1
assert all(r.get("score", 0) > 0 for r in ranked)
sources = {r.get("source_step") for r in ranked}
assert "D5" in sources, sources

api = context_ranking_v1_payload(text=QUERY, task_id="validate-d9-api")
assert api.get("ok"), api
pr = api.get("packet_ranking") or {}
assert len(pr.get("ranked_evidence") or []) >= 3
assert pr.get("producer") == "D9"

print(
    "PASS context ranking v1",
    "ranked",
    live.get("ranked_count"),
    "goal",
    live.get("goal_class"),
    "sources",
    sorted(sources),
)
PY

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import inspect

from pre_llm.planning_engine.api import planning_engine_v1_payload
from pre_llm.planning_engine.planning_engine import run_planning_engine
from pre_llm.planning_engine.store import PLANNING_SSOT_PATH, SCHEMA

import pre_llm.planning_engine.planning_engine as pe
src = inspect.getsource(pe)
for forbidden in ("openai", "openrouter", "anthropic", "requests.post"):
    assert forbidden not in src.lower(), f"forbidden in D10: {forbidden}"

QUERY = "ship D10 planning engine semantic plan graph validate_packet pre-LLM"
live = run_planning_engine(text=QUERY, task_id="validate-d10", force_refresh=True)
assert live.get("ok"), live
assert live.get("schema") == SCHEMA
assert PLANNING_SSOT_PATH.is_file(), "planning_engine_v1.json missing"
assert live.get("plan_ready"), live
assert live.get("node_count", 0) >= 3, f"too few nodes: {live.get('node_count')}"
assert live.get("edge_count", 0) >= 2, f"too few edges: {live.get('edge_count')}"

graph = live.get("graph") or {}
nodes = graph.get("nodes") or []
edges = graph.get("edges") or []
assert live.get("goal_class") == "build", live.get("goal_class")
assert any(n.get("kind") == "fallback" for n in nodes), "fallback node missing"
assert any(e.get("kind") == "sequential" for e in edges)
assert any(n.get("evidence_refs") for n in nodes if n.get("kind") != "fallback")

api = planning_engine_v1_payload(text=QUERY, task_id="validate-d10-api")
assert api.get("ok"), api
pp = api.get("packet_plan") or {}
g = pp.get("graph") or {}
assert len(g.get("nodes") or []) >= 3
assert pp.get("producer") == "D10"

print(
    "PASS planning engine v1",
    "nodes",
    live.get("node_count"),
    "edges",
    live.get("edge_count"),
    "goal",
    live.get("goal_class"),
)
PY

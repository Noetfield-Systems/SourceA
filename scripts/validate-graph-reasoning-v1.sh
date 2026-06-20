#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import inspect

from pre_llm.graph_reasoning.api import graph_reasoning_v1_payload
from pre_llm.graph_reasoning.reasoning_engine import run_graph_reasoning
from pre_llm.graph_reasoning.store import REASONING_SSOT_PATH, SCHEMA

import pre_llm.graph_reasoning.reasoning_engine as re_mod
src = inspect.getsource(re_mod)
for forbidden in ("openai", "openrouter", "anthropic", "requests.post"):
    assert forbidden not in src.lower(), f"forbidden in D8: {forbidden}"

TARGET = "scripts/pre_llm/context_packet/schema.py"
TEXT = f"D8 graph reasoning root cause impact traversal {TARGET}"
live = run_graph_reasoning(
    text=TEXT,
    target=TARGET,
    target_type="file",
    task_id="validate-d8",
    force_refresh=True,
)
assert live.get("ok"), live
assert live.get("schema") == SCHEMA
assert REASONING_SSOT_PATH.is_file(), "graph_reasoning_v1.json missing"
assert live.get("reasoning_ready"), live
assert live.get("path_count", 0) >= 2, f"too few paths: {live.get('path_count')}"

paths = live.get("paths") or []
kinds = {p.get("kind") for p in paths}
assert "impact" in kinds, kinds
assert "root_cause" in kinds or "traversal" in kinds, kinds
assert any(p.get("node_count", 0) >= 1 for p in paths)

api = graph_reasoning_v1_payload(text=TEXT, target=TARGET, task_id="validate-d8-api")
assert api.get("ok"), api
pr = api.get("packet_reasoning") or {}
assert len(pr.get("paths") or []) >= 2
assert pr.get("producer") == "D8"

print(
    "PASS graph reasoning v1",
    "paths",
    live.get("path_count"),
    "kinds",
    sorted(kinds),
)
PY

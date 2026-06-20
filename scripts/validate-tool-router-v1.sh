#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import inspect

from pre_llm.tool_router.api import tool_router_v1_payload
from pre_llm.tool_router.router_engine import run_tool_router
from pre_llm.tool_router.store import ROUTER_SSOT_PATH, SCHEMA

import pre_llm.tool_router.router_engine as re_mod
src = inspect.getsource(re_mod)
for forbidden in ("openai", "openrouter", "anthropic", "requests.post"):
    assert forbidden not in src.lower(), f"forbidden in D11: {forbidden}"

QUERY = "ship D11 tool router policy cost capability selection validate_packet"
live = run_tool_router(text=QUERY, task_id="validate-d11", force_refresh=True)
assert live.get("ok"), live
assert live.get("schema") == SCHEMA
assert ROUTER_SSOT_PATH.is_file(), "tool_router_v1.json missing"
assert live.get("router_ready"), live
assert live.get("selection_count", 0) >= 3, live
assert live.get("allowed_count", 0) >= 2, live

selection = live.get("selection") or []
perms = {s.get("permission") for s in selection}
assert "read" in perms
assert all(s.get("policy_gate") for s in selection)
assert any(s.get("cost_estimate", 0) > 0 for s in selection)
blocked = [s for s in selection if not s.get("allowed")]
assert blocked, "expected some policy-blocked execute tools"

api = tool_router_v1_payload(text=QUERY, task_id="validate-d11-api")
assert api.get("ok"), api
pt = api.get("packet_tools") or {}
assert len(pt.get("selection") or []) >= 3
assert pt.get("producer") == "D11"

print(
    "PASS tool router v1",
    "selection",
    live.get("selection_count"),
    "allowed",
    live.get("allowed_count"),
    "cost",
    live.get("total_cost_estimate"),
)
PY

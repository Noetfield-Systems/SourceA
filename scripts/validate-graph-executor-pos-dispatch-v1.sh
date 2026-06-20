#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
import urllib.request

from runtime.graph_executor.executor_engine import run_graph_executor
from runtime.graph_executor.spine_bridge import build_spine_bridge
from runtime.orchestrator.orchestrator_engine import run_runtime_orchestration

TASK = "pos-dispatch-smoke-1"
GOAL = "pos-run"

run_runtime_orchestration(goal_tool_id=GOAL, task_id=TASK)
bridge = build_spine_bridge(goal_tool_id=GOAL, task_id=TASK)
run_graph_executor(goal_tool_id=GOAL, task_id=TASK)
assert bridge.get("ok"), bridge
assert bridge.get("dispatch_ready") is False, bridge
assert bridge.get("auto_dispatch") is False, bridge
assert bridge.get("founder_confirm_required") is True, bridge
assert bridge.get("instruction", {}).get("action") != "auto_dispatch_approved", bridge

first = bridge.get("first_action_id") or ""
if first == "pos-dispatch":
    assert bridge.get("policy_class") == "suggest", bridge
    assert bridge.get("planner_auto_bridge_ready") is False, bridge
    assert bridge.get("instruction", {}).get("action") == "founder_confirm_required", bridge

with urllib.request.urlopen("http://127.0.0.1:13020/api/graph-executor-v1", timeout=90) as resp:
    api = json.loads(resp.read().decode())
assert api.get("ok"), api
assert api.get("auto_dispatch") is False, api
assert api.get("dispatch_ready") is False, api
if api.get("first_action_id") == "pos-dispatch":
    assert api.get("policy_class") == "suggest", api
print(
    "OK: validate-graph-executor-pos-dispatch-v1 · first_action",
    api.get("first_action_id"),
    "policy_class",
    api.get("policy_class"),
)
PY

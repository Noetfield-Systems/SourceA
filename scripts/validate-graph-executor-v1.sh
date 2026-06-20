#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
import urllib.request

from runtime.orchestrator.orchestrator_engine import run_runtime_orchestration
from runtime.graph_executor.executor_engine import run_graph_executor, EXECUTOR_SSOT_PATH

run_runtime_orchestration(goal_tool_id="pos-run", task_id="graph-exec-smoke-1")
bridge = run_graph_executor(goal_tool_id="pos-run", task_id="graph-exec-smoke-1")
assert bridge.get("schema") == "graph-executor-v1", bridge
assert bridge.get("ok"), bridge
assert bridge.get("dispatch_ready") is False, bridge
assert EXECUTOR_SSOT_PATH.is_file(), "graph_executor_v1.json missing"
assert "policy_class" in bridge, bridge

with urllib.request.urlopen("http://127.0.0.1:13020/api/graph-executor-v1", timeout=90) as resp:
    api = json.loads(resp.read().decode())
assert api.get("ok"), api
from runtime.dispatch_policy.policy_engine import dispatch_policy_payload

policy = dispatch_policy_payload()
assert api.get("eval_1b_gate_ok") == policy.get("eval_1b_gate_ok"), (api, policy)
assert api.get("founder_spine_bridge_gate_ok") is True, api
assert api.get("spine_bridge_ready") is True, api
print("OK: validate-graph-executor-v1 · bridge_ready", api.get("spine_bridge_ready"))
PY

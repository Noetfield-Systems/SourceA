#!/usr/bin/env bash
# graph-executor eval_1b_gate_ok must match dispatch-policy (strict live gate).
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
import urllib.request

from runtime.dispatch_policy.policy_engine import dispatch_policy_payload
from runtime.graph_executor.executor_engine import run_graph_executor
from runtime.orchestrator.orchestrator_engine import run_runtime_orchestration

run_runtime_orchestration(goal_tool_id="pos-run", task_id="gate-honesty-smoke")
bridge = run_graph_executor(goal_tool_id="pos-run", task_id="gate-honesty-smoke")
policy = dispatch_policy_payload()
strict = bool(policy.get("eval_1b_gate_ok"))
bridge_strict = bool(bridge.get("eval_1b_gate_ok"))
assert bridge_strict == strict, (
    f"graph-executor eval_1b_gate_ok={bridge_strict} != dispatch-policy {strict}"
)

with urllib.request.urlopen("http://127.0.0.1:13020/api/graph-executor-v1", timeout=90) as resp:
    api = json.loads(resp.read().decode())
with urllib.request.urlopen("http://127.0.0.1:13020/api/dispatch-policy-v1", timeout=90) as resp:
    api_policy = json.loads(resp.read().decode())

assert api.get("eval_1b_gate_ok") == api_policy.get("eval_1b_gate_ok"), (api, api_policy)
assert api.get("dispatch_ready") is False, api
assert "founder_spine_bridge_gate_ok" in api, api
print(
    "OK: validate-graph-executor-gate-honesty-v1 · "
    f"eval_1b_gate_ok={strict} founder_bridge={api.get('founder_spine_bridge_gate_ok')}"
)
PY

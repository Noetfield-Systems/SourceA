#!/usr/bin/env bash
# Founder spine bridge — eval proof via spine-smoke-echo when gate open (sa-0416)
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
import urllib.request

from runtime.graph_executor.spine_bridge import build_spine_bridge
from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready

exp_ready, exp_blockers, _ = orchestrator_dispatch_ready()
bridge = build_spine_bridge()
assert bridge.get("ok"), bridge
assert bridge.get("founder_spine_bridge_gate_ok"), bridge.get(
    "founder_spine_bridge_note", "Founder spine bridge gate closed"
)
assert bool(bridge.get("orchestrator_dispatch_ready")) == exp_ready, (
    bridge.get("orchestrator_dispatch_ready"),
    exp_blockers,
)
assert bridge.get("dispatch_ready") is False, bridge
proof = bridge.get("eval_proof_bridge") or {}
assert proof.get("spine_bridge_ready"), proof

with urllib.request.urlopen("http://127.0.0.1:13020/api/graph-executor-v1", timeout=60) as resp:
    api = json.loads(resp.read().decode())
assert api.get("ok"), api
assert api.get("founder_spine_bridge_gate_ok"), api
print("OK: validate-spine-bridge-founder-v1 · proof", proof.get("action_id"))
PY

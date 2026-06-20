#!/usr/bin/env bash
# validate-spine-bridge-proof-matrix-v1.sh — sa-0973 ACT proof types matrix crosswalk
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
import urllib.request
from pathlib import Path

from runtime.dispatch_policy.policy_engine import LAW_LAYER1_CLASSES, founder_spine_bridge_gate_status, eval_1b_gate_status, orchestrator_dispatch_ready
from runtime.graph_executor.spine_bridge import build_spine_bridge
from runtime.dispatch_policy.classifier import LOW_RISK_ACTIONS

ROOT = Path(__file__).resolve().parents[1]
law = ROOT / "brain-os" / "law" / "DISPATCH_POLICY_LOCKED_v1.md"
assert law.is_file(), "DISPATCH_POLICY_LOCKED_v1.md missing"

bridge = build_spine_bridge()
assert bridge.get("ok"), bridge

# Matrix fields must exist on every bridge payload
for key in (
    "eval_1b_gate_ok",
    "founder_spine_bridge_gate_ok",
    "policy_class",
    "instruction",
    "eval_proof_bridge",
    "dispatch_ready",
    "founder_confirm_required",
    "planner_bridge_ready",
    "spine_bridge_ready",
):
    assert key in bridge, f"bridge missing matrix field {key!r}"

exp_ready, exp_blockers, _ = orchestrator_dispatch_ready()
assert bool(bridge.get("dispatch_ready")) == exp_ready, (
    f"dispatch_ready={bridge.get('dispatch_ready')!r} expected {exp_ready!r} blockers={exp_blockers}"
)
assert list(bridge.get("dispatch_ready_blockers") or []) == exp_blockers, bridge
assert bridge.get("auto_dispatch") is False, "auto_dispatch must be false"
assert bridge.get("founder_confirm_required") is True, "founder_confirm_required must be true"

policy = bridge.get("policy_class") or ""
assert policy in LAW_LAYER1_CLASSES, f"policy_class {policy!r} not in Layer-1 law"

proof = bridge.get("eval_proof_bridge") or {}
assert proof.get("action_id") == "spine-smoke-echo", proof
assert proof.get("policy_class") == "auto_low_risk", proof
assert "spine_bridge_ready" in proof, proof
assert proof.get("enqueue_spec"), "eval proof must ship enqueue_spec"

instr = bridge.get("instruction") or {}
assert instr.get("action") in (
    "founder_confirm_required",
    "founder_confirm_then_enqueue_spine",
    "blocked_or_review",
), instr

assert "spine-smoke-echo" in LOW_RISK_ACTIONS, "smoke echo must be low-risk action"

eval_ok, eval_note = eval_1b_gate_status()
founder_ok, founder_note = founder_spine_bridge_gate_status()
assert bridge.get("eval_1b_gate_ok") == eval_ok
assert bridge.get("founder_spine_bridge_gate_ok") == founder_ok

# Graph executor API mirrors gate fields when reachable
try:
    with urllib.request.urlopen("http://127.0.0.1:13020/api/graph-executor-v1", timeout=30) as resp:
        api = json.loads(resp.read().decode())
    if api.get("ok"):
        assert "founder_spine_bridge_gate_ok" in api, api
        assert bool(api.get("dispatch_ready")) == exp_ready, (
            f"API dispatch_ready={api.get('dispatch_ready')!r} expected {exp_ready!r}"
        )
except Exception as exc:
    raise AssertionError(f"graph-executor-v1 unreachable: {exc}") from exc

src = Path("runtime/graph_executor/spine_bridge.py").read_text(encoding="utf-8")
assert "eval_proof_bridge" in src and "dispatch_ready" in src, "spine_bridge SSOT markers"

print(
    "OK: validate-spine-bridge-proof-matrix-v1 · "
    f"policy={policy} eval_gate={eval_ok} founder_gate={founder_ok} · "
    f"proof={proof.get('action_id')} dispatch_ready={exp_ready} · sa-0973"
)
PY

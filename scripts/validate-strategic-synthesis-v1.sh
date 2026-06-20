#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
python3 - <<'PY'
from pathlib import Path
from strategic_synthesis_hub import strategic_synthesis_payload
from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready

p = strategic_synthesis_payload()
assert p.get("ok"), "STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md missing"
assert len(p.get("strategic_goals") or []) >= 3, "goals"
assert len(p.get("next_plans") or []) >= 5, "next_plans"
assert len(p.get("pendings") or []) >= 8, "pendings"
gates = p.get("machine_gates") or {}
exp_ready, exp_blockers, _ = orchestrator_dispatch_ready()
assert bool(gates.get("dispatch_ready")) == exp_ready, (gates, exp_blockers)
bottleneck = p.get("bottleneck") or ""
assert "dispatch_ready=" in bottleneck.lower(), bottleneck
eval_ok = bool(gates.get("eval_1b_gate_ok"))
one = p.get("one_line") or ""
if eval_ok:
    assert "eval_1b_gate_ok=true" in one, one
else:
    assert "eval_1b_gate_ok=false" in one, one
eval_plan = next((x for x in (p.get("next_plans") or []) if x.get("id") == "eval-1b"), {})
if eval_ok:
    assert eval_plan.get("status") == "done", eval_plan
else:
    assert eval_plan.get("status") == "in_progress", eval_plan
print("OK: validate-strategic-synthesis-v1")
PY

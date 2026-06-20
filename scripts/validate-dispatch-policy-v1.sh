#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
import urllib.request
from pathlib import Path

from runtime.dispatch_policy.policy_engine import (
    current_eval_tier,
    dispatch_policy_payload,
    evaluate,
    evaluate_action,
)

# ── Hub payload + activation gates v1.1 ─────────────────────────────────────
payload = dispatch_policy_payload()
from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready

exp_ready, exp_blockers, _ = orchestrator_dispatch_ready()
assert payload.get("schema") == "dispatch-policy-v1", payload
assert payload.get("classes"), payload
assert bool(payload.get("dispatch_ready")) == exp_ready, (
    payload.get("dispatch_ready"),
    exp_blockers,
)
assert payload.get("dispatch_ready_blockers") == exp_blockers, payload
assert "eval_1b_gate_ok" in payload, payload
assert "eval_1b_note" in payload, payload
assert payload.get("current_eval_tier") in ("none", "structural", "behavioral_pass", "behavioral_fail"), payload
assert payload.get("allowlist_version") == "v1", payload
assert payload.get("last_decision"), payload

import model_dispatch

gate_disk = model_dispatch.current_gate_mode()
assert payload.get("gate_mode") == gate_disk, payload.get("gate_mode")
assert payload.get("current_gate_mode") == gate_disk, payload.get("current_gate_mode")
assert payload.get("gate_is_enforce") == (gate_disk == "enforce"), payload.get("gate_is_enforce")

rep_path = Path.home() / ".sina" / "eval_packet_v1b_report.json"
if rep_path.is_file():
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    ci_path = Path.home() / ".sina" / "eval_1b_ci_mode_v1.json"
    structural = False
    if ci_path.is_file():
        structural = bool(json.loads(ci_path.read_text()).get("structural_fallback"))
    if rep.get("mode") == "live" and rep.get("live_ok") and not structural:
        assert payload.get("eval_1b_gate_ok") is True, (payload.get("eval_1b_note"), rep)
    elif structural or rep.get("mode") != "live" or not rep.get("live_ok"):
        assert payload.get("eval_1b_gate_ok") is False, payload

ev = evaluate_action("spine-smoke-echo")
assert ev.get("policy_class") == "auto_low_risk", ev
assert ev.get("eval_1b_gate_ok") == payload.get("eval_1b_gate_ok"), (ev, payload)

# ── V-dispatch-01 SAFE_AUTO dispatches when graph approved ──────────────────
approve_graph = {
    "recommendation": "approve",
    "plan_score": 0.9,
    "has_cycles": False,
    "violations": [],
}
allow_router = {
    "routing_decision": "allow",
    "confidence": 0.9,
    "blocking_reason": None,
}
d1 = evaluate(
    verified_graph=approve_graph,
    router=allow_router,
    eval_tier="structural",
    task_class="validate-only",
)
assert d1["dispatch_ready"] is True, d1
assert d1["reason"] == "allowlist_safe_task", d1
print("V-dispatch-01 PASS: validate-only → dispatch_ready True")

# ── V-dispatch-02 BEHAVIORAL blocks without behavioral_pass ─────────────────
d2 = evaluate(
    verified_graph=approve_graph,
    router=allow_router,
    eval_tier="structural",
    task_class="file-write",
)
assert d2["dispatch_ready"] is False, d2
assert d2["reason"] == "behavioral_proof_required", d2
print("V-dispatch-02 PASS: file-write + structural → blocked")

# ── V-dispatch-03 graph reject always blocks ────────────────────────────────
d3 = evaluate(
    verified_graph={
        "recommendation": "reject",
        "plan_score": 0.1,
        "has_cycles": True,
        "violations": ["cycle"],
    },
    router=allow_router,
    eval_tier="behavioral_pass",
    task_class="validate-only",
)
assert d3["dispatch_ready"] is False, d3
assert d3["reason"] == "graph_rejected", d3
print("V-dispatch-03 PASS: rejected graph → blocked")

# ── V-dispatch-04 API live ──────────────────────────────────────────────────
with urllib.request.urlopen("http://127.0.0.1:13020/api/dispatch-policy-v1", timeout=60) as resp:
    api_hub = json.loads(resp.read().decode())
assert api_hub.get("ok"), api_hub
assert api_hub.get("dispatch_ready") == exp_ready, api_hub
assert api_hub.get("eval_1b_gate_ok") == payload.get("eval_1b_gate_ok"), api_hub
assert api_hub.get("gate_mode") == gate_disk, api_hub.get("gate_mode")
assert api_hub.get("current_gate_mode") == gate_disk, api_hub.get("current_gate_mode")

with urllib.request.urlopen(
    "http://127.0.0.1:13020/api/dispatch-policy-v1?task_class=validate-only&eval_tier=structural",
    timeout=60,
) as resp:
    api_eval = json.loads(resp.read().decode())
assert "dispatch_ready" in api_eval, api_eval
assert api_eval.get("decision"), api_eval
assert api_eval["decision"].get("task_class") == "validate-only", api_eval
print("V-dispatch-04 PASS: GET /api/dispatch-policy-v1 → 200")

# ── V-dispatch-05 hub dispatch_ready matches activation gates ───────────────
assert api_hub.get("dispatch_ready") == exp_ready, api_hub
assert api_eval.get("dispatch_ready") == exp_ready, api_eval
assert api_eval.get("schema") == "dispatch-policy-api-v1", api_eval
print(f"V-dispatch-05 PASS: hub dispatch_ready={exp_ready} (activation gates)")

# ── V-dispatch-06 orchestrator shadow dry_run ───────────────────────────────
from runtime.orchestrator.orchestrator_engine import run_runtime_orchestration

orch = run_runtime_orchestration(goal_tool_id="pos-run", task_id="v-dispatch-06")
assert bool(orch.get("dispatch_ready")) == exp_ready, orch
dec = orch.get("dispatch_decision") or {}
assert dec.get("schema") == "dispatch-policy-v1", dec
assert dec.get("dry_run") is True, dec
print("V-dispatch-06 PASS: orchestrator shadow dry_run=true")

# ── V-dispatch-07 dual-layer alignment ────────────────────────────────────────
alignment = payload.get("alignment") or {}
assert alignment.get("mapping_ok") is True, alignment
print("V-dispatch-07 PASS: dual_layer classifier alignment mapping_ok=true")

# ── V-dispatch-08 eval_1b_gate honest ─────────────────────────────────────────
ci_path = Path.home() / ".sina" / "eval_1b_ci_mode_v1.json"
if ci_path.is_file():
    ci = json.loads(ci_path.read_text(encoding="utf-8"))
    if ci.get("mode") == "structural_only" or ci.get("structural_fallback"):
        assert payload.get("eval_1b_gate_ok") is False, (payload, ci)
print(f"V-dispatch-08 PASS: eval_1b_gate_ok={payload.get('eval_1b_gate_ok')} honest")

tier = current_eval_tier()
print(
    f"OK: validate-dispatch-policy-v1 · gate_ok={payload.get('eval_1b_gate_ok')} "
    f"mode={payload.get('eval_1b_mode')} ci={payload.get('eval_1b_ci_mode')} "
    f"eval_tier={tier}"
)
PY

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
export SINA_GATE_MODE=enforce
python3 - <<'PY'
import json

import model_dispatch as md

blocked = md.gate_decision(
    {"gate_eligible": False, "readiness_score": 0.5, "missing_for_gate": ["constraints"]}
)
assert blocked.get("allowed") is False, blocked
assert blocked.get("mode") == "enforce"
assert blocked.get("reason") == "gate_eligible_false"

allowed = md.gate_decision(
    {"gate_eligible": True, "readiness_score": 1.0, "missing_for_gate": []}
)
assert allowed.get("allowed") is True, allowed
assert allowed.get("reason") == "gate_pass"

QUERY = "ship D15 context assembly gate eligible llm_context_packet pre-LLM"
prep = md.prepare_packet(task_id="enforce-validate", query_text=QUERY)
val = prep["validation"]
assert val.get("gate_eligible") is True, val

out = md.dispatch_chat(
    system="test",
    user=QUERY,
    chat_fn=lambda s, u: (True, "pong"),
    task_id="enforce-validate",
    source="validate-enforce-script",
)
assert out.get("ok") and out.get("response") == "pong"
assert out.get("blocked") is False
assert out.get("gate", {}).get("mode") == "enforce"

assert md.GATE_SSOT_PATH.is_file(), "model_dispatch_gate_v1.json missing"
ssot = json.loads(md.GATE_SSOT_PATH.read_text())
assert ssot.get("latest", {}).get("current_mode") == "enforce"
assert ssot.get("schema") == md.GATE_SCHEMA

print(
    "PASS model gate enforce v1",
    "readiness",
    val.get("readiness_score"),
    "gate_eligible",
    val.get("gate_eligible"),
)
PY

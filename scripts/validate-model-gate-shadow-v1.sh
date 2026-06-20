#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
export SINA_GATE_MODE=shadow
python3 - <<'PY'
import model_dispatch as md

prep = md.prepare_packet(task_id="shadow-validate", query_text="build D5 vector retrieval")
val = prep["validation"]
assert "readiness_score" in val
dec = md.gate_decision(val)
assert dec.get("allowed") is True, "shadow must allow model"
assert dec.get("mode") == "shadow"
out = md.dispatch_chat(
    system="test",
    user="ping",
    chat_fn=lambda s, u: (True, "pong"),
    task_id="shadow-validate",
    source="validate-script",
)
assert out.get("ok") and out.get("response") == "pong"
assert md.SHADOW_LOG.is_file(), "gate_shadow_v1.jsonl missing"
assert md.GATE_SSOT_PATH.is_file(), "model_dispatch_gate_v1.json missing"
status = md.gate_status_payload(task_id="shadow-status", query_text="build D5 vector retrieval")
assert status.get("ok") and status.get("producer") == "D15.1"
print("PASS model gate shadow v1", "readiness", val.get("readiness_score"))
PY

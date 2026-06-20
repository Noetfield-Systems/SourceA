#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import inspect

from pre_llm.context_assembly.api import context_assembly_v1_payload
from pre_llm.context_assembly.assembly_engine import run_context_assembly
from pre_llm.context_packet.schema import PACKET_SSOT_PATH, SCHEMA, validate_packet

import pre_llm.context_assembly.assembly_engine as ae
src = inspect.getsource(ae)
for forbidden in ("openai", "openrouter", "anthropic", "requests.post"):
    assert forbidden not in src.lower(), f"forbidden in D15: {forbidden}"

QUERY = "ship D15 context assembly gate eligible llm_context_packet pre-LLM world model"
live = run_context_assembly(text=QUERY, task_id="validate-d15", force_refresh=True)
assert live.get("ok"), live
assert PACKET_SSOT_PATH.is_file(), "llm_context_packet_v1.json missing"

pkt = live.get("packet") or {}
assert pkt.get("schema") == SCHEMA
val = live.get("validation") or validate_packet(pkt)
assert val.get("gate_eligible") is True, val
assert float(val.get("readiness_score") or 0) >= 1.0, val

assert (pkt.get("constraints") or {}).get("policy_refs"), "constraints.policy_refs required"
assert (pkt.get("compressed_context") or {}).get("narrative", "").strip()
assert (pkt.get("provenance") or {}).get("producer_steps")
assert "D15" in (pkt.get("provenance") or {}).get("producer_steps", [])

asm = live.get("assembly") or {}
assert asm.get("assembly_ready") is True

api = context_assembly_v1_payload(text=QUERY, task_id="validate-d15-api")
assert api.get("ok"), api
assert api.get("gate_eligible") is True
assert api.get("producer") == "D15"

print(
    "PASS context assembly v1",
    "readiness",
    val.get("readiness_score"),
    "gate_eligible",
    val.get("gate_eligible"),
    "producers",
    len((pkt.get("provenance") or {}).get("producer_steps") or []),
)
PY

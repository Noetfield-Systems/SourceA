#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import inspect

from pre_llm.context_assembly.assembly_engine import run_context_assembly
from pre_llm.context_packet.schema import PACKET_SSOT_PATH, SCHEMA, validate_packet
from pre_llm.packet_memory_merge.api import packet_memory_merge_v1_payload
from pre_llm.packet_memory_merge.store import MERGE_SSOT_PATH

import pre_llm.packet_memory_merge.merge_engine as me
src = inspect.getsource(me)
for forbidden in ("run_context_compression", "context_ranking", "planning_engine", "openrouter"):
    assert forbidden not in src, f"D16 must not recompute pipeline: {forbidden}"

QUERY = "ship D16 unified memory merge into llm context packet gate eligible"
asm = run_context_assembly(text=QUERY, task_id="validate-d16-asm", force_refresh=True)
assert asm.get("ok"), asm
pkt = asm.get("packet") or {}
assert (pkt.get("memory") or {}).get("merge_ready") is True, "D15 chain must run D16 writeback"
assert len((pkt.get("memory") or {}).get("slots") or []) >= 1

live = packet_memory_merge_v1_payload(text=QUERY, task_id="validate-d16-api", force_refresh=True)
assert live.get("ok"), live
assert MERGE_SSOT_PATH.is_file(), "packet_memory_merge_v1.json missing"
assert live.get("producer") == "D16"
assert live.get("gate_eligible") is True, live.get("validation")

pkt2 = live.get("packet") or {}
assert pkt2.get("schema") == SCHEMA
assert "D16" in (pkt2.get("provenance") or {}).get("producer_steps", [])
mem = pkt2.get("memory") or {}
assert mem.get("merge_ready") is True
assert "D16" in (mem.get("producer") or "")
assert len(mem.get("slots") or []) >= 1
assert PACKET_SSOT_PATH.is_file()

val = live.get("validation") or validate_packet(pkt2)
assert val.get("gate_eligible") is True, val
print(
    "PASS packet memory merge v1",
    "slots",
    len(mem.get("slots") or []),
    "sources",
    mem.get("sources_merged"),
    "readiness",
    val.get("readiness_score"),
)
PY

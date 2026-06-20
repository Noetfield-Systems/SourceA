#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import inspect

from pre_llm.context_compression.api import context_compression_v1_payload
from pre_llm.context_compression.compression_engine import run_context_compression
from pre_llm.context_compression.store import COMPRESSION_SSOT_PATH, SCHEMA
from pre_llm.context_packet.schema import hydrate_from_disk_substrate, empty_packet_template, validate_packet

import pre_llm.context_compression.compression_engine as ce
src = inspect.getsource(ce)
for forbidden in ("openai", "openrouter", "anthropic", "requests.post"):
    assert forbidden not in src.lower(), f"forbidden in D14: {forbidden}"

QUERY = "ship D14 context compression token budget narrative ranked evidence pre-LLM"
live = run_context_compression(text=QUERY, task_id="validate-d14", force_refresh=True)
assert live.get("ok"), live
assert live.get("schema") == SCHEMA
assert COMPRESSION_SSOT_PATH.is_file(), "context_compression_v1.json missing"
assert live.get("compression_ready"), live

budget = live.get("budget") or {}
assert int(budget.get("token_limit") or 0) > 0
assert int(budget.get("tokens_used") or 0) > 0
assert budget.get("within_budget") is True
assert int(budget.get("evidence_out") or 0) >= 1

layers = live.get("layers") or []
assert len(layers) >= 4
assert any(l.get("layer") == "ranking" for l in layers)

narrative = (live.get("narrative") or "").strip()
assert narrative, "compressed narrative required"
assert "Goal:" in narrative
assert "Evidence:" in narrative

api = context_compression_v1_payload(text=QUERY, task_id="validate-d14-api")
assert api.get("ok"), api
pc = api.get("packet_compression") or {}
pcc = api.get("packet_compressed_context") or {}
assert pc.get("producer") == "D14"
assert pcc.get("producer") == "D14"
assert (pcc.get("narrative") or "").strip()

h = hydrate_from_disk_substrate(empty_packet_template())
v = validate_packet(h)
assert (h.get("compression") or {}).get("budget", {}).get("token_limit", 0) > 0
assert (h.get("compressed_context") or {}).get("narrative", "").strip()
print(
    "PASS context compression v1",
    "limit",
    budget.get("token_limit"),
    "used",
    budget.get("tokens_used"),
    "evidence_out",
    budget.get("evidence_out"),
    "readiness",
    v.get("readiness_score"),
)
PY

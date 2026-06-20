#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import inspect

from pre_llm.validation_layer.api import validation_layer_v1_payload
from pre_llm.validation_layer.validation_engine import run_validation_layer
from pre_llm.validation_layer.store import VALIDATION_SSOT_PATH, SCHEMA

import pre_llm.validation_layer.validation_engine as ve
src = inspect.getsource(ve)
for forbidden in ("openai", "openrouter", "anthropic", "requests.post"):
    assert forbidden not in src.lower(), f"forbidden in D12: {forbidden}"

QUERY = "ship D12 validation layer dry-run safety compile validate_packet pre-LLM"
live = run_validation_layer(text=QUERY, task_id="validate-d12", force_refresh=True)
assert live.get("ok"), live
assert live.get("schema") == SCHEMA
assert VALIDATION_SSOT_PATH.is_file(), "validation_layer_v1.json missing"
assert live.get("validation_ready"), live
assert live.get("check_count", 0) >= 8, live
assert live.get("dry_run") is True

checks = live.get("checks") or []
cats = {c.get("category") for c in checks}
assert "substrate" in cats
assert "graph_safety" in cats
assert "dry_run" in cats
assert all(c.get("status") in ("pass", "warn", "fail") for c in checks)
assert live.get("fail_count", 1) == 0, f"failures: {live.get('fail_count')}"

api = validation_layer_v1_payload(text=QUERY, task_id="validate-d12-api")
assert api.get("ok"), api
pv = api.get("packet_validation") or {}
assert len(pv.get("checks") or []) >= 8
assert pv.get("producer") == "D12"

print(
    "PASS validation layer v1",
    "checks",
    live.get("check_count"),
    "required",
    f"{live.get('required_pass')}/{live.get('required_total')}",
    "warns",
    live.get("warn_count"),
)
PY

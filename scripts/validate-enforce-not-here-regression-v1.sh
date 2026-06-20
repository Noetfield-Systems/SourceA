#!/usr/bin/env bash
# sa-0036 / sa-0086 / sa-0011 — ENFORCE-only not_here rows drop when gate_mode is enforce
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import importlib
import os

import audit_hub_source_alignment as audit
import model_dispatch
import system_roadmap
from system_roadmap import _build_world_target_map

_enforce_only = (
    "ENFORCE gate in production (shadow today)",
    "ENFORCE gate flip",
)

_prev = os.environ.get("SINA_GATE_MODE")
os.environ["SINA_GATE_MODE"] = "enforce"
importlib.reload(model_dispatch)
importlib.reload(system_roadmap)
try:
    assert system_roadmap._gate_is_enforce(), "SINA_GATE_MODE=enforce must resolve enforce"
    wtm = _build_world_target_map()
    nh = (wtm.get("honest_score") or {}).get("not_here") or []
    tgt = (wtm.get("reality_alignment") or {}).get("target") or []
    for stale in _enforce_only:
        assert not any(stale in str(line) for line in nh), (
            f"not_here stale under enforce: {stale!r} in {nh!r}"
        )
        assert not any(stale in str(line) for line in tgt), (
            f"target stale under enforce: {stale!r} in {tgt!r}"
        )

    errors: list[str] = []
    audit._check_honest_score_not_here_regression(errors, {"world_target_map": wtm})
    assert not errors, errors
finally:
    if _prev is None:
        os.environ.pop("SINA_GATE_MODE", None)
    else:
        os.environ["SINA_GATE_MODE"] = _prev
    importlib.reload(model_dispatch)
    importlib.reload(system_roadmap)

print(
    "OK: validate-enforce-not-here-regression-v1 · "
    "ENFORCE-only rows absent when gate_mode=enforce"
)
PY

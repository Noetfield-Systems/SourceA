#!/usr/bin/env bash
# sa-0037 / sa-0087 / sa-0012 — _phase_d_complete() must match D1–D16 on-disk artifacts
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import audit_hub_source_alignment as audit
from system_roadmap import _phase_d_complete, _phase_d_step_ids, _phases_def, _pre_llm_shipped_count

ship = _pre_llm_shipped_count()
pdc = _phase_d_complete()
phase_d_ids = _phase_d_step_ids(_phases_def())

assert pdc == (ship == 16), f"_phase_d_complete={pdc} vs shipped={ship}/16"
if pdc:
    assert ship == 16, f"phase_d_complete true but only {ship}/16 artifacts"
assert len(phase_d_ids) == 16, f"expected 16 phase D ids, got {len(phase_d_ids)}"

errors: list[str] = []
audit._check_phase_d_complete_artifacts_regression(errors)
assert not errors, errors

print(
    f"OK: validate-phase-d-complete-artifacts-v1 · "
    f"shipped={ship}/16 · pdc={pdc} · ids={len(phase_d_ids)}"
)
PY

#!/usr/bin/env bash
# validate-machine-three-pipelines-v1.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
fail() { echo "FAIL: validate-machine-three-pipelines-v1 — $*" >&2; exit 1; }

for s in machine_three_pipelines_lib_v1.py machine_calibrate_pipeline_v1.py machine_tune_pipeline_v1.py \
  machine_forge_pipeline_v1.py machine_three_pipelines_router_v1.py machine_upgrade_baseline_v1.py \
  refinement_unified_router_v1.py; do
  [[ -f "${ROOT}/scripts/${s}" ]] || fail "missing $s"
  python3 -m py_compile "${ROOT}/scripts/${s}" || fail "py_compile $s"
done

[[ -f "${ROOT}/REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md" ]] || fail "missing unified law"
[[ -f "${ROOT}/MACHINE_THREE_PIPELINES_CALIBRATE_TUNE_FORGE_LOCKED_v1.md" ]] || fail "missing machine law"

echo "== calibrate smoke =="
python3 "${ROOT}/scripts/machine_calibrate_pipeline_v1.py" --json >/dev/null || fail "calibrate"

[[ -f "${SINA}/machine-calibrate-receipt-v1.json" ]] || fail "calibrate receipt"

echo "OK: validate-machine-three-pipelines-v1 · calibrate smoke PASS"

#!/usr/bin/env bash
# validate-agent-runtime-mac-light-v1.sh — ship tier only · ≤90s · no network marathon (INCIDENT-039)
set -euo pipefail
cd "$(dirname "$0")/.."

started=$(date +%s)
fail=0

_run() {
  local name="$1"
  shift
  if "$@"; then
    echo "OK: $name"
  else
    echo "FAIL: $name"
    fail=1
  fi
}

_run_sh() {
  local name="$1"
  shift
  if bash "$@"; then
    echo "OK: $name"
  else
    echo "FAIL: $name"
    fail=1
  fi
}

echo "=== Agent runtime mac-light (ship tier · no network) ==="

_run_sh "bay" scripts/validate-cloud-comprehension-bay-v1.sh
_run_sh "golden" scripts/validate-comprehension-golden-v1.sh
_run_sh "ld-archive" scripts/validate-cloud-ld-drain-archive-v1.sh
_run_sh "ld-dry-run" scripts/validate-cloud-dispatch-dry-run-v1.sh
_run_sh "promotion" scripts/validate-agent-runtime-promotion-v1.sh
_run_sh "rollout" scripts/validate-agent-runtime-rollout-v1.sh
_run_sh "serialization" scripts/validate-comprehension-serialization-v1.sh
_run_sh "index" scripts/validate-agent-runtime-index-v1.sh
_run_sh "factories" scripts/validate-agent-runtime-factories-v1.sh
_run "golden-modes" python3 scripts/test_comprehension_golden_modes_v1.py

elapsed=$(( $(date +%s) - started ))
if [[ "$elapsed" -gt 90 ]]; then
  echo "FAIL: mac-light exceeded 90s (${elapsed}s)"
  fail=1
else
  echo "OK: mac-light elapsed ${elapsed}s"
fi

if [[ "$fail" -eq 0 ]]; then
  echo "PASS: validate-agent-runtime-mac-light-v1"
  exit 0
fi
echo "FAIL: validate-agent-runtime-mac-light-v1"
exit 1

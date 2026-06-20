#!/usr/bin/env bash
# worker_verify_fast_v1.sh — Worker default VERIFY (~10s). Full FCB = Safety only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: worker_verify_fast_v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/WORKER_NO_SLOW_VERIFY_SHELL_LOCKED_v1.md" ]] || fail "missing law doc"

# Permanent factory gates — auto-revert REGISTRY done without receipt; broker cycle required
bash validate-registry-honest-gate-v1.sh
bash validate-broker-receipt-cycle-v1.sh

bash validate-super-fast-hub-v1.sh
if [[ "${WORKER_VERIFY_FCB:-0}" == "1" ]]; then
  SINA_FCB_FAST=1 python3 find_critical_bugs.py >/dev/null
fi

echo "OK: worker_verify_fast_v1 · L1 tier + receipt/broker gates (set WORKER_VERIFY_FCB=1 for FCB fast add-on)"

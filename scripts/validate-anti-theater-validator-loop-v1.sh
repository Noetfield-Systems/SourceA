#!/usr/bin/env bash
# validate-anti-theater-validator-loop-v1.sh — PRO anti-theater unified loop + guard stack
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"
fail() { echo "FAIL: validate-anti-theater-validator-loop-v1 — $*" >&2; exit 1; }

test -f data/anti-theater-validator-loop-v1.json || fail "missing SSOT"
test -f scripts/anti_theater_validator_loop_v1.py || fail "missing orchestrator"

python3 scripts/anti_theater_validator_loop_v1.py --json >/dev/null || fail "loop run"
test -f "${SINA}/anti-theater-validator-loop-receipt-v1.json" || fail "missing receipt"

python3 scripts/anti_theater_validator_loop_v1.py --regression --json >/dev/null || fail "regression"

python3 - <<'PY' || fail "receipt guard checks"
import json
from pathlib import Path
row = json.loads((Path.home() / ".sina/anti-theater-validator-loop-receipt-v1.json").read_text())
assert row.get("ok") is True, row.get("violations")
ids = {c.get("id") for c in (row.get("checks") or [])}
for need in (
    "form_founder_supremacy",
    "ui_zero_drift",
    "founder_no_invitation",
    "anti_staleness_vocab",
    "mac_law_mandatory",
):
    assert need in ids, f"missing check {need}"
print(f"OK: anti-theater receipt · checks={len(ids)} · ok=True")
PY

echo "PASS: validate-anti-theater-validator-loop-v1"

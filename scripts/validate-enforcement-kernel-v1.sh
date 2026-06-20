#!/usr/bin/env bash
# validate-enforcement-kernel-v1.sh — K1 tamper-on-read + critic_boot bridge (SSOT §13 P0)
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts:$(pwd)/packages/sourcea-boot/src"

QUICK=0
[[ "${1:-}" == "--quick" ]] && QUICK=1

fail() { echo "FAIL: validate-enforcement-kernel-v1 — $*" >&2; exit 1; }

[[ -f scripts/critic_boot_v1.py ]] || fail "critic_boot missing"
[[ -f scripts/validate-demo-enforcement-v1.sh ]] || fail "demo enforcement validator missing"

python3 - <<'PY' || fail "critic_boot contract"
import json
import subprocess

proc = subprocess.run(
    ["python3", "scripts/critic_boot_v1.py", "--json", "--in-gate"],
    capture_output=True,
    text=True,
)
if not proc.stdout.strip():
    raise SystemExit(proc.stderr or "no critic_boot output")
row = json.loads(proc.stdout)
assert row.get("schema") == "critic-boot-v1"
assert row.get("verdict") in ("PASS", "BLOCK")
assert len(row.get("checks") or []) == 4
print("OK: critic_boot · 4 checks · verdict", row.get("verdict"))
PY

export PYTHONPATH="$(pwd)/packages/sourcea-boot/src:${PYTHONPATH}"
python3 -m sourcea_boot.cli --json --no-write >/dev/null 2>&1 || true
python3 - <<'PY' || fail "sourcea-boot contract"
import json
import subprocess

proc = subprocess.run(
    ["python3", "-m", "sourcea_boot.cli", "--json", "--no-write"],
    capture_output=True,
    text=True,
)
if not proc.stdout.strip():
    raise SystemExit(proc.stderr or "no sourcea-boot output")
row = json.loads(proc.stdout)
assert row.get("verdict") in ("PASS", "BLOCK")
assert len(row.get("checks") or []) == 4
print("OK: sourcea_boot.runner unified · 4 checks · verdict", row.get("verdict"))
PY

if [[ "$QUICK" -eq 1 ]]; then
  python3 - <<'PY' || fail "receipt checksum quick"
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from commit_intent_v1 import verify_receipt_checksum

latest = Path.home() / ".sina/demo-enforcement/receipts/latest-demo-receipt.json"
if latest.is_file():
    rec = json.loads(latest.read_text(encoding="utf-8"))
    if not verify_receipt_checksum(rec):
        raise SystemExit("latest receipt checksum invalid")
    print("OK: K1 quick · receipt checksum valid")
else:
    print("OK: K1 quick · no demo receipt yet (skip checksum)")
PY
  echo "OK: validate-enforcement-kernel-v1 · quick"
  exit 0
fi

bash scripts/validate-demo-enforcement-v1.sh || fail "demo enforcement base"
bash scripts/validate-demo-enforcement-v1.sh --tamper-test || fail "tamper-on-read FAIL missing"
echo "OK: validate-enforcement-kernel-v1 · K1 tamper-on-read"

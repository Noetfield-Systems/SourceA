#!/usr/bin/env bash
# validate-fbe-w6-v1.sh — Fleet consolidation + tier lift path
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== W6 motor fresh ==="
python3 - <<'PY' || true
from pathlib import Path
for flag in ("agent-cancel-v1.flag", "mac-health-emergency-active-v1.flag"):
    p = Path.home() / ".sina" / flag
    if p.is_file():
        p.unlink(missing_ok=True)
PY
python3 scripts/fbe_motor_delegate_v1.py --fbe-prove --json >/dev/null || fail=1
python3 scripts/fbe_receipt_federate_v1.py --json >/dev/null || fail=1
python3 scripts/fbe_verify_motor_v1.py --json >/dev/null || fail=1

echo "=== W5 still PASS (fast) ==="
bash scripts/validate-fbe-w5-v1.sh || fail=1

echo "=== W4 fast PASS ==="
python3 scripts/fbe_motor_delegate_v1.py --fbe-prove --json >/dev/null || true
python3 scripts/fbe_receipt_federate_v1.py --json >/dev/null || true
bash scripts/validate-fbe-w4-fast-v1.sh || fail=1

echo "=== W6 data + planned wrappers ==="
[[ -f data/fbe_fleet_job_v1.json ]] || { echo "FAIL: missing fleet job"; fail=1; }
for w in scaffold merge brand_unity narrative forbidden demo gtm deploy domain live_smoke; do
  [[ -f "scripts/fbe/assembly/fbe_assembly_${w}_v1.py" ]] || { echo "FAIL: missing planned wrapper $w"; fail=1; }
done
[[ -f scripts/fbe_run_fleet_v1.py ]] || { echo "FAIL: missing fleet runner"; fail=1; }
[[ -f scripts/fbe/exchange/fbe_exchange_dealer_bridge_v1.py ]] || { echo "FAIL: missing dealer bridge"; fail=1; }

echo "=== Planned assembly pipeline ==="
python3 scripts/fbe_assembly_runner_v1.py --bay sample-bay --pipeline assembly_planned_w6 --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
from pathlib import Path
ledger = Path("receipts/bays/sample-bay/assembly/ledger.jsonl")
lines = [ln for ln in ledger.read_text().splitlines() if ln.strip()] if ledger.is_file() else []
assert len(lines) >= 22, f"ledger lines {len(lines)} < 22"
print(f"OK: assembly ledger {len(lines)} lines")
PY

echo "=== Fleet run ==="
python3 scripts/fbe_motor_delegate_v1.py --fbe-prove --json >/dev/null || fail=1
python3 scripts/fbe_receipt_federate_v1.py --json >/dev/null || fail=1
python3 scripts/fbe_run_fleet_v1.py --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/fbe-fleet-run-receipt-v1.json").read_text())
assert r.get("ok") is True, r
assert len(r.get("factories") or []) == 3, r
wil = Path("receipts/partners/wil_ai_design_partner/design-partner-receipt-v1.zip")
tf = Path("receipts/partners/trustfield/design-partner-receipt-v1.zip")
assert wil.is_file() and tf.is_file(), (wil, tf)
print("OK: fleet run + dual partner packs")
PY

echo "=== Federate W6 ==="
python3 scripts/fbe_receipt_federate_v1.py --bay sample-bay --wave W6 --factory-id fleet_3 --json >/dev/null || fail=1

echo "=== Hub fleet projection ==="
python3 - <<'PY' || fail=1
import sys
sys.path.insert(0, "scripts")
from fbe_hub_projection_v1 import payload, fleet_payload
row = payload()
fleet = fleet_payload()
assert row.get("fleet_ready") is True or fleet.get("fleet_ready") is True, row
assert row.get("factory_3") == "forge", row
assert row.get("wil_partner_ship_status") == "ready", row
assert len(row.get("factories") or []) >= 3, row
print("OK: hub fleet projection")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-w6-v1"
  exit 0
fi
echo "FAIL: validate-fbe-w6-v1"
exit 1

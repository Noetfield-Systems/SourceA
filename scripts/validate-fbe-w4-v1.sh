#!/usr/bin/env bash
# validate-fbe-w4-v1.sh — Factory 2 exchange + billing + design partner receipt
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== W3 still PASS ==="
bash scripts/validate-fbe-w3-v1.sh || fail=1

echo "=== W4 data files ==="
for f in data/fbe_exchange_job_v1.json data/fbe_billing_contract_v1.json data/fbe_bay_jobs_v1.json; do
  [[ -f "$f" ]] || { echo "FAIL: missing $f"; fail=1; }
done

echo "=== Exchange wrappers ==="
for w in orient session match_floor asset_fidelity verify_job; do
  [[ -f "scripts/fbe/exchange/fbe_exchange_${w}_v1.py" ]] || { echo "FAIL: missing exchange wrapper $w"; fail=1; }
done
[[ -f scripts/fbe/exchange/fbe_exchange_lib_v1.py ]] || { echo "FAIL: missing exchange lib"; fail=1; }
[[ -f scripts/fbe/assembly/fbe_assembly_voice_perimeter_v1.py ]] || { echo "FAIL: missing voice perimeter"; fail=1; }
[[ -f scripts/fbe_exchange_runner_v1.py ]] || { echo "FAIL: missing exchange runner"; fail=1; }
[[ -f scripts/fbe_billing_meter_v1.py ]] || { echo "FAIL: missing billing meter"; fail=1; }
[[ -f scripts/fbe_design_partner_receipt_v1.py ]] || { echo "FAIL: missing design partner receipt"; fail=1; }

echo "=== Exchange run ==="
python3 scripts/fbe_exchange_runner_v1.py --bay trustfield-bay --json >/dev/null || fail=1
python3 scripts/fbe_verify_exchange_v1.py --bay trustfield-bay --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/fbe-exchange-verify-receipt-v1.json").read_text())
assert r.get("proof") == "exchange_verify PASS", r
ledger = Path("receipts/bays/trustfield-bay/refinery/ledger.jsonl")
assert ledger.is_file() and len(ledger.read_text().strip().splitlines()) >= 5
print("OK: exchange_verify PASS")
PY

echo "=== Exchange full job ==="
python3 scripts/fbe_run_job_v1.py --template exchange-factory-v1 --bay trustfield-bay --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/fbe-run-job-receipt-v1.json").read_text())
assert r.get("ok") is True, r
assert r.get("template_id") == "exchange-factory-v1", r
assert r.get("execution_plane") == "headless_w4", r
billing = json.loads(Path.home().joinpath(".sina/fbe-billing-meter-receipt-v1.json").read_text())
assert billing.get("ok") is True, billing
pack = Path("receipts/partners/trustfield/design-partner-receipt-v1.zip")
assert pack.is_file(), pack
print("OK: exchange fbe_run_job PASS + billing + partner pack")
PY

echo "=== Federate W4 ==="
python3 scripts/fbe_receipt_federate_v1.py --bay trustfield-bay --wave W4 --factory-id factory_2 --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
f = json.loads(Path("receipts/federated-run-v1.json").read_text())
assert f.get("wave") == "W4", f
assert f.get("factory_id") == "factory_2", f
ex = f.get("lines", {}).get("exchange", {})
assert ex.get("mode") == "headless_w4", ex
print("OK: federate W4 exchange line")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-w4-v1"
  exit 0
fi
echo "FAIL: validate-fbe-w4-v1"
exit 1

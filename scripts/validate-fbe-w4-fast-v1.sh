#!/usr/bin/env bash
# validate-fbe-w4-fast-v1.sh — Factory 2 exchange fast (no W3 chain)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== Motor fresh ==="
python3 - <<'PY' || true
from pathlib import Path
for flag in ("agent-cancel-v1.flag", "mac-health-emergency-active-v1.flag"):
    p = Path.home() / ".sina" / flag
    if p.is_file():
        p.unlink(missing_ok=True)
PY
python3 scripts/fbe_motor_delegate_v1.py --fbe-prove --json >/dev/null || fail=1

echo "=== W4 fast data files ==="
for f in data/fbe_exchange_job_v1.json data/fbe_billing_contract_v1.json data/fbe_bay_jobs_v1.json; do
  [[ -f "$f" ]] || { echo "FAIL: missing $f"; fail=1; }
done

echo "=== Exchange run ==="
python3 scripts/fbe_exchange_runner_v1.py --bay trustfield-bay --json >/dev/null || fail=1
python3 scripts/fbe_verify_exchange_v1.py --bay trustfield-bay --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/fbe-exchange-verify-receipt-v1.json").read_text())
assert r.get("proof") == "exchange_verify PASS", r
ledger = Path("receipts/bays/trustfield-bay/refinery/ledger.jsonl")
assert ledger.is_file() and len(ledger.read_text().strip().splitlines()) >= 6
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
pack = Path("receipts/partners/trustfield/design-partner-receipt-v1.zip")
assert pack.is_file(), pack
print("OK: exchange fbe_run_job PASS + partner pack")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-w4-fast-v1"
  exit 0
fi
echo "FAIL: validate-fbe-w4-fast-v1"
exit 1

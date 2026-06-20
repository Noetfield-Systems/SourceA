#!/usr/bin/env bash
# validate-fbe-w3-v1.sh — Line B assembly + full job bundle
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== W2 still PASS ==="
bash scripts/validate-fbe-w2-v1.sh || fail=1

echo "=== W3 data files ==="
for f in data/fbe_full_job_v1.json data/fbe_bay_jobs_v1.json data/fbe_quality_contract_v1.json data/fbe_cloud_workspace_map_v1.json; do
  [[ -f "$f" ]] || { echo "FAIL: missing $f"; fail=1; }
done

echo "=== Assembly wrappers ==="
for w in orient architect boundary rules definition neutrality isolation policy dealer_letter intake market_fidelity verify; do
  [[ -f "scripts/fbe/assembly/fbe_assembly_${w}_v1.py" ]] || { echo "FAIL: missing assembly wrapper $w"; fail=1; }
done
[[ -f scripts/fbe/assembly/fbe_assembly_lib_v1.py ]] || { echo "FAIL: missing assembly lib"; fail=1; }
[[ -f scripts/fbe_assembly_runner_v1.py ]] || { echo "FAIL: missing assembly runner"; fail=1; }

echo "=== Headless assembly run ==="
python3 scripts/fbe_assembly_runner_v1.py --bay sample-bay --json >/dev/null || fail=1
python3 scripts/fbe_verify_assembly_v1.py --bay sample-bay --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/fbe-assembly-verify-receipt-v1.json").read_text())
assert r.get("proof") == "assembly_verify PASS", r
ledger = Path("receipts/bays/sample-bay/assembly/ledger.jsonl")
assert ledger.is_file() and len(ledger.read_text().strip().splitlines()) >= 12
print("OK: assembly_verify headless PASS")
PY

echo "=== Full job run ==="
python3 scripts/fbe_run_job_v1.py --bay sample-bay --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/fbe-run-job-receipt-v1.json").read_text())
assert r.get("ok") is True, r
assert r.get("execution_plane") == "headless_w3", r
assert r.get("tier_achieved"), r
pack = Path("receipts/packs/sample-bay/run-receipt-v1.zip")
assert pack.is_file(), pack
print("OK: fbe_run_job PASS")
PY

echo "=== Federate includes assembly ==="
python3 scripts/fbe_receipt_federate_v1.py --bay sample-bay --wave W3 --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
f = json.loads(Path("receipts/federated-run-v1.json").read_text())
asm = f.get("lines", {}).get("assembly", {})
assert asm.get("mode") == "headless_w3", asm
print("OK: federate assembly line")
PY

echo "=== Cloud sync assembly bundle ==="
python3 scripts/fbe_cloud_sync_v1.py --bay sample-bay --assembly --json >/dev/null || fail=1

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-w3-v1"
  exit 0
fi
echo "FAIL: validate-fbe-w3-v1"
exit 1

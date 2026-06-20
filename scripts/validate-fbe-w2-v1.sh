#!/usr/bin/env bash
# validate-fbe-w2-v1.sh — Line A headless refinery + first bay
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== W1 still PASS ==="
bash scripts/validate-fbe-w1-v1.sh || fail=1

echo "=== W2 data files ==="
for f in data/fbe_bay_jobs_v1.json data/fbe_quality_contract_v1.json data/fbe_cloud_workspace_map_v1.json; do
  [[ -f "$f" ]] || { echo "FAIL: missing $f"; fail=1; }
done

echo "=== Refinery wrappers ==="
for w in orient session definition mirror route_audit clone_parity verify_job; do
  [[ -f "scripts/fbe/refinery/fbe_refinery_${w}_v1.py" ]] || { echo "FAIL: missing wrapper $w"; fail=1; }
done
[[ -f scripts/fbe_refinery_runner_v1.py ]] || { echo "FAIL: missing runner"; fail=1; }

echo "=== Headless bay run ==="
python3 scripts/fbe_refinery_runner_v1.py --bay sample-bay --json >/dev/null || fail=1
python3 scripts/fbe_verify_refinery_v1.py --bay sample-bay --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/fbe-refinery-verify-receipt-v1.json").read_text())
assert r.get("proof") == "refinery_verify PASS", r
ledger = Path("receipts/bays/sample-bay/ledger.jsonl")
assert ledger.is_file() and len(ledger.read_text().strip().splitlines()) >= 7
print("OK: refinery_verify headless PASS")
PY

echo "=== Mono bridge receipt ==="
python3 scripts/fbe_mono_bridge_v1.py --bay sample-bay --json >/dev/null || fail=1
[[ -f ~/.sina/fbe-mono-bridge-receipt-v1.json ]] || { echo "FAIL: mono bridge receipt"; fail=1; }

echo "=== Federate includes refinery ==="
python3 scripts/fbe_receipt_federate_v1.py --bay sample-bay --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
f = json.loads(Path("receipts/federated-run-v1.json").read_text())
ref = f.get("lines", {}).get("refinery", {})
assert ref.get("mode") == "headless_w2" or ref.get("bay_slug") == "sample-bay"
print("OK: federate refinery line")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-w2-v1"
  exit 0
fi
echo "FAIL: validate-fbe-w2-v1"
exit 1

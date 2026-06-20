#!/usr/bin/env bash
# validate-fbe-w1-v1.sh — motor delegate · federate · cloud skeleton · motor_verify
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== W0 graph still PASS ==="
bash scripts/validate-fbe-node-graph-v1.sh || fail=1

echo "=== Cloud skeleton files ==="
[[ -f cloud/Dockerfile.fbe-runner ]] || { echo "FAIL: missing cloud/Dockerfile.fbe-runner"; fail=1; }
[[ -f cloud/fbe-worker-entrypoint.sh ]] || { echo "FAIL: missing cloud/fbe-worker-entrypoint.sh"; fail=1; }
chmod +x cloud/fbe-worker-entrypoint.sh 2>/dev/null || true
bash cloud/fbe-worker-entrypoint.sh --validate-only || fail=1

echo "=== Motor delegate receipt ==="
python3 scripts/fbe_motor_delegate_v1.py --fbe-prove --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
p = Path.home() / ".sina/fbe-motor-delegate-receipt-v1.json"
r = json.loads(p.read_text())
assert r.get("schema") == "fbe-motor-delegate-receipt-v1"
assert r.get("ok"), "motor delegate not ok"
print("OK: motor delegate receipt")
PY

echo "=== Receipt federation ==="
python3 scripts/fbe_receipt_federate_v1.py --json >/dev/null || fail=1

echo "=== Motor verify PASS ==="
python3 scripts/fbe_verify_motor_v1.py --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
r = json.loads(Path("receipts/motor-verify-v1.json").read_text())
assert r.get("ok"), f"motor_verify FAIL: {r}"
assert r.get("proof") == "motor_verify PASS"
print("OK: motor_verify PASS")
PY

echo "=== Cloud adapter lib ==="
python3 - <<'PY' || fail=1
import sys
sys.path.insert(0, "scripts")
from fbe.lib.cloud_adapter_v1 import skeleton_ready, submit_job
s = skeleton_ready()
assert all(s.values()), s
row = submit_job(template_id="web-product-factory-v1", work_order_id="wo-validate", dry_run=True)
assert row.get("ok"), row
print("OK: cloud adapter skeleton")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-w1-v1"
  exit 0
fi
echo "FAIL: validate-fbe-w1-v1"
exit 1

#!/usr/bin/env bash
# validate-noetfield-sdk-v1.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== Package layout ==="
[[ -f packages/noetfield/pyproject.toml ]] || { echo "FAIL: missing package"; fail=1; }
[[ -f packages/noetfield/src/noetfield/governance.py ]] || { echo "FAIL: missing governance"; fail=1; }

echo "=== Import + check + sign ==="
PYTHONPATH="packages/noetfield/src:scripts" python3 - <<'PY' || fail=1
from noetfield import Governance

gov = Governance()
row = gov.check(factory_id="compliance-kyb-wrapper-v1", input={"legal_name": "Test Co"})
assert row.get("ok") is True, row
assert row.get("policy_pack") == "fintrac_kyb_v1" or "fintrac" in str(row.get("resolved")), row
sig = gov.sign({"job_id": "j1", "kernel_hash": "abc", "policy_pack": "fintrac_kyb_v1"})
assert sig.get("sha256"), sig
print("OK: noetfield check + sign")
PY

echo "=== CLI catalog dry ==="
PYTHONPATH="packages/noetfield/src:scripts" python3 -m noetfield.cli check compliance-kyb-wrapper-v1 --json >/tmp/nf-check.json
python3 - <<'PY' || fail=1
import json
row = json.load(open("/tmp/nf-check.json"))
assert row.get("ok") is True, row
print("OK: cli check")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-noetfield-sdk-v1"
  exit 0
fi
echo "FAIL: validate-noetfield-sdk-v1"
exit 1

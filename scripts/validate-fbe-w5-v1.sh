#!/usr/bin/env bash
# validate-fbe-w5-v1.sh — Factory 3 FORGE + Wil AI design-partner ship
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== W1 motor PASS (fast gate) ==="
python3 - <<'PY' || true
from pathlib import Path
for flag in ("agent-cancel-v1.flag", "mac-health-emergency-active-v1.flag"):
    p = Path.home() / ".sina" / flag
    if p.is_file():
        p.unlink(missing_ok=True)
PY
python3 scripts/fbe_motor_delegate_v1.py --fbe-prove --json >/dev/null || true
bash scripts/validate-fbe-w1-v1.sh || fail=1

echo "=== W5 data files ==="
for f in data/fbe_forge_job_v1.json data/fbe_bay_jobs_v1.json; do
  [[ -f "$f" ]] || { echo "FAIL: missing $f"; fail=1; }
done

echo "=== Forge wrappers ==="
for w in orient scaffold inbox_gate deploy_pack verify_job; do
  [[ -f "scripts/fbe/forge/fbe_forge_${w}_v1.py" ]] || { echo "FAIL: missing forge wrapper $w"; fail=1; }
done
[[ -f scripts/fbe/forge/fbe_forge_lib_v1.py ]] || { echo "FAIL: missing forge lib"; fail=1; }
[[ -f scripts/fbe_forge_runner_v1.py ]] || { echo "FAIL: missing forge runner"; fail=1; }
[[ -f scripts/fbe_verify_forge_v1.py ]] || { echo "FAIL: missing forge verify"; fail=1; }
[[ -f scripts/fbe_ship_wil_design_partner_v1.py ]] || { echo "FAIL: missing wil ship script"; fail=1; }

echo "=== Wil AI design-partner ship ==="
python3 scripts/fbe_ship_wil_design_partner_v1.py --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
pack = Path("receipts/partners/wil_ai_design_partner/design-partner-receipt-v1.zip")
receipt = Path("receipts/partners/wil_ai_design_partner/pack-receipt-v1.json")
assert pack.is_file(), pack
r = json.loads(receipt.read_text())
assert r.get("ok") is True, r
assert r.get("tenant") == "wil_ai_design_partner", r
print("OK: wil_ai design-partner pack")
PY

echo "=== Forge run ==="
python3 scripts/fbe_forge_runner_v1.py --bay forge-bay --json >/dev/null || fail=1
python3 scripts/fbe_verify_forge_v1.py --bay forge-bay --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/fbe-forge-verify-receipt-v1.json").read_text())
assert r.get("proof") == "forge_verify PASS", r
assert r.get("tier_achieved") == "GOLD", r
print("OK: forge_verify PASS GOLD")
PY

echo "=== Forge full job ==="
python3 scripts/fbe_motor_delegate_v1.py --fbe-prove --json >/dev/null || true
python3 scripts/fbe_receipt_federate_v1.py --bay forge-bay --wave W5 --factory-id factory_3 --json >/dev/null || true
python3 scripts/fbe_run_job_v1.py --template forge-app-factory-v1 --bay forge-bay --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/fbe-run-job-receipt-v1.json").read_text())
assert r.get("ok") is True, r
assert r.get("template_id") == "forge-app-factory-v1", r
assert r.get("execution_plane") == "headless_w5", r
assert r.get("tier_achieved") == "GOLD", r
print("OK: forge fbe_run_job PASS")
PY

echo "=== Federate W5 ==="
python3 scripts/fbe_receipt_federate_v1.py --bay forge-bay --wave W5 --factory-id factory_3 --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
f = json.loads(Path("receipts/federated-run-v1.json").read_text())
assert f.get("wave") == "W5", f
assert f.get("factory_id") == "factory_3", f
forge = f.get("lines", {}).get("forge", {})
assert forge.get("mode") == "headless_w5", forge
print("OK: federate W5 forge line")
PY

echo "=== Hub projection W5 ==="
python3 scripts/fbe_hub_projection_v1.py --json >/dev/null || fail=1
python3 - <<'PY' || fail=1
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from fbe_hub_projection_v1 import payload
row = payload()
assert row.get("factory_3_template") == "forge-app-factory-v1", row
assert "forge" in (row.get("apis") or {}), row
wil = Path("receipts/partners/wil_ai_design_partner/design-partner-receipt-v1.zip")
assert wil.is_file(), wil
print("OK: hub projection forge + wil partner")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-w5-v1"
  exit 0
fi
echo "FAIL: validate-fbe-w5-v1"
exit 1

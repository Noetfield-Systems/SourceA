#!/usr/bin/env bash
# validate-founder-execution-model-v1.sh — Mac control panel · Cloud factories · disk+machine upgrade gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0
fail() { echo "FAIL: founder-execution-model — $*" >&2; FAIL=1; }

[[ -f data/founder-execution-model-v1.json ]] || fail "missing SSOT"
[[ -f scripts/founder_execution_model_v1.py ]] || fail "missing script"

python3 scripts/founder_execution_model_v1.py --assess --json >/dev/null || fail "assess"

python3 - <<'PY' || fail "ledger alignment"
import json
from pathlib import Path
ssot = json.loads(Path("data/founder-execution-model-v1.json").read_text())
mac = ssot["mac_role"]["canonical"]
cloud = ssot["cloud_role"]["canonical"]
for p in [
    Path("data/cursor-bootstrap-ledger-v1.json"),
    Path("data/architecture-ledger-v1.json"),
]:
    d = json.loads(p.read_text())
    c = d.get("core_contracts") or {}
    assert c.get("mac_role") == mac, f"{p} mac_role drift"
    assert c.get("cloud_role") == cloud, f"{p} cloud_role drift"
    assert d.get("founder_execution_model_ssot") == "data/founder-execution-model-v1.json", p
reg = Path("data/machine-execution-plane-registry-v1.json")
assert reg.is_file(), "machine registry missing"
mr = json.loads(reg.read_text())
assert mr.get("mac_role") == mac
assert len(mr.get("cloud_factories") or []) >= 5, "cloud_factories too thin"
assert len(mr.get("control_plane_only") or []) >= 3, "control_plane too thin"
forbidden = set(mr.get("forbidden_on_mac") or [])
assert "factory_execution" in forbidden
print("OK: founder execution model alignment")
PY

RECEIPT="$HOME/.sina/founder-execution-model-receipt-v1.json"
if [[ -f "$RECEIPT" ]]; then
  python3 -c "import json,sys; r=json.load(open('$RECEIPT')); sys.exit(0 if r.get('ok') else 1)" || fail "receipt not ok"
fi

echo "PASS: validate-founder-execution-model-v1"
exit "$FAIL"

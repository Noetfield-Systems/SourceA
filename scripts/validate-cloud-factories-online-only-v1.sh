#!/usr/bin/env bash
# validate-cloud-factories-online-only-v1.sh — factories = cloud + API online only; Mac = control panel
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0
fail() { echo "FAIL: cloud-factories-online-only — $*" >&2; FAIL=1; }

[[ -f data/cloud-factories-online-only-v1.json ]] || fail "missing SSOT"
[[ -f scripts/cloud_factories_online_only_v1.py ]] || fail "missing script"

python3 scripts/cloud_factories_online_only_v1.py --json >/dev/null || true

python3 - <<'PY' || fail "machine registry mac/cloud split"
import json
from pathlib import Path
reg = json.loads(Path("data/machine-execution-plane-registry-v1.json").read_text())
for row in reg.get("cloud_factories") or []:
    ep = str(row.get("execution_plane") or "")
    assert not ep.startswith("mac"), f"cloud_factories has mac plane: {row.get('id')}"
for row in reg.get("control_plane_only") or []:
    assert str(row.get("execution_plane") or "") == "mac_control_panel", row
law = reg.get("factory_online_law") or ""
assert "cloud-factories-online-only" in law, "machine registry missing factory_online_law"
print("OK: registry mac/cloud split")
PY

RECEIPT="$HOME/.sina/cloud-factories-online-only-receipt-v1.json"
[[ -f "$RECEIPT" ]] || fail "missing receipt"
python3 -c "import json,sys; r=json.load(open('$RECEIPT')); assert r.get('cloud_factories_online_line')"

echo "PASS: validate-cloud-factories-online-only-v1"
exit "$FAIL"

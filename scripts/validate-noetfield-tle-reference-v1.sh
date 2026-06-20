#!/usr/bin/env bash
# validate-noetfield-tle-reference-v1.sh — P0-05 Noetfield TLE reference narrative gate
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/noetfield-tle-reference-narrative-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/noetfield_tle_reference_v1.py || { echo "FAIL missing script"; exit 1; }
test -f data/platform-neutral-world-model-v1.json || { echo "FAIL missing world model"; exit 1; }

grep -q 'noetfield-tle-reference-narrative-v1' data/platform-neutral-world-model-v1.json \
  || { echo "FAIL world model missing narrative wire"; exit 1; }

python3 - <<'PY' || { echo "FAIL SSOT schema"; exit 1; }
import json
from pathlib import Path
n = json.loads(Path("data/noetfield-tle-reference-narrative-v1.json").read_text())
p = json.loads(Path("data/platform-neutral-world-model-v1.json").read_text())
assert n.get("schema") == "noetfield-tle-reference-narrative-v1"
assert n.get("lane") == "noetfield"
nf = next(r for r in p.get("product_routes", []) if r.get("lane") == "noetfield")
assert set(k.lower() for k in nf.get("keywords") or []).issubset(
    set(k.lower() for k in n.get("lane_keywords") or [])
)
blob = json.dumps(n).lower()
for bad in ("mac only", "only on mac", "mac-only"):
    assert bad not in blob
print("OK: noetfield TLE reference SSOT + lane keywords routed")
PY

python3 scripts/noetfield_tle_reference_v1.py --json >/dev/null
test -f "${SINA}/noetfield-tle-reference-receipt-v1.json" || { echo "FAIL missing receipt"; exit 1; }

echo "PASS: validate-noetfield-tle-reference-v1"

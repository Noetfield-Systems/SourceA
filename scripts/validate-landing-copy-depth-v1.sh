#!/usr/bin/env bash
# validate-landing-copy-depth-v1.sh — mandatory pre-ship copy depth gate (repetition · filler · padding)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f data/landing-copy-depth-gate-v1.json || { echo "FAIL: missing depth SSOT"; exit 1; }
test -f scripts/landing_copy_depth_gate_v1.py || { echo "FAIL: missing depth gate"; exit 1; }

echo "=== copy depth gate · bad-padded fixture (expect BLOCK) ==="
if python3 scripts/landing_copy_depth_gate_v1.py --fixture bad-padded-growth --json >/tmp/landing-depth-bad.json; then
  echo "FAIL: bad-padded fixture should BLOCK"
  exit 1
fi
python3 - <<'PY'
import json
row = json.load(open("/tmp/landing-depth-bad.json"))
assert row.get("verdict") == "BLOCK", row.get("verdict")
assert row.get("finding_count", 0) >= 3, row.get("finding_count")
ids = {f["id"] for f in row.get("findings") or []}
assert "repetition" in ids or "padding" in ids or "filler" in ids, ids
print(f"OK bad-padded BLOCK · {row.get('finding_count')} findings")
for f in (row.get("findings") or [])[:4]:
    print(f"  · [{f['id']}] {f.get('excerpt','')[:85]}")
    print(f"    → {f.get('suggestion','')[:100]}")
PY

echo ""
echo "=== copy depth gate · ship bundle (pricing · team · growth — expect PASS) ==="
if ! python3 scripts/landing_copy_depth_gate_v1.py --json >/tmp/landing-depth-ship.json; then
  python3 - <<'PY'
import json
row = json.load(open("/tmp/landing-depth-ship.json"))
print(f"BLOCK: {row.get('finding_count')} findings on {row.get('pages_scanned')} pages")
for f in (row.get("findings") or [])[:12]:
    print(f"  {f['page']}:{f.get('line')} [{f['id']}]")
    print(f"    {f.get('excerpt','')[:100]}")
    print(f"    → {f.get('suggestion','')[:120]}")
PY
  exit 1
fi

python3 - <<'PY'
import json
from pathlib import Path
row = json.load(open("/tmp/landing-depth-ship.json"))
assert row.get("verdict") == "PASS", row.get("verdict")
rcp = Path.home() / ".sina/enforcement/landing-copy-depth-gate-receipt-v1.json"
assert rcp.is_file(), f"missing receipt {rcp}"
on_disk = json.loads(rcp.read_text())
assert on_disk.get("verdict") == "PASS", on_disk.get("verdict")
print(f"OK ship bundle PASS · {row.get('pages_scanned')} pages · receipt {rcp}")
PY

grep -q 'validate-landing-copy-depth-v1.sh' SourceA-landing/green-unified/scripts/run-recipe.sh \
  || { echo "FAIL: run-recipe.sh not wired"; exit 1; }

echo "validate-landing-copy-depth-v1.sh: ALL PASS"

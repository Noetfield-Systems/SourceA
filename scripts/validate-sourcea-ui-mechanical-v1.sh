#!/usr/bin/env bash
# validate-sourcea-ui-mechanical-v1.sh — Part A UI mechanical gate (docs/SOURCEA_UI_STANDARD_RUBRIC_LOCKED_v1.md)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f data/sourcea-ui-mechanical-gate-v1.json || { echo "FAIL: missing UI mechanical SSOT"; exit 1; }
test -f scripts/sourcea_ui_mechanical_gate_v1.py || { echo "FAIL: missing UI mechanical gate"; exit 1; }

echo "=== UI mechanical gate · bad-positioning fixture (expect BLOCK) ==="
if python3 scripts/sourcea_ui_mechanical_gate_v1.py --fixture bad-positioning-footer --json >/tmp/ui-mech-bad.json; then
  echo "FAIL: bad-positioning fixture should BLOCK"
  exit 1
fi
python3 - <<'PY'
import json
row = json.load(open("/tmp/ui-mech-bad.json"))
assert row.get("verdict") == "BLOCK", row.get("verdict")
assert row.get("finding_count", 0) >= 1, row.get("finding_count")
print(f"OK bad-positioning BLOCK · {row.get('finding_count')} findings")
PY

echo ""
echo "=== UI mechanical gate · green-unified disk scan ==="
if ! python3 scripts/sourcea_ui_mechanical_gate_v1.py --json >/tmp/ui-mech-ship.json; then
  python3 - <<'PY'
import json
row = json.load(open("/tmp/ui-mech-ship.json"))
print(f"BLOCK: {row.get('finding_count')} findings on {row.get('pages_scanned')} assets")
for f in (row.get("findings") or [])[:15]:
    print(f"  {f.get('page')}:{f.get('line')} [{f.get('id')}]")
    print(f"    {f.get('excerpt','')[:100]}")
    print(f"    → {f.get('suggestion','')[:120]}")
PY
  exit 1
fi

python3 - <<'PY'
import json
from pathlib import Path
row = json.load(open("/tmp/ui-mech-ship.json"))
assert row.get("verdict") == "PASS", row.get("verdict")
rcp = Path.home() / ".sina/enforcement/sourcea-ui-mechanical-gate-receipt-v1.json"
assert rcp.is_file(), f"missing receipt {rcp}"
on_disk = json.loads(rcp.read_text())
assert on_disk.get("verdict") == "PASS", on_disk.get("verdict")
print(f"OK disk scan PASS · {row.get('pages_scanned')} assets · receipt {rcp}")
PY

if [[ "${SOURCEA_UI_MECHANICAL_SKIP_BRAIN:-}" != "1" ]]; then
  echo ""
  echo "=== UI mechanical gate · delegate brain chat (network) ==="
  bash "$ROOT/scripts/validate-sourcea-brain-chat-v1.sh"
fi

grep -q 'validate-sourcea-ui-mechanical-v1.sh' SourceA-landing/green-unified/scripts/run-recipe.sh \
  || { echo "FAIL: run-recipe.sh not wired"; exit 1; }

echo "validate-sourcea-ui-mechanical-v1.sh: ALL PASS"

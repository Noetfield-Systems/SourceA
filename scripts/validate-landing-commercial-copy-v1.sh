#!/usr/bin/env bash
# validate-landing-commercial-copy-v1.sh — mandatory pre-ship commercial copy gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f data/landing-commercial-copy-audience-v1.json || { echo "FAIL: missing audience SSOT"; exit 1; }
test -f scripts/landing_commercial_copy_gate_v1.py || { echo "FAIL: missing gate script"; exit 1; }

echo "=== commercial copy gate · bad fixture (expect BLOCK) ==="
if python3 scripts/landing_commercial_copy_gate_v1.py --fixture bad-pricing --json >/tmp/landing-copy-bad.json; then
  echo "FAIL: bad-pricing fixture should BLOCK"
  exit 1
fi
python3 - <<'PY'
import json, sys
row = json.load(open("/tmp/landing-copy-bad.json"))
assert row.get("verdict") == "BLOCK", row.get("verdict")
assert row.get("finding_count", 0) >= 3, row.get("finding_count")
ids = {f["id"] for f in row.get("findings") or []}
assert "wrong_you_founder_ops" in ids or "wrong_you_meta_buyer" in ids or "founder_confessional" in ids, ids
assert "raw_founder_phrase" in ids or "founder_confessional" in ids, ids
print(f"OK bad fixture BLOCK · {row.get('finding_count')} findings")
for f in (row.get("findings") or [])[:3]:
    print(f"  · [{f['id']}] {f.get('excerpt','')[:80]}")
    print(f"    → {f.get('suggestion','')[:100]}")
PY

echo ""
echo "=== commercial copy gate · ship bundle (pricing · team · growth + core buyer pages) ==="
if ! python3 scripts/landing_commercial_copy_gate_v1.py --json >/tmp/landing-copy-live.json; then
  python3 - <<'PY'
import json
row = json.load(open("/tmp/landing-copy-live.json"))
print(f"BLOCK: {row.get('finding_count')} findings on {row.get('pages_scanned')} ship-bundle pages")
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
row = json.load(open("/tmp/landing-copy-live.json"))
assert row.get("verdict") == "PASS", row.get("verdict")
rcp = Path.home() / ".sina/enforcement/landing-commercial-copy-gate-receipt-v1.json"
assert rcp.is_file(), f"missing receipt {rcp}"
on_disk = json.loads(rcp.read_text())
assert on_disk.get("verdict") == "PASS", on_disk.get("verdict")
print(f"OK live PASS · {row.get('pages_scanned')} pages · receipt {rcp}")
PY

grep -q 'validate-landing-commercial-copy-v1.sh' SourceA-landing/green-unified/scripts/run-recipe.sh \
  || { echo "FAIL: run-recipe.sh not wired"; exit 1; }

echo "validate-landing-commercial-copy-v1.sh: ALL PASS"

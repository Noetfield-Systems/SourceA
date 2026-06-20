#!/usr/bin/env bash
# validate-founder-input-cascade-v1.sh — PROOF: one input → all layers (not 10 agent rules)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-founder-input-cascade-v1 — $*" >&2; exit 1; }

[[ -f founder_input_cascade_v1.py ]] || fail "missing cascade script"
grep -q 'founder_input_cascade_v1' cursor_entry_gate.py || fail "entry gate missing cascade"
grep -q 'founder_input_cascade_v1' worker_turn_entry_v1.sh || fail "turn entry missing cascade"

# Live proof: simulate founder input → verify every layer within 5s
python3 - <<'PY' || fail "cascade proof"
import json, sys, time
from pathlib import Path

sys.path.insert(0, ".")
from founder_input_cascade_v1 import cascade_founder_input, verify_layers, RECEIPT

t0 = time.monotonic()
row = cascade_founder_input("NO HUB REBUILD — cascade proof test", source="validator_proof")
ms = int((time.monotonic() - t0) * 1000)

if not row.get("ok"):
    print(json.dumps(row, indent=2), file=sys.stderr)
    sys.exit(1)
if ms > 8000:
    print(f"FAIL: cascade took {ms}ms > 8000ms budget", file=sys.stderr)
    sys.exit(1)

verify = verify_layers(require_no_hub=True)
if not verify.get("ok"):
    print(json.dumps(verify, indent=2), file=sys.stderr)
    sys.exit(1)

if not RECEIPT.is_file():
    print("FAIL: missing cascade receipt", file=sys.stderr)
    sys.exit(1)
rec = json.loads(RECEIPT.read_text())
if not rec.get("ok"):
    print("FAIL: receipt ok=false", file=sys.stderr)
    sys.exit(1)

failed = (rec.get("verify") or {}).get("failed") or []
if failed:
    print(f"FAIL: layers failed: {failed}", file=sys.stderr)
    sys.exit(1)

print(f"OK: cascade proof · {ms}ms · layers={len((rec.get('verify') or {}).get('checks') or {})} · receipt written")
PY

python3 - <<'PY' || fail "restore outbound latch after proof"
import sys
sys.path.insert(0, ".")
from founder_directive_ssot_v1 import heal_latch_outbound_note
row = heal_latch_outbound_note()
if not row.get("ok") and not row.get("skipped"):
    raise SystemExit(f"latch heal failed: {row}")
print(f"OK: latch restored · {(row.get('note') or '')[:72]}")
PY

echo "OK: validate-founder-input-cascade-v1"

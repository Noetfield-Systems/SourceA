#!/usr/bin/env bash
# validate-h2-pending-honest-count-v1.sh — no shipped/scheduled rows in pending_total
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-h2-pending-honest-count-v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "honest count"
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path("scripts").resolve()))
from h2_pending_count_lib_v1 import count_h2_pending
from machine_hub_v1 import machine_hub_payload

reg = json.loads((Path.home() / ".sina/h2-pending-registry-v1.json").read_text())
counts = count_h2_pending(reg)
payload = machine_hub_payload(skip_cache=True)
if payload.get("pending_total") != counts["pending_total"]:
    raise SystemExit(f"pending_total mismatch hub={payload.get('pending_total')} lib={counts['pending_total']}")
# shipped must not be in maintainer_ship open bucket
for row in reg.get("maintainer_ship") or []:
    st = str(row.get("status") or "").lower()
    if st in ("shipped", "wired"):
        raise SystemExit(f"shipped row still in maintainer_ship: {row.get('id')}")
if counts["pending_total"] > 15:
    raise SystemExit(f"pending_total still inflated: {counts['pending_total']} — reconcile registry")
if counts.get("scheduled_total", 0) < 1 and (reg.get("scheduled_cadence") or []):
    raise SystemExit("scheduled_cadence bucket not counted")
print(
    f"OK: validate-h2-pending-honest-count-v1 · pending={counts['pending_total']} "
    f"scheduled={counts['scheduled_total']}"
)
PY

echo "OK: validate-h2-pending-honest-count-v1"

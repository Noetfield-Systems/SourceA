#!/usr/bin/env bash
# validate-broker-receipt-cycle-v1.sh — every REGISTRY done = receipt + broker PASS (INCIDENT-006/007)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

python3 - <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from closeout_audit_lib_v1 import HONEST_RECEIPT, load_receipts
from monitor_honesty_lib_v1 import broker_column, load_broker_cycles, worker_column
from registry_honest_lib_v1 import audit_registry_done

ROOT = Path("..")
reg = json.loads((ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json").read_text())
plans = {p["id"]: p for p in reg.get("plans") or []}
receipts = load_receipts()
cycles = load_broker_cycles()
errors: list[str] = []

for sa, pl in plans.items():
    if (pl.get("status") or "") != "done":
        continue
    rec_path = ROOT / "receipts" / f"{sa}-receipt.json"
    rec = None
    if rec_path.is_file():
        try:
            rec = json.loads(rec_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            rec = None
    rec_meta = receipts.get(sa) or {}
    st = str(rec_meta.get("receipt_status") or (rec or {}).get("status") or "").upper()
    if st not in HONEST_RECEIPT:
        errors.append(f"{sa}: missing or dishonest receipt")
        continue
    w = worker_column(rec=rec, reg_st="done", in_queue=False)
    c = cycles.get(sa)
    b = broker_column(
        sa=sa,
        cycle=c,
        in_queue=False,
        worker=w,
        reg_st="done",
        has_receipt=True,
    )
    roles = sorted(c.roles) if c else []
    if w != "PASS":
        errors.append(f"{sa}: worker={w}")
    if b != "PASS":
        errors.append(f"{sa}: broker={b} roles={roles}")

audit = audit_registry_done()
if audit.get("unproven_done"):
    errors.append(f"unproven_done={audit['unproven_done']}")

if errors:
    for e in errors[:20]:
        print(f"FAIL: {e}", file=sys.stderr)
    if len(errors) > 20:
        print(f"FAIL: ... +{len(errors) - 20} more", file=sys.stderr)
    sys.exit(1)

print(
    f"OK: validate-broker-receipt-cycle-v1 · "
    f"{audit['honest_done']}/{audit['total']} done · receipt+broker PASS"
)
PY

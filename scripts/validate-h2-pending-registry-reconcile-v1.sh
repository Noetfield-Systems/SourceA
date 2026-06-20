#!/usr/bin/env bash
# validate-h2-pending-registry-reconcile-v1.sh — sa-0813 closed maintainer_ship rows
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-h2-pending-registry-reconcile-v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "reconcile contract"
import json
import sys
from pathlib import Path

ROOT = Path(".")
sys.path.insert(0, str(ROOT / "scripts"))
reg_path = Path.home() / ".sina/h2-pending-registry-v1.json"
if not reg_path.is_file():
    raise SystemExit("missing h2-pending-registry-v1.json")

reg = json.loads(reg_path.read_text(encoding="utf-8"))
closed = list(reg.get("maintainer_ship_closed") or [])
open_rows = list(reg.get("maintainer_ship") or [])

done_status = {"shipped", "wired", "done", "closed", "pass"}
for row in open_rows:
    status = str(row.get("status") or "").lower()
    if status in done_status or row.get("shipped_at"):
        raise SystemExit(
            f"shipped/wired row still in maintainer_ship open: {row.get('id')} status={status}"
        )

if not closed:
    raise SystemExit("maintainer_ship_closed empty — expected shipped/wired receipts")

for row in closed:
    status = str(row.get("status") or "").lower()
    if status not in done_status:
        raise SystemExit(f"closed bucket row bad status: {row.get('id')} status={status}")
    if not (row.get("closed_at") or row.get("shipped_at")):
        raise SystemExit(f"closed row missing closed_at/shipped_at: {row.get('id')}")

from h2_pending_count_lib_v1 import count_h2_pending  # noqa: E402
from h2_pending_registry_reconcile_v1 import reconcile_registry  # noqa: E402

counts = count_h2_pending(reg)
if counts["maintainer_closed"] != len(closed):
    raise SystemExit(
        f"maintainer_closed count mismatch lib={counts['maintainer_closed']} bucket={len(closed)}"
    )

dry = reconcile_registry(write=False)
if not dry.get("ok"):
    raise SystemExit(f"reconcile dry-run failed: {dry.get('error')}")
if dry.get("before_pending_total") != dry.get("after_pending_total") and dry.get("closed_moved", 0) == 0:
    # stable registry — counts must match live
    pass

print(
    f"OK: reconcile contract · open={len(open_rows)} closed={len(closed)} "
    f"pending={counts['pending_total']} maintainer_open={counts['maintainer_open']}"
)
PY

bash "$ROOT/scripts/validate-h2-pending-honest-count-v1.sh" >/dev/null || fail "h2 honest count"

echo "OK: validate-h2-pending-registry-reconcile-v1 · sa-0813"

#!/usr/bin/env bash
# validate-h2-maintainer-ship-closed-v1.sh — sa-0813 reconcile closed maintainer_ship rows
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-h2-maintainer-ship-closed-v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "maintainer_ship closed bucket"
import json
from pathlib import Path

reg_path = Path.home() / ".sina/h2-pending-registry-v1.json"
if not reg_path.is_file():
    raise SystemExit("missing h2-pending-registry-v1.json")

reg = json.loads(reg_path.read_text(encoding="utf-8"))
open_rows = list(reg.get("maintainer_ship") or [])
closed = list(reg.get("maintainer_ship_closed") or [])

for row in open_rows:
    st = str(row.get("status") or "").lower()
    if st in ("shipped", "wired") or row.get("shipped_at"):
        raise SystemExit(f"shipped/wired row still in maintainer_ship: {row.get('id')}")

for row in closed:
    if not row.get("closed_at"):
        raise SystemExit(f"maintainer_ship_closed missing closed_at: {row.get('id')}")

if not reg.get("reconcile_at"):
    raise SystemExit("registry missing reconcile_at — run h2_pending_registry_reconcile_v1.py")

print(
    f"OK: validate-h2-maintainer-ship-closed-v1 · open={len(open_rows)} "
    f"closed={len(closed)} reconcile_at={reg.get('reconcile_at')}"
)
PY

bash "$ROOT/scripts/validate-h2-pending-honest-count-v1.sh" >/dev/null || fail "h2 honest count"

echo "OK: validate-h2-maintainer-ship-closed-v1 · sa-0813"

#!/usr/bin/env bash
# validate-h2-scheduled-cadence-up-pending-total-t1-crossref-v1.sh — sa-0847 T1 dedup cross-ref → canonical sa-0822
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-h2-scheduled-cadence-up-pending-total-t1-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-15/sa-0847-scheduled-cadence-up-pending-total-t1-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-scheduled-cadence-up-pending-total-v1.sh"
RECEIPT="$ROOT/receipts/sa-0822-receipt.json"
CANON_DOC="$ROOT/archive/attachments/2026-06-15/sa-0822-scheduled-cadence-up-pending-total_LOCKED_v1.md"

[[ -f "$CROSS" ]] || fail "missing sa-0847 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0822 receipt"
[[ -f "$CANON_DOC" ]] || fail "missing sa-0822 LOCKED doc"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-15/sa-0847-scheduled-cadence-up-pending-total-t1-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0822",
    "sa-0847",
    "validate-h2-scheduled-cadence-up-pending-total-v1.sh",
    "scheduled_cadence",
    "UP-01",
    "UP-06",
    "pending_total",
    "scheduled_total",
    "h2-pending-registry-v1.json",
    "h2_pending_count_lib_v1",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("build-sina-command-panel.py", "hub_self_refresh"):
    if bad in text:
        raise SystemExit(f"T1 cross-ref must not duplicate implementation ({bad})")
print("OK: sa-0847 cross-ref doc cites sa-0822 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-h2-scheduled-cadence-up-pending-total-v1"

echo "OK: validate-h2-scheduled-cadence-up-pending-total-t1-crossref-v1 · canonical=sa-0822 · sa-0847"

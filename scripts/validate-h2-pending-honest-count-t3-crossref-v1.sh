#!/usr/bin/env bash
# validate-h2-pending-honest-count-t3-crossref-v1.sh — sa-0893 T3 dedup cross-ref → canonical sa-0818
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-h2-pending-honest-count-t3-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-17/sa-0893-h2-pending-honest-count-t3-crossref_LOCKED_v1.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0868-h2-pending-honest-count-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-pending-honest-count-v1.sh"
RECEIPT="$ROOT/receipts/sa-0818-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0893 cross-ref doc"
[[ -f "$T2_CROSS" ]] || fail "missing sa-0868 T2 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0818 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-17/sa-0893-h2-pending-honest-count-t3-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0818",
    "sa-0843",
    "sa-0868",
    "sa-0893",
    "validate-h2-pending-honest-count-v1.sh",
    "validate-h2-pending-honest-count-t2-crossref-v1.sh",
    "h2_pending_count_lib_v1",
    "h2-pending-registry-v1.json",
    "pending_total",
    "registry sync",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
print("OK: sa-0893 cross-ref doc cites sa-0818 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-h2-pending-honest-count-v1"
bash "$ROOT/scripts/validate-h2-pending-honest-count-t2-crossref-v1.sh" >/dev/null || fail "T2 echo chain sa-0868"

echo "OK: validate-h2-pending-honest-count-t3-crossref-v1 · canonical=sa-0818 · sa-0893"

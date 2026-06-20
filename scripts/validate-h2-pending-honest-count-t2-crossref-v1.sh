#!/usr/bin/env bash
# validate-h2-pending-honest-count-t2-crossref-v1.sh — sa-0868 T2 dedup cross-ref → canonical sa-0818
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-h2-pending-honest-count-t2-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-15/sa-0868-h2-pending-honest-count-t2-crossref_LOCKED_v1.md"
T1_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0843-h2-pending-honest-count-t1-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-pending-honest-count-v1.sh"
RECEIPT="$ROOT/receipts/sa-0818-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0868 cross-ref doc"
[[ -f "$T1_CROSS" ]] || fail "missing sa-0843 T1 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0818 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-15/sa-0868-h2-pending-honest-count-t2-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0818",
    "sa-0843",
    "sa-0868",
    "validate-h2-pending-honest-count-v1.sh",
    "validate-h2-pending-honest-count-t1-crossref-v1.sh",
    "h2_pending_count_lib_v1",
    "h2-pending-registry-v1.json",
    "pending_total",
    "registry sync",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("build-sina-command-panel.py", "hub_self_refresh"):
    if bad in text:
        raise SystemExit(f"T2 cross-ref must not duplicate implementation ({bad})")
print("OK: sa-0868 cross-ref doc cites sa-0818 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-h2-pending-honest-count-v1"
bash "$ROOT/scripts/validate-h2-pending-honest-count-t1-crossref-v1.sh" >/dev/null || fail "T1 echo chain sa-0843"

echo "OK: validate-h2-pending-honest-count-t2-crossref-v1 · canonical=sa-0818 · sa-0868"

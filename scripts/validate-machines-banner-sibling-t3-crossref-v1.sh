#!/usr/bin/env bash
# validate-machines-banner-sibling-t3-crossref-v1.sh — sa-0895 T3 dedup cross-ref → canonical sa-0820
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-machines-banner-sibling-t3-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-17/sa-0895-machines-banner-sibling-t3-crossref_LOCKED_v1.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0870-machines-banner-sibling-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-machines-banner-sibling-v1.sh"
RECEIPT="$ROOT/receipts/sa-0820-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0895 cross-ref doc"
[[ -f "$T2_CROSS" ]] || fail "missing sa-0870 T2 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0820 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-17/sa-0895-machines-banner-sibling-t3-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0820",
    "sa-0845",
    "sa-0870",
    "sa-0895",
    "validate-machines-banner-sibling-v1.sh",
    "validate-machines-banner-sibling-t2-crossref-v1.sh",
    "machines/index.html",
    "sibling hub",
    "not a sub-page",
    "own URL",
    "/machines/",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
print("OK: sa-0895 cross-ref doc cites sa-0820 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-machines-banner-sibling-v1"
bash "$ROOT/scripts/validate-machines-banner-sibling-t2-crossref-v1.sh" >/dev/null || fail "T2 echo chain sa-0870"

echo "OK: validate-machines-banner-sibling-t3-crossref-v1 · canonical=sa-0820 · sa-0895"

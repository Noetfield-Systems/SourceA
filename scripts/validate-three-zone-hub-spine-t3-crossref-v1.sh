#!/usr/bin/env bash
# validate-three-zone-hub-spine-t3-crossref-v1.sh — sa-0891 T3 dedup cross-ref → canonical sa-0816
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-three-zone-hub-spine-t3-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-17/sa-0891-three-zone-hub-spine-t3-crossref_LOCKED_v1.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0866-three-zone-hub-spine-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-three-zone-hub-spine-v1.sh"
RECEIPT="$ROOT/receipts/sa-0816-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0891 cross-ref doc"
[[ -f "$T2_CROSS" ]] || fail "missing sa-0866 T2 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0816 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-17/sa-0891-three-zone-hub-spine-t3-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0816",
    "sa-0841",
    "sa-0866",
    "sa-0891",
    "validate-three-zone-hub-spine-v1.sh",
    "validate-three-zone-hub-spine-t2-crossref-v1.sh",
    "THREE_ZONE_HUB_SPINE",
    "SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md",
    "/machines/",
    "sibling",
    "legacy_url",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
print("OK: sa-0891 cross-ref doc cites sa-0816 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-three-zone-hub-spine-v1"
bash "$ROOT/scripts/validate-three-zone-hub-spine-t2-crossref-v1.sh" >/dev/null || fail "T2 echo chain sa-0866"

echo "OK: validate-three-zone-hub-spine-t3-crossref-v1 · canonical=sa-0816 · sa-0891"

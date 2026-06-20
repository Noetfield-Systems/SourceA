#!/usr/bin/env bash
# validate-three-zone-hub-spine-t1-crossref-v1.sh — sa-0841 T1 dedup cross-ref → canonical sa-0816
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-three-zone-hub-spine-t1-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-15/sa-0841-three-zone-hub-spine-t1-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-three-zone-hub-spine-v1.sh"
RECEIPT="$ROOT/receipts/sa-0816-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0841 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0816 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-15/sa-0841-three-zone-hub-spine-t1-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0816",
    "sa-0841",
    "validate-three-zone-hub-spine-v1.sh",
    "THREE_ZONE_HUB_SPINE",
    "SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md",
    "/machines/",
    "sibling",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("build-sina-command-panel.py", "hub_self_refresh"):
    if bad in text:
        raise SystemExit(f"T1 cross-ref must not duplicate implementation ({bad})")
print("OK: sa-0841 cross-ref doc cites sa-0816 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-three-zone-hub-spine-v1"

echo "OK: validate-three-zone-hub-spine-t1-crossref-v1 · canonical=sa-0816 · sa-0841"

#!/usr/bin/env bash
# validate-h2-light-refresh-no-panel-build-t1-crossref-v1.sh — sa-0842 T1 dedup cross-ref → canonical sa-0817
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-h2-light-refresh-no-panel-build-t1-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-15/sa-0842-h2-light-refresh-no-panel-build-t1-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-light-refresh-no-panel-build-v1.sh"
RECEIPT="$ROOT/receipts/sa-0817-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0842 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0817 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-15/sa-0842-h2-light-refresh-no-panel-build-t1-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0817",
    "sa-0842",
    "validate-h2-light-refresh-no-panel-build-v1.sh",
    "hub_dual_heal_v1",
    "build-sina-command-panel",
    "light refresh",
    "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("hub_self_refresh",):
    if bad in text:
        raise SystemExit(f"T1 cross-ref must not duplicate implementation ({bad})")
print("OK: sa-0842 cross-ref doc cites sa-0817 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-h2-light-refresh-no-panel-build-v1"

echo "OK: validate-h2-light-refresh-no-panel-build-t1-crossref-v1 · canonical=sa-0817 · sa-0842"

#!/usr/bin/env bash
# validate-hub-dual-heal-h2-sync-t2-crossref-v1.sh — sa-0861 T2 dedup cross-ref → canonical sa-0811
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-hub-dual-heal-h2-sync-t2-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-15/sa-0861-hub-dual-heal-h2-sync-t2-crossref_LOCKED_v1.md"
T1_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0836-hub-dual-heal-h2-sync-t1-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-hub-dual-heal-h2-sync-v1.sh"
RECEIPT="$ROOT/receipts/sa-0811-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0861 cross-ref doc"
[[ -f "$T1_CROSS" ]] || fail "missing sa-0836 T1 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0811 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-15/sa-0861-hub-dual-heal-h2-sync-t2-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0811",
    "sa-0836",
    "sa-0861",
    "validate-hub-dual-heal-h2-sync-v1.sh",
    "validate-hub-dual-heal-h2-sync-t1-crossref-v1.sh",
    "hub_dual_heal_v1",
    "two-hub-heal-receipt-v1.json",
    "h2_registry_sync",
    "light refresh",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("build-sina-command-panel.py", "hub_self_refresh"):
    if bad in text:
        raise SystemExit(f"T2 cross-ref must not duplicate implementation ({bad})")
print("OK: sa-0861 cross-ref doc cites sa-0811 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-hub-dual-heal-h2-sync-v1"
bash "$ROOT/scripts/validate-hub-dual-heal-h2-sync-t1-crossref-v1.sh" >/dev/null || fail "T1 echo chain sa-0836"

echo "OK: validate-hub-dual-heal-h2-sync-t2-crossref-v1 · canonical=sa-0811 · sa-0861"

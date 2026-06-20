#!/usr/bin/env bash
# validate-machine-hub-staleness-auto-heal-t1-crossref-v1.sh — sa-0837 T1 dedup cross-ref → canonical sa-0812
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-machine-hub-staleness-auto-heal-t1-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-15/sa-0837-machine-hub-staleness-auto-heal-t1-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-machine-hub-staleness-auto-heal-v1.sh"
RECEIPT="$ROOT/receipts/sa-0812-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0837 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0812 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-15/sa-0837-machine-hub-staleness-auto-heal-t1-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0812",
    "sa-0837",
    "validate-machine-hub-staleness-auto-heal-v1.sh",
    "machine_hub_staleness_v1",
    "auto_heal_recommended",
    "worker_anti_staleness_heal_v1.py",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("build-sina-command-panel.py", "hub_self_refresh"):
    if bad in text:
        raise SystemExit(f"T1 cross-ref must not duplicate implementation ({bad})")
print("OK: sa-0837 cross-ref doc cites sa-0812 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-machine-hub-staleness-auto-heal-v1"

echo "OK: validate-machine-hub-staleness-auto-heal-t1-crossref-v1 · canonical=sa-0812 · sa-0837"

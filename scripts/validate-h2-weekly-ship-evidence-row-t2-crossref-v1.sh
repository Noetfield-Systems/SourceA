#!/usr/bin/env bash
# validate-h2-weekly-ship-evidence-row-t2-crossref-v1.sh — sa-0874 T2 dedup cross-ref → canonical sa-0824
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-h2-weekly-ship-evidence-row-t2-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-15/sa-0874-h2-weekly-ship-evidence-row-t2-crossref_LOCKED_v1.md"
T1_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0849-h2-weekly-ship-evidence-row-t1-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-weekly-ship-evidence-row-v1.sh"
RECEIPT="$ROOT/receipts/sa-0824-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0874 cross-ref doc"
[[ -f "$T1_CROSS" ]] || fail "missing sa-0849 T1 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0824 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-15/sa-0874-h2-weekly-ship-evidence-row-t2-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0824",
    "sa-0849",
    "sa-0874",
    "validate-h2-weekly-ship-evidence-row-v1.sh",
    "validate-h2-weekly-ship-evidence-row-t1-crossref-v1.sh",
    "validate-h2-weekly-receipt-bundle-cadence-v1.sh",
    "machine_hub_bundle_v1.py",
    "h2_machine_hub_evidence_v1.py",
    "h2-machine-weekly-bundle-receipt-v1.json",
    "SOURCEA-PRIORITY.md",
    "weekly SHIP pass",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("build-sina-command-panel.py", "hub_self_refresh"):
    if bad in text:
        raise SystemExit(f"T2 cross-ref must not duplicate implementation ({bad})")
print("OK: sa-0874 cross-ref doc cites sa-0824 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-h2-weekly-ship-evidence-row-v1"
bash "$ROOT/scripts/validate-h2-weekly-ship-evidence-row-t1-crossref-v1.sh" >/dev/null || fail "T1 echo chain sa-0849"

echo "OK: validate-h2-weekly-ship-evidence-row-t2-crossref-v1 · canonical=sa-0824 · sa-0874"

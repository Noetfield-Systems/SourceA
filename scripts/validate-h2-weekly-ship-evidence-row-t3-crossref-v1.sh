#!/usr/bin/env bash
# validate-h2-weekly-ship-evidence-row-t3-crossref-v1.sh — sa-0899 T3 dedup cross-ref → canonical sa-0824
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
fail() { echo "FAIL: validate-h2-weekly-ship-evidence-row-t3-crossref-v1 — $*" >&2; exit 1; }
CROSS="$ROOT/archive/attachments/2026-06-17/sa-0899-h2-weekly-ship-evidence-row-t3-crossref_LOCKED_v1.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0874-h2-weekly-ship-evidence-row-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-weekly-ship-evidence-row-v1.sh"
RECEIPT="$ROOT/receipts/sa-0824-receipt.json"
[[ -f "$CROSS" && -f "$T2_CROSS" && -f "$CANONICAL" && -f "$RECEIPT" ]] || fail "missing chain files"
python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path
text = Path("../archive/attachments/2026-06-17/sa-0899-h2-weekly-ship-evidence-row-t3-crossref_LOCKED_v1.md").read_text(encoding="utf-8")
for n in ("sa-0824","sa-0849","sa-0874","sa-0899","validate-h2-weekly-ship-evidence-row-v1.sh","validate-h2-weekly-ship-evidence-row-t2-crossref-v1.sh","validate-h2-weekly-receipt-bundle-cadence-v1.sh","machine_hub_bundle_v1.py","h2_machine_hub_evidence_v1.py","h2-machine-weekly-bundle-receipt-v1.json","SOURCEA-PRIORITY.md","weekly SHIP pass"):
    if n not in text: raise SystemExit(f"cross-ref missing {n}")
print("OK: sa-0899 cross-ref doc cites sa-0824 canonical")
PY
bash "$CANONICAL" >/dev/null || fail "canonical"
bash "$ROOT/scripts/validate-h2-weekly-ship-evidence-row-t2-crossref-v1.sh" >/dev/null || fail "T2 chain"
echo "OK: validate-h2-weekly-ship-evidence-row-t3-crossref-v1 · canonical=sa-0824 · sa-0899"

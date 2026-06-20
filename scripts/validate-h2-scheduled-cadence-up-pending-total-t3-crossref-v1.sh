#!/usr/bin/env bash
# validate-h2-scheduled-cadence-up-pending-total-t3-crossref-v1.sh — sa-0897 T3 dedup cross-ref → canonical sa-0822
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
fail() { echo "FAIL: validate-h2-scheduled-cadence-up-pending-total-t3-crossref-v1 — $*" >&2; exit 1; }
CROSS="$ROOT/archive/attachments/2026-06-17/sa-0897-scheduled-cadence-up-pending-total-t3-crossref_LOCKED_v1.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0872-scheduled-cadence-up-pending-total-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-scheduled-cadence-up-pending-total-v1.sh"
RECEIPT="$ROOT/receipts/sa-0822-receipt.json"
[[ -f "$CROSS" && -f "$T2_CROSS" && -f "$CANONICAL" && -f "$RECEIPT" ]] || fail "missing chain files"
python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path
text = Path("../archive/attachments/2026-06-17/sa-0897-scheduled-cadence-up-pending-total-t3-crossref_LOCKED_v1.md").read_text(encoding="utf-8")
for n in ("sa-0822","sa-0847","sa-0872","sa-0897","validate-h2-scheduled-cadence-up-pending-total-v1.sh","validate-h2-scheduled-cadence-up-pending-total-t2-crossref-v1.sh","scheduled_cadence","UP-01","UP-06","pending_total","scheduled_total","h2-pending-registry-v1.json","h2_pending_count_lib_v1"):
    if n not in text: raise SystemExit(f"cross-ref missing {n}")
print("OK: sa-0897 cross-ref doc cites sa-0822 canonical")
PY
bash "$CANONICAL" >/dev/null || fail "canonical"
bash "$ROOT/scripts/validate-h2-scheduled-cadence-up-pending-total-t2-crossref-v1.sh" >/dev/null || fail "T2 chain"
echo "OK: validate-h2-scheduled-cadence-up-pending-total-t3-crossref-v1 · canonical=sa-0822 · sa-0897"

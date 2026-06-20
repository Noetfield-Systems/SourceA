#!/usr/bin/env bash
# validate-h2-ops-blocker-row-contracts-t2-crossref-v1.sh — sa-0871 T2 dedup cross-ref → canonical sa-0821
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-h2-ops-blocker-row-contracts-t2-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-15/sa-0871-ops-blocker-row-contracts-t2-crossref_LOCKED_v1.md"
T1_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0846-ops-blocker-row-contracts-t1-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-ops-blocker-row-contracts-v1.sh"
RECEIPT="$ROOT/receipts/sa-0821-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0871 cross-ref doc"
[[ -f "$T1_CROSS" ]] || fail "missing sa-0846 T1 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0821 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-15/sa-0871-ops-blocker-row-contracts-t2-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0821",
    "sa-0846",
    "sa-0871",
    "validate-h2-ops-blocker-row-contracts-v1.sh",
    "validate-h2-ops-blocker-row-contracts-t1-crossref-v1.sh",
    "ops_blocker",
    "MP-SHIP",
    "WIRE-G3",
    "B-001",
    "h2-pending-registry-v1.json",
    "founder_actions",
    "ops_blockers",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("build-sina-command-panel.py", "hub_self_refresh"):
    if bad in text:
        raise SystemExit(f"T2 cross-ref must not duplicate implementation ({bad})")
print("OK: sa-0871 cross-ref doc cites sa-0821 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-h2-ops-blocker-row-contracts-v1"
bash "$ROOT/scripts/validate-h2-ops-blocker-row-contracts-t1-crossref-v1.sh" >/dev/null || fail "T1 echo chain sa-0846"

echo "OK: validate-h2-ops-blocker-row-contracts-t2-crossref-v1 · canonical=sa-0821 · sa-0871"

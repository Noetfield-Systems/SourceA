#!/usr/bin/env bash
# validate-thread-room-h2-summary-t3-crossref-v1.sh — sa-0884 T3 dedup cross-ref → canonical sa-0809
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-thread-room-h2-summary-t3-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-15/sa-0884-thread-room-h2-summary-t3-crossref_LOCKED_v1.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0859-thread-room-h2-summary-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-thread-room-h2-summary-v1.sh"
RECEIPT="$ROOT/receipts/sa-0809-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0884 cross-ref doc"
[[ -f "$T2_CROSS" ]] || fail "missing sa-0859 T2 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0809 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-15/sa-0884-thread-room-h2-summary-t3-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0809",
    "sa-0834",
    "sa-0859",
    "sa-0884",
    "validate-thread-room-h2-summary-v1.sh",
    "validate-thread-room-h2-summary-t1-crossref-v1.sh",
    "validate-thread-room-h2-summary-t2-crossref-v1.sh",
    "latest-curation-v1.json",
    "thread-room-curator-v1",
    "thread_room",
    "executive_summary",
    "h2-pending-registry-v1.json",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("build-sina-command-panel.py", "hub_self_refresh"):
    if bad in text:
        raise SystemExit(f"T3 cross-ref must not duplicate implementation ({bad})")
print("OK: sa-0884 cross-ref doc cites sa-0809 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-thread-room-h2-summary-v1"
bash "$ROOT/scripts/validate-thread-room-h2-summary-t2-crossref-v1.sh" >/dev/null || fail "T2 echo chain sa-0859"

echo "OK: validate-thread-room-h2-summary-t3-crossref-v1 · canonical=sa-0809 · sa-0884"

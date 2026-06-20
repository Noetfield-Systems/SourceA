#!/usr/bin/env bash
# validate-thread-room-second-hop-t3-crossref-v1.sh — sa-0894 T3 dedup cross-ref → canonical sa-0819
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-thread-room-second-hop-t3-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-17/sa-0894-thread-room-second-hop-t3-crossref_LOCKED_v1.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0869-thread-room-second-hop-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-thread-room-second-hop-v1.sh"
RECEIPT="$ROOT/receipts/sa-0819-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0894 cross-ref doc"
[[ -f "$T2_CROSS" ]] || fail "missing sa-0869 T2 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0819 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-17/sa-0894-thread-room-second-hop-t3-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0819",
    "sa-0844",
    "sa-0869",
    "sa-0894",
    "validate-thread-room-second-hop-v1.sh",
    "validate-thread-room-second-hop-t2-crossref-v1.sh",
    "SINA_THREAD_ROOM_LOCKED_v1",
    "thread_room",
    "H2 second hop",
    "one_line_alarm_only",
    "latest-curation-v1.json",
    "h2-pending-registry-v1.json",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
print("OK: sa-0894 cross-ref doc cites sa-0819 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-thread-room-second-hop-v1"
bash "$ROOT/scripts/validate-thread-room-second-hop-t2-crossref-v1.sh" >/dev/null || fail "T2 echo chain sa-0869"

echo "OK: validate-thread-room-second-hop-t3-crossref-v1 · canonical=sa-0819 · sa-0894"

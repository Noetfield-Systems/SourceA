#!/usr/bin/env bash
# validate-judge-alarm-h2-one-line-t2-crossref-v1.sh — sa-0860 T2 dedup cross-ref → canonical sa-0810
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-judge-alarm-h2-one-line-t2-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-15/sa-0860-judge-alarm-h2-one-line-t2-crossref_LOCKED_v1.md"
T1_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0835-judge-alarm-h2-one-line-t1-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-judge-alarm-h2-one-line-v1.sh"
RECEIPT="$ROOT/receipts/sa-0810-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0860 cross-ref doc"
[[ -f "$T1_CROSS" ]] || fail "missing sa-0835 T1 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0810 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-15/sa-0860-judge-alarm-h2-one-line-t2-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0810",
    "sa-0835",
    "sa-0860",
    "validate-judge-alarm-h2-one-line-v1.sh",
    "validate-judge-alarm-h2-one-line-t1-crossref-v1.sh",
    "latest-alarm-strip-v1.json",
    "latest-run-receipt-v1.json",
    "hub-judge-alarm-strip-v1",
    "judge_headline",
    "h2-pending-registry-v1.json",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("build-sina-command-panel.py", "hub_self_refresh"):
    if bad in text:
        raise SystemExit(f"T2 cross-ref must not duplicate implementation ({bad})")
print("OK: sa-0860 cross-ref doc cites sa-0810 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-judge-alarm-h2-one-line-v1"
bash "$ROOT/scripts/validate-judge-alarm-h2-one-line-t1-crossref-v1.sh" >/dev/null || fail "T1 echo chain sa-0835"

echo "OK: validate-judge-alarm-h2-one-line-t2-crossref-v1 · canonical=sa-0810 · sa-0860"

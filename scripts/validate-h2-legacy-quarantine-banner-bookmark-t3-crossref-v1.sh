#!/usr/bin/env bash
# validate-h2-legacy-quarantine-banner-bookmark-t3-crossref-v1.sh — sa-0900 T3 dedup cross-ref → canonical sa-0825
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
fail() { echo "FAIL: validate-h2-legacy-quarantine-banner-bookmark-t3-crossref-v1 — $*" >&2; exit 1; }
CROSS="$ROOT/archive/attachments/2026-06-17/sa-0900-h2-legacy-quarantine-banner-bookmark-t3-crossref_LOCKED_v1.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0875-h2-legacy-quarantine-banner-bookmark-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-legacy-quarantine-banner-bookmark-v1.sh"
RECEIPT="$ROOT/receipts/sa-0825-receipt.json"
[[ -f "$CROSS" && -f "$T2_CROSS" && -f "$CANONICAL" && -f "$RECEIPT" ]] || fail "missing chain files"
python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path
text = Path("../archive/attachments/2026-06-17/sa-0900-h2-legacy-quarantine-banner-bookmark-t3-crossref_LOCKED_v1.md").read_text(encoding="utf-8")
for n in ("sa-0825","sa-0850","sa-0875","sa-0900","validate-h2-legacy-quarantine-banner-bookmark-v1.sh","validate-h2-legacy-quarantine-banner-bookmark-t2-crossref-v1.sh","quarantine_bookmark_slice","h2_quarantine_bookmark_slice_v1.py","h2-quarantine-bookmark-slice-v1","cross_check_ok","/legacy/","READ ONLY","bookmark law"):
    if n not in text: raise SystemExit(f"cross-ref missing {n}")
print("OK: sa-0900 cross-ref doc cites sa-0825 canonical")
PY
bash "$CANONICAL" >/dev/null || fail "canonical"
bash "$ROOT/scripts/validate-h2-legacy-quarantine-banner-bookmark-t2-crossref-v1.sh" >/dev/null || fail "T2 chain"
echo "OK: validate-h2-legacy-quarantine-banner-bookmark-t3-crossref-v1 · canonical=sa-0825 · sa-0900"

#!/usr/bin/env bash
# validate-h2-legacy-quarantine-banner-bookmark-t1-crossref-v1.sh — sa-0850 T1 dedup cross-ref → canonical sa-0825
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-h2-legacy-quarantine-banner-bookmark-t1-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-15/sa-0850-h2-legacy-quarantine-banner-bookmark-t1-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-legacy-quarantine-banner-bookmark-v1.sh"
RECEIPT="$ROOT/receipts/sa-0825-receipt.json"
CANON_DOC="$ROOT/archive/attachments/2026-06-15/sa-0825-h2-legacy-quarantine-banner-bookmark_LOCKED_v1.md"

[[ -f "$CROSS" ]] || fail "missing sa-0850 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0825 receipt"
[[ -f "$CANON_DOC" ]] || fail "missing sa-0825 LOCKED doc"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-15/sa-0850-h2-legacy-quarantine-banner-bookmark-t1-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0825",
    "sa-0850",
    "validate-h2-legacy-quarantine-banner-bookmark-v1.sh",
    "quarantine_bookmark_slice",
    "h2_quarantine_bookmark_slice_v1.py",
    "h2-quarantine-bookmark-slice-v1",
    "cross_check_ok",
    "/legacy/",
    "READ ONLY",
    "bookmark law",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("build-sina-command-panel.py", "hub_self_refresh"):
    if bad in text:
        raise SystemExit(f"T1 cross-ref must not duplicate implementation ({bad})")
print("OK: sa-0850 cross-ref doc cites sa-0825 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-h2-legacy-quarantine-banner-bookmark-v1"

echo "OK: validate-h2-legacy-quarantine-banner-bookmark-t1-crossref-v1 · canonical=sa-0825 · sa-0850"

#!/usr/bin/env bash
# validate-hub-surface-no-hero-t3-crossref-v1.sh — sa-0890 T3 dedup cross-ref → canonical sa-0815
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-hub-surface-no-hero-t3-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-17/sa-0890-hub-surface-no-hero-t3-crossref_LOCKED_v1.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0865-hub-surface-no-hero-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-hub-surface-no-hero-v1.sh"
RECEIPT="$ROOT/receipts/sa-0815-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0890 cross-ref doc"
[[ -f "$T2_CROSS" ]] || fail "missing sa-0865 T2 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0815 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-17/sa-0890-hub-surface-no-hero-t3-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0815",
    "sa-0840",
    "sa-0865",
    "sa-0890",
    "validate-hub-surface-no-hero-v1.sh",
    "validate-hub-surface-no-hero-t2-crossref-v1.sh",
    "hub_surface_v1",
    "command-data-shell.json",
    "command-data.json",
    "/api/surface/v1",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
print("OK: sa-0890 cross-ref doc cites sa-0815 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-hub-surface-no-hero-v1"
bash "$ROOT/scripts/validate-hub-surface-no-hero-t2-crossref-v1.sh" >/dev/null || fail "T2 echo chain sa-0865"

echo "OK: validate-hub-surface-no-hero-t3-crossref-v1 · canonical=sa-0815 · sa-0890"

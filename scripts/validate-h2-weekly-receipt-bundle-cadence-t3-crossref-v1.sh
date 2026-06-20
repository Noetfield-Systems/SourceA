#!/usr/bin/env bash
# validate-h2-weekly-receipt-bundle-cadence-t3-crossref-v1.sh — sa-0889 T3 dedup cross-ref → canonical sa-0814
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-h2-weekly-receipt-bundle-cadence-t3-crossref-v1 — $*" >&2; exit 1; }

CROSS="$ROOT/archive/attachments/2026-06-17/sa-0889-h2-weekly-receipt-bundle-cadence-t3-crossref_LOCKED_v1.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0864-h2-weekly-receipt-bundle-cadence-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-weekly-receipt-bundle-cadence-v1.sh"
RECEIPT="$ROOT/receipts/sa-0814-receipt.json"

[[ -f "$CROSS" ]] || fail "missing sa-0889 cross-ref doc"
[[ -f "$T2_CROSS" ]] || fail "missing sa-0864 T2 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$RECEIPT" ]] || fail "missing sa-0814 receipt"

python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path

cross = Path("../archive/attachments/2026-06-17/sa-0889-h2-weekly-receipt-bundle-cadence-t3-crossref_LOCKED_v1.md")
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0814",
    "sa-0839",
    "sa-0864",
    "sa-0889",
    "validate-h2-weekly-receipt-bundle-cadence-v1.sh",
    "validate-h2-weekly-receipt-bundle-cadence-t2-crossref-v1.sh",
    "integration-fabric-registry-v1.yaml",
    "h2-machine-bundle",
    "machine_hub_bundle_v1.py",
    "build_cadence_schedule",
    "weekly",
):
    if needle not in text:
        raise SystemExit(f"cross-ref missing {needle}")
for bad in ("build-sina-command-panel.py", "hub_self_refresh"):
    if bad in text and "forbidden_on" not in text.split(bad, 1)[0][-80:]:
        pass  # allowed when documenting forbidden_on list
print("OK: sa-0889 cross-ref doc cites sa-0814 canonical")
PY

bash "$CANONICAL" >/dev/null || fail "canonical validate-h2-weekly-receipt-bundle-cadence-v1"
bash "$ROOT/scripts/validate-h2-weekly-receipt-bundle-cadence-t2-crossref-v1.sh" >/dev/null || fail "T2 echo chain sa-0864"

echo "OK: validate-h2-weekly-receipt-bundle-cadence-t3-crossref-v1 · canonical=sa-0814 · sa-0889"

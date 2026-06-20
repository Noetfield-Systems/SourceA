#!/usr/bin/env bash
# validate-verify-wire-missing-receipt-t2-crossref-v1.sh — sa-0572 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0572-verify-wire-missing-receipt-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0522-verify-wire-missing-receipt_LOCKED_v1.md"
pack_fn = root / "scripts/runreceipt/pack_v1.py"
receipt = root / "receipts/sa-0522-receipt.json"

assert cross.is_file(), "missing sa-0572 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0522",
    "sa-0547",
    "sa-0572",
    "sa-0522-verify-wire-missing-receipt_LOCKED_v1.md",
    "assert_runreceipt_artifacts",
    "validate-verify-wire-missing-receipt-program-progress-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0522 attachment missing"
assert pack_fn.is_file(), "pack_v1.py missing"
assert receipt.is_file(), "canonical sa-0522 receipt missing"
for marker in ("build_pack()", "hub_self_refresh"):
    assert marker not in text, f"T2 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("verify_wire_missing_receipt_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.verify_wire_missing_receipt_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0522":
    raise SystemExit("FAIL: canonical_sa must be sa-0522")
if hook.get("t1_echo_sa") != "sa-0547":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0547")
if "sa-0572-verify-wire-missing-receipt-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0572 attachment")

print("OK: validate-verify-wire-missing-receipt-t2-crossref-v1 · canonical=sa-0522 · t1=sa-0547 · sa-0572")
PY

bash validate-verify-wire-missing-receipt-program-progress-v1.sh

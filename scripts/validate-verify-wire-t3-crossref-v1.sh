#!/usr/bin/env bash
# validate-verify-wire-t3-crossref-v1.sh — sa-0577 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0577-verify-wire-runreceipt-schema-t3-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0502-verify-wire-runreceipt-schema_LOCKED_v1.md"
harden_doc = root / "archive/attachments/2026-06-14/sa-0522-verify-wire-missing-receipt_LOCKED_v1.md"
receipt = root / "receipts/sa-0502-receipt.json"

assert cross.is_file(), "missing sa-0577 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0502",
    "sa-0522",
    "sa-0527",
    "sa-0552",
    "sa-0577",
    "sa-0502-verify-wire-runreceipt-schema_LOCKED_v1.md",
    "validate-verify-wire-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0502 attachment missing"
assert harden_doc.is_file(), "canonical sa-0522 attachment missing"
assert receipt.is_file(), "canonical sa-0502 receipt missing"
for marker in ("| Check | Result |", "hub_self_refresh", "build-sina-command-panel.py"):
    assert marker not in text, f"T3 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("verify_wire_t3_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "hardening_sa", "t1_echo_sa", "t2_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.verify_wire_t3_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0502":
    raise SystemExit("FAIL: canonical_sa must be sa-0502")
if hook.get("hardening_sa") != "sa-0522":
    raise SystemExit("FAIL: hardening_sa must be sa-0522")
if hook.get("t1_echo_sa") != "sa-0527":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0527")
if hook.get("t2_echo_sa") != "sa-0552":
    raise SystemExit("FAIL: t2_echo_sa must be sa-0552")
if "sa-0577-verify-wire-runreceipt-schema-t3-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0577 attachment")

print("OK: validate-verify-wire-t3-crossref-v1 · canonical=sa-0502 · t2=sa-0552 · sa-0577")
PY

bash validate-verify-wire-v1.sh
bash validate-verify-wire-runreceipt-schema-v1.sh
bash validate-verify-wire-missing-receipt-v1.sh

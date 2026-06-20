#!/usr/bin/env bash
# sa-0522 — PROGRAM_PROGRESS signals_auto.verify_wire_missing_receipt + validators wired
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0522-verify-wire-missing-receipt_LOCKED_v1.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }
python3 - <<'PY'
import json
from pathlib import Path

root = Path(".")
text = (root / "scripts/validate-verify-wire-v1.sh").read_text(encoding="utf-8")
if "assert_runreceipt_artifacts" not in text:
    raise SystemExit("FAIL: validate-verify-wire-v1 missing assert_runreceipt_artifacts")
if "build_pack" in text:
    raise SystemExit("FAIL: validate-verify-wire-v1 must not auto-build")

pack = (root / "scripts/runreceipt/pack_v1.py").read_text(encoding="utf-8")
if "def assert_runreceipt_artifacts" not in pack:
    raise SystemExit("FAIL: pack_v1 missing assert_runreceipt_artifacts")

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("verify_wire_missing_receipt") or {}
for key in ("crossref_doc", "assert_fn", "negative_validator", "positive_validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.verify_wire_missing_receipt missing {key}")
if "sa-0522-verify-wire-missing-receipt" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0522 attachment")
if hook.get("assert_fn") != "scripts/runreceipt/pack_v1.py::assert_runreceipt_artifacts":
    raise SystemExit("FAIL: assert_fn path mismatch")

print("OK: validate-verify-wire-missing-receipt-program-progress-v1 · sa-0522")
PY
bash scripts/validate-verify-wire-missing-receipt-v1.sh

#!/usr/bin/env bash
# validate-runreceipt-schema-hub-link-t2-crossref-v1.sh — sa-0555 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0555-runreceipt-schema-hub-link-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0505-runreceipt-schema-hub-link_LOCKED_v1.md"
schema = root / "product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md"
receipt = root / "receipts/sa-0505-receipt.json"

assert cross.is_file(), "missing sa-0555 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0505",
    "sa-0530",
    "sa-0555",
    "sa-0505-runreceipt-schema-hub-link_LOCKED_v1.md",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0505 attachment missing"
assert schema.is_file(), "RUNRECEIPT schema law missing"
assert receipt.is_file(), "canonical sa-0505 receipt missing"
for marker in ("run.jsonl", "summary.json", "pack_v1.py"):
    assert marker not in text, f"T2 cross-ref must not duplicate prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("runreceipt_schema_hub_link_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.runreceipt_schema_hub_link_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0505":
    raise SystemExit("FAIL: canonical_sa must be sa-0505")
if hook.get("t1_echo_sa") != "sa-0530":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0530")
if "sa-0555-runreceipt-schema-hub-link-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0555 attachment")

print("OK: validate-runreceipt-schema-hub-link-t2-crossref-v1 · canonical=sa-0505 · t1=sa-0530 · sa-0555")
PY

bash validate-runreceipt-schema-hub-link-v1.sh

#!/usr/bin/env bash
# validate-runreceipt-factory-p0-hook-t2-crossref-v1.sh — sa-0564 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0564-runreceipt-factory-p0-hook-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0514-runreceipt-factory-p0-hook_LOCKED_v1.md"
hub_data = root / "agent-control-panel/command-data.json"
receipt = root / "receipts/sa-0514-receipt.json"

assert cross.is_file(), "missing sa-0564 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0514",
    "sa-0539",
    "sa-0564",
    "sa-0514-runreceipt-factory-p0-hook_LOCKED_v1.md",
    "validate-runreceipt-factory-p0-hook-v1.sh",
    "runreceipt_parallel",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0514 attachment missing"
assert hub_data.is_file(), "command-data.json missing"
assert receipt.is_file(), "canonical sa-0514 receipt missing"
for marker in ("build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T2 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("runreceipt_factory_p0_hook_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.runreceipt_factory_p0_hook_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0514":
    raise SystemExit("FAIL: canonical_sa must be sa-0514")
if hook.get("t1_echo_sa") != "sa-0539":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0539")
if "sa-0564-runreceipt-factory-p0-hook-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0564 attachment")

print("OK: validate-runreceipt-factory-p0-hook-t2-crossref-v1 · canonical=sa-0514 · t1=sa-0539 · sa-0564")
PY

bash validate-runreceipt-factory-p0-hook-v1.sh

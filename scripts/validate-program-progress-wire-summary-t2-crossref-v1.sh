#!/usr/bin/env bash
# validate-program-progress-wire-summary-t2-crossref-v1.sh — sa-0565 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0565-program-progress-wire-summary-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0515-program-progress-wire-summary_LOCKED_v1.md"
receipt = root / "receipts/sa-0515-receipt.json"

assert cross.is_file(), "missing sa-0565 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0515",
    "sa-0540",
    "sa-0565",
    "sa-0515-program-progress-wire-summary_LOCKED_v1.md",
    "locked_plan.json",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0515 attachment missing"
assert receipt.is_file(), "canonical sa-0515 receipt missing"
for marker in ("physical_iphone", "g3_tailscale", "build-sina-command-panel.py", "hub_self_refresh", "wire_proof"):
    assert marker not in text, f"T2 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("program_progress_wire_summary_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.program_progress_wire_summary_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0515":
    raise SystemExit("FAIL: canonical_sa must be sa-0515")
if hook.get("t1_echo_sa") != "sa-0540":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0540")
if "sa-0565-program-progress-wire-summary-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0565 attachment")

print("OK: validate-program-progress-wire-summary-t2-crossref-v1 · canonical=sa-0515 · t1=sa-0540 · sa-0565")
PY

bash validate-program-progress-wire-summary-v1.sh

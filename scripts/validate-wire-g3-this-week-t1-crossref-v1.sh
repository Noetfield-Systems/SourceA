#!/usr/bin/env bash
# validate-wire-g3-this-week-t1-crossref-v1.sh — sa-0529 ACT T1 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0529-wire-g3-this-week-t1-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0504-wire-g3-this-week_LOCKED_v1.md"
receipt = root / "receipts/sa-0504-receipt.json"

assert cross.is_file(), "missing sa-0529 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in ("sa-0504", "sa-0529", "sa-0504-wire-g3-this-week_LOCKED_v1.md"):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0504 attachment missing"
assert receipt.is_file(), "canonical sa-0504 receipt missing"
for marker in ("strategic_synthesis_hub.this_week()", "WIRE_LANE_PROGRESS + hub Track"):
    assert marker not in text, f"T1 cross-ref must not duplicate prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("wire_g3_this_week_t1_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.wire_g3_this_week_t1_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0504":
    raise SystemExit("FAIL: canonical_sa must be sa-0504")
if "sa-0529-wire-g3-this-week-t1-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0529 attachment")

print("OK: validate-wire-g3-this-week-t1-crossref-v1 · canonical=sa-0504 · sa-0529")
PY

bash validate-wire-g3-this-week-v1.sh

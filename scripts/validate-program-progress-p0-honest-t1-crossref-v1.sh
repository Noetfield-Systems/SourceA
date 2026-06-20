#!/usr/bin/env bash
# validate-program-progress-p0-honest-t1-crossref-v1.sh — sa-0533 ACT T1 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0533-program-progress-p0-honest-t1-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0508-program-progress-p0-honest_LOCKED_v1.md"
hierarchy_law = root / "brain-os/system/GOAL_HIERARCHY_LOCKED_v1.md"
receipt = root / "receipts/sa-0508-receipt.json"

assert cross.is_file(), "missing sa-0533 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in ("sa-0508", "sa-0533", "sa-0508-program-progress-p0-honest_LOCKED_v1.md", "GOAL_HIERARCHY_LOCKED_v1.md"):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0508 attachment missing"
assert hierarchy_law.is_file(), "GOAL_HIERARCHY_LOCKED_v1.md missing"
assert receipt.is_file(), "canonical sa-0508 receipt missing"
for marker in ("validate-program-progress-factory-divergence-v1", "validate-no-fake-progress-form-v1"):
    assert marker not in text, f"T1 cross-ref must not duplicate chain validator prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("program_progress_p0_honest_t1_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.program_progress_p0_honest_t1_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0508":
    raise SystemExit("FAIL: canonical_sa must be sa-0508")
if "sa-0533-program-progress-p0-honest-t1-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0533 attachment")

print("OK: validate-program-progress-p0-honest-t1-crossref-v1 · canonical=sa-0508 · sa-0533")
PY

bash validate-program-progress-p0-honest-v1.sh

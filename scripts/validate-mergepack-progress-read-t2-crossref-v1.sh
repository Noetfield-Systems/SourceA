#!/usr/bin/env bash
# validate-mergepack-progress-read-t2-crossref-v1.sh — sa-0573 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0573-mergepack-progress-read-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0523-mergepack-progress-nonblocking-read_LOCKED_v1.md"
read_fn = root / "scripts/mergepack_progress_read_v1.py"
receipt = root / "receipts/sa-0523-receipt.json"

assert cross.is_file(), "missing sa-0573 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0523",
    "sa-0548",
    "sa-0573",
    "sa-0523-mergepack-progress-nonblocking-read_LOCKED_v1.md",
    "read_mergepack_progress_safe",
    "validate-mergepack-progress-read-program-progress-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0523 attachment missing"
assert read_fn.is_file(), "mergepack_progress_read_v1.py missing"
assert receipt.is_file(), "canonical sa-0523 receipt missing"
for marker in ("build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T2 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("mergepack_progress_read_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.mergepack_progress_read_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0523":
    raise SystemExit("FAIL: canonical_sa must be sa-0523")
if hook.get("t1_echo_sa") != "sa-0548":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0548")
if "sa-0573-mergepack-progress-read-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0573 attachment")

print("OK: validate-mergepack-progress-read-t2-crossref-v1 · canonical=sa-0523 · t1=sa-0548 · sa-0573")
PY

bash validate-mergepack-progress-read-program-progress-v1.sh

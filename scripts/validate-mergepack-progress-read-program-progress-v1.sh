#!/usr/bin/env bash
# sa-0523 — PROGRAM_PROGRESS mergepack_progress_read hook + safe read wired
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0523-mergepack-progress-nonblocking-read_LOCKED_v1.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path

root = Path(".")
helper = root / "scripts/mergepack_progress_read_v1.py"
if not helper.is_file():
    raise SystemExit("FAIL: missing mergepack_progress_read_v1.py")
text = helper.read_text(encoding="utf-8")
if "def read_mergepack_progress_safe" not in text:
    raise SystemExit("FAIL: helper missing read_mergepack_progress_safe")

for script in ("scripts/update-program-progress.py", "scripts/build-sina-daily-bowl.py"):
    body = (root / script).read_text(encoding="utf-8")
    if "read_mergepack_progress_safe" not in body:
        raise SystemExit(f"FAIL: {script} must use read_mergepack_progress_safe")

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("mergepack_progress_read") or {}
for key in ("crossref_doc", "read_fn", "non_blocking", "negative_validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.mergepack_progress_read missing {key}")
if "sa-0523-mergepack-progress" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0523 attachment")
if hook.get("read_fn") != "scripts/mergepack_progress_read_v1.py::read_mergepack_progress_safe":
    raise SystemExit("FAIL: read_fn path mismatch")
if hook.get("non_blocking") is not True:
    raise SystemExit("FAIL: non_blocking must be true")

print("OK: validate-mergepack-progress-read-program-progress-v1 · sa-0523")
PY
bash scripts/validate-mergepack-progress-nonblocking-v1.sh

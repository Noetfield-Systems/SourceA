#!/usr/bin/env bash
# council_strategic_brief workstream + eval_comparison validator strings must exist on disk.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export ROOT

python3 - <<'PY'
import os
import sys
from pathlib import Path

root = Path(os.environ["ROOT"])
scripts = root / "scripts"
sys.path.insert(0, str(scripts))

from council_strategic_brief import strategic_brief_payload  # noqa: E402

payload = strategic_brief_payload()
errors: list[str] = []
validators: set[str] = set()

for ws in payload.get("workstreams") or []:
    v = (ws.get("validator") or "").strip()
    if v:
        validators.add(v)
    for item in ws.get("validators") or []:
        if item:
            validators.add(str(item).strip())

ec = payload.get("eval_comparison") or {}
for arm_key in ("eval_1", "eval_1b"):
    arm = ec.get(arm_key) or {}
    v = (arm.get("validator") or "").strip()
    if v:
        validators.add(v)
    for item in arm.get("validators") or []:
        if item:
            validators.add(str(item).strip())

brief_path = root / "COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md"
brief_text = brief_path.read_text(encoding="utf-8") if brief_path.is_file() else ""

for v in sorted(validators):
    script = scripts / v
    if not script.is_file():
        errors.append(f"missing scripts/{v} (declared in council_strategic_brief)")
    if v.startswith("validate-eval") and brief_text and v not in brief_text:
        errors.append(f"COUNCIL_BRIEF missing eval validator mention: {v}")

eval_ws = {ws.get("id"): ws for ws in payload.get("workstreams") or []}
for wid in ("eval-1", "eval-1b"):
    ws = eval_ws.get(wid) or {}
    primary = ws.get("validator")
    if not primary:
        errors.append(f"workstream {wid} missing validator")
    elif not (scripts / primary).is_file():
        errors.append(f"workstream {wid} validator not on disk: {primary}")

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)
print(
    f"OK: validate-council-strategic-brief-eval-v1 · "
    f"{len(validators)} validator strings match disk + council brief"
)
PY

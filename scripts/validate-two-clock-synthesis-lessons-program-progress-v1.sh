#!/usr/bin/env bash
# sa-0524 — PROGRAM_PROGRESS two_clock_synthesis_lessons hook + validator wired
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0524-two-clock-synthesis-lessons_LOCKED_v1.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path

pp = json.loads(Path("PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("two_clock_synthesis_lessons") or {}
for key in ("crossref_doc", "canonical_case_study", "hub_field", "validator", "synthesis_lesson"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.two_clock_synthesis_lessons missing {key}")
if "sa-0524-two-clock-synthesis-lessons" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0524 attachment")
if hook.get("hub_field") != "two_clock_lesson":
    raise SystemExit("FAIL: hub_field must be two_clock_lesson")
if hook.get("synthesis_lesson") != "STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md §9.4":
    raise SystemExit("FAIL: synthesis_lesson mismatch")

text = Path("scripts/strategic_synthesis_hub.py").read_text(encoding="utf-8")
if "def two_clock_lesson" not in text:
    raise SystemExit("FAIL: strategic_synthesis_hub missing two_clock_lesson()")

print("OK: validate-two-clock-synthesis-lessons-program-progress-v1 · sa-0524")
PY
bash scripts/validate-two-clock-synthesis-lessons-v1.sh

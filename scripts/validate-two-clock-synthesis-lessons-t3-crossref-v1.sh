#!/usr/bin/env bash
# validate-two-clock-synthesis-lessons-t3-crossref-v1.sh — sa-0599 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0599-two-clock-synthesis-lessons-t3-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0524-two-clock-synthesis-lessons_LOCKED_v1.md"
case_study = root / "archive/attachments/2026-06-14/sa-0967-two-speed-clocks-strategic-slice-lane-p0-case-study_LOCKED_v1.md"
receipt = root / "receipts/sa-0524-receipt.json"

assert cross.is_file(), "missing sa-0599 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0524",
    "sa-0549",
    "sa-0574",
    "sa-0599",
    "sa-0524-two-clock-synthesis-lessons_LOCKED_v1.md",
    "sa-0967-two-speed-clocks",
    "two_clock_lesson",
    "validate-two-clock-synthesis-lessons-program-progress-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0524 attachment missing"
assert case_study.is_file(), "canonical sa-0967 case study missing"
assert receipt.is_file(), "canonical sa-0524 receipt missing"
for marker in ("build-sina-command-panel.py", "hub_self_refresh", "_RAW_SECTIONS"):
    assert marker not in text, f"T3 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("two_clock_synthesis_lessons_t3_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "t2_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.two_clock_synthesis_lessons_t3_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0524":
    raise SystemExit("FAIL: canonical_sa must be sa-0524")
if hook.get("t1_echo_sa") != "sa-0549":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0549")
if hook.get("t2_echo_sa") != "sa-0574":
    raise SystemExit("FAIL: t2_echo_sa must be sa-0574")
if "sa-0599-two-clock-synthesis-lessons-t3-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0599 attachment")

print("OK: validate-two-clock-synthesis-lessons-t3-crossref-v1 · canonical=sa-0524 · t2=sa-0574 · sa-0599")
PY

bash validate-two-clock-synthesis-lessons-program-progress-v1.sh

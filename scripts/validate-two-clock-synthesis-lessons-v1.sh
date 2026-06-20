#!/usr/bin/env bash
# sa-0524 — two-clock slice ∥ lane P0 documented in synthesis lessons
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import importlib.util
from pathlib import Path

root = Path.cwd().parent
attach = root / "archive/attachments/2026-06-14/sa-0524-two-clock-synthesis-lessons_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0967-two-speed-clocks-strategic-slice-lane-p0-case-study_LOCKED_v1.md"
synth_doc = root / "STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md"
assert attach.is_file(), "missing sa-0524 attachment"
assert canonical.is_file(), "missing sa-0967 canonical case study"
assert synth_doc.is_file(), "missing STRATEGIC_NEXT_STEPS_SYNTHESIS"

synth_text = synth_doc.read_text(encoding="utf-8")
if "Two clocks normal (slice ∥ lane P0)" not in synth_text:
    raise SystemExit("FAIL: STRATEGIC_NEXT_STEPS §9 lesson #4 missing")

spec = importlib.util.spec_from_file_location("ssh", Path("strategic_synthesis_hub.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

payload = mod.strategic_synthesis_payload()
lessons = payload.get("lessons") or []
if not any("Two clocks" in str(x) for x in lessons):
    raise SystemExit(f"FAIL: hub lessons missing two-clock entry: {lessons}")

tcl = payload.get("two_clock_lesson") or {}
for key in ("lesson_id", "summary", "crossref_doc", "canonical_case_study", "clock_a", "clock_b"):
    if key not in tcl:
        raise SystemExit(f"FAIL: two_clock_lesson missing {key}")
if "sa-0524-two-clock-synthesis-lessons" not in str(tcl.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0524 attachment")
if "sa-0967-two-speed-clocks" not in str(tcl.get("canonical_case_study", "")):
    raise SystemExit("FAIL: canonical_case_study must point to sa-0967")

if payload.get("do_now_primary") != "STRATEGIC-SLICE":
    raise SystemExit(f"FAIL: do_now_primary {payload.get('do_now_primary')}")

goals = {g.get("id"): g for g in payload.get("strategic_goals") or []}
if goals.get("goal-commercial-revenue", {}).get("title", "").find("lane P0") < 0:
    raise SystemExit("FAIL: goal-commercial-revenue must reference lane P0")

print("OK: validate-two-clock-synthesis-lessons-v1 · sa-0524")
PY

# sa-0524 — two-clock slice ∥ parallel lane P0 in synthesis lessons

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T13:40Z · **Phase:** s5-P3 commercial · **Tier:** T0

## Problem

`strategic_synthesis_hub` exposed a one-line lesson (`"Two clocks: slice ∥ lane P0"`) without a commercial-lane crosswalk to locked synthesis prose or the sa-0967 case study.

## Two-clock model (commercial lane)

| Clock | Namespace | Hub headline? | PASS signal |
|-------|-----------|---------------|-------------|
| **A — Strategic slice** | STRATEGIC-SLICE · WTM D-phase | **Yes** — sole founder P0 | Eval-1b live · dispatch eligible · spine bridge |
| **B — Parallel lane P0** | TrustField · Wire · MergePack · FORGE | Parallel cards only | Lane deposit · outreach receipt · vault attest · `verify:wire` |

**Law:** `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` §9 lesson #4 · canonical deep-dive `sa-0967-two-speed-clocks-strategic-slice-lane-p0-case-study_LOCKED_v1.md`.

## Machine proof

| Check | Result |
|-------|--------|
| `strategic_synthesis_hub.two_clock_lesson` | Wired in `/api/strategic-synthesis-v1` payload |
| `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` §9 | Lesson #4 aligned |
| `validate-two-clock-synthesis-lessons-v1.sh` | PASS |

## PROGRAM_PROGRESS hook

`signals_auto.two_clock_synthesis_lessons` → this attachment + hub `two_clock_lesson` block.

*End sa-0524*

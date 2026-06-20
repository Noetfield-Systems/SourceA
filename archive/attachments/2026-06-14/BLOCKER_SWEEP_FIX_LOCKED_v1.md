# Blocker sweep + fix 2026-06-14

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Authority:** ASF — CHECK ALL BLOCKERS AND FIX THEM ALL

## Fixed (executor)

| Blocker | Fix |
|---------|-----|
| **Worker turn open** sa-0953 CHECK | Broker submit CHECK round · turn closed · queue advanced to ACT pos 26 |
| **sa-TEST turn bind drift** | `goal1-worker-turn-bind-v1.json` → sa-0953 pos 25/156 |
| **B-001 ingest pipeline** | `repair_promptos_rejected_ingest_v1.py` — 5/5 rejected YAML re-ingested · folder empty |
| **find_critical: auto-run flag** | Created `~/.sina/auto-run-disabled-v1.flag` (law-required) |
| **find_critical: system-audits loop** | Added README_INDEX pointer to `BRAIN_FULL_TRANSFER_PROMPT_LOCKED_v1.md` |
| **ARCHITECT_REPORT B-001** | `system_blockers: []` · blocker_count 0 |

## Validators PASS (post-fix)

- validate-two-hub-v1
- validate-founder-agentic-commercial-policy-v1
- validate-system-audits-mandatory-loop-v1
- worker cursor_entry_gate (role worker)

## Intentional holds (not bugs — ASF law)

| Item | Why left |
|------|----------|
| **SINGLE_SA / kill_flag** | Factory paused — next deliver needs ASF resume drain |
| **MP-SHIP** | Vercel deployment protection — founder business action |
| **WIRE-G3** | Tailscale wire proof — human gate |
| **GLOBAL_BLOCKERS** seven77 | board / vault keys — human |
| **virlux Railway 404** | Documented fallback to Vercel URL |

## Script added

`scripts/repair_promptos_rejected_ingest_v1.py` — heals SinaPromptOS rejected inbox (missing next_action).

*End BLOCKER_SWEEP_FIX_LOCKED_v1*

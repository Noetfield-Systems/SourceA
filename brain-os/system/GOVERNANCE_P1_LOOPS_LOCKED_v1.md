# Governance P1 loops (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_tag:** `AUTO-TRACE-GOV-P1-LOOPS-v1`  
**agent:** `Auto`  
**Locked:** 2026-06-08 · **Parent:** `EXECUTION_AUTHORITY_MAP_LOCKED_v1.md` · `authority.yaml`

## P0 (shipped)

`authority.yaml` · `next-execution-pointer-v1.json` · `runtime/execution.json` · `validate-authority-runtime-v1.sh`

## P1 (enforce)

| # | Enforcement | Script |
|---|-------------|--------|
| 1 | Rail A blocks manual inject | `authority_enforce_p1_lib.check_rail_manual_inject` |
| 2 | Worker prompt cannot change pick | `authority_enforce_p1_lib.check_prompt_pick_authority` |
| 3 | Brain SYNC cites specialist traces | `~/.sina/brain/reconciled_decision.yaml` |
| 4 | Pointer drift warning on broker | `authority_enforce_p1_lib.check_pointer_alignment` |
| 5 | Verify | `scripts/validate-authority-p1-v1.sh` |

## Brain writes (Execution Core only)

`~/.sina/brain/reconciled_decision.yaml` — must cite `governance_goal_specialist-*` / `COMMERCIAL_GOAL-*` when used.

`~/.sina/brain/execution_core_handoff-v1.json` — optional handoff receipt before non-pointer sa.

## P1.5 (live verification — 2026-06-08)

| # | Item | Implementation |
|---|------|----------------|
| 1 | Advisor composer breach | `cursor_entry_gate.py --scan-text` + `AUTHORITY_ADVISOR_PICK_BREACH` |
| 2 | Reconciled before inject | `check_reconciled_before_inject` + orchestrator `pre_inject` SYNC |
| 3 | ASF-signed manual_fallback | `validate_manual_fallback` — rejects bare `true` |
| 4 | Event contract | `EVENT_CONTRACT.yaml` + `execution_event_log_v1.py` |

**Unified lock:** `AUTHORITY_RUNTIME_VERIFICATION_LOCKED_v1.md` — five-source convergence · proof classes · next move.

**Claude honest gap:** `validate-authority-p1-v1.sh PASS` = code exists; boundary test + live AUTO-RUN prove behavior.

## L3 done when

- `validate-authority-convergence-v1.sh` PASS
- Rail A + manual inject blocked in `worker_inject_lib`
- Broker path uses pointer alignment check
- P1.5 hooks present · full AUTO-RUN event chain = L3.5

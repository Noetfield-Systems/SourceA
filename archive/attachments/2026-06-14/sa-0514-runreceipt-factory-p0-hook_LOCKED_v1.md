# sa-0514 — RunReceipt factory hook in command center P0 card

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**Law:** `GOAL_HIERARCHY_LOCKED_v1.md` · `ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md` · sa-0967 two-speed clocks

## Hook logged

Hub founder P0 card (`command_center.founder.p0`) is **STRATEGIC-SLICE** (Clock A north star).  
Parallel factory SKU is nested as **`runreceipt_parallel`** — not the headline P0 id.

| Field | Value |
|-------|-------|
| p0.id | STRATEGIC-SLICE |
| runreceipt_parallel.id | P0-RUNRECEIPT |
| runreceipt_parallel.thread | THREAD-FACTORY |
| runreceipt_parallel.title | RunReceipt — agent run PASS/FAIL receipt |
| runreceipt_parallel.note | Factory parallel only — THREAD-FACTORY when ASF names it |

## Machine sources

| Artifact | Role |
|----------|------|
| `scripts/sina_command_lib.py` → `founder_automation_p0()` | Builds P0 + `runreceipt_parallel` from bowl / `PROGRAM_PROGRESS` |
| `agent-control-panel/command-data.json` | Hub projection SSOT |
| `PROGRAM_PROGRESS.json` → `parallel_plans` id `P0-RUNRECEIPT` | Factory parallel plan at 100% |
| `product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md` | Schema law (sa-0502) |

## Two-speed alignment

- **Clock A:** STRATEGIC-SLICE hero on Today tab  
- **Clock B factory parallel:** RunReceipt visible via `runreceipt_parallel` — does not replace spine headline  

Validator: `scripts/validate-runreceipt-factory-p0-hook-v1.sh`

*End sa-0514*

# sa-0517 — PRODUCT_FACTORY roadmap vs hub progress signals

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**Law:** sa-0967 two-speed clocks · `GOAL_HIERARCHY_LOCKED_v1.md` · `ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md`

## Roadmap vs hub (not drift)

| Source | Factory P0 signal | Hub / PROGRAM_PROGRESS signal | Verdict |
|--------|-------------------|-------------------------------|---------|
| `PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md` | MergePack BUILD queue | `MERGEPACK-L1` parallel plan 85% · `active_parallel` | **Aligned** |
| Factory rescore law | RunReceipt factory SKU | `locks.p0_sku` RunReceipt · `P0-RUNRECEIPT` 100% | **Aligned** |
| Founder north star | (roadmap lane only) | `locks.founder_p0_id` STRATEGIC-SLICE · hub P0 hero | **Aligned** — Clock A ≠ Clock B |
| `command-data.json` | Factory roadmap indexed | `runreceipt_parallel` + `roadmaps_goals` parallel_plans | **Aligned** |

## Two-speed note

Roadmap doc P0 header names **MergePack** as factory queue SKU. Hub headline stays **STRATEGIC-SLICE**; RunReceipt is **factory parallel only** — intentional per rescore + sa-0967.

Validator: `scripts/validate-product-factory-roadmap-hub-signals-v1.sh`

*End sa-0517*

# Brain → Governance wire gap (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF governance issue  
**Fix:** `scripts/brain_governance_wire_v1.py` · `~/.sina/governance-brain-wire-v1.json`

---

## Root cause

Governance Specialist ran **without reading Brain decisions**. Cascade only handled founder latch text — not Brain LOCKED law or `reconciled_decision.yaml`.

**Stale poison on disk:**
- `~/.sina/brain/reconciled_decision.yaml` — AUTO-RUN · sa-0790 · Jun 12
- `~/.sina/brain-current-action-v1.json` — sa-0798

**Live queue head:** sa-0106 (OpenRouter s1 pack)

---

## Permanent fix

| Layer | Change |
|-------|--------|
| `brain_governance_wire_v1.py` | Sync brain snapshot + bind `active_decisions[]` |
| `governance_center_run_v1.py` | Step `brain_governance_wire` every cycle |
| `governance_stairlift_sync_v1.py` | Watch SUPER_FAST_HUB + wire JSON |
| `governance-specialist-in-charge.mdc` | Mandatory wire before any reply |

**Rule:** When `reconciled_decision.stale=true` → **IGNORE** · obey `active_decisions[]`.

---

*End BRAIN_GOVERNANCE_WIRE_GAP_LOCKED_v1*

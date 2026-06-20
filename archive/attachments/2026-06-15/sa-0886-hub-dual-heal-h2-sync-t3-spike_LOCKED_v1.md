# sa-0886 — hub_dual_heal_v1 H2 sync after H1 light refresh (T3 spike)

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **Phase:** phase-s8-hub-ui-ux · **Tier:** T3  
**Task:** Run `hub_dual_heal_v1` — H2 sync after H1 light refresh  
**Receipt:** `~/.sina/two-hub-heal-receipt-v1.json` · reason `sa-0886-T3-spike`

---

## Result

| Step | OK | Notes |
|------|-----|-------|
| h1_worker_hub_heal | partial | Ran; H1 shell age drove `health=critical` at probe (dual_proof_ok true) |
| h2_registry_sync | **PASS** | pending_total 12 |
| h2_payload_refresh | **PASS** | H2 cache invalidated · fresh payload |
| agentic_pipeline_v2 | **PASS** | fast tier |
| **Overall dual heal** | **PASS** | `ok: true` — H2 sync primary objective met |

| Hub | Staleness after heal |
|-----|----------------------|
| H1 `/` | critical · age ~1690s at run · dual_proof_ok true · latches green |
| H2 `/machines/` | **fresh** · age 1.2s · form_aligned true |

**Law:** H2 sync is primary for this SA; H1 `critical` = shell age not dual_proof failure (sa-0867 cross-ref).

---

## Verify

```bash
python3 scripts/hub_dual_heal_v1.py --json --reason sa-0886-T3-spike
bash scripts/worker_verify_fast_v1.sh  # exit 52 — validate-super-fast-hub H1 health=critical (staleness)
```

**T3 verdict:** Document spike **SHIP** · H2 objective PASS · H1 light refresh deferred to founder Safety tap or next heal cycle.

---

## Pointers

- `scripts/hub_dual_heal_v1.py`
- `SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md`
- `archive/attachments/2026-06-15/sa-0867-h2-light-refresh-no-panel-build-t2-crossref_LOCKED_v1.md`

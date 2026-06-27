# sa-next-0289 — SourceA next plan

**Version:** 1 · **Tier:** T3 · **Phase:** LATER
**Theme:** t03-landing · Landing & web
**Workstream:** w09-integrate · Integrate
**Slice:** 9/10 · **Receipt gate:** revenue_outreach
**Legacy upgrade:** UP-0289 (CU · Chat Unify machines)
**SSOT:** `docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md`

## Scope

Revenue Engine · Proof Pack · landing · factory-runtime-spike

## Task

**Session unify audit** — Chat Unify machines (CU).

Landing & web · Integrate · slice 9/10.
Bounded path only. Receipt logged before done.
Parent: Revenue Engine · Proof Pack · landing · factory-runtime-spike.
Priority doc: `brain-os/plan-registry/SOURCEA-PRIORITY.md`.

## Verify

```bash
cd ~/Desktop/SourceA && python3 scripts/sourcea_revenue_engine_crm_v1.py summary --json
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-next-0289`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md`
3. No cross-lane edits without EDIT ALLOWED

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: merge_upgrade_888_into_portfolio_next_v1.py v1
legacy_upgrade_id: UP-0289

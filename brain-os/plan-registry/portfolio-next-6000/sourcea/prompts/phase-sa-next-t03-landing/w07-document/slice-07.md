# sa-next-0267 — SourceA next plan

**Version:** 1 · **Tier:** T2 · **Phase:** LATER
**Theme:** t03-landing · Landing & web
**Workstream:** w07-document · Document
**Slice:** 7/10 · **Receipt gate:** runtime_spike_pass
**Legacy upgrade:** UP-0267 (CU · Chat Unify machines)
**SSOT:** `docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md`

## Scope

Revenue Engine · Proof Pack · landing · factory-runtime-spike

## Task

**Webhook relay HA** — Chat Unify machines (CU).

Landing & web · Document · slice 7/10.
Bounded path only. Receipt on disk before done.
Parent: Revenue Engine · Proof Pack · landing · factory-runtime-spike.
Priority doc: `brain-os/plan-registry/SOURCEA-PRIORITY.md`.

## Verify

```bash
cd ~/Desktop/SourceA && python3 scripts/sourcea_revenue_engine_crm_v1.py summary --json
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-next-0267`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md`
3. No cross-lane edits without EDIT ALLOWED

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: merge_upgrade_888_into_portfolio_next_v1.py v1
legacy_upgrade_id: UP-0267

# sa-next-0342 — SourceA next plan

**Version:** 1 · **Tier:** T0 · **Phase:** LATER
**Theme:** t04-runtime · Factory runtime
**Workstream:** w05-operate · Operate
**Slice:** 2/10 · **Receipt gate:** enterprise_signal
**Legacy upgrade:** UP-0342 (CLD · Cloud motor & FBE)
**SSOT:** `docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md`

## Scope

Revenue Engine · Proof Pack · landing · factory-runtime-spike

## Task

**Worker dispatch receipt** — Cloud motor & FBE (CLD).

Factory runtime · Operate · slice 2/10.
Bounded path only. Receipt on disk before done.
Parent: Revenue Engine · Proof Pack · landing · factory-runtime-spike.
Priority doc: `brain-os/plan-registry/SOURCEA-PRIORITY.md`.

## Verify

```bash
cd ~/Desktop/SourceA && python3 scripts/sourcea_revenue_engine_crm_v1.py summary --json
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-next-0342`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md`
3. No cross-lane edits without EDIT ALLOWED

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: merge_upgrade_888_into_portfolio_next_v1.py v1
legacy_upgrade_id: UP-0342

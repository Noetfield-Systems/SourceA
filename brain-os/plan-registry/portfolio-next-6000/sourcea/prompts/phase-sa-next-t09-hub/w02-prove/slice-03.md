# sa-next-0813 — SourceA next plan

**Version:** 1 · **Tier:** T1 · **Phase:** MOONSHOT
**Theme:** t09-hub · Hub & control plane
**Workstream:** w02-prove · Prove
**Slice:** 3/10 · **Receipt gate:** runtime_spike_pass
**Legacy upgrade:** UP-0813 (HUB · Hub & standalone apps)
**SSOT:** `docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md`

## Scope

Revenue Engine · Proof Pack · landing · factory-runtime-spike

## Task

**Machine Hub H2 ship** — Hub & standalone apps (HUB).

Hub & control plane · Prove · slice 3/10.
Bounded path only. Receipt on disk before done.
Parent: Revenue Engine · Proof Pack · landing · factory-runtime-spike.
Priority doc: `brain-os/plan-registry/SOURCEA-PRIORITY.md`.

## Verify

```bash
cd ~/Desktop/SourceA && python3 scripts/sourcea_revenue_engine_crm_v1.py summary --json
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-next-0813`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md`
3. No cross-lane edits without EDIT ALLOWED

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: merge_upgrade_888_into_portfolio_next_v1.py v1
legacy_upgrade_id: UP-0813

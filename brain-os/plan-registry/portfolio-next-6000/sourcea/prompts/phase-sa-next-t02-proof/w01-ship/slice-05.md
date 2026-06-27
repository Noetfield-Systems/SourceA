# sa-next-0105 — SourceA next plan

**Version:** 1 · **Tier:** T2 · **Phase:** NEXT
**Theme:** t02-proof · Proof & receipts
**Workstream:** w01-ship · Ship
**Slice:** 5/10 · **Receipt gate:** design_partner
**Legacy upgrade:** UP-0105 (WEB · Storefront & site)
**SSOT:** `docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md`

## Scope

Revenue Engine · Proof Pack · landing · factory-runtime-spike

## Task

**Forensic proof page** — Storefront & site (WEB).

Proof & receipts · Ship · slice 5/10.
Bounded path only. Receipt logged before done.
Parent: Revenue Engine · Proof Pack · landing · factory-runtime-spike.
Priority doc: `brain-os/plan-registry/SOURCEA-PRIORITY.md`.

## Verify

```bash
cd ~/Desktop/SourceA && python3 scripts/sourcea_revenue_engine_crm_v1.py summary --json
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-next-0105`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md`
3. No cross-lane edits without EDIT ALLOWED

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: merge_upgrade_888_into_portfolio_next_v1.py v1
legacy_upgrade_id: UP-0105

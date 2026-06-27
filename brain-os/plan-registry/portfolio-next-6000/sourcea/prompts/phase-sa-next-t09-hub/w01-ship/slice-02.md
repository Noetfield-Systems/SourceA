# sa-next-0802 — SourceA next plan

**Version:** 1 · **Tier:** T0 · **Phase:** MOONSHOT
**Theme:** t09-hub · Hub & control plane
**Workstream:** w01-ship · Ship
**Slice:** 2/10 · **Receipt gate:** proof_pack_sealed
**Legacy upgrade:** UP-0802 (MED · Media & commercial factory)
**SSOT:** `docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md`

## Scope

Revenue Engine · Proof Pack · landing · factory-runtime-spike

## Task

**Portfolio reel** — Media & commercial factory (MED).

Hub & control plane · Ship · slice 2/10.
Bounded path only. Receipt logged before done.
Parent: Revenue Engine · Proof Pack · landing · factory-runtime-spike.
Priority doc: `brain-os/plan-registry/SOURCEA-PRIORITY.md`.

## Verify

```bash
cd ~/Desktop/SourceA && python3 scripts/sourcea_revenue_engine_crm_v1.py summary --json
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-next-0802`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md`
3. No cross-lane edits without EDIT ALLOWED

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: merge_upgrade_888_into_portfolio_next_v1.py v1
legacy_upgrade_id: UP-0802

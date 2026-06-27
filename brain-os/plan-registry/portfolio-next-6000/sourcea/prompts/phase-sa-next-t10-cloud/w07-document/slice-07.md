# sa-next-0967 — SourceA next plan

**Version:** 1 · **Tier:** T2 · **Phase:** MOONSHOT
**Theme:** t10-cloud · Cloud & integrate
**Workstream:** w07-document · Document
**Slice:** 7/10 · **Receipt gate:** runtime_spike_pass
**SSOT:** `docs/PORTFOLIO_NEXT_6000_PLANS_LOCKED_v1.md`

## Scope

Revenue Engine · Proof Pack · landing · factory-runtime-spike

## Task

SourceA · Cloud & integrate · Document · slice 7/10 — P2 — harden · validate · document. Bounded path only. Receipt logged before done. Parent: Revenue Engine · Proof Pack · landing · factory-runtime-spike. Priority doc: `brain-os/plan-registry/SOURCEA-PRIORITY.md`.

## Verify

```bash
cd ~/Desktop/SourceA && python3 scripts/sourcea_revenue_engine_crm_v1.py summary --json
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-next-0967`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md`
3. No cross-lane edits without EDIT ALLOWED

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_next_6000_plans_v1.py v1

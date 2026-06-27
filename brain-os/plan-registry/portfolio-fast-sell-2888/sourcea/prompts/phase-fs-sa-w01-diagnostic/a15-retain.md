# fs-sa-0015 — Fast-sell plan

**Version:** 1 · **Tier:** T2 · **Phase:** NOW
**Lane:** SourceA · **Wedge:** w01-diagnostic · Tier-1 diagnostic / audit wedge
**Action:** a15-retain · Retainer renewal touch
**Comp anchor:** Trigger.dev · Langfuse
**Tier 1:** Asset B diagnostic $3K slice
**Tier 2:** DFY $3–10K + retainer
**SSOT:** `docs/PORTFOLIO_TWO_TIER__PRO_ANALYSIS_LOCKED_v1.md`

## Task

Fast-sell: SourceA · Tier-1 diagnostic / audit wedge · Retainer renewal touch. Ship smallest slice that moves a buyer toward **Asset B diagnostic $3K slice** with a path to **DFY $3–10K + retainer**. Receipt logged before done.

## Verify

```bash
python3 ~/Desktop/SourceA/scripts/sourcea_revenue_engine_crm_v1.py summary --json
```

## Closeout

1. `status: done` in REGISTRY.json for `fs-sa-0015`
2. Log economic signal if outreach closed (W3 / NW)
3. Bounded path only — no cross-lane without EDIT ALLOWED

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: FAST SELL · PLAN WITH NO ASF
generator: generate_portfolio_fast_sell_2888_plans_v1.py v1

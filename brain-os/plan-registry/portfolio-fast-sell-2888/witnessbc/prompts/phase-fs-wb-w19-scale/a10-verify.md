# fs-wb-0352 — Fast-sell plan

**Version:** 1 · **Tier:** T0 · **Phase:** MOONSHOT
**Lane:** WitnessBC · **Wedge:** w19-scale · Repeatable playbook + template
**Action:** a10-verify · Verify PASS receipt
**Comp anchor:** LowerPlane · Delve
**Tier 1:** Public proof page pilot
**Tier 2:** Civic annual + audit export
**SSOT:** `docs/PORTFOLIO_TWO_TIER__PRO_ANALYSIS_LOCKED_v1.md`

## Task

Fast-sell: WitnessBC · Repeatable playbook + template · Verify PASS receipt. Ship smallest slice that moves a buyer toward **Public proof page pilot** with a path to **Civic annual + audit export**. Receipt on disk before done.

## Verify

```bash
curl -sf https://witnessbc.com/health || test -f ~/Desktop/SourceA/witnessbc-site/content/pricing.html
```

## Closeout

1. `status: done` in REGISTRY.json for `fs-wb-0352`
2. Log economic signal if outreach closed (W3 / NW)
3. Bounded path only — no cross-lane without EDIT ALLOWED

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: FAST SELL · PLAN WITH NO ASF
generator: generate_portfolio_fast_sell_2888_plans_v1.py v1

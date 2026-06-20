# sa-mkt-0812 — Vellum · Pricing & packaging

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-pricing
**Stack:** SourceA · ** row:** 17 · **Phase:** phase-c17-vellum
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

| Field | Value |
|-------|-------|
| Company | Vellum |
| Product | LLM ops platform |
| What they sell | Prompt deployment, eval, and monitoring for production LLM apps |
| Who buys | LLM product teams |
| Pricing | Team/enterprise custom tiers |
| How it runs | Version prompts; run evals; monitor production |
| Source links | https://www.vellum.ai |
| Portfolio lesson | Versioned prompt + eval on every dispatch |

## Task (Critical — smallest shippable slice with receipt)

Map Vellum revenue model (Seat + usage enterprise) to our `SourceA agency + Buyer-1 pricing narrative` tier names — no hidden fees theater

## Implementation extraction

`Vellum · Pricing & packaging` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0812`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Vellum` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2

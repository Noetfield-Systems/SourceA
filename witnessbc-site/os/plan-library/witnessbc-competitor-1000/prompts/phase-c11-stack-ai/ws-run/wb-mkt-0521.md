# wb-mkt-0521 — Stack AI · Run history & proof

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-run
**Stack:** WitnessBC · **Competitor row:** 31 · **Phase:** phase-c11-stack-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Stack AI |
| Product | Enterprise AI agents |
| What they sell | No-code enterprise AI agents with SOC2/HIPAA compliance |
| Who buys | Regulated enterprise IT |
| Pricing | Free 500 runs/mo; enterprise custom |
| How it runs | Build agent workflows; deploy with access control |
| Source links | https://www.stack-ai.com |
| Portfolio lesson | SOC2/HIPAA lane packaging for Witness AI Ops retainer |

## Task (Critical — smallest shippable slice with receipt)

From https://www.stack-ai.com document Stack AI run/history UX: Build agent workflows; deploy with access control — map to `Witness AI Flow install replay demo + 6 receipt types`

## Implementation extraction

`Stack AI · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0521`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Stack AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

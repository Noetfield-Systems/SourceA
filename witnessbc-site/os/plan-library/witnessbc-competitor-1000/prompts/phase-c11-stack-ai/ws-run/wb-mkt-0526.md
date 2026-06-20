# wb-mkt-0526 — Stack AI · Run history & proof

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-run
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

## Task (Medium — hardening, validator, docs)

Surface run id + link in Hub/factory glance for founder audit

## Implementation extraction

`Stack AI · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0526`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Stack AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

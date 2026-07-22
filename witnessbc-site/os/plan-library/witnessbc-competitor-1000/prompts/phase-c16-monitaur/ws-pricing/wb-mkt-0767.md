# wb-mkt-0767 — Monitaur · Pricing & packaging

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-pricing
**Stack:** WitnessBC · **Competitor row:** 36 · **Phase:** phase-c16-monitaur
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Monitaur |
| Product | ML governance lifecycle |
| What they sell | Governance for ML models from development to production |
| Who buys | Regulated ML teams |
| Pricing | Enterprise custom |
| How it runs | Policy workflows; model documentation; audit trail |
| Source links | https://www.monitaur.ai |
| Portfolio lesson | Model/agent inventory for policy packs |

## Task (Medium — hardening, validator, docs)

Add upgrade CTA path: sandbox/free → paid bay matching Monitaur upgrade pattern where applicable

## Implementation extraction

`Monitaur · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0767`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Monitaur` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

# wb-mkt-0779 — Monitaur · Run history & proof

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-run
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

## Task (Low — research, defer note, or compare-only)

Regression: rerun verify after run UI change

## Implementation extraction

`Monitaur · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0779`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Monitaur` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

# wb-mkt-0926 — Voiceflow · Run history & proof

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-run
**Stack:** WitnessBC · **Competitor row:** 39 · **Phase:** phase-c19-voiceflow
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Voiceflow |
| Product | Conversation agent builder |
| What they sell | Build chat and voice agents with logs and analytics |
| Who buys | CX and product teams |
| Pricing | Free + paid team tiers — https://www.voiceflow.com/pricing |
| How it runs | Visual builder; deploy channels; conversation logs |
| Source links | https://www.voiceflow.com |
| Portfolio lesson | Conversation run history on agent loops |

## Task (Medium — hardening, validator, docs)

Surface run id + link in Hub/factory glance for founder audit

## Implementation extraction

`Voiceflow · Run history & proof` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0926`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Voiceflow` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

# wb-mkt-0158 — Scrut Automation · Buyer-visible UX

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-ux
**Stack:** WitnessBC · **Competitor row:** 24 · **Phase:** phase-c04-scrut-automation
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Scrut Automation |
| Product | GRC automation |
| What they sell | Compliance automation for SOC 2, ISO, and risk management |
| Who buys | Mid-market compliance leads |
| Pricing | Custom mid-market pricing |
| How it runs | Control monitoring; evidence vault; audit readiness |
| Source links | https://scrut.io |
| Portfolio lesson | Shadow-mode parallel install narrative for Witness AI Flow |

## Task (Low — research, defer note, or compare-only)

Reject abstract rename — keep market words buyers know from Scrut Automation (GRC automation)

## Implementation extraction

`Scrut Automation · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0158`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Scrut Automation` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

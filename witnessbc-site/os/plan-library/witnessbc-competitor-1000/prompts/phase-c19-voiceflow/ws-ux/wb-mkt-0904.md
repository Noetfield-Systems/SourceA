# wb-mkt-0904 — Voiceflow · Buyer-visible UX

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-ux
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

## Task (High — next sprint parity with competitor)

E2E or glance check: founder can see `Buyer-visible UX` outcome without Terminal; receipt timestamp on disk

## Implementation extraction

`Voiceflow · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0904`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Voiceflow` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

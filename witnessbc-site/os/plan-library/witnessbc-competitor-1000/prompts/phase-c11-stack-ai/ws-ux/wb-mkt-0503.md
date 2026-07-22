# wb-mkt-0503 — Stack AI · Buyer-visible UX

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-ux
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

## Task (High — next sprint parity with competitor)

Add `witnessbc.com pricing + toolkits hub` UI field or copy block implementing smallest slice of `SOC2/HIPAA lane packaging for Witness AI Ops retainer`; preserve honest tier label

## Implementation extraction

`Stack AI · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0503`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Stack AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

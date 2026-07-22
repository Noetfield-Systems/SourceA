# wb-mkt-0633 — Lakera Guard · Onboarding & PLG

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-onboard
**Stack:** WitnessBC · **Competitor row:** 33 · **Phase:** phase-c13-lakera-guard
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Lakera Guard |
| Product | GenAI security |
| What they sell | Runtime guardrails for LLM apps — block injections and policy violations |
| Who buys | AppSec and platform teams |
| Pricing | Enterprise custom |
| How it runs | API middleware scans prompts/responses; logs decisions |
| Source links | https://www.lakera.ai |
| Portfolio lesson | Policy at dispatch allow/block log |

## Task (High — next sprint parity with competitor)

Add checklist or wizard step on `witnessbc.com pricing + toolkits hub` — no Terminal required

## Implementation extraction

`Lakera Guard · Onboarding & PLG` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0633`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Lakera Guard` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

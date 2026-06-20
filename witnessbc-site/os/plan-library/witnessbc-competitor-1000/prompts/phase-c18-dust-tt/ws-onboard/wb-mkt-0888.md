# wb-mkt-0888 — Dust.tt · Onboarding & PLG

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-onboard
**Stack:** WitnessBC · **Competitor row:** 38 · **Phase:** phase-c18-dust-tt
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Dust.tt |
| Product | Enterprise AI assistants |
| What they sell | Build internal AI assistants connected to company data |
| Who buys | Enterprise ops teams |
| Pricing | Team tiers custom |
| How it runs | Template assistants; team workspaces; usage controls |
| Source links | https://dust.tt |
| Portfolio lesson | Packaged team templates for first install |

## Task (Low — research, defer note, or compare-only)

Integrate `Policy packs mapped to agent receipt gates` hook needed for onboarding (API key, MCP, connector)

## Implementation extraction

`Dust.tt · Onboarding & PLG` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0888`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Dust.tt` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

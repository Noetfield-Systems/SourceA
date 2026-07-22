# wb-mkt-0856 — Dust.tt · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
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

## Task (Medium — hardening, validator, docs)

Add `Witness AI Flow install replay demo + 6 receipt types` mock row labeled mock_only until live — match Dust.tt run/history metaphor not invented name

## Implementation extraction

`Dust.tt · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0856`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Dust.tt` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

# wb-mkt-0301 — Secureframe · Buyer-visible UX

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-ux
**Stack:** WitnessBC · **Competitor row:** 27 · **Phase:** phase-c07-secureframe
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Secureframe |
| Product | Automated compliance |
| What they sell | Automate evidence for SOC 2, ISO 27001, and more |
| Who buys | Mid-market SaaS |
| Pricing | Custom; typically $10k+ (market) |
| How it runs | Integrations → continuous monitoring → audit export |
| Source links | https://secureframe.com |
| Portfolio lesson | Export bundle buyer can hand to auditor |

## Task (Critical — smallest shippable slice with receipt)

Open https://secureframe.com — screenshot or quote the exact buyer-facing Buyer-visible UX sentence Secureframe uses; paste into plan evidence (vendor says: Automate evidence for SOC 2, ISO 27001, and more)

## Implementation extraction

`Secureframe · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0301`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Secureframe` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2

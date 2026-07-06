# Pricing page route reliability (200 + linked from nav)

**Plan ID:** `sdr-p1-007` · **Tier:** P1 · **Updated:** 2026-07-06T09:17:58Z

## Problem
Pricing route partially confirmed during external review.

## Goal
/pricing returns 200 and nav Pricing link resolves

## Done when
curl 200 on /pricing and validate-sourcea-contract-pages or link check PASS

## Verify
```
cd ~/Desktop/SourceA && curl -fsS -o /dev/null -w '%{http_code}' https://sourcea.app/pricing | grep -q 200 && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/pricing

## Client demo
Click nav Pricing — page loads

## Work path
`SourceA-landing/green-unified/pricing.html`

---
*Child plan · rolled into UP-DR upgrade wave*

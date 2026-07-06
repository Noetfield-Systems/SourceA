# Canonical pricing ladder across Offer/Start/Pricing

**Plan ID:** `sdr-p1-002` · **Tier:** P1 · **Updated:** 2026-07-06T09:03:49Z

## Problem
Price bands inconsistent across pages.

## Goal
One ladder: 48h $1.5K–$5K · custom $3K–$10K · support from $2K/mo

## Done when
pricing.html offer.html start.html share same tier copy hash

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/pricing && --marker "$1,500" && --marker "$5,000" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count && cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/offer && --marker "48-hour" && --marker "$1,500" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/pricing

## Client demo
Tab three pages — pricing matches

## Work path
`SourceA-landing/green-unified/pricing.html`

---
*One row per Auto Runtime tick · Supabase proof required · INCIDENT-045*

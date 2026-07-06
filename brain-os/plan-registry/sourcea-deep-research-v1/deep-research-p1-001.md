# One primary CTA: Request a 48-hour build

**Plan ID:** `sdr-p1-001` · **Tier:** P1 · **Updated:** 2026-07-06T09:17:58Z

## Problem
Too many CTAs fragment buyer path.

## Goal
Homepage hero primary CTA = Request a 48-hour build; secondary See proof

## Done when
Homepage has data-sa-primary-cta marker linking to /start or /offer

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/ --marker "Request a 48-hour build" --marker "See proof" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/

## Client demo
10-second test: visitor names paid path without reading nav

## Work path
`SourceA-landing/green-unified/index.html`

---
*Child plan · rolled into UP-DR upgrade wave*

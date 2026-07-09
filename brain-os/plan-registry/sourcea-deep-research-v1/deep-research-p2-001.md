# Footer relation map: SourceA · Noetfield · TrustField · Gateway

**Plan ID:** `sdr-p2-001` · **Tier:** P2 · **Updated:** 2026-07-06T09:17:58Z

## Problem
TrustField/Gateway relationship not visible.

## Goal
Footer or about shows one-line relation map

## Done when
Footer contains data-sa-relation-map with four entities

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/ --marker "data-sa-relation-map" --marker "Noetfield" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/

## Client demo
Footer answers who-owns-what in 10s

## Work path
`SourceA-landing/green-unified/index.html`

---
*Child plan · rolled into UP-DR upgrade wave*

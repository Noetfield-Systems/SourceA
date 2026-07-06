# OpenGraph / LinkedIn share card

**Plan ID:** `sdr-p2-002` · **Tier:** P2 · **Updated:** 2026-07-06T09:17:58Z

## Problem
Social preview not verified.

## Goal
og:title and og:description match research §9 P2 copy

## Done when
index.html head has og:title Proof-backed AI execution systems

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/ --marker "og:title" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/

## Client demo
LinkedIn post inspector shows correct preview

## Work path
`SourceA-landing/green-unified/index.html`

---
*Child plan · rolled into UP-DR upgrade wave*

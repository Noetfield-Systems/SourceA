# Homepage copy upgrade: proof-backed MVPs headline

**Plan ID:** `sdr-p1-006` · **Tier:** P1 · **Updated:** 2026-07-06T09:03:49Z

## Problem
Hero still dense; research recommends clearer commercial headline.

## Goal
Hero matches research §10 headline + subheadline

## Done when
Homepage contains Proof-backed MVPs and acquisition systems, shipped fast

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/ && --marker "Proof-backed MVPs" && --marker "acquisition systems" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/

## Client demo
Read hero — ICP clear in one breath

## Work path
`SourceA-landing/green-unified/index.html`

---
*One row per Auto Runtime tick · Supabase proof required · INCIDENT-045*

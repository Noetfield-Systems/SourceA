# Privacy/data note visible before intake Submit

**Plan ID:** `sdr-p1-003` · **Tier:** P1 · **Updated:** 2026-07-06T09:03:49Z

## Problem
Form collects email/project; privacy assurance missing.

## Goal
Intake form shows no-resale privacy note above Submit

## Done when
Start page has data-sa-privacy-note marker before submit button

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/start && --marker "no resale" && --marker "data-sa-privacy-note" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/start

## Client demo
Scroll intake — privacy visible before Submit

## Work path
`SourceA-landing/green-unified/start.html`

---
*One row per Auto Runtime tick · Supabase proof required · INCIDENT-045*

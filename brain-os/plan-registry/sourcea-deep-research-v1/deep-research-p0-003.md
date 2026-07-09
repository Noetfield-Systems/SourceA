# Verify intake submit: store lead + confirmation + notification

**Plan ID:** `sdr-p0-003` · **Tier:** P0 · **Updated:** 2026-07-06T09:17:58Z

## Problem
Lead capture is P0 commercial path; submit not externally verified.

## Goal
Start/intake POST stores row in Supabase and shows success reference

## Done when
mvp-intake-config exposes worker URL; verify_mvp_intake_proof_v1 PASS

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_mvp_intake_proof_v1.py --json && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
supabase://mvp_intake_leads

## Client demo
Submit test lead on /start — show confirmation ID + Supabase row

## Work path
`cloud/workers/sourcea-mvp-intake-v1/`

---
*Child plan · rolled into UP-DR upgrade wave*

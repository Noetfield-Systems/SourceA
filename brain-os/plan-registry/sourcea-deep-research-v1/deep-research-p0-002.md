# Forge Terminal: fix Connecting… or show honest offline state

**Plan ID:** `sdr-p0-002` · **Tier:** P0 · **Updated:** 2026-07-06T09:03:49Z

## Problem
Public demo stuck on Connecting damages conversion.

## Goal
Terminal shows online send path OR clear offline + forge@sourcea.app fallback

## Done when
Terminal page markers present; health/send path returns ok or offline banner

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/sourcea/forge/terminal && --marker "Forge Terminal" && --marker "data-sa-proof-cta" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/sourcea/forge/terminal

## Client demo
Send one prompt on terminal — response or explicit offline state

## Work path
`SourceA-landing/green-unified/sourcea/forge/terminal.html`

---
*One row per Auto Runtime tick · Supabase proof required · INCIDENT-045*

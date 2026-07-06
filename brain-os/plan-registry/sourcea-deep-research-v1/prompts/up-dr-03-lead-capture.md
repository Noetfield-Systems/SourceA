# Lead capture — intake submit

**Plan ID:** `UP-DR-03` · **Tier:** P0 · **Wave:** W1

## Goal
Start/intake POST stores row in Supabase and shows success reference

## Done when
mvp-intake-config exposes worker URL; verify_mvp_intake_proof_v1 PASS

## Child steps
- **sdr-p0-003** — Verify intake submit: store lead + confirmation + notification (open)

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
*One CLOUD-SEC row per Auto Runtime tick · Supabase proof · INCIDENT-045*

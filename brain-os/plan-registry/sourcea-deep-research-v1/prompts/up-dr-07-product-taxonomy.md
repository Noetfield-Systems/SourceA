# Product taxonomy

**Plan ID:** `UP-DR-07` · **Tier:** P1 · **Wave:** W1

## Goal
One box: SourceA=product · Forge=engine · components named once

## Done when
Homepage has data-sa-taxonomy box with three-line explainer

## Child steps
- **sdr-p1-004** — Simplify product taxonomy box on homepage (open)

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/ --marker "data-sa-taxonomy" --marker "Forge is the execution engine" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/

## Client demo
Read taxonomy box aloud — under 15 seconds

## Work path
`SourceA-landing/green-unified/index.html`

---
*One CLOUD-SEC row per Auto Runtime tick · Supabase proof · INCIDENT-045*

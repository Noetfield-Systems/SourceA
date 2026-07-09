# Shareability + ship gate

**Plan ID:** `UP-DR-10` · **Tier:** P2 · **Wave:** W1

## Goal
og:title and og:description match research §9 P2 copy

## Done when
index.html head has og:title Proof-backed AI execution systems

## Child steps
- **sdr-p2-002** — OpenGraph / LinkedIn share card (open)

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/ --marker "og:title" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count && bash scripts/validate-sourcea-deep-research-10-v1.sh
```

## Proof artifact
https://sourcea.app/

## Client demo
LinkedIn post inspector shows correct preview

## Work path
`SourceA-landing/green-unified/index.html`

---
*One CLOUD-SEC row per Auto Runtime tick · Supabase proof · INCIDENT-045*

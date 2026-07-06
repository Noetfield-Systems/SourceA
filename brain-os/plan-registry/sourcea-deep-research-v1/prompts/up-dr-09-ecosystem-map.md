# Ecosystem map

**Plan ID:** `UP-DR-09` · **Tier:** P2 · **Wave:** W1

## Goal
Footer or about shows one-line relation map

## Done when
Footer contains data-sa-relation-map with four entities

## Child steps
- **sdr-p2-001** — Footer relation map: SourceA · Noetfield · TrustField · Gateway (open)

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
*One CLOUD-SEC row per Auto Runtime tick · Supabase proof · INCIDENT-045*

# Buyer path — primary CTA + hero

**Plan ID:** `UP-DR-04` · **Tier:** P1 · **Wave:** W1

## Goal
Homepage hero primary CTA = Request a 48-hour build; secondary See proof · Hero matches research §10 headline + subheadline

## Done when
Homepage has data-sa-primary-cta marker linking to /start or /offer · Homepage contains Proof-backed MVPs and acquisition systems, shipped fast

## Child steps
- **sdr-p1-001** — One primary CTA: Request a 48-hour build (open)
- **sdr-p1-006** — Homepage copy upgrade: proof-backed MVPs headline (open)

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/ --marker "Request a 48-hour build" --marker "See proof" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count && cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/ --marker "Proof-backed MVPs" --marker "acquisition systems" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/

## Client demo
10-second test: visitor names paid path without reading nav · Read hero — ICP clear in one breath

## Work path
`SourceA-landing/green-unified/index.html`

---
*One CLOUD-SEC row per Auto Runtime tick · Supabase proof · INCIDENT-045*

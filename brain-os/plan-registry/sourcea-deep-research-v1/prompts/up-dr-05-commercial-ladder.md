# Commercial ladder — pricing

**Plan ID:** `UP-DR-05` · **Tier:** P1 · **Wave:** W1

## Goal
One ladder: 48h $1.5K–$5K · custom $3K–$10K · support from $2K/mo · /pricing returns 200 and nav Pricing link resolves

## Done when
pricing.html offer.html start.html share same tier copy hash · curl 200 on /pricing and validate-sourcea-contract-pages or link check PASS

## Child steps
- **sdr-p1-002** — Canonical pricing ladder across Offer/Start/Pricing (open)
- **sdr-p1-007** — Pricing page route reliability (200 + linked from nav) (open)

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/pricing --marker "$1,500" --marker "$5,000" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count && cd ~/Desktop/SourceA && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/offer --marker "48-hour" --marker "$1,500" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count && cd ~/Desktop/SourceA && curl -fsS -o /dev/null -w '%{http_code}' https://sourcea.app/pricing | grep -q 200 && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/pricing

## Client demo
Tab three pages — pricing matches · Click nav Pricing — page loads

## Work path
`SourceA-landing/green-unified/pricing.html`

---
*One CLOUD-SEC row per Auto Runtime tick · Supabase proof · INCIDENT-045*

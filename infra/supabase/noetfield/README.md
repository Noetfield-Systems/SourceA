# Supabase — Noetfield (dedicated project)

**Tier:** Production (module-scoped)  
**Cloud ref:** `tkgpapowwplupyekpivy`  
**Module:** noetfield only

## Schema

| Schema | Purpose |
|--------|---------|
| `noetfield` | TLE receipts, decision audit, drift, copilot pilot |

## Secrets

`~/.sourcea-secrets/noetfield.env` — see `config.example.env`

## Rules

- **Not** portfolio-spine (`ldfruywifqnfpwsfgmdl`) — Noetfield has its own project.
- No cross-project JOINs with TrustField/WitnessBC — async events only.
- Migrations in `migrations/` when added.

## Dashboard

https://supabase.com/dashboard/project/tkgpapowwplupyekpivy

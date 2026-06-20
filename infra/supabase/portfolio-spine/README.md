# Portfolio Spine — Supabase project

**Tier:** Production  
**Modules:** noetfield · trustfield · witnessbc · foundation

## Schema map (initial)

| Schema | Owner module | Purpose |
|--------|--------------|---------|
| `gov` | foundation | Shared governance metadata, policy version refs |
| `noetfield` | noetfield | TLE receipts, decision audit, drift |
| `trustfield` | trustfield | Readiness evidence, program delivery state |
| `witnessbc` | witnessbc | Witness / attestation records |
| `foundation` | foundation | Shared identity, org, cross-module refs |
| `audit` | foundation | Append-only audit spine (cross-schema events) |

## Rules

- RLS enabled on every table.
- Per-schema DB roles — apps get schema-scoped grants only.
- Migrations live in `migrations/` — PR + CI required for prod.
- **Virlux does not belong here** (ASF: Virlux → labs-sandbox).

## Secrets

`~/.sourcea-secrets/portfolio-spine.env` — see `config.example.env`.

## Cross-project boundary

No imports from `labs-sandbox`. Consume Virlux via async signed events only.

# Labs Sandbox — Supabase project

**Tier:** Disposable / Labs  
**Modules:** virlux · labs/* · research · experiments

**ASF decision:** Virlux lives here until explicitly promoted to a production ring-fence tier.

## Schema map (initial)

| Schema | Owner module | Purpose |
|--------|--------------|---------|
| `virlux_ops` | virlux | Payment-rail experiments, factory verify, MCP receipts |
| `labs` | labs | Agent experiments, throwaway tables |
| `research` | research | Research sensor outputs, non-prod |

## Rules

- Assume **delete and recreate** is acceptable.
- This is the **only** Supabase project whose keys may appear in agent dev workflows.
- No FINTRAC production data until Virlux graduates — treat as MOCK / pilot scope.
- Do not copy Portfolio Spine migrations here.

## Secrets

`~/.sourcea-secrets/labs-sandbox.env` — see `config.example.env`.

## Integration out

When Virlux completes an action relevant to governance, emit a **signed event** consumed by Portfolio Spine — never a cross-project FK.

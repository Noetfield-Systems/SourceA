# Labs Sandbox — Supabase project

**Tier:** Disposable / Labs  
**Modules:** virlux · labs/* · research · experiments

**ASF decision (2026-06-20):** Virlux agentic factory SaaS stays online here. **No payment settlement or FINTRAC/MSB data on VIRLUX** — that lane is TrustField or a future company.

## Schema map (initial)

| Schema | Owner module | Purpose |
|--------|--------------|---------|
| `virlux_ops` | virlux | Agentic factory verify, catalog, MCP receipts, sandbox bays |
| `labs` | labs | Agent experiments, throwaway tables |
| `research` | research | Research sensor outputs, non-prod |

## Rules

- Assume **delete and recreate** is acceptable for labs experiments.
- This is the **only** Supabase project whose keys may appear in agent dev workflows.
- **No FINTRAC production data, payment settlement, or MSB customer financial data on VIRLUX.**
- Do not copy Portfolio Spine migrations here.

## Secrets

`~/.sourcea-secrets/labs-sandbox.env` — see `config.example.env`.

## Integration out

When Virlux completes an action relevant to governance, emit a **signed event** consumed by Portfolio Spine — never a cross-project FK.

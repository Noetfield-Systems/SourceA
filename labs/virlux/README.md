# Virlux — Labs tier (static / pre-product)

**Tier:** `labs-sandbox` Supabase project · schema `virlux_ops` when backend exists  
**Status today:** Landing / marketing surface — no production payment rails

## Graduation trigger (non-negotiable)

**The moment Virlux touches real money or real financial/user data, it must graduate out of `labs/` into its own isolated Supabase project before that code ships** — not after. A static site is safe here because it holds nothing sensitive; do not quietly add payment calls or customer PII storage under this path.

## Deferred (not deleted from plan)

When Virlux becomes real: ring-fenced project · FINTRAC/OSFI scope · restrictive RLS · PITR — see `infra/README.md` and ASF promotion ADR.

## Integration with Portfolio Spine

Async only — signed receipts/events. No cross-project DB joins. See `data/supabase-portfolio-tiers-v1.json`.

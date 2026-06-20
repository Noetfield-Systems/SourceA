# Virlux — agentic factory SaaS (online)

**Saved:** 2026-06-20T21:00:00Z · **Decision:** `ASF-2026-06-20-VIRLUX-AGENTIC-ONLY`  
**Tier:** `labs-sandbox` Supabase project · schema `virlux_ops`  
**Status:** **Live online** — Build Factory agentic SaaS · verify factory · MCP · sandbox bays  
**Product:** Controlled agentic factories — not payments · not FINTRAC

## ASF policy (2026-06-20)

**FINTRAC / cross-border payments / MSB rails are OUT of VIRLUX.**

| Lane | Owner |
|------|--------|
| Agentic factory building SaaS | **VIRLUX** (catalog, sandbox bay, run detail, MCP verify receipt) |
| Canadian MSB / FINTRAC program | **TrustField** when that ships |
| Payment rails as a product | **Future company** — not under VIRLUX |

## Supabase placement

VIRLUX stays on **`labs-sandbox`** Supabase while the product is agentic SaaS without payment settlement or MSB customer financial data. **Online is fine** — `labs-sandbox` is a portfolio tier name, not an “offline only” restriction.

**Graduation trigger (non-negotiable):** The moment VIRLUX touches **real money, payment settlement, or MSB/FINTRAC customer financial data**, stop — that code belongs on **TrustField** or a **new isolated Supabase project**, not here.

## Honest tier ladder (ship UX — ASF agree)

Sandbox (`mock_only`) → freemium cap → paid bay + **run detail page** + **MCP verify receipt**.

## Integration with Portfolio Spine

Async only — signed receipts/events. No cross-project DB joins.

**Machine SSOT:** `data/supabase-portfolio-tiers-v1.json` · **Human infra:** `infra/README.md`

## Daily stay-up

Run with the full portfolio (both Supabase tiers + all sites):

```bash
bash ~/Desktop/SourceA/scripts/run-portfolio-supabase-daily-v1.sh
```

Receipt: `~/.sina/portfolio-supabase-daily-pulse-v1.json` · VIRLUX rows: `virlux_web` · `virlux_api` · `labs-sandbox` Supabase health.

## Canonical repo & agent law

| Artifact | Path |
|----------|------|
| Primary implementation | `~/Desktop/VIRLUX` |
| Independence statement (law) | `~/Desktop/VIRLUX/os/agents/auto-virlux-delivery/receipts/INDEPENDENCE-STATEMENT-v2.md` |
| SourceA lane handoff | `brain-os/lanes/MANDATORY_VIRLUX_CHAT_LOCKED_v1.md` |
| Design ↔ delivery bridge | `docs/VIRELUX_REPO_ALIGNMENT.md` |
| Comparables (100 rows) | `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md` |

**Superseded:** `INDEPENDENCE-STATEMENT-DRAFT-v1.md` (payments north star) — do not treat as law.

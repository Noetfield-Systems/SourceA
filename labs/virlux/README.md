# Virlux — agentic factory SaaS (online)

**Tier:** `labs-sandbox` Supabase project · schema `virlux_ops`  
**Status:** **Live online** — Build Factory agentic SaaS · verify factory · MCP · sandbox bays  
**Product:** Governed agentic factories — not payments · not FINTRAC

## ASF policy (2026-06-20)

**FINTRAC / cross-border payments / MSB rails are OUT of VIRLUX.**

- VIRLUX = **agentic factory building SaaS** (catalog, sandbox bay, run detail, MCP verify receipt).
- **TrustField** = Canadian MSB / FINTRAC program lane when that ships.
- **Future company** = if payment rails return as a separate product later — not under VIRLUX.

## Supabase placement

VIRLUX stays on **`labs-sandbox`** Supabase while the product is agentic SaaS without real money movement or MSB customer data. That is **fine for online** — no separate “lab only” restriction beyond portfolio tier hygiene.

**Graduation trigger (still non-negotiable):** The moment VIRLUX touches **real money, payment settlement, or MSB/FINTRAC customer financial data**, stop — that code belongs on **TrustField** or a **new isolated Supabase project**, not here.

## Honest tier ladder (ship UX)

Sandbox (`mock_only`) → freemium cap → paid bay + **run detail page** + **MCP verify receipt**.

## Integration with Portfolio Spine

Async only — signed receipts/events. No cross-project DB joins. See `data/supabase-portfolio-tiers-v1.json`.

## Canonical repo

Primary implementation: `~/Desktop/VIRLUX` · Pointer docs: `labs/virlux/` in SourceA.

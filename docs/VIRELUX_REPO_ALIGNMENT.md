# VIRLUX repo alignment — DESIGN ↔ DELIVERY bridge

**Saved:** 2026-06-20T21:00:00Z · **Version:** 1.1 · **Authority:** ASF  
**INTERNAL ONLY — Desktop SourceA — NOT for GitHub / NOT public online**

| Field | Value |
|-------|-------|
| **Status** | Active — agentic-only pivot locked 2026-06-20 |
| **Canonical location** | `~/Desktop/SourceA/docs/VIRELUX_REPO_ALIGNMENT.md` |
| **Delivery repo** | `kazemnezhadsina144-dot/VIRLUX` (Virlux Inc.) |
| **Decision** | `ASF-2026-06-20-VIRLUX-AGENTIC-ONLY` |

---

## Product law (ASF 2026-06-20)

| In scope on VIRLUX | Out of scope on VIRLUX |
|--------------------|------------------------|
| Build Factory catalog | Cross-border B2B payments app |
| Sandbox → freemium → paid bay | FINTRAC / MSB registration product |
| Run detail page + MCP verify receipt | Payment lifecycle / async settlement UX |
| Specialist team hire shell | Real money movement APIs |

**Supabase:** online on **`labs-sandbox`** — fine for agentic SaaS without payment settlement data.  
**Payments / FINTRAC lane:** TrustField or a future company — not VIRLUX.

---

## Layer tags (R9)

| Plane | Statement |
|-------|-------------|
| **[DESIGN]** | Mono `system_registry.json` may list `virelux` as placeholder until ASF promotes registry + ANNOUNCEMENT_BOARD. |
| **[DELIVERY]** | VIRLUX repo is **active, shippable agentic factory SaaS**: marketing `:3100`, dashboard `:3001`, API `:3002`. Independent of SinaaiRuntime. |
| **[EXECUTION]** | SinaaiRuntime `:8000` does **not** host VIRLUX. No Runtime submodule dependency. |

**G5 (locked):** Registry **records** execution; it does **not gate** Delivery shipping.

---

## Binding contract

| Clause | DESIGN (mono) | DELIVERY (VIRLUX repo) | Resolution |
|--------|---------------|------------------------|------------|
| **V1** | Product entity placeholder | **Agentic factory SaaS** (Build Factory + verify + MCP) | Dual instance until registry promotion |
| **V2** | Ports `:8000` spine | Ports `3100/3001/3002` only | Separate product; no port conflict |
| **V3** | Phase 0 declaration | Active build + deploy online | Drift Type A — informational; owner ASF |
| **V4** | TrustField = separate company | VIRLUX = Virlux Inc. only; **no payment rails on VIRLUX** | No cross-brand in shipped code |
| **V5** | ASF → registry → board | ASF → PR → public locks | Two valid update paths |

**Supersedes v1.0 clause V1** “Full B2B payments stack” — payments deferred off VIRLUX per ASF pivot.

---

## Registry promotion (when ASF approves)

Update `SinaaiMonoRepo/SinaaiDataBase/governance/system_registry.json`:

```json
{
  "id": "virelux",
  "name": "VIRLUX",
  "path": "external:github/kazemnezhadsina144-dot/VIRLUX",
  "ports": [3100, 3001, 3002],
  "status": "active",
  "executable": true,
  "product": "agentic_factory_saas",
  "note": "Independent product repo — Build Factory + verify; not SinaaiRuntime submodule; FINTRAC/payments OUT"
}
```

Add dated entry to `ANNOUNCEMENT_BOARD.md`.

---

## Drift record

| Field | Value |
|-------|-------|
| SSOT ideal | virelux registry placeholder |
| Delivery reality | Agentic factory live / deploying on Vercel + labs-sandbox Supabase |
| Type | A — Informational |
| Owner | ASF |
| Action | Registry promotion when ready; does not block shipping |

---

## Related pointers

- `labs/virlux/README.md` — SourceA pointer SSOT
- `~/Desktop/VIRLUX/os/agents/auto-virlux-delivery/receipts/INDEPENDENCE-STATEMENT-v2.md`
- `data/supabase-portfolio-tiers-v1.json`
- `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

---

## Document control

- v1.0 — 2026-06-01 — Initial bridge doc
- v1.1 — 2026-06-20 — ASF agentic-only pivot; payments clause removed from VIRLUX scope

# VIRLUX repo alignment — DESIGN ↔ DELIVERY bridge

**INTERNAL ONLY — Desktop SourceA — NOT for GitHub / NOT public online**

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Status** | Draft for ASF review |
| **Authority** | ASF (human founder) |
| **Canonical location** | `/Users/sinakazemnezhad/Desktop/SourceA/VIRELUX_REPO_ALIGNMENT.md` |
| **Subordinate to** | `SINA_OS_SSOT_LOCKED.md`, `AUTO_CONFLICT_ENGINE_V3_LOCKED.md` |
| **Delivery repo** | `kazemnezhadsina144-dot/VIRLUX` (Virlux Inc. product) |

---

## Layer tags (R9)

| Plane | Statement |
|-------|-------------|
| **[DESIGN]** | Mono `system_registry.json` lists `virelux` as **Not implemented / not executable** until ASF publishes registry + ANNOUNCEMENT_BOARD update. |
| **[DELIVERY]** | VIRLUX GitHub repo is an **active, shippable product**: marketing `:3100`, dashboard `:3001`, API `:3002`. Independent of SinaaiRuntime. |
| **[EXECUTION]** | SinaaiRuntime `:8000` does **not** host VIRLUX. No Runtime submodule dependency. |

**G5 (locked):** Registry **records** execution; it does **not gate** Delivery shipping.

---

## Binding contract

| Clause | DESIGN (mono) | DELIVERY (VIRLUX repo) | Resolution |
|--------|---------------|------------------------|------------|
| **V1** | Product entity placeholder | Full B2B payments stack | Dual instance until registry promotion |
| **V2** | Ports `:8000` spine | Ports `3100/3001/3002` only | Separate product; no port conflict with mono spine |
| **V3** | Phase 0 declaration | Active build + deploy | Drift Type A — informational; owner ASF |
| **V4** | TrustField = separate company (not Noetfield-owned) | VIRLUX = Virlux Inc. only | No cross-brand in shipped code; TrustField–Noetfield collaboration is commercial, not structural merge |
| **V5** | ASF → registry → board | ASF → PR → public locks | Two valid update paths |

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
  "note": "Independent product repo — not a SinaaiRuntime submodule"
}
```

Add dated entry to `ANNOUNCEMENT_BOARD.md`.

---

## Drift record (optional)

| Field | Value |
|-------|-------|
| SSOT ideal | virelux not implemented |
| Delivery reality | Product live / deploying |
| Type | A — Informational |
| Owner | ASF |
| Action | Registry promotion when ready; does not block shipping |

---

## Document control

- v1.0 — 2026-06-01 — Initial bridge doc for Validation & Visibility upgrade

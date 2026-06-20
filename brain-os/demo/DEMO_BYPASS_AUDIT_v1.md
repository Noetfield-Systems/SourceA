# DEMO_BYPASS_AUDIT_v1 — honest bypass inventory

**Sprint:** `DEMO-ENF-COPILOT-2026-06-11`  
**Updated:** 2026-06-11  
**Rule:** Demo path cannot lie; full repo may still bypass until commit gate v1 post-1.10.

---

## Demo-scoped path (sacred)

| Entry | Writes | Validator |
|-------|--------|-----------|
| `sourcea_execute_v1.py --demo-enforcement` | receipt + spine (ALLOW) | `validate-demo-enforcement-v1.sh` |
| `commit_intent_v1.py --demo-enforcement` | same | same |
| `governance_demo_gate_v1.py` | none (read-only eval) | inline DENY/PASS |

**Tamper:** edit `~/.sina/demo-enforcement/receipts/latest-demo-receipt.json` → checksum FAIL.

**Exceptions documented:** none for Copilot demo path.

---

## Known bypass paths (full repo)

| Bypass | Risk | Demo claim impact | Fix slice |
|--------|------|-------------------|-----------|
| Direct Worker/Cursor ACT without `sourcea_execute` | High | Do not claim whole-OS uncheatable | DEMO-ENF-S9 · commit gate v1 post-1.10 |
| Scripts writing `command-data*.json` without spine | INCIDENT-027 class | Cosmetic hero lag only | Maintainer FR-003 + hero scrub |
| Hand-edit RT LIVE receipt without checksum | Medium | Caught by universe validator | Shipped |
| `closeout_gate` bulk-stamp fraud | Medium | Factory lane — separate demo | `closeout_gate_v1.py` |
| Hub projection read as law | High (027 lesson) | Validators are authority | Education + validator PASS |
| SEMEJ / mx runtime unless demo-critical | Low | Out of 6mo scope | DELETE |

---

## What investors can trust today

- Copilot demo BLOCK / ALLOW / tamper FAIL — **live reproducible**
- RT LIVE receipt ↔ spine — **validator PASS**
- Factory honest counter — **unproven_done: 0**

## What investors cannot trust yet

- Every repo write goes through single `commit()`
- Multi-tenant cloud / SOC2
- M365 API integration (stub only)

---

## Next hardening (ordered)

1. `validate-demo-bypass-inventory-v1.sh` (DEMO-ENF-S9)
2. Hub Commit Action → `commit_intent_v1.py` only (demo scope)
3. Unified commit gate v1 — post Phase 1.10 seal

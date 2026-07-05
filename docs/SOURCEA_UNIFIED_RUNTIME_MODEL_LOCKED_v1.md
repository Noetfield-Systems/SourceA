# SourceA Unified Runtime Model (LOCKED v1)

**Saved at:** 2026-07-05T12:45:00Z  
**Version:** 1.0.0 LOCKED  
**Supersedes:** `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md` as runtime SSOT map  
**Parents:** `data/founder-execution-model-v1.json` · `docs/SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md`

---

## One sentence

> No single flat SSOT — five layers: Mac control · rules · law · factory · receipts.

---

## Five-layer model

| Layer | SSOT | Status | Owns |
|-------|------|--------|------|
| **L0 Mac control** | `data/founder-execution-model-v1.json` · `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md` | SHIPPED | Gating · routing · founder session · Hub :13020 |
| **L1 Rules in charge** | `.cursor/rules/000-entry-gate.mdc` · 9 always-apply rules | SHIPPED | Cursor agent behavior |
| **L2 Law plane** | `docs/SOURCEA_GOVERNANCE_ENTRY_UNIFIED_LOCKED_v1.md` + cited LOCKED docs | LOCKED | Policy · incidents · enforcement |
| **L3 Factory motor** | Railway `sourcea-fbe-runner` · CF cron · `docs/CONTROLLED_AUTORUN_LAWS_v3.md` | LIVE | Execute · verify · cloud drain |
| **L4 Receipts** | `~/.sina/*.json` · `receipts/cloud/` | APPEND-ONLY | Proof · audit trail |

---

## Mac vs Cloud boundary

| Plane | Must | Must NOT |
|-------|------|----------|
| **Mac (L0)** | Session gate · Hub proceed · read receipts | Factory body · heavy validators · local CLI drain |
| **Cloud (L3)** | FBE · auto-tick · product artifacts | Pretend to be Mac control · law SSOT |

---

## Mac belt ⊃ cloud PEVC

```
SCAN → SAY → PICK → PROVE → SHIP
                              └─ cloud Plan→Control→Execute→Verify→Commit (inside SHIP only)
```

---

## Reconciliation

| Topic | Mac truth | Cloud truth | Reconcile via |
|-------|-----------|-------------|---------------|
| Autorun queue head | `~/.sina/phase-observed-v1.json` | Railway `/api/cloud-drain/queue/v1` | `hub_cloud_drain_proceed_v1.py` |
| Kernel target | Workbench architecture doc | `SOURCEA_CLOUD_KERNEL_TARGET_v1.3.pdf` | `SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md` |

---

## Do not merge

- L0 Mac control plane into L1–L8 cloud kernel PDF
- Chat memory into any layer
- `command-data.json` as agent law SSOT (Hub display only)

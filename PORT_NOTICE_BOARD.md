# PORT NOTICE BOARD (live — agents read this first)

**Updated:** 2026-06-12T16:59:07Z  
**Locked rules:** `PORT_NOTICE_BOARD_LOCKED_v1.md`  
**Law:** `SINAAI_PORT_REGISTRY_LAW_LOCKED_v1.md`  

---

## SUGGESTED FREE PORTS (use these — do not guess)

| Use case | Port | Command |
|----------|------|---------|
| **DevBridge Safari desk** | **3004** | `cd ~/Desktop/AI\ Dev\ Bridge\ OS && npm run start` |
| **DevBridge Mac agent (WS)** | **8766** (already running — reuse) | `npm start` / agent :8766 |
| **Never for DevBridge desk** | **3000–3003** | Noetfield / VIRLUX / ASF reserved |

**All free desk ports:** 3004, 3005, 3006, 3007, 3008, 3009, 3010

---

## VIOLATIONS — fix before bind

- **:13020** — Port 13020 is bound by unknown_python but catalog owner is sina_command; no other product may listen here.
- **:13030** — Port 13030 is bound by unknown_python but catalog owner is hub_rebuild_worker; no other product may listen here.

**Auto-fix DevBridge desk:** `cd ~/Desktop/AI\ Dev\ Bridge\ OS && npm run fix:ports`

---

**Live scan:** 3 busy · 44 free

Full table: `PORT_REGISTRY.md` · Machine: `PORT_REGISTRY.json`

**Refresh:** `cd ~/Desktop/SinaPromptOS && python main.py --port-registry`

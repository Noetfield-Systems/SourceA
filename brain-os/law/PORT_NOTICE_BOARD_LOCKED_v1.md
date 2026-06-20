# Port Notice Board — LOCKED (agent entry point)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**Locked:** 2026-06-03  
**Path:** `/Users/sinakazemnezhad/Desktop/SourceA/PORT_NOTICE_BOARD_LOCKED_v1.md`

---

## Rule (mandatory)

Every agent **reads the live board first** — not this file alone:

| File | Role |
|------|------|
| **`PORT_NOTICE_BOARD.md`** | **Live** — suggested free ports + violations (auto-updated) |
| `PORT_REGISTRY.json` | Machine truth |
| `PORT_REGISTRY.md` | Full table |
| `SINAAI_PORT_REGISTRY_LAW_LOCKED_v1.md` | Law P1–P9 |

---

## Who updates the live board

**Port Registry Agent** — `SinaPromptOS/core/port_registry_agent.py`

Runs when:

- `python main.py --port-registry`
- `./scripts/update-port-registry.sh`
- Start of `./scripts/run-full-cycle.sh`
- **`npm run fix:ports`** / **`npm start`** in AI Dev Bridge OS (refreshes board)

---

## What the board always shows

1. **SUGGESTED FREE PORTS** — next port for DevBridge desk (**3004–3010** only) and agent (8766+)
2. **VIOLATIONS** — wrong process on a port; fix before bind
3. **Never use 3000–3003** for DevBridge desk (Noetfield / VIRLUX / ASF reserved)

Agents must use suggested ports — **do not use :3000, :3001, :3002, or :3003 for DevBridge desk.**

---

**End — locked.**

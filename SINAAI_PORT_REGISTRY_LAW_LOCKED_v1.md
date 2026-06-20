# Sinaai — Port Registry Law (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## Mandatory for every agent before bind, listen, or document a port

**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-03-PORT-REG  
**Classification:** INTERNAL ONLY  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINAAI_PORT_REGISTRY_LAW_LOCKED_v1.md`  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3  
**Maintainer:** ASF  
**Locked:** 2026-06-03

---

## 1. Purpose

Ports on the ASF Mac are **shared infrastructure**. Collisions (e.g. DevBridge on `:3000` while Noetfield or Mono UI already listen) break wire proof, runtime, and multi-agent work.

This law defines:

1. **What each port is for** (declared owner + purpose)  
2. **What is busy right now** (live scan)  
3. **Who may bind** (exclusive ownership — no other product may listen on a reserved or busy port)

---

## 2. Mandatory read order (all agents)

**Before** starting a server, editing `port` in config, documenting a URL with a port, or running `npm start` / `uvicorn` / `next dev`:

| Order | File | Role |
|-------|------|------|
| **0** | `~/Desktop/SourceA/PORT_NOTICE_BOARD.md` | **Live notice board — suggested free ports + violations** |
| **0b** | `~/Desktop/SourceA/PORT_NOTICE_BOARD_LOCKED_v1.md` | Locked rules for the board |
| **0c** | `~/Desktop/SourceA/PORT_REGISTRY.json` | Machine truth |
| **0d** | `~/Desktop/SourceA/PORT_REGISTRY.md` | Full port table |
| **1** | `~/Desktop/SourceA/SINA_OS_SSOT_LOCKED.md` §5 | Declared mono spine ports |
| **2** | This law | Rules below |

Repo Cursor agents: also read **§0** in `CURSOR_REPO_AGENT_NOTICE_PROMPTS_v1.md` (GENERAL block).

**Skipping the registry is a law violation** — treat as blocker until registry is read and obeyed.

---

## 3. Live registry (always updated)

| Artifact | Path | Updated by |
|----------|------|------------|
| Catalog (declared owners) | `PORT_CATALOG.json` | ASF / architecture change only |
| Live registry | `PORT_REGISTRY.json` | **Port Registry Agent** (automated) |
| Human view | `PORT_REGISTRY.md` | same agent |

**Port Registry Agent:** `SinaPromptOS/core/port_registry_agent.py`  
**Commands:**

```bash
cd ~/Desktop/SinaPromptOS && source .venv/bin/activate
python main.py --port-registry
# or
./scripts/update-port-registry.sh
```

**Must run:**

- At start of every `./scripts/run-full-cycle.sh` (before feedback cycle)  
- Before `npm start` in AI Dev Bridge OS when desk port is unknown  
- After starting/stopping Noetfield, Runtime, VIRLUX, or DevBridge

Optional cron (ASF): every 15 minutes — `scripts/install-port-registry-cron.sh`

---

## 4. Locked rules

| ID | Rule |
|----|------|
| **P1** | Read `PORT_REGISTRY.md` (or `.json`) **first** when any task touches a port. |
| **P2** | **Exclusive bind:** only the declared `owner_id` for a port may `listen` on it. |
| **P3** | If `status` is `busy` and `listener.owner_id` ≠ declared `owner_id` → **violation** — do not bind; fix or stop the occupant. |
| **P4** | If `status` is `free` → only the declared `owner_id` (or ASF-approved fallback in catalog) may bind. |
| **P5** | **Never** bind DevBridge desk on **3000–3003** (reserved). Desk uses **3004–3010** only. |
| **P6** | **8766** — one listener only: DevBridge agent **or** Prompt OS dashboard sketch — never both. |
| **P7** | Do not document URLs with ports that contradict the live registry (e.g. “use :3000 for DevBridge”). |
| **P8** | Port Registry Agent updates the list; agents **do not** hand-edit `PORT_REGISTRY.json` / `.md`. |
| **P9** | ASF may override P2–P4 in writing; agents may not. |

---

## 5. Declared owners (summary)

Full detail in `PORT_CATALOG.json`. Summary:

| Port(s) | owner_id | Purpose |
|---------|----------|---------|
| 8000 | sinaai_runtime | Mono execution spine |
| 3000 | mono_ui / noetfield_legacy_redirect | Mono UI; Noetfield redirect when dev-local runs |
| 8001 | golden_edge_or_noetfield_governance | SSOT optional scoring; Noetfield governance API when dev runs |
| 8010, 8020 | mono_legacy | Frozen — no new bind |
| 3001 | virlux_dashboard | VIRLUX dashboard (or stale DevBridge — violation) |
| 3002 | virlux_api | VIRLUX API |
| 3100 | virlux_marketing | VIRLUX marketing |
| 3004–3010 | devbridge_desk | DevBridge Safari desk (auto-pick) |
| 8766 | devbridge_agent | DevBridge WebSocket agent |
| 8765 | sinapromptos_streamlit | Prompt OS Streamlit UI |
| 8767–8786 | devbridge_agent_fallback | DevBridge agent if 8766 busy |
| 8780 | devbridge_relay | DevBridge relay dev |
| 13080, 13000, 18002 | noetfield_dev | Noetfield local dev stack |
| 13020 | sina_command | Sina Command hub UI + API |
| 13030 | hub_rebuild_worker | Hub rebuild queue consumer (external worker, Phase N1) |
| 9473 | cursor_os_pro | Cursor OS Pro bridge |
| 8082 | expo_dev | Expo / mobile dev (typical) |

Hub stabilization binds **13020 + 13030 only**. **13021–13023** are occupied sidecars (Monitor, Mono, Chat-Unify) — do not assign hub-rebuild-worker there.

---

## 6. Violations and enforcement

- Registry `violations[]` lists current conflicts (wrong process on a port).  
- Agents must **stop** and report violations — not add another listener.  
- Prompt OS may surface violations in `ECOSYSTEM_STATUS.md` after publish.

---

## 7. SSOT cross-reference

- Mono port map: `SINA_OS_SSOT_LOCKED.md` §5  
- DevBridge collision sheet: `AI Dev Bridge OS/docs/PORTS_LOCKED.md` (subordinate to this law + live registry)  
- Noetfield: `Noetfield/docs/LOCAL_DEV.md`  
- VIRLUX: `SourceA/VIRELUX_REPO_ALIGNMENT.md`

---

**End of law — locked.**

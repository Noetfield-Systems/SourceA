# Agent — No Hub Rebuild Stuck Loop (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13 · **Authority:** ASF — hub rebuild chatter blocks all lanes  
**Router:** `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` · `SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md`  
**Index:** `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` row `NO_HUB_REBUILD_STUCK`

---

## Law (one sentence)

**Worker · Brain · Maintainer · every agent: ship the sa/task in the repository — never default to hub rebuild, full refresh, or `build-sina-command-panel.py`; Super Fast Hub light sync + task validators only.**

---

## Why everyone gets stuck

| Stuck pattern | What happens |
|---------------|--------------|
| Worker closeout runs **strict build** | 5–50 min · random FAIL · sa never closes |
| Brain status → **rebuild hub** | Narration replaces pick/handoff |
| Maintainer touches hero → **full panel build** | Blocks all lanes |
| Agent says **"hub green"** | Founder waits · business stops |
| **`hub_self_refresh --full`** | Queues :13030 rebuild · SSE hang |
| **Worker VERIFY full `find_critical_bugs`** | **60–180s** · 44-step anti-staleness · Cursor “Waiting for shell” |

**Business blocker:** tasks wait on UI factory instead of product disk.

---

## Default sync (all agents — every status/closeout)

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
bash validate-super-fast-hub-v1.sh
python3 hub_self_refresh_v1.py --json
curl -s http://127.0.0.1:13020/api/worker-hub/v1
```

**Optional read-only:** `python3 find_critical_bugs.py` (or `SINA_FCB_FAST=1` on CHECK turns)

**Forbidden as default verify** — instant FAIL if in closeout without sa/task explicitly editing legacy panel UI:

```bash
SINA_AUDIT_STRICT=1 python3 build-sina-command-panel.py   # BANNED default
POST /refresh {"mode":"full"}                              # BANNED default
python3 hub_self_refresh_v1.py --full                      # BANNED unless gate below
```

---

## Who may run full hub build (rare)

| Agent | When | Command |
|-------|------|---------|
| **M2 / Maintainer** | Edited `agent-control-panel/assets/app.js` or `app.css` **only** | `build-sina-command-panel.py` + ASF or sa says hub UI |
| **Nobody else** | — | File `POST /api/agent-review` · Worker continues sa |

**Full refresh gate:** `AGENT_HUB_FULL_REBUILD_OK=1` env **and** Maintainer sa **and** legacy UI change.

---

## Per-lane rules

| Lane | Ship truth | Never |
|------|------------|-------|
| **Worker** | sa receipt · **`worker_verify_fast_v1.sh`** | Hub rebuild · **full find_critical_bugs** |
| **Brain** | pick · handoff · Valid YES from hygiene | Implement · rebuild · "refresh hub" to ASF |
| **Maintainer 2** | hub UI diff only · super-fast validator | Strict build for non-UI sa |
| **Gov / Commercial** | LOCKED law in repository | Hub tabs as progress |
| **All** | Mention **task outcome** first | Lead with "hub…" |

---

## Forbidden phrases (closeout / status)

- "Need hub rebuild" · "Run strict build" · "Refresh hub first" · "Hub is green"
- "Waiting on panel build" · "build-sina-command-panel failed so…"

**Replace with:** sa-XXXX done/blocked · validator path · Worker Hub 1.5KB snapshot.

---

## Founder surface

Founder uses **`http://127.0.0.1:13020/`** Super Fast Hub only. Agents **never** ask founder to rebuild, refresh legacy, or open monolith for status.

---

## Machine proof

```bash
bash scripts/validate-super-fast-hub-v1.sh
bash scripts/validate-agent-no-hub-rebuild-stuck-v1.sh
```

---

*End AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1*

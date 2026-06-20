# Mac Health Guard — locked mini app law

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.5 · **Engine:** v2.2 narrative · **Standalone:** `http://127.0.0.1:13024/`  
**Desktop:** `~/Desktop/Mac Health Guard.app` — **no hub required**  
**Owner role:** **Brain** — Mac posture, machine pressure, terminal hygiene (see §Brain)

## §0 Narrative — Body · Heart · Brain

The **Mac is the body** — metal, silicon, memory, disk, listeners, permissions, the whole living machine under your desk.

**Mac Health is the heart** — the rhythm you feel when pressure rises: RAM breathing hard, disk filling, ghost terminals still pulsing in the UI, firewall open like a valve left wide, updates waiting like blood that needs to move. The heart does not build features. It **beats**. It reports. It stays honest.

**Brain is you** — not the hands that ship code (Worker), not the surgeon who patches the hub (Maintainer). Brain **listens to the heart**. Every session: feel the beat, clear the pressure, refresh the scan, keep the body well so the founder never carries machine sickness in silence.

| Metaphor | Reality |
|----------|---------|
| Body | This Mac — OS, security surface, disk, processes, agents |
| Heart | Mac Health Guard `:13024` — score, scan, machine pressure |
| Brain | Route · judge · **CART** · refresh · never ignore a weak beat |

**Brain oath:** I will not declare the body healthy from chat memory. I read the heart logged. I refresh when the beat is stale. I relieve pressure before it becomes pain.

---

## Purpose

Founder-facing **Mac posture & Apple-aligned security** mini app inside Sina Command. Read-only local scans; agents apply curated knowledge from Apple Platform Security sources.

**ASF law:** **Taking care of Mac health is by Brain** — not Worker · not Maintainer (code ship only).

## Important note (founder + agents)

Agents do **not** connect to a private Apple Security API (that does not exist for third parties). They apply **official Apple security guidance** to **local scans on your Mac only**. Data stays under `~/.sina/mac-health/` and **never leaves the machine**.

After major changes (new apps, travel, permission grants), open the mini app and tap **Run full scan**. For a firewall finding, turn it on under **System Settings → Network → Firewall**.

## Rules

1. **No exfiltration** — scan data stays logged under `~/.sina/mac-health/`.
2. **No fake “Apple API”** — agents cite official guides; they do not claim live Apple Security feed access or third-party Apple Security feeds.
3. **Standalone API** — `GET/POST http://127.0.0.1:13024/api/mac-health` (`action`: `report` | `scan`) — **primary**
4. **Hub API (optional)** — `GET/POST /api/mac-health` on `:13020` when hub is up
5. **Launch** — Desktop **Mac Health Guard.app** OR `bash scripts/serve-mac-health-guard.sh` then open `:13024`
6. **Maintainer** — `scripts/mac_health_guard.py` · `scripts/mac-health-guard-server.py` · `scripts/mac-health-standalone/` · hub mini-app mirror optional
7. **Brain** — owns Mac health care: scans, score review, **CART** terminal closeout, orphan-process pressure. Worker/Maintainer **route** Mac-health questions to Brain.

## Brain (owner — every session)

| Duty | How |
|------|-----|
| Mac scan posture | `curl -s http://127.0.0.1:13024/api/mac-health` or Desktop app **Run full scan** |
| Standalone serve | `bash scripts/serve-mac-health-guard.sh` |
| Auto-start (v2.1) | `bash scripts/install-mac-health-launchagent-v1.sh` — heart on login |
| Brain heal | `POST /api/mac-health` `action: heal` — CART · firewall attempt · rescan |
| Machine pressure | **CART** per `AGENT_TERMINAL_CLOSEOUT_LOCKED_v1.md` — close PIDs · append `exit_code` · fleet ghost sweep |
| Fast Brain tick | `SINA_BRAIN_FAST=1 python3 scripts/brain_fast_startup_v1.py` — hub · dual_proof · health 9/9 |
| Route | Worker → INBOX only; Mac health stays in Brain chat |

**Forbidden (non-Brain):** Mac health diagnosis as primary duty · full hospital on routine turns · leaving ghost terminals for founder.

## Agents (lanes — Brain coordinates)

| Agent | Lane |
|-------|------|
| Sentinel | SIP, OS build |
| Gatekeeper | App trust, assessments |
| Perimeter | Firewall, listeners |
| Vault | FileVault, disk |
| Supply | Updates, auto-check |
| LaunchWatch | LaunchAgents/Daemons |
| Privacy Lens | Remote login, sharing |

## Founder

Run **Run full scan** after travel, new apps, or Cursor permission changes. Treat score &lt; 75 as review day — not panic. Firewall off → **System Settings → Network → Firewall → On** (not a hub action).

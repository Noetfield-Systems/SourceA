# World Target Model Tab — UI Upgrade Ledger — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T16:54:05Z · **Authority:** Founder — per-app UI upgrade tracking  
**surface_id:** `wtm_tab` · **Repo:** SourceA · **URL:** http://127.0.0.1:13020/?tab=system-roadmap  
**Root:** `agent-control-panel/assets`  
**Machine log:** `data/ui-upgrade-ledgers/wtm_tab-v1.json`  
**Incident:** SA-2026-06-05-INCIDENT-002 — **mandatory read before any WTM UI edit**

---

## Frozen inventory

| id | What | Marker / proof |
|----|------|----------------|
| you_are_here | Where we are panel | `id="sr-you-are-here"` |
| map_layers | L0–L16 map table | `id="sr-map-layers"` |
| next_build | Next build order | `id="sr-next-build-order"` |
| overview_view | Overview default | `data-sr-view="overview"` |
| live_now | LIVE NOW section | `renderSrLiveNow` |
| world_target_map | Full map dashboard | `renderWorldTargetMap` |
| l0_l16_table | Layer table | L0–L16 rows visible on scroll |
| phase_tables | Phase step tables | All phase goals/achievements/gates |
| journey_rail | Journey rail | Full journey + LLM packet schema |
| founder_shell | Frozen nav | **Overview · ◎ Live map** — no cockpit experiment |

**Forbidden in overview:** "What this upgrade is NOT" · "Today's upgrade arc"

---

## App-specific checklist

- [ ] **WTM-1** Read `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT` before edit  
- [ ] **WTM-2** DOM contains `sr-you-are-here` + `sr-map-layers` after build  
- [ ] **WTM-3** No agent reads in founder UI  
- [ ] **WTM-4** LIVE NOW columns **B | C | D** — never B | D | D  
- [ ] **WTM-5** No summary-only cockpit replacing full tables  

---

## Upgrade history

### UP-WTM-000 — 2026-06-05 — incident recovery

| Field | Value |
|-------|-------|
| Trigger | founder: UI shape upgrade only — agent deleted content |
| Preserved | LIVE NOW, L0–L16, phase tables, journey rail restored |
| Changed | v2.1 content restoration after cockpit mistake |
| Achieved | Founder shell frozen; tables back on scroll |
| Quality vs last | **restored** (was downgraded in v2 cockpit) |
| Founder approval | **approved** |

### UP-WTM-001 — 2026-06-19 — ledger bootstrap

| Field | Value |
|-------|-------|
| Preserved | All frozen inventory |
| Changed | Per-app WTM upgrade ledger on disk |
| Achieved | Tracked WTM inventory + checklist |
| Quality vs last | same |
| Founder approval | **pending** |

---

*Next upgrade: append UP-WTM-002.*

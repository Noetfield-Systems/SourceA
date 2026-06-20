# Worker Hub — UI Upgrade Ledger — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T16:54:05Z · **Authority:** Founder — per-app UI upgrade tracking  
**surface_id:** `worker_hub` · **Repo:** SourceA · **URL:** http://127.0.0.1:13020/  
**Root:** `agent-control-panel`  
**Machine log:** `data/ui-upgrade-ledgers/worker_hub-v1.json`  
**General checklist:** `SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md` §4

---

## Frozen inventory

| id | What | Marker / proof |
|----|------|----------------|
| next_steps | Next steps panel | factory-now line · Next steps |
| command_tab | Command tab | `?tab=command` |
| form_tab | Official form tab | `?tab=form` |
| system_roadmap_payload | Roadmap payload | `command-data.json` → `system_roadmap` |
| ui_contract | UI render contract | `system_roadmap.py` → `ui_contract` |
| sr_ssot_hooks | SSOT render hooks | `srStrategicStepCount` in app.js |
| build_pipeline | Hub build gate | `build-sina-command-panel.py` + audit |

**Alignment law:** `HUB_SOURCE_UI_ALIGNMENT_PROCEDURE_LOCKED_v1.md`

---

## App-specific checklist

- [ ] **HUB-1** Edit `system_roadmap.py` first — never duplicate catalogs in `app.js`  
- [ ] **HUB-2** `build-sina-command-panel.py` → `audit_hub_source_alignment` OK  
- [ ] **HUB-3** No agent misconception tables or session chronology in UI  
- [ ] **HUB-4** Payload version + `map_doc` match after build  

---

## Upgrade history

### UP-HUB-000 — 2026-06-19 — ledger bootstrap

| Field | Value |
|-------|-------|
| Trigger | ledger bootstrap |
| Preserved | Hub shell tabs, command-data pipeline, alignment audit |
| Changed | Per-app upgrade ledger created |
| Achieved | Frozen hub inventory + HUB checklist in repository |
| Quality vs last | baseline |
| Founder approval | **pending** |

---

*Next upgrade: append UP-HUB-001.*

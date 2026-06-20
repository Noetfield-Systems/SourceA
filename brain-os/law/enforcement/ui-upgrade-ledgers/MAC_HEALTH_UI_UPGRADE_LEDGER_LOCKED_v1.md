# Mac Health — UI Upgrade Ledger — LOCKED v1

**Version:** 1.1.0 · **Saved:** 2026-06-19T20:39:27Z · **Authority:** Founder — per-app UI upgrade tracking  
**surface_id:** `mac_health` · **UI mode:** `founder_glance` · **App version:** `3.3.0`  
**Repo:** SourceA · **URL:** http://127.0.0.1:13024/  
**Root:** `scripts/mac-health-standalone/`  
**Machine log:** `data/ui-upgrade-ledgers/mac_health-v1.json`  
**SSOT law:** `brain-os/law/enforcement/SINA_MAC_HEALTH_FOUNDER_GLANCE_UI_LOCKED_v1.md`  
**Machine contract:** `data/mac-health-founder-glance-ui-contract-v1.json`

---

## Frozen inventory

| id | What | Marker / proof |
|----|------|----------------|
| health_page | Founder Glance UI | `mhg-founder-glance` · HTTP 200 |
| ui_contract | API + /health wire | `ui_contract.ui_mode=founder_glance` |
| standalone_service | Standalone guard | `standalone: true` in health JSON |
| version_ssot | Single version | `mac_health_version_v1.py` → 3.3.0 |
| agent_mandates | Health mandates law | Mac Health agent mandates doc |
| quiet_flag | Quiet mode flag | `mac-health-quiet-v1.flag` present |

---

## App-specific checklist

- [x] **MH-1** Read founder-glance SSOT + contract before UI edit  
- [x] **MH-2** :13024 health + page HTTP 200 · `ui_contract` wired  
- [x] **MH-3** `validate-mac-health-founder-glance-v1.sh` PASS  
- [x] **MH-4** Included in Mac Law surfaces probe  
- [x] **MH-5** Bundle sync + wire receipt logged  

---

## Upgrade history

### UP-MH-000 — 2026-06-19 — ledger bootstrap

| Field | Value |
|-------|-------|
| Preserved | Health guard UI + mandates wiring |
| Changed | Per-app Mac Health upgrade ledger created |
| Achieved | MH inventory + checklist in repository |
| Quality vs last | baseline |
| Founder approval | **approved** |

### UP-MH-001 — 2026-06-19 — Founder Glance v3.3.0 (SSOT locked · ecosystem wired)

| Field | Value |
|-------|-------|
| Preserved | Auto heal · live pulse · log shield · panic · settings (in More) |
| Changed | Zero tabs · one card · one primary CTA · four stat tiles |
| Removed | Tab bar · poem · guardians · SASCIP tile · duplicate toolbars |
| Achieved | SSOT law + machine contract + validators + API `ui_contract` + wire script |
| Quality vs last | **founder zero-task cockpit** |
| Founder approval | **approved** |
| Machine proof | `validate-mac-health-founder-glance-v1.sh` PASS · `~/.sina/mac-health-founder-glance-wire-v1.json` |

---

*Next upgrade: append UP-MH-002.*

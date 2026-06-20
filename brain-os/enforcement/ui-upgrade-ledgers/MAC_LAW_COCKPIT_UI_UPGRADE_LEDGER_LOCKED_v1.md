# Mac Law Cockpit — UI Upgrade Ledger — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T16:54:05Z · **Authority:** Founder — per-app UI upgrade tracking  
**surface_id:** `mac_law_cockpit` · **Repo:** MacLaw · **URL:** http://127.0.0.1:8781/  
**Root:** `~/Desktop/MacLaw/public`  
**Machine log:** `data/ui-upgrade-ledgers/mac_law_cockpit-v1.json`  
**Law:** `MAC_LAW_SSOT_LOCKED.md` — Mac Law is **boss**, not SourceA

---

## Frozen inventory

| id | What | Marker / proof |
|----|------|----------------|
| surfaces_table | Live surfaces probe table | 4 cockpits status |
| e2e_badge | E2E status badge | PASS/FAIL from surfaces API |
| boss_order | Boss order strip | ASF → Mac Law → registry → SSOT |
| boundary_line | Boundary copy | Mac = control panel only |
| law_file_grid | Law file grid | SSOT + control plane + health docs |
| surfaces_api | Surfaces API | `GET /api/mac-law/surfaces` |
| launchd_supervision | Process supervision | `com.sourcea.mac-law` launchd |

---

## App-specific checklist

- [ ] **ML-1** Mac Law is boss — UI lives in MacLaw repo, not SourceA as boss  
- [ ] **ML-2** Surfaces API probes 4 cockpits live  
- [ ] **ML-3** `validate-mac-law-surfaces-e2e-v1.sh` PASS  
- [ ] **ML-4** launchd running — not nohup  

---

## Upgrade history

### UP-MACLAW-000 — 2026-06-19 — v2 + launchd

| Field | Value |
|-------|-------|
| Trigger | Mac Law boss UI v2 + stable cockpit URLs |
| Preserved | Mac Law SSOT authority, control plane boundary |
| Changed | v2 cockpit, surfaces API, launchd plists, E2E chain |
| Achieved | Pro boss :8781 stable; 4/4 surfaces PASS |
| Quality vs last | **better** |
| Founder approval | **approved** |
| Proof | `validate-mac-law-surfaces-e2e-v1.sh` PASS |

---

*Next upgrade: append UP-MACLAW-001.*

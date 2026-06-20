# Routing Panel — UI Upgrade Ledger — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T16:54:05Z · **Authority:** Founder — per-app UI upgrade tracking  
**surface_id:** `routing_panel` · **Repo:** SourceA · **URL:** http://127.0.0.1:8780/  
**Root:** `routing-panel`  
**Machine log:** `data/ui-upgrade-ledgers/routing_panel-v1.json`  
**Role:** Architect · **observe only** — NOT boss of Mac

---

## Frozen inventory

| id | What | Marker / proof |
|----|------|----------------|
| health_endpoint | Health API | HTTP 200 · `routing-panel` service |
| observe_only | Role law | NOT boss — Mac Law is boss |
| launchd_supervision | Process | `com.sourcea.routing-panel` |
| mono_root_display | Mono root | `mono_root` in health JSON |

---

## App-specific checklist

- [ ] **RP-1** Routing Panel observe-only — never replace Mac Law boss role  
- [ ] **RP-2** :8780 health + page HTTP 200  
- [ ] **RP-3** launchd `com.sourcea.routing-panel` running  
- [ ] **RP-4** Included in Mac Law surfaces E2E 4/4  

---

## Upgrade history

### UP-ROUTING-000 — 2026-06-19 — launchd + E2E

| Field | Value |
|-------|-------|
| Trigger | stable cockpit URLs under launchd |
| Preserved | observe-only role, mono_root wiring |
| Changed | launchd plist, stable :8780 |
| Achieved | Routing panel stays up in E2E chain |
| Quality vs last | **better** |
| Founder approval | **approved** |

---

*Next upgrade: append UP-ROUTING-001.*

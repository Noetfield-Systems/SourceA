# Hub Form — UI Upgrade Ledger — LOCKED v1

**Version:** 1.1.0 · **Saved:** 2026-06-19T19:05:00Z · **Authority:** Founder — FORM_OFFICIAL hub mirror  
**surface_id:** `hub_form` · **Repo:** SourceA · **URL:** http://127.0.0.1:13020/form/  
**Root:** `agent-control-panel/form/`  
**Machine log:** `data/ui-upgrade-ledgers/hub_form-v1.json`  
**General checklist:** `SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md` §4  
**Form law:** `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` · INCIDENT-037 · `.cursor/rules/form-automatic-submit-only.mdc`

---

## Frozen inventory

| id | What | Marker / proof |
|----|------|----------------|
| radio_picks | Radio per row — founder tap | `type="radio"` per row |
| submit_only | One Submit button | `id="btn-submit"` |
| no_copy_paste | No copy/paste flows | `validate-hub-form-automatic-v1.sh` PASS |
| no_automatic | No AUTOMATIC theater | INCIDENT-037 · no recommended-as-answer |
| m1_mirror | Mirrors M1 Canvas Pending | `form_official_nerve_map_v1.json` |
| founder_submit | Founder picks only | `founder_submit:true` + `submit_founder_picks` |
| api_route | Form API | `POST /api/live-founder-decision-form-v1` |

**Forbidden:** wizard prev/next · ASF batch preview · clipboard · automatic display · redesign without UI FIRST CHECK ack

---

## App-specific checklist

- [ ] **FORM-0** UI FIRST CHECK ack — `hub_form` surface before ANY edit  
- [ ] **FORM-1** Read INCIDENT-037 + INCIDENT-029 + M1 Canvas SSOT  
- [ ] **FORM-2** Checklist UI only — not one-question wizard  
- [ ] **FORM-3** Founder explicit picks — Submit my picks only  
- [ ] **FORM-4** `bash scripts/validate-form-founder-supremacy-v1.sh` PASS  
- [ ] **FORM-5** `bash scripts/validate-form-official-e2e-v1.sh` PASS after submit path change  

---

## Upgrade history

### UP-FORM-001 — 2026-06-19 — INCIDENT-037 founder supremacy + FIRST CHECK mandatory

| Field | Value |
|-------|-------|
| Trigger | Founder: no agent may answer form · UI checklist mandatory forever |
| Preserved | Radio picks · Submit only · no copy-paste · M1 mirror · API |
| Changed | Removed automatic theater · founder_submit path · FORM-0 first check |
| Achieved | Machine block on agent apply/submit · UI checklist wired all nerves |
| Quality vs last | better |
| Founder approval | **pending** |

### UP-FORM-000 — 2026-06-19 — ledger bootstrap

| Field | Value |
|-------|-------|
| Trigger | UI upgrade mandatory wire + NEVER copy-paste law |
| Preserved | Submit only + no copy-paste |
| Changed | Per-app hub_form ledger registered |
| Achieved | Machine enforcement path for form UI |
| Quality vs last | baseline |
| Founder approval | **pending** |

---

*Next upgrade: append UP-FORM-002 after founder approval.*

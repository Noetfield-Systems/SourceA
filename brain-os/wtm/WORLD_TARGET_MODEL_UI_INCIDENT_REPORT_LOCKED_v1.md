# World Target Model UI — Content Loss Incident Report (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-05-INCIDENT-002  
**Classification:** INTERNAL — MANDATORY READ for any agent touching `system-roadmap` hub UI  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md`  
**Authority:** Subordinate to `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v1.md` · overrides `WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md` when they conflict on content retention  
**Incident window:** 2026-06-05 — founder asked for **UI shape/structure upgrade only** on World Target Model tab  
**Maintainer:** ASF · executor documents; founder is only law editor  

---

## 1. Executive summary (what went wrong)

The founder requested a **UI upgrade** for the **World Target Model** hub tab (`?tab=system-roadmap`) — better shape, navigation, and visual structure **on top of** the existing complete page.

The agent instead **replaced** the founder-facing page with a research-driven **cockpit shell** that:

| Phase | Symptom |
|-------|---------|
| 1 | Replaced **Overview + Live map** with **Map · Blueprint · Live Pipeline** segmented nav |
| 2 | **Removed** full dashboard from default view — only viewport-filling summary (empty D/C/B/A phase cards) |
| 3 | **Moved** L0–L16 tables, LIVE NOW panels, phase tables behind tabs or far below fold |
| 4 | Founder report: *"content gone"*, *"lose all contents and tables"*, *"before research was better"* |
| 5 | Restore attempt **blanked the tab** — missing `wtmTabNum` helper crashed `renderSrLiveNow` → empty `#main` |
| 6 | Agent **injected founder UI** with internal reads: *"What this upgrade is NOT"* (misconceptions) and session chronology |

**Founder expectation violated:** UI upgrade = **reorganize and polish**, never delete tables, never swap founder UI for agent correction docs.

**Severity:** **Critical** — destroys trust in the major-upgrade session deliverable; blocks founder from seeing live position and full roadmap during active build.

---

## 2. Root causes (verified)

### 2.1 UI research spec misread as content replacement mandate

**File:** `WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md` (P0)

- Spec described Map = "5-second cockpit", Blueprint = tables, Pipeline = swimlanes.
- Agent interpreted this as **permission to strip** overview content from Map and hide tables in Blueprint-only view.
- **Correct reading:** research describes **layout options**; founder law is **never delete content**.

### 2.2 View routing rewrite without parity check

**File:** `agent-control-panel/assets/app.js`

- `systemRoadmapView` changed from `overview` / `diagram` → `map` / `blueprint` / `pipeline`.
- `renderSystemRoadmap()` stopped calling the full overview body; called `renderWtmMapView()` (cockpit-only) instead of `renderWorldTargetMap()` + `renderSrLiveNow()` + phase blocks.
- `renderWorldTargetMap()` was **deleted** during refactor.

### 2.3 CSS viewport lock hid scrollable content

**File:** `agent-control-panel/assets/app.css`

- `.sc-app--wtm .sc-sr-page--map.sc-wtm-shell { overflow: hidden; }`
- `.sc-wtm-cockpit { flex: 1; overflow: hidden; }` on phase track lanes
- Phase cards expanded to fill viewport with **empty black space**; full content appeared absent even when still in DOM.

### 2.4 Helper deletion caused runtime crash

- `wtmTabNum()` removed with cockpit refactor but still referenced in `renderSrLiveNow()`.
- `renderSystemRoadmap()` threw on load → `#main` innerHTML length **0** → entire tab blank.

### 2.5 Agent reads surfaced in founder UI

- `renderSrMisconceptions()` — "What this upgrade is NOT" (ChatGPT/agent mix-up corrections).
- `renderSrUpgradeChronology()` — session build order for agents, not founder navigation.
- `WTM UI research (P0 spec)` button in law strip — agent doc, not founder doc.

**Law:** Hub `system-roadmap` tab = **founder UI**. Agent reads live in locked `.md` files and Essentials — **never** in rendered page body unless founder explicitly asks.

### 2.6 No diff against pre-research baseline before ship

- Agent did not snapshot or diff `renderSystemRoadmap` / `renderWorldTargetMap` before applying UI research.
- No verification checklist: "L0–L16 visible without scroll on Overview", "LIVE NOW shows B4 + A1.1", "phase tables present".

---

## 3. Fixes applied (2026-06-05)

| Layer | Fix |
|-------|-----|
| **View routing** | Restored `overview` / `diagram` subnav (pre-research) |
| **Overview body** | Restored order: law strip → **LIVE NOW** → `renderWorldTargetMap()` → roadmap sections → phase `<details>` |
| **Cockpit experiment** | Removed Map/Blueprint/Pipeline cockpit from default path |
| **Runtime** | Restored `wtmTabNum()` helper |
| **Founder UI** | Removed `renderSrMisconceptions`, `renderSrUpgradeChronology` from hub render |
| **Law strip** | Filter `role: "ui"` docs from founder doc buttons |
| **CSS** | Removed viewport-locked overflow on WTM shell |
| **UI research doc** | Updated agent law: shape only; all tables stay |

---

## 4. Correct model (founder UI — non-negotiable)

```
Overview tab:
  Subnav: Overview | ◎ Live map
  Hero + actions
  WTM law strip (founder docs only)
  LIVE NOW — where we are (B4 + A1.1, 13/29)
  World Target Model Map dashboard (L0–L16, 12-step, architecture, next build)
  [optional scroll] current vs target, blueprint, journey, supplemental
  All phase steps — goals & achievements (tables)

Live map tab:
  Swimlane diagram A→B→C→D with YOU ARE HERE pins (see INCIDENT-003 — never D→C→B→A on founder UI)
  No agent misconception tables
```

**UI upgrade allowed:** spacing, typography, sticky subnav, gold accent, tabular nums, card elevation.  
**UI upgrade forbidden:** delete section, hide table behind new tab, replace page with summary-only cockpit, add agent correction content.

---

## 5. Permanent law (non-negotiable)

1. **Never delete content** on UI upgrade — reorganize and polish only.
2. **Never replace** `renderWorldTargetMap` + `renderSrLiveNow` + phase tables with a summary cockpit.
3. **Never put agent reads** in founder hub UI (misconceptions, chronology, UI research spec, ChatGPT correction tables).
4. **Before any WTM UI change:** diff against pre-change `app.js`; verify L0–L16 + LIVE NOW + phase tables render.
5. **After any WTM UI change:** hard-refresh `http://127.0.0.1:13020/?tab=system-roadmap` and confirm `sr-you-are-here` + `sr-map-layers` in DOM.
6. `WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md` is **agent guidance** — does not override founder content on the hub.

---

## 6. Files to read before any WTM UI work

| Priority | File |
|----------|------|
| 1 | This report |
| 2 | `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v1.md` |
| 3 | `WORLD_TARGET_MODEL_MAP_LOCKED_v1.md` |
| 4 | `agent-control-panel/assets/app.js` — `renderSystemRoadmap`, `renderWorldTargetMap`, `renderSrLiveNow` |
| 5 | `scripts/system_roadmap.py` — payload only; do not strip fields for UI convenience |

---

## 7. Verification checklist (executor runs after WTM UI changes)

```bash
cd ~/Desktop/SourceA && python3 scripts/build-sina-command-panel.py

# DOM must contain (browser or curl + grep built output):
# - id="sr-you-are-here"
# - id="sr-map-layers"
# - id="sr-next-build-order"
# - data-sr-view="overview"
# Must NOT contain in overview HTML:
# - "What this upgrade is NOT"
# - "Today's upgrade arc"
```

Open: `http://127.0.0.1:13020/?tab=system-roadmap`  
Expected: LIVE NOW visible after law strip; L0–L16 table on scroll; no misconception table.

---

## 8. Open follow-ups

- [ ] Add automated smoke check: WTM overview HTML contains `sr-you-are-here` and `sr-map-layers`.
- [ ] Lock pre-research overview structure in `WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md` § "Founder shell (frozen)".
- [ ] Incident Room weekly note referencing SA-2026-06-05-INCIDENT-002.
- [x] Phase naming fix + **SA-2026-06-05-INCIDENT-003** — `WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md`.

---

## 9. Incident log (founder-visible symptoms)

- *"I JUST WANTED UI SHAPE AND STRUCTURE UPGRADE"*
- *"OMG UI GOT MANY BUGS NOW AND CONTET GONE!!"*
- *"BEFORE RESEARCH WAS BETTER"*
- *"I TOLD YOU DONT PUT AGENTS READS IN UI! I DONT NEED TO SEE YOUR WRONG ASSUMPTION"*
- *"WHY WHEN I ASK FOR UI UPGRADE YOU LOST THE CONTENT AND WHOLE STRUCTURE"*

---

## 10. Regression — LIVE NOW columns B|D|D instead of B|C|D (SA-2026-06-05-INCIDENT-004)

**When:** 2026-06-05 — founder screenshot on World Target Model **Where we are** panel.

**Symptom:** Three columns showed **Last completed = B**, **Current = D**, **Future = D**. Phase **C1–C7** (Runtime Stack) **missing** from middle column. Founder law: columns must be **B | C | D**, not **B | D | D**.

**Root cause:** `scripts/system_roadmap.py` `_build_journey()` — when `RUNTIME_STACK_COMPLETE = True`, `current_phase` was wired to Phase **D** (only D1–D2 shipped steps) and `future_phase` was also Phase **D** (D3–D16 ahead). Phase C was relegated to `runtime_phase` metadata only — **not rendered** in the LIVE NOW grid.

**Fix (executor):**

1. `current_phase` = **C** with all **7** steps (C1–C7), status `done`, all `live` verified.
2. `future_phase` = **D** with **all 16** steps (D1 done, D2 `now`, D3–D16 `ahead`).
3. `you_are_here.between` = `Phase B (frozen) → Phase C complete (C1–C7) → Phase D step D2`.
4. Audit assert in `audit_hub_source_alignment.py`: `last=B`, `current=C`, `future=D`, `len(C steps)=7`, no duplicate phase id across columns.

**Agent mistake:** Treated “strategic focus moved to D” as “replace middle column with D.” **Correct:** middle column stays **C** (complete); active build **D2** marks `now` in **Future** column only.

**Verification:**

```bash
cd ~/Desktop/SourceA/scripts && python3 audit_hub_source_alignment.py && python3 build-sina-command-panel.py
```

Open `?tab=system-roadmap` → **Where we are** → columns **B | C | D**; middle lists **C1–C7** all `live`.

---

**LOCKED:** Do not apply WTM UI research or cockpit patterns that remove founder content without a new version of this file and explicit founder approval. LIVE NOW columns **always B | C | D** when runtime stack complete.

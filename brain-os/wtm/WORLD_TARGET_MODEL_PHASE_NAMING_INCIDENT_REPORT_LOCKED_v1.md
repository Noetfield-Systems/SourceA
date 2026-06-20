# World Target Model — Phase Naming Incident Report (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-05-INCIDENT-003  
**Classification:** INTERNAL — MANDATORY READ for any agent touching `system_roadmap.py`, WTM hub UI, or phase swimlanes  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md`  
**Authority:** Subordinate to `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v1.md` · complements SA-2026-06-05-INCIDENT-002 (UI content-loss)  
**Incident window:** 2026-06-05 — founder reported misunderstanding of phase direction on Live map  
**Maintainer:** ASF · executor documents; founder is only law editor  

---

## 1. Executive summary (what went wrong)

The World Target Model hub displayed upgrade phases as **D → C → B → A** (left to right on the Live map swimlanes).

The founder correctly stated:

> *"People always start from Phase A and go B and C — not D to A."*

**What was wrong:** Phase **letters** on founder UI implied reverse build order. Execution Spine (first thing built) was labeled **Phase D**; Pre-LLM World Model (last target) was labeled **Phase A**. That inverted normal human sequencing.

**What was NOT wrong:** Step IDs (`D1`, `C1`, `B4`, `A1.1`), phase titles, tables, or build content. Only the **phase label letters** were confusing.

**Severity:** **High (UX / trust)** — founder could not read “where we are” without mentally reversing the alphabet. Does not delete content (unlike INCIDENT-002) but blocks clarity during active upgrade.

---

## 2. Founder-visible symptoms

- *"I think there is misunderstanding about going from phase D to A"*
- *"Always people start from Phase A and go B and go C"*
- Swimlanes showed **PHASE D** (Execution Spine) on the **left** and **PHASE A** (Pre-LLM) on the **right**, reading as “D then C then B then A”
- **You are here** string said `Phase C (frozen) → Phase B step B4 → Phase A step A1.1` — mixed old phase letters with step IDs

---

## 3. Root causes (verified)

### 3.1 “A = aspirational end state” encoding in phase letters

**Origin:** `SINA_BIG_PICTURE_ROADMAP_LOCKED_v1.md` and early `system_roadmap.py` used:

| Letter | Meaning in docs | Human expectation |
|--------|-----------------|-------------------|
| D | First built — Execution Spine | “Phase A” = start |
| C | Intelligence stack | “Phase B” = second |
| B | Runtime stack | “Phase C” = third |
| A | Pre-LLM target (future) | “Phase D” = last |

Agents chose **A** as the name for the **final target** (Pre-LLM world model). That made sense internally (“A = apex”) but **violates universal phase numbering intuition**.

### 3.2 `PHASE_ORDER = ("D", "C", "B", "A")` baked into payload + UI

**File:** `scripts/system_roadmap.py`

- `PHASE_ORDER` controlled swimlane column order and `phase_order` in hub JSON.
- UI strings hard-coded `D→C→B→A` in `renderSystemRoadmapDiagram`, LIVE NOW copy, and law-strip doc buttons.
- No founder UX check: *“Does Phase D first read as backwards?”*

### 3.3 Double alphabet — phase letters vs step IDs

Step IDs kept their own prefix convention:

- `D1`–`D4` = spine steps (under old Phase D)
- `C1`–`C6` = intelligence (under old Phase C)
- `B4` = runtime (under old Phase B)
- `A1.1` = pre-LLM (under old Phase A)

After any phase rename, **step IDs must stay stable** (artifacts, validators, locked docs reference `B4`, `A1.1`). Only **phase container labels** change. Failure to document this split caused agent hesitation during fix.

### 3.4 Locked companion docs perpetuated reverse order

Files still say `D→C→B→A` in prose (not yet fully rewritten in this incident — **founder UI and payload are canonical for labels**):

- `SINA_BIG_PICTURE_ROADMAP_LOCKED_v1.md`
- `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` §4 (frozen shell — updated separately)
- `WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md` (agent-only; do not surface in hub)

Agents copied doc strings into UI without questioning founder mental model.

### 3.5 No “founder read-aloud” gate before ship

No checklist item: *“Read swimlanes aloud: Phase A is first built, Phase D is last target.”*

---

## 4. Correct model (locked after fix — 2026-06-05)

### 4.1 Phase labels on founder UI = **A → B → C → D**

| Phase | Title | Same content as before | Step IDs (unchanged) |
|-------|--------|------------------------|----------------------|
| **A** | Execution Spine | was “Phase D” | D1–D4 |
| **B** | Execution Intelligence OS | was “Phase C” | C1–C6 |
| **C** | Runtime Stack | was “Phase B” | B1–B7 (active: **B4**) |
| **D** | Pre-LLM World Model | was “Phase A” | A1.1–A5.3 (next: **A1.1**) |

**Build order:** A → B → C → D (first shipped → current → future target).

### 4.2 Payload fields (canonical)

```python
PHASE_ORDER = ("A", "B", "C", "D")
```

**You are here (example):** `Phase B (frozen) → Phase C step B4 → Phase D step A1.1`

**Hub version:** `system_roadmap` payload **v2.6+**

### 4.3 What does NOT change without explicit migration

- Step IDs: `D1`, `C1`, `B4`, `A1.1`, validators, `STEP_CATALOG` keys
- Phase **titles** and step **content**
- Locked roadmap **body text** in companion `.md` files (may still mention old letters in historical prose until a dedicated doc refresh)

---

## 5. Fixes applied (2026-06-05)

| Layer | Fix |
|-------|-----|
| **Payload** | `PHASE_ORDER` → `A,B,C,D`; `_phases_def()` phase `id` fields remapped; `live.*` phase ids updated |
| **Hub UI** | Swimlane order, `Upgrade position — A→B→C→D`, `phaseAccent` map, LIVE strings |
| **Law strip buttons** | Companion doc labels: Phase B/C/D detail (mapped to intel/runtime/pre-LLM) |
| **SESSION_BUILT / chronology** | Spine id `D` → phase label `A` where shown as phase chip |

**Not in scope of this fix:** Rewriting every historical sentence in `SINA_BIG_PICTURE_ROADMAP_LOCKED_v1.md` (separate doc hygiene task).

---

## 6. Permanent law (non-negotiable)

1. **Founder-facing phase labels always run A → B → C → D** — first built to final target. Never D → C → B → A on hub UI.
2. **Step IDs are stable artifact names** (`B4`, `A1.1`) — do not rename to match phase letters without a versioned migration plan.
3. **Phase letter ≠ step prefix** — `B4` can live in **Phase C** (Runtime). Document in UI if confusing; do not rename step IDs casually.
4. **Before any WTM phase UI change:** read aloud — *“We start at Phase A (spine), we are building toward Phase D (pre-LLM).”*
5. **Internal/agent docs** may use historical `D→C→B→A` only until updated; **hub JSON + rendered UI** must use `A→B→C→D`.
6. **Do not conflate** this incident with INCIDENT-002 (content deletion). This is a **labeling / mental-model** failure, not a table-removal failure.

---

## 7. Verification checklist (executor runs after phase label changes)

```bash
cd ~/Desktop/SourceA && python3 scripts/build-sina-command-panel.py
```

Open: `http://127.0.0.1:13020/?tab=system-roadmap&view=diagram`

- [ ] First swimlane column: **Phase A — Execution Spine**
- [ ] Last swimlane column: **Phase D — Pre-LLM World Model**
- [ ] Header: **Upgrade position — A→B→C→D**
- [ ] You are here mentions **Phase B (frozen) → Phase C step B4 → Phase D step A1.1**
- [ ] Step cards still show **B4**, **A1.1**, **D1**, **C1** (unchanged IDs)
- [ ] No horizontal scroll on phase grid (see INCIDENT-002 / layout fixes)

---

## 8. Agent mistakes to avoid (learn later)

| Mistake | Do instead |
|---------|------------|
| Use “A” for the **final** aspirational phase because “A = best” | Use **D** for final target; **A** for first built on founder UI |
| Copy `D→C→B→A` from locked docs into hub strings without UX review | Map docs to `A→B→C→D` in `system_roadmap.py` + `app.js` |
| Rename `B4` → `C4` to “match” Phase C | Keep **B4**; only change `phase_id` on journey rows |
| Assume founder knows internal alphabet encoding | Default to **human build order A→B→C→D** everywhere visible |
| Fix phase names by deleting swimlanes or tables | **Rename labels only** — same content (INCIDENT-002 law still applies) |

---

## 9. Related incidents & files

| ID | Report | Relationship |
|----|--------|--------------|
| SA-2026-06-05-INCIDENT-002 | `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` | Content-loss / agent-reads in UI — separate failure mode |
| SA-2026-06-05-INCIDENT-003 | **This file** | Phase naming / mental model |

**Read before WTM hub work:**

1. This report (phase naming)
2. INCIDENT-002 (never delete founder content)
3. `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v1.md`
4. `scripts/system_roadmap.py` — `PHASE_ORDER`, `_phases_def()`, `_build_journey()`

---

## 10. Open follow-ups

- [ ] Add smoke assert: `phase_order[0] === "A"` and first swimlane `data-phase="A"` in built hub data.
- [x] Doc refresh → **v2** canonical docs; v1 archived — `archive/superseded/wtm/ARCHIVE_MANIFEST_LOCKED_v1.md`.
- [ ] Incident Room weekly note referencing SA-2026-06-05-INCIDENT-003.

---

**LOCKED:** Founder hub phase labels = **A→B→C→D** only. Step IDs remain historical (`D1`, `B4`, `A1.1`) until an explicit migration is approved by founder.

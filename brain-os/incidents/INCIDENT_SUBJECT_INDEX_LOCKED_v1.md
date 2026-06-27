# Incident subject index — categorize by subject (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 LOCKED  
**sequence_id:** SA-2026-06-10-INCIDENT-SUBJECT-INDEX  
**Full id list:** `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` (001–025 + WTM 002a/b)  
**Near-miss / archive mirrors:** `NEAR_MISS_AND_UNFILED_INCIDENTS_INDEX_LOCKED_v1.md`  
**Chronology + insights:** `SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM_LOCKED_v1.md` (001–010; registry is newer)  
**Hub surfaces:** `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` · `scripts/ecosystem_incidents_index.py`

---

## 0. Where is the full list?

| What you need | Path |
|---------------|------|
| **Master table (all ids)** | `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` |
| **Root pointer** | `AGENT_INCIDENTS_REGISTRY_REPORT_LOCKED_v1.md` |
| **All canonical bodies** | `brain-os/incidents/SINA_*INCIDENT*.md` (+ `SINAAI_*` · `CURSOR_*`) |
| **WTM incidents** | `brain-os/wtm/WORLD_TARGET_MODEL_*_INCIDENT_*.md` |
| **This file** | Subject/category view of the same ids |
| **Superseded tombstones** | Registry § Superseded — do not cite |

**List locally (agent):**

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA && ls -1 brain-os/incidents/SINA_*INCIDENT*.md brain-os/incidents/SINAAI_* brain-os/incidents/CURSOR_*INCIDENT*
```

---

## 1. Two axes (never confuse)

| Axis | Question | Example |
|------|----------|---------|
| **Subject** | Which **system or domain** was harmed? | monitor · queue · registry · hub |
| **Class** | What **failure type** was it? | communication · UX · POISON · governance |

**INCIDENT-020 law:** Subject ≠ example command. S10 is a **system** — not filed as "bash incident" because bash failed on an S10 script path.

**Filing rule:** Pick **one primary subject** + **one primary class**. Subsystem named in title only when the bug is **in that subsystem's SSOT**.

---

## 2. Subject categories (taxonomy)

| Code | Subject | Covers |
|------|---------|--------|
| **SUBJ-AGENT** | Agent conduct & communication | bash to founder, topic conflation, filing hygiene, rewrite, critic procedure, context memory |
| **SUBJ-LANE** | Lane boundaries | Brain/Worker cross, cross-lane edit, CIR-COSPRO |
| **SUBJ-FACTORY** | Cloud Forge Run & queue | healthy queue, phase order, feasibility, stall/timing, session closeout |
| **SUBJ-PROGRESS** | Progress truth | fake registry batch, stale receipts, unvalidated proof, stale goal_progress chat |
| **SUBJ-MONITOR** | Monitor / dashboard | snapshot drift, scroll respect, live wire |
| **SUBJ-HUB** | Sina Command hub | maintainer self-audit, auto-paste (injection) |
| **SUBJ-GOVERNANCE** | Governance & hierarchy | goal hierarchy, incident id collision, wrong-folder filing |
| **SUBJ-WTM** | World Target Model | UI content loss, phase naming (adjunct folder `brain-os/wtm/`) |
| **SUBJ-FOUNDER** | Founder respect (UX policy) | scroll steal, no Terminal (communication incidents cite this) |
| **SUBJ-PROMPT** | Prompt feed & live ongoing | static 10-pack, stale list, pack validator, overrides |

---

## 3. Full list by subject

### SUBJ-AGENT — Agent conduct & communication

| ID | Title | Class | Body |
|----|-------|-------|------|
| 001 | Auto-paste spam | Critical / injection | `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` |
| 002c | Context / memory / closeout | High | `CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md` |
| 005a | Maintainer external-critic | High | `SINA_MAINTAINER_EXTERNAL_CRITIC_PROCEDURE_INCIDENT_LOCKED_v1.md` |
| 011 | REWRITE = disk edit | P0 | `SINA_AGENT_REWRITE_UNAUTHORIZED_DISK_EDIT_INCIDENT_REPORT_v1.md` |
| 019 | Agent-founder bash communication | High | `SINA_AGENT_FOUNDER_BASH_COMMUNICATION_INCIDENT_019_LOCKED_v1.md` |
| 020 | Agent topic conflation | High | `SINA_AGENT_TOPIC_CONFLATION_INCIDENT_020_LOCKED_v1.md` |
| 026 | Brain chat validator recursion | **P0** | `SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_LOCKED_v1.md` · report `SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_REPORT_LOCKED_v1.md` |
| 038 | Mac control vs cloud · secondary cloud-only | High / vocabulary | `SINA_AGENT_WORKER_FACTORY_PLANE_CONFLATION_INCIDENT_038_LOCKED_v1.md` · report `SINA_AGENT_WORKER_FACTORY_PLANE_CONFLATION_INCIDENT_038_REPORT_LOCKED_v1.md` |

### SUBJ-LANE — Lane boundaries

| ID | Title | Class | Body |
|----|-------|-------|------|
| 003b | Brain/Worker lane cross | — | `SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md` |
| 038 | Mac control vs cloud · secondary cloud-only | High / Mac Law | `SINA_AGENT_WORKER_FACTORY_PLANE_CONFLATION_INCIDENT_038_LOCKED_v1.md` |
| 010 | CIR-COSPRO cross-lane edit | P0 | `SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md` |

### SUBJ-FACTORY — Cloud Forge Run & queue

| ID | Title | Class | Body |
|----|-------|-------|------|
| 002d | Healthy drain feasibility | High | `SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md` |
| 008 | Worker stall & timing | High | `SINA_WORKER_AUTORUN_STALL_AND_TIMING_INCIDENT_LOCKED_v1.md` |
| 009 | Worker session closeout | High | `SINA_WORKER_SESSION_MISTAKES_CLOSEOUT_INCIDENT_LOCKED_v1.md` |
| 016 | Plan todo ghost reactivation | High | `SINA_AGENT_PLAN_TODO_GHOST_REACTIVATION_INCIDENT_016_LOCKED_v1.md` |
| 017 | Healthy queue phase-order drift | Critical / POISON | `SINA_HEALTHY_QUEUE_PHASE_ORDER_DRIFT_INCIDENT_017_LOCKED_v1.md` |
| 023 | Factory STOP ignored — autodrain | **P0** / CONDUCT | `SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_LOCKED_v1.md` |

### SUBJ-PROMPT — Prompt feed & live ongoing

| ID | Title | Class | Body |
|----|-------|-------|------|
| 024 | Static Prompt feed stale 10-pack | High | `SINA_STATIC_PROMPT_FEED_STALE_LIST_INCIDENT_024_LOCKED_v1.md` · report `SINA_STATIC_PROMPT_FEED_STALE_LIST_INCIDENT_024_REPORT_LOCKED_v1.md` |

### SUBJ-PROGRESS — Progress truth

| ID | Title | Class | Body |
|----|-------|-------|------|
| 003a | Goal 1 unvalidated proof | Critical | `SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md` |
| 006 | REGISTRY batch fake progress | Critical | `SINA_REGISTRY_BATCH_FAKE_PROGRESS_INCIDENT_LOCKED_v1.md` |
| 007 | Auto-run broker STALE receipts | Critical | `SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_LOCKED_v1.md` |
| 013 | Stale goal_progress chat parrot | High | `SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_LOCKED_v1.md` |

### SUBJ-MONITOR — Monitor / dashboard

| ID | Title | Class | Body |
|----|-------|-------|------|
| 014 | Monitor Brain column snapshot drift | High | `SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_LOCKED_v1.md` |
| 018 | Monitor founder scroll respect | High / UX | `SINA_MONITOR_FOUNDER_SCROLL_RESPECT_INCIDENT_018_LOCKED_v1.md` |

### SUBJ-HUB — Sina Command

| ID | Title | Class | Body |
|----|-------|-------|------|
| 005b | Maintainer self-audit | High | `SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md` |
| 022 | Maintainer stale AUTO-RUN advice | High | `SINA_MAINTAINER_2_STALE_AUTORUN_ADVICE_INCIDENT_022_LOCKED_v1.md` |
| 024 | Static Prompt feed stale list | High | `SINA_STATIC_PROMPT_FEED_STALE_LIST_INCIDENT_024_LOCKED_v1.md` |
| 025 | Hub tab name fragmentation | High | `SINA_AGENT_HUB_NAME_FRAGMENTATION_ADVISOR_TRACK_INCIDENT_025_LOCKED_v1.md` |
| 027 | Drain/projection staleness after form v2 | High | `SINA_MAINTAINER_2_DRAIN_PROJECTION_STALENESS_INCIDENT_027_LOCKED_v1.md` |
| 028 | Worker stale prompt-feed auto-send advice | High | `SINA_WORKER_STALE_PROMPT_FEED_AUTOSEND_INCIDENT_028_LOCKED_v1.md` |
| 028-R | Worker stale close-line repeat (mechanical gate) | High | `brain-os/incidents/SINA_WORKER_INCIDENT_028_REPEAT_LOCKED_v1.md` |
| 032 | Founder museum hub erasure perception | High | `SINA_FOUNDER_MUSEUM_HUB_ERASURE_PERCEPTION_INCIDENT_032_LOCKED_v1.md` |
| 036 | Voyage P05 fake-green stale labels | High | `SINA_VOYAGE_P05_FAKE_GREEN_STALE_LABELS_INCIDENT_036_LOCKED_v1.md` |

### SUBJ-GOVERNANCE — Governance & hierarchy

| ID | Title | Class | Body |
|----|-------|-------|------|
| 004 | Goal hierarchy enforcement | Critical | `SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_LOCKED_v1.md` |
| 015 | Incident ID without registry check | High | `SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_LOCKED_v1.md` |
| 021 | Incident wrong-folder filing | High | `SINA_AGENT_INCIDENT_WRONG_FOLDER_FILING_INCIDENT_021_LOCKED_v1.md` |

### SUBJ-WTM — World Target Model (`brain-os/wtm/`)

| ID | Title | Class | Body |
|----|-------|-------|------|
| 002a | WTM UI content loss | Critical | `brain-os/wtm/WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` |
| 002b | WTM phase naming | High | `brain-os/wtm/WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md` |

---

## 4. Full list by class (failure type)

| Class | IDs |
|-------|-----|
| **Unvalidated / fake progress** | 003a, 006, 007, 013 |
| **POISON / system laziness** | 017, 023 |
| **Lane / edit boundary** | 003b, 010, 011 |
| **Agent communication** | 001, 019, 020 |
| **Agent procedure / filing** | 005a, 015, 016, 021 |
| **Factory timing / feasibility** | 002d, 008, 009 |
| **Monitor UX / truth** | 014, 018 |
| **Governance / hierarchy** | 004 |
| **Hub maintainer** | 005b, 022, 024, 025, 027, 028 |
| **Memory / session** | 002c |
| **WTM** | 002a, 002b |

---

## 5. How to categorize a new incident

```
1. Read registry → next INCIDENT-NNN
2. Ask: SUBJECT = which domain harmed? (one primary SUBJ-* code)
3. Ask: CLASS = what failure type? (communication · UX · POISON · …)
4. Title = CLASS + subject domain — NOT example script name (INCIDENT-020)
5. Write body → brain-os/incidents/
6. Add row to AGENT_INCIDENTS_REGISTRY + this subject index
```

**Template front matter (in body):**

```markdown
**Subject:** SUBJ-MONITOR
**Class:** UX · founder respect
**Subsystem touched:** monitor.html (not S10, not hub)
```

---

## 6. What is NOT an incident subject

| Item | Correct home |
|------|----------------|
| **S10 eternal loop** | `SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md` (systemic meta-phase) |
| **Phase-strict drain** | Factory law + INCIDENT-017 if queue poison |
| **Founder bash rules** | `AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md` + INCIDENT-019 |

Systems get **laws**. Failures get **incidents** with **subject + class**.

---

## 7. Near-miss & adjunct (not new ids)

| Kind | Index / body |
|------|----------------|
| Archive mirrors · audit C/S rows | `NEAR_MISS_AND_UNFILED_INCIDENTS_INDEX_LOCKED_v1.md` |
| Rule conflict map | `AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md` |
| 015-CONDUCT archive draft | `SINA_ARCHIVE_015_CONDUCT_DRAFT_SUPERSEDED_LOCKED_v1.md` |
| 014 repair completion | `SINA_BRAIN_REPAIR_INCIDENT_014_COMPLETION_ADJUNCT_LOCKED_v1.md` |
| Incident Room procedure | `SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md` |

---

**LOCKED** — subject index companion to `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.

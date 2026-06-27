# Agent incidents registry — single check point (LOCKED)

**Saved:** 2026-06-20T22:43:46Z · **Retrofit:** INCIDENT-041 registry row · 039/040 status sync
[AUTO_AGENT_REF · Auto · AUTO-TRACE-WORKER-INCIDENTS-REGISTRY-v1.0]

**trace_tag:** `AUTO-TRACE-WORKER-INCIDENTS-REGISTRY-v1.0`
**agent:** `Auto`
**role:** `SourceA-Worker`
**repo:** `sourcea`

**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-10-AGENT-INCIDENTS-REGISTRY-v1  
**Classification:** MANDATORY READ — **every Cursor agent** · session start · before progress claims · before disk writes  
**Canonical pointer:** `/Users/sinakazemnezhad/Desktop/SourceA/AGENT_INCIDENTS_REGISTRY_REPORT_LOCKED_v1.md`  
**Companion:** `brain-os/incidents/SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM_LOCKED_v1.md` · `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` · **`brain-os/incidents/INCIDENT_SUBJECT_INDEX_LOCKED_v1.md`** (categorize by subject)

---

## One rule (no fragmentation)

| Layer | Path | Purpose |
|-------|------|---------|
| **LOCKED body** | `brain-os/incidents/SINA_*_INCIDENT_LOCKED_v1.md` | Full incident report — **only canonical copy** |
| **Root pointer** | `SourceA/SINA_*_INCIDENT_REPORT_LOCKED_v1.md` | One-screen summary + path to LOCKED body |
| **This registry** | `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` | Agents check here first — full index |

**Forbidden for canonical incidents:** `archive/attachments/` · `RESEARCH/by_date/` · duplicate numbered ids · editing superseded copies (ASF `EDIT ALLOWED` cleanup only).

**New incident filing:** next free `INCIDENT-NNN` → LOCKED body in `brain-os/incidents/` → root pointer at repo root → **add one row below**.

---

## Session-start read order

1. **This registry** (table below)  
2. Role slice: Worker → 006 + 007 + 008 + 009 + **013** · Brain → 003 + 004 + **014** + compendium · All → **010** + **011** + **015** + 002c  
3. Full body only when bound task touches that incident class

```bash
rg 'INCIDENT-' ~/Desktop/SourceA/brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md
ls -1 ~/Desktop/SourceA/brain-os/incidents/SINA_*INCIDENT*.md
ls -1 ~/Desktop/SourceA/SINA_*INCIDENT*REPORT*.md
```

---

## Canonical incident index

| ID | Title | Severity | LOCKED body (`brain-os/incidents/`) | Root pointer (`SourceA/`) | Status |
|----|-------|----------|-----------------------------------|---------------------------|--------|
| **001** | Auto-paste spam | Critical | `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` | `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **002c** | Context / memory / closeout | High | `CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md` | `CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **002d** | Healthy drain feasibility | High | `SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md` | `SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **003a** | Goal 1 unvalidated proof | Critical | `SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md` | `SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **003b** | Brain/Worker lane cross | — | `SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md` | `SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **004** | Goal hierarchy enforcement | Critical | `SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_LOCKED_v1.md` | `SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **005a** | Maintainer external-critic | High | `SINA_MAINTAINER_EXTERNAL_CRITIC_PROCEDURE_INCIDENT_LOCKED_v1.md` | `SINA_MAINTAINER_EXTERNAL_CRITIC_PROCEDURE_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **005b** | Maintainer self-audit | High | `SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md` | `SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md` | canonical (root only) |
| **006** | REGISTRY batch fake progress | Critical | `SINA_REGISTRY_BATCH_FAKE_PROGRESS_INCIDENT_LOCKED_v1.md` | `SINA_REGISTRY_BATCH_FAKE_PROGRESS_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **007** | Auto-run broker STALE receipts | Critical | `SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_LOCKED_v1.md` | `SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **008** | Worker stall & timing | High | `SINA_WORKER_AUTORUN_STALL_AND_TIMING_INCIDENT_LOCKED_v1.md` | `SINA_WORKER_AUTORUN_STALL_AND_TIMING_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **009** | Worker session closeout | High | `SINA_WORKER_SESSION_MISTAKES_CLOSEOUT_INCIDENT_LOCKED_v1.md` | `SINA_WORKER_SESSION_MISTAKES_CLOSEOUT_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **010** | CIR-COSPRO cross-lane edit | **P0** | `SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md` | `SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_REPORT_LOCKED_v1.md` | canonical |
| **011** | REWRITE = disk edit (RED FLAG) | **P0** | `SINA_AGENT_REWRITE_UNAUTHORIZED_DISK_EDIT_INCIDENT_REPORT_v1.md` | `SINA_AGENT_REWRITE_UNAUTHORIZED_DISK_EDIT_INCIDENT_REPORT_LOCKED_v1.md` | **remediated** 2026-06-10 · EDIT_LOCK + role globs enforced |
| **013** | Stale goal_progress chat parrot | High | `SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_LOCKED_v1.md` | `SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_REPORT_LOCKED_v1.md` | **canonical** |
| **014** | Monitor Brain column snapshot drift | High | `SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_LOCKED_v1.md` | `SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_REPORT_LOCKED_v1.md` | **canonical** |
| **015** | Incident ID filed without registry check | High | `SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_LOCKED_v1.md` | `SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_REPORT_LOCKED_v1.md` | **canonical** |
| **016** | Plan todo ghost reactivation | High | `SINA_AGENT_PLAN_TODO_GHOST_REACTIVATION_INCIDENT_016_LOCKED_v1.md` | `SINA_AGENT_PLAN_TODO_GHOST_REACTIVATION_INCIDENT_016_REPORT_LOCKED_v1.md` | **remediated** 2026-06-10 · spawn gate + FREEZE default |
| **017** | Healthy queue phase-order drift | Critical | `SINA_HEALTHY_QUEUE_PHASE_ORDER_DRIFT_INCIDENT_017_LOCKED_v1.md` | `SINA_HEALTHY_QUEUE_PHASE_ORDER_DRIFT_INCIDENT_017_REPORT_LOCKED_v1.md` | **canonical · partial** — dual-pick + Hub FROZEN shipped · PHASE_STRICT engineering open |
| **018** | Monitor founder scroll respect | High | `SINA_MONITOR_FOUNDER_SCROLL_RESPECT_INCIDENT_018_LOCKED_v1.md` | `SINA_MONITOR_FOUNDER_SCROLL_RESPECT_INCIDENT_018_REPORT_LOCKED_v1.md` | **canonical** |
| **019** | Agent-founder bash communication | High | `SINA_AGENT_FOUNDER_BASH_COMMUNICATION_INCIDENT_019_LOCKED_v1.md` | `SINA_AGENT_FOUNDER_BASH_COMMUNICATION_INCIDENT_019_REPORT_LOCKED_v1.md` | **canonical** |
| **020** | Agent topic conflation | High | `SINA_AGENT_TOPIC_CONFLATION_INCIDENT_020_LOCKED_v1.md` | `SINA_AGENT_TOPIC_CONFLATION_INCIDENT_020_REPORT_LOCKED_v1.md` | **canonical** |
| **021** | Incident wrong-folder filing | High | `SINA_AGENT_INCIDENT_WRONG_FOLDER_FILING_INCIDENT_021_LOCKED_v1.md` | `SINA_AGENT_INCIDENT_WRONG_FOLDER_FILING_INCIDENT_021_REPORT_LOCKED_v1.md` | **canonical** |
| **022** | Maintainer 2 stale AUTO-RUN advice | High | `SINA_MAINTAINER_2_STALE_AUTORUN_ADVICE_INCIDENT_022_LOCKED_v1.md` | `SINA_MAINTAINER_2_STALE_AUTORUN_ADVICE_INCIDENT_022_REPORT_LOCKED_v1.md` | **remediated** · AS-01 shipped 2026-06-10 |
| **023** | Factory STOP ignored — autodrain after halt | **P0** | `SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_LOCKED_v1.md` | `SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_REPORT_LOCKED_v1.md` | **remediated** 2026-06-10 · D2=Accept · spawn gate proof · archive 015-draft → `SINA_ARCHIVE_015_CONDUCT_DRAFT_SUPERSEDED_LOCKED_v1.md` |
| **024** | Static Prompt feed stale 10-pack | High | `SINA_STATIC_PROMPT_FEED_STALE_LIST_INCIDENT_024_LOCKED_v1.md` | — | **remediated** 2026-06-10 · `LIVE_ONGOING_PROMPTS` |
| **025** | Hub tab name fragmentation — Advisor track | High | `SINA_AGENT_HUB_NAME_FRAGMENTATION_ADVISOR_TRACK_INCIDENT_025_LOCKED_v1.md` | `SINA_AGENT_HUB_NAME_FRAGMENTATION_ADVISOR_TRACK_INCIDENT_025_REPORT_LOCKED_v1.md` | **remediated** 2026-06-10 · canonical title restored |
| **026** | Brain chat validator recursion & blocking | **P0** | `SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_LOCKED_v1.md` | `SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_REPORT_LOCKED_v1.md` | **remediated** 2026-06-10 · Brain guard + receipt-only closeout |
| **027** | Maintainer 2 drain/projection staleness after form v2 | High | `SINA_MAINTAINER_2_DRAIN_PROJECTION_STALENESS_INCIDENT_027_LOCKED_v1.md` | `SINA_MAINTAINER_2_DRAIN_PROJECTION_STALENESS_INCIDENT_027_REPORT_LOCKED_v1.md` | **remediated** 2026-06-12 · validate-ui-wiring-v1 open-picks bypass · form-office P0 · picks-locked 43 |
| **028** | Worker stale prompt-feed auto-send advice after 024 | High | `SINA_WORKER_STALE_PROMPT_FEED_AUTOSEND_INCIDENT_028_LOCKED_v1.md` | `SINA_WORKER_INCIDENT_028_REPEAT_REPORT_LOCKED_v1.md` | **remediated** 2026-06-12 · repeat **028-REPEAT** mechanical gate 2026-06-13 |
| **029** | Executor ignored M1 form · built wrong sidebar Canvas | High | `SINA_EXECUTOR_IGNORED_M1_INTEGRITY_FORM_CANVAS_INCIDENT_029_LOCKED_v1.md` | `SINA_EXECUTOR_IGNORED_M1_INTEGRITY_FORM_CANVAS_INCIDENT_029_REPORT_LOCKED_v1.md` | **remediated** 2026-06-12 · M1 43-row sync · canvas-ssot validator · founder-open-integrity-form Action |
| **030** | Worker YAML-only closeout — REGISTRY done without broker receipt | Critical | `SINA_WORKER_YAML_ONLY_CLOSEOUT_FAKE_GREEN_INCIDENT_030_LOCKED_v1.md` | `SINA_WORKER_YAML_ONLY_CLOSEOUT_FAKE_GREEN_INCIDENT_030_REPORT_LOCKED_v1.md` | **remediated** 2026-06-13 · broker-receipt gates · worker_verify_closeout_v1 |
| **031** | Worker ignored ASF no-hub stop — stale steering to hub lane | High | `SINA_WORKER_IGNORED_ASF_NO_HUB_STOP_STALE_STEERING_INCIDENT_031_LOCKED_v1.md` | `SINA_WORKER_IGNORED_ASF_NO_HUB_STOP_STALE_STEERING_INCIDENT_031_REPORT_LOCKED_v1.md` | **remediated** 2026-06-13 · `worker_asf_directive_latch_v1.py` |
| **032** | Founder museum hub erasure perception | High | `SINA_FOUNDER_MUSEUM_HUB_ERASURE_PERCEPTION_INCIDENT_032_LOCKED_v1.md` | `SINA_FOUNDER_MUSEUM_HUB_ERASURE_PERCEPTION_INCIDENT_032_REPORT_LOCKED_v1.md` | **OPEN** · museum link AR-b9955efbce |
| **033** | Brain stale + command-data SSOT + false cart PASS | Critical | `SINA_BRAIN_STALE_COMMAND_DATA_GOVERNANCE_FAILURE_INCIDENT_033_LOCKED_v1.md` | `SINA_BRAIN_STALE_COMMAND_DATA_GOVERNANCE_FAILURE_INCIDENT_033_REPORT_LOCKED_v1.md` | **canonical** |
| **034** | Prohibition instead of disk wire | High | `SINA_PROHIBITION_INSTEAD_OF_DISK_WIRE_INCIDENT_034_LOCKED_v1.md` | `SINA_PROHIBITION_INSTEAD_OF_DISK_WIRE_INCIDENT_034_REPORT_LOCKED_v1.md` | **canonical** |
| **035** | Agent pipeline / Maze speed trap | High | `SINA_AGENT_PIPELINE_MAZE_SPEED_TRAP_INCIDENT_035_LOCKED_v1.md` | `SINA_AGENT_PIPELINE_MAZE_SPEED_TRAP_INCIDENT_035_REPORT_LOCKED_v1.md` | **canonical** · speed balance shipped |
| **036** | Voyage P05 fake-green — stale hub/bowl labels | High | `SINA_VOYAGE_P05_FAKE_GREEN_STALE_LABELS_INCIDENT_036_LOCKED_v1.md` | `SINA_VOYAGE_P05_FAKE_GREEN_STALE_LABELS_INCIDENT_036_REPORT_LOCKED_v1.md` | **OPEN** · hub walk PASS · validator queued |
| **037** | Agent answered FORM 116 instead of ASF | **P0** | `docs/SOURCEA_INCIDENT_037_FORM_FOUNDER_SUPREMACY_LOCKED_v1.md` | — | **remediated** 2026-06-19 · `form-agent-submit-forbidden-v1.flag` · Hub radio UI · **NOT** INCIDENT-029 |
| **038** | Agent conflated Mac control · Worker · cloud · secondary plans | High | `SINA_AGENT_WORKER_FACTORY_PLANE_CONFLATION_INCIDENT_038_LOCKED_v1.md` | `SINA_AGENT_WORKER_FACTORY_PLANE_CONFLATION_INCIDENT_038_REPORT_LOCKED_v1.md` | **remediated v1.1** 2026-06-20 · Mac control only · secondary cloud-only · forbidden: Worker runs every plan |
| **039** | Mac founder session stuck in validators (~11 min) | **P0** | `SINA_MAC_FOUNDER_SESSION_VALIDATOR_STUCK_INCIDENT_039_LOCKED_v1.md` | `SINA_MAC_FOUNDER_SESSION_VALIDATOR_STUCK_INCIDENT_039_REPORT_LOCKED_v1.md` | **CLOSED** 2026-06-20 Batch D · conduct law in rule 034 |
| **040** | Mac Law wiring session · validator marathon ~28 min · ignored RED FLAG | **P0** | `SINA_MAC_LAW_WIRING_VALIDATOR_MARATHON_INCIDENT_040_LOCKED_v1.md` | `SINA_MAC_LAW_WIRING_VALIDATOR_MARATHON_INCIDENT_040_REPORT_LOCKED_v1.md` | **CLOSED** 2026-06-20 Batch B/C · light assess only on Mac |
| **041** | Agent held open Cursor terminal for Hub server · Batch E · ASF aborted | **P0 RED FLAG ACTIVE** | `SINA_AGENT_OPEN_TERMINAL_HUB_HOLD_INCIDENT_041_LOCKED_v1.md` | `SINA_AGENT_OPEN_TERMINAL_HUB_HOLD_INCIDENT_041_REPORT_LOCKED_v1.md` | **OPEN** 2026-06-20 · `~/.sina/incident-041-open-terminal-red-flag-v1.flag` · **never leave open terminal for Hub** · one-shot boot only |
| **042** | Cloud Forge Run batch 3 · Railway/CF chain · Dockerfile drift · agent full-pack pattern drift | **P0** | `SINA_CLOUD_FORGE_RUN_BATCH3_RAILWAY_CHAIN_INCIDENT_042_LOCKED_v1.md` | `SINA_CLOUD_FORGE_RUN_BATCH3_RAILWAY_CHAIN_INCIDENT_042_REPORT_LOCKED_v1.md` | **OPEN partial** 2026-06-23 · full_pack law locked · batch 3 armed · close at CLOUD-SEC-300 complete |
| **043** | Cloud Forge Run “100 rows per turn” · agent vocabulary split · ASF order disobedience | **P0** | `SINA_CLOUD_FORGE_RUN_HUNDRED_ROWS_VOCABULARY_INCIDENT_043_LOCKED_v1.md` | `SINA_CLOUD_FORGE_RUN_HUNDRED_ROWS_VOCABULARY_INCIDENT_043_REPORT_LOCKED_v1.md` | **OPEN** 2026-06-24 · mandatory terminology law · read before any cloud-forge-run reply |
| **047** | Forge Terminal Living Desktop E2E (template) | High | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_LIVING_DESKTOP_E2E_LOCKED_v1.md` §Incident template | — | **template** · file as `SINA_FORGE_TERMINAL_LIVING_DESKTOP_<TOPIC>_INCIDENT_NNN_LOCKED_v1.md` |
| **046** | Forge Terminal Quality Engine E2E (template) | High | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_QUALITY_ENGINE_E2E_LOCKED_v1.md` §Incident template | — | **template** · file as `SINA_FORGE_TERMINAL_QUALITY_ENGINE_<TOPIC>_INCIDENT_NNN_LOCKED_v1.md` |
| **045** | Forge Terminal desktop E2E / bundle integrity (template) | High | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_DESKTOP_E2E_LOCKED_v1.md` §Incident template | — | **template** · file as `SINA_FORGE_TERMINAL_<TOPIC>_INCIDENT_NNN_LOCKED_v1.md` |

---

## Superseded — do not cite

| Wrong id / path | Reason | Use instead |
|-----------------|--------|-------------|
| `SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_REPORT_INCIDENT_LOCKED_v1.md` | Reused **INCIDENT-010** (CIR-COSPRO) | **INCIDENT-013** |
| `SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_012_LOCKED_v1.md` | Duplicate id **012** | **INCIDENT-013** |
| Root copies of above | Same duplicate content | **INCIDENT-013** pointer |
| `SINA_S10_WRONG_BASH_CWD_INCIDENT_019_REPORT_LOCKED_v1.md` | Wrong topic + root-only body | **INCIDENT-019** + **INCIDENT-020** |
| Full incident bodies at SourceA root (018–020 session) | Skipped `brain-os/incidents/` | **INCIDENT-021** + canonical bodies |
| `RESEARCH/.../agent-auto-mono-2026-06-10-incidents-compendium-full.md` | Advise-only mirror — not SSOT | This registry + compendium LOCKED |
| `agent-governance-events.jsonl` id `INCIDENT-011-brain-column-display-drift` | Wrong id — **011** is REWRITE disk edit | **INCIDENT-014** (monitor) + **INCIDENT-015** (filing mistake) |

---

## WTM adjunct (same two-layer pattern)

| ID | LOCKED body | Root pointer |
|----|-------------|--------------|
| **002a** UI content loss | `brain-os/wtm/WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` | `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` |
| **002b** Phase naming | `brain-os/wtm/WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md` | `WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md` |

---

## Master compendium

| Doc | Role |
|-----|------|
| `brain-os/incidents/SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM_LOCKED_v1.md` | Chronology + session insights 001–010 |
| `SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM_REPORT_LOCKED_v1.md` | Root pointer |
| `brain-os/incidents/NEAR_MISS_AND_UNFILED_INCIDENTS_INDEX_LOCKED_v1.md` | Archive mirrors · audit C/S near-misses · adjunct bodies |
| `brain-os/incidents/INCIDENT_SUBJECT_INDEX_LOCKED_v1.md` | Subject + class taxonomy (001–025) |
| `brain-os/incidents/AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md` | P0/P1 conflict map (C01–C12 · S01–S10) |

---

**END REGISTRY** — agents: read this file + role slice every session.

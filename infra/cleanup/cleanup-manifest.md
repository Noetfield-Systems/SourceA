# Cleanup manifest — SourceA root sprawl

**Status:** CLEANUP_COMPLETE — Batch 6 closeout (Option A + Path 2)  
**Updated:** 2026-06-20T22:50:00Z  
**Inventory:** `infra/cleanup/inventory-root.tsv` (**2** files after batch 5f — keep-root only)  
**Machine receipt:** `data/cleanup-track-progress-v1.json`

## Patch tree — cleanup track (do not lose thread)

```
SourceA root cleanup
├── ✅ Batch 1   AGENT_* → brain-os/              (26 · 0cf364d8)
├── ✅ Batch 2   SINA_AGENT_* + incidents         (25 · 94c2dd2b)
├── ✅ Batch 3   tier-0 SSOT law at root           (25 · 0bb4a1b1 · regression)
├── ✅ Batch 3.5 pointer sync + taxonomy fold     (c688cd75)
├── ✅ Batch 3.5b archive path-string rollback      (11 · 305a666a)
├── ✅ Batch 4   SINA_COMMAND_* + incidents        (25 · executed 2026-06-20)
├── ✅ Batch 5a  SOURCEA_* → brain-os/law/          (69 · executed 2026-06-20)
├── ✅ Batch 5b  WORLD_* stubs → archive/root-stubs/  (10 · executed 2026-06-20)
├── ✅ Batch 5c  FOUNDER_* → enforcement               (7 · executed 2026-06-20)
├── ✅ Batch 5d  CURSOR_* → law + archive              (5 · executed 2026-06-20)
├── ✅ Batch 5e  SINA_* → law + incidents              (51 · executed 2026-06-20)
├── ✅ Batch 5f  OTHER → law/system/archive            (86 · executed 2026-06-20)
├── ✅ Taxonomy  Option A                         (ASF 2026-06-20)
├── ✅ Lineage   Path 2                           (ASF 2026-06-20)
├── ✅ Batch 6   archive trim duplicate root-stubs      (20 deleted · 2026-06-20)
├── ✅ Runtime trim ~/.sina inject + vector reindex     (2026-06-20)
```

**North star:** one canonical tree · agents read one path · zero drift · trim everywhere (not museum).

**Open ASF picks:** (1) taxonomy A/B · (2) lineage Path 1 vs 2 · (3) Batch 4 APPROVED · (4) operator executes batch 4

**ASF locked (2026-06-20):** Taxonomy **Option A** · Lineage **Path 2** · Batch 4 **APPROVED**

## Approval

- [x] Secret scan clear
- [x] Batch 1 executed — commit `0cf364d8`
- [x] Batch 2 executed — commit `94c2dd2b`
- [x] Batch 3 executed — commit `0bb4a1b1` (premature — regression fixed in 3.5)
- [x] **Batch 3.5 emergency** — pointer sync + taxonomy consolidation (`law/entry`, `law/enforcement`)
- [x] **Taxonomy Option A** — ASF 2026-06-20
- [x] **Lineage Path 2** — ASF 2026-06-20
- [x] **Batch 5a executed** — 2026-06-20 (69 moved · root **158** files)
- [x] **Batch 5b executed** — 2026-06-20 (10 archived · root **148** files)
- [x] Critic packet 5a: `infra/cleanup/batch-5a-diff-for-critics.md`
- [x] **Batch 4 executed** — 2026-06-20 (25 moved/archived · root **227** files)
- [x] Critic packet + pre-flight: `infra/cleanup/batch-4-diff-for-critics.md` (25/25 sources · scan clear · dupe fixed)
- [x] Taxonomy/lineage pick doc: `infra/cleanup/taxonomy-asf-pick-v1.md`
- [x] Batch 5 triage draft: `infra/cleanup/batch-5-triage-draft.md`
- [x] Machine progress receipt: `data/cleanup-track-progress-v1.json`

## Batch plan


| Batch | Theme                                        | Files   | Commit prefix                    |
| ----- | -------------------------------------------- | ------- | -------------------------------- |
| **1** | `AGENT_*` → `brain-os/`                      | 26 ✅    | `cleanup: batch-1 agent law`     |
| **2** | `SINA_AGENT_*` + leftovers + incident reports | 25 ✅   | `cleanup: batch-2 sina agent`    |
| **3** | Tier-0 ASF + SINA + SOURCEA SSOT law           | 25 ✅   | `cleanup: batch-3 portfolio law` |
| **3.5** | Emergency pointer sync + taxonomy fix        | — ✅    | `chore(cleanup): batch 3.5`      |
| **4** | `SINA_COMMAND_*` legacy hub + incident reports | 25 ✅ | `cleanup: batch-4 command incidents` |
| **5a** | `SOURCEA_*` → `brain-os/law/`                  | 69 ✅ | `cleanup: batch-5a sourcea law` |
| 5b–5f | Remainder sub-batches                        | 158     | `cleanup: batch-5b …`              |


## Batch 1 — manifest rows (review these)


| source                                                           | size | first_heading                          | proposed_dest           | batch | action  |
| ---------------------------------------------------------------- | ---- | -------------------------------------- | ----------------------- | ----- | ------- |
| `./AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md`                 | 28K  | Agent Application Use Blueprint        | `brain-os/law/`         | 1     | move    |
| `./AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md`                       | 4.0K | Sina Command as unifying hub           | `brain-os/law/`         | 1     | move    |
| `./AGENT_CONTROL_PANEL_SPEC_LOCKED_v1.md`                        | 8.0K | Agent Control Panel spec               | `brain-os/law/`         | 1     | move    |
| `./AGENT_COUNCIL_ROOM_LOCKED_v1.md`                              | 8.0K | Agent Council Room                     | `brain-os/law/`         | 1     | move    |
| `./AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md`         | 12K  | Agent Decision Stack & Smart Judgment  | `brain-os/law/`         | 1     | move    |
| `./AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md`                      | 4.0K | Agent disk live wire first             | `brain-os/law/enforcement/` | 1     | move    |
| `./AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md`            | 16K  | Agent ecosystem sprint                 | `brain-os/law/`         | 1     | move    |
| `./AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md`              | 8.0K | Agent ecosystem unification policy     | `brain-os/law/`         | 1     | move    |
| `./AGENT_ESSAY_DISCOURSE_LOCKED_v1.md`                           | 4.0K | Agent essay discourse                  | `brain-os/law/`         | 1     | move    |
| `./AGENT_EXECUTOR_DAILY_DUTY_CARD_LOCKED_v1.md`                  | 8.0K | Agent executor daily duty card         | `brain-os/law/enforcement/` | 1     | move    |
| `./AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md`                | 4.0K | Agent → founder bash communication     | `brain-os/law/enforcement/` | 1     | move    |
| `./AGENT_GOVERNANCE_INDEX_LOCKED_v1.md`                          | 8.0K | Agent governance index                 | `brain-os/law/`         | 1     | move    |
| `./AGENT_INCIDENTS_REGISTRY_REPORT_LOCKED_v1.md`                 | 4.0K | Agent incidents registry report        | `brain-os/incidents/`   | 1     | move    |
| `./AGENT_DIAG_CLIPBOARD_PAIRING_HIJACK_2026-05-27_LOCKED.md`     | 4.0K | Clipboard hijack diag                  | `brain-os/incidents/`   | 1     | move    |
| `./AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md`                 | 4.0K | Agent memory mirror enforcement        | `brain-os/law/enforcement/` | 1     | move    |
| `./AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md`                    | 4.0K | MergePack is NOT an agent              | `brain-os/law/`         | 1     | move    |
| `./AGENT_MIND_SHARE_LOCKED_v1.md`                                | 4.0K | Agent Mind Share                       | `brain-os/law/`         | 1     | move    |
| `./AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md`                      | 4.0K | No Hub Rebuild Stuck Loop              | `brain-os/law/enforcement/` | 1     | move    |
| `./AGENT_OPERATING_ROLES_LOCKED_v1.md`                           | 4.0K | Agent operating roles                  | `brain-os/law/`         | 1     | move    |
| `./AGENT_SCOREBOARD_LOCKED_v1.md`                                | 4.0K | Agent session scoreboard               | `brain-os/law/`         | 1     | move    |
| `./AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md`              | 8.0K | Agent Skills & Research Pipeline       | `brain-os/law/`         | 1     | move    |
| `./AGENT_TERMINAL_CLOSEOUT_LOCKED_v1.md`                         | 4.0K | Agent terminal closeout                | `brain-os/law/enforcement/` | 1     | move    |
| `./AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md` | 12K  | Orientation · Hospital · Maze          | `brain-os/law/`         | 1     | move    |
| `./AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md`              | 4.0K | Workspace vault middle layer           | `brain-os/law/`         | 1     | move    |
| `./AGENT_RULES_IN_CHARGE_LOCKED_v1.md`                           | 4.0K | MOVED — canonical SSOT (root stub)     | `archive/root-stubs/`   | 1     | archive |
| `./AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md`                      | 4.0K | SAVE · WORK · EDIT ALLOWED (root stub) | `archive/root-stubs/`   | 1     | archive |


### Batch 1 — deferred to batch 2 (not in this commit)


| source                                        | note                                                                  |
| --------------------------------------------- | --------------------------------------------------------------------- |
| `./AGENT_DESK_START_HERE.md`                  | → `brain-os/law/entry/` (entry gate doc)                                  |
| `./AGENT_RULE_CONFLICT_*`                     | → `brain-os/incidents/` (may dupe files already there — verify first) |
| `./AGENT_SELF_AUDIT_ASF_REPORT_2026-06-04.md` | → `docs/archive/` (dated report, not law)                             |


## Batch 2 — manifest rows (review these)

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|
| `./AGENT_DESK_START_HERE.md` | 4.0K | ASF Agent Desk — start here | `brain-os/law/entry/` | 2 | move |
| `./AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md` | 4.0K | root pointer (canonical in incidents) | `archive/root-stubs/` | 2 | archive |
| `./AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_REPORT_LOCKED_v1.md` | 4.0K | rule conflict audit pointer | `brain-os/incidents/` | 2 | move |
| `./AGENT_SELF_AUDIT_ASF_REPORT_2026-06-04.md` | 8.0K | dated ASF presentation report | `docs/archive/` | 2 | move |
| `./SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md` | 4.0K | Agent Conflict Room | `brain-os/law/` | 2 | move |
| `./SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md` | 4.0K | root pointer (canonical in incidents) | `archive/root-stubs/` | 2 | archive |
| `./SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md` | 4.0K | Private agent workspaces | `brain-os/law/` | 2 | move |
| `./SINA_AGENT_LOOP_ORDER_v1.md` | 4.0K | Sina Agent Loop — 10 rounds | `brain-os/law/` | 2 | move |
| `./SINA_AGENT_LOOP_10_PREP_v1.md` | 4.0K | Agent loop 10-round prep | `brain-os/law/enforcement/` | 2 | move |
| `./SOURCEA_AGENTIC_ENFORCEMENT_STACK_LOCKED_v2.md` | 8.0K | Agentic enforcement stack | `brain-os/law/` | 2 | move |
| `./SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md` | 8.0K | Agentic layer stack | `brain-os/law/` | 2 | move |
| `./CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md` | 4.0K | root pointer (canonical in incidents) | `archive/root-stubs/` | 2 | archive |
| `./CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | Cursor agent context memory incident | `brain-os/incidents/` | 2 | move |
| `./SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md` | 4.0K | root pointer (canonical in incidents) | `archive/root-stubs/` | 2 | archive |
| `./SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | Brain/worker lane cross incident | `brain-os/incidents/` | 2 | move |
| `./SINA_AGENT_FOUNDER_BASH_COMMUNICATION_INCIDENT_019_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-019 pointer | `brain-os/incidents/` | 2 | move |
| `./SINA_AGENT_HUB_NAME_FRAGMENTATION_ADVISOR_TRACK_INCIDENT_025_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-025 pointer | `brain-os/incidents/` | 2 | move |
| `./SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-015 pointer | `brain-os/incidents/` | 2 | move |
| `./SINA_AGENT_INCIDENT_WRONG_FOLDER_FILING_INCIDENT_021_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-021 pointer | `brain-os/incidents/` | 2 | move |
| `./SINA_AGENT_PIPELINE_MAZE_SPEED_TRAP_INCIDENT_035_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-035 report | `brain-os/incidents/` | 2 | move |
| `./SINA_AGENT_PLAN_TODO_GHOST_REACTIVATION_INCIDENT_016_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-016 pointer | `brain-os/incidents/` | 2 | move |
| `./SINA_AGENT_REWRITE_UNAUTHORIZED_DISK_EDIT_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-011 report | `brain-os/incidents/` | 2 | move |
| `./SINA_AGENT_TOPIC_CONFLATION_INCIDENT_020_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-020 pointer | `brain-os/incidents/` | 2 | move |
| `./SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-026 report | `brain-os/incidents/` | 2 | move |
| `./SINA_BRAIN_STALE_COMMAND_DATA_GOVERNANCE_FAILURE_INCIDENT_033_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-033 report | `brain-os/incidents/` | 2 | move |


## Batch 3 — manifest rows (tier-0 portfolio & governance SSOT)

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|
| `./SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` | 52K | Sina Authority Index Map | `brain-os/system/` | 3 | move |
| `./SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | 16K | Sina Governance Entry | `brain-os/law/entry/` | 3 | move |
| `./SINA_OS_SSOT_LOCKED.md` | 4.0K | Sina OS Master SSOT | `brain-os/law/` | 3 | move |
| `./SINA_OS_SSOT_READ_ORDER_ADDENDUM_v1.md` | 4.0K | SSOT read order addendum | `brain-os/law/` | 3 | move |
| `./SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` | 8.0K | SourceA unified portfolio SSOT | `brain-os/law/` | 3 | move |
| `./SOURCEA_REPO_SSOT_LOCKED.md` | 4.0K | SourceA repo SSOT | `brain-os/law/` | 3 | move |
| `./SOURCEA_EXECUTION_LAW_LOCKED_v1.md` | 4.0K | SourceA execution law | `brain-os/law/` | 3 | move |
| `./SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md` | 4.0K | No fake progress law | `brain-os/law/` | 3 | move |
| `./SINA_ENFORCEMENT_PORTFOLIO_DECISION_FORM_LOCKED_v1.md` | 8.0K | Portfolio decision form | `brain-os/law/` | 3 | move |
| `./SINA_ENFORCEMENT_6MO_LAW_SUPERSESSION_LOCKED_v1.md` | 8.0K | ENFORCEMENT-6MO supersession | `brain-os/law/` | 3 | move |
| `./SINA_ENFORCEMENT_6MO_PRESERVED_SPIRIT_AND_LINEAGE_LOCKED_v1.md` | 12K | Preserved spirit & lineage | `brain-os/law/` | 3 | move |
| `./SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` | 4.0K | Source alignment law | `brain-os/law/` | 3 | move |
| `./SINA_UNIFIED_ENGINE_STORY_LOCKED_v1.md` | 4.0K | Unified engine story | `brain-os/law/` | 3 | move |
| `./SOURCEA_SSOT_FOUNDATION_WRITING_GUIDE_LOCKED_v1.md` | 4.0K | SSOT writing guide | `brain-os/law/` | 3 | move |
| `./SOURCEA_FLEET_HEADLINE_READ_ORDER_LOCKED_v1.md` | 4.0K | Fleet headline read order | `brain-os/law/` | 3 | move |
| `./SOURCEA_VALID_YES_PROGRESS_VERDICT_LOCKED_v1.md` | 4.0K | Valid YES progress verdict | `brain-os/law/` | 3 | move |
| `./SOURCEA_GOLDEN_INSIGHT_AND_SAFETY_LOCKED_v1.md` | 4.0K | Golden insight & safety | `brain-os/law/` | 3 | move |
| `./ASF_MILESTONE_GLOSSARY_LOCKED_v1.md` | 4.0K | ASF milestone glossary | `brain-os/law/` | 3 | move |
| `./ASF_MASTER_ORDERS_ORGANIZED_LOCKED_v1.md` | 12K | ASF master orders | `brain-os/law/` | 3 | move |
| `./ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md` | 20K | ASF program threads registry | `brain-os/system/` | 3 | move |
| `./ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md` | 12K | Program progress command center | `brain-os/system/` | 3 | move |
| `./ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md` | 8.0K | ASF full day playbook | `brain-os/law/enforcement/` | 3 | move |
| `./ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md` | 4.0K | Retire Sina Command forever | `brain-os/law/` | 3 | move |
| `./SINA_BIG_PICTURE_ROADMAP_LOCKED_v2.md` | 4.0K | Big picture roadmap | `brain-os/law/` | 3 | move |
| `./SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md` | 4.0K | MOVED — canonical SSOT (stub) | `archive/root-stubs/` | 3 | archive |


## Batch 4 — manifest rows (`SINA_COMMAND_*` legacy hub + incident reports)

**Theme:** Retired Sina Command hub docs → `archive/legacy/sina-command/`; root incident pointers/reports → `brain-os/incidents/` (stubs → `archive/root-stubs/`).

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|
| `./SINA_COMMAND_CENTER_VISION_LOCKED_v1.md` | 12K | Sina Command Center vision | `archive/legacy/sina-command/` | 4 | move |
| `./SINA_COMMAND_DEACTIVATED_INCIDENT_READ_POLICY_LOCKED_v1.md` | 4.0K | Deactivated + incident read policy | `archive/legacy/sina-command/` | 4 | move |
| `./SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` | 4.0K | Sina Command edit lock | `archive/legacy/sina-command/` | 4 | move |
| `./SINA_COMMAND_GUIDE_LOCKED_v1.md` | 4.0K | Sina Command guide | `archive/legacy/sina-command/` | 4 | move |
| `./SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md` | 4.0K | INCIDENT-005b root pointer | `archive/root-stubs/` | 4 | archive |
| `./SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` | 4.0K | Founder no Terminal law | `archive/legacy/sina-command/` | 4 | move |
| `./SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md` | 8.0K | System update notice | `archive/legacy/sina-command/` | 4 | move |
| `./SINA_COMMAND_UI_PLAYFUL_LOCKED_v1.md` | 4.0K | Playful Path UI design | `archive/legacy/sina-command/` | 4 | move |
| `./ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` | 4.0K | Ecosystem incidents index | `brain-os/incidents/` | 4 | move |
| `./INCIDENT_SUBJECT_INDEX_REPORT_LOCKED_v1.md` | 4.0K | Incident subject index pointer | `brain-os/incidents/` | 4 | move |
| `./SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md` | 4.0K | root stub | `archive/root-stubs/` | 4 | archive |
| `./SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-010 report | `brain-os/incidents/` | 4 | move |
| `./SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM_REPORT_LOCKED_v1.md` | 4.0K | compendium pointer | `brain-os/incidents/` | 4 | move |
| `./SINA_EXECUTOR_IGNORED_M1_INTEGRITY_FORM_CANVAS_INCIDENT_029_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-029 report | `brain-os/incidents/` | 4 | move |
| `./SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-023 root pointer (canonical in incidents/) | `archive/root-stubs/` | 4 | archive |
| `./SINA_FOUNDER_MUSEUM_HUB_ERASURE_PERCEPTION_INCIDENT_032_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-032 pointer | `brain-os/incidents/` | 4 | move |
| `./SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | goal hierarchy incident | `brain-os/incidents/` | 4 | move |
| `./SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | Goal 1 broker stale | `brain-os/incidents/` | 4 | move |
| `./SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md` | 4.0K | root pointer | `archive/root-stubs/` | 4 | archive |
| `./SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | Goal 1 unvalidated proof | `brain-os/incidents/` | 4 | move |
| `./SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | MOVED pointer stub | `archive/root-stubs/` | 4 | archive |
| `./SINA_HEALTHY_QUEUE_PHASE_ORDER_DRIFT_INCIDENT_017_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-017 pointer | `brain-os/incidents/` | 4 | move |
| `./SINA_MAINTAINER_2_DRAIN_PROJECTION_STALENESS_INCIDENT_027_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-027 report | `brain-os/incidents/` | 4 | move |
| `./SINA_MAINTAINER_2_STALE_AUTORUN_ADVICE_INCIDENT_022_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-022 pointer | `brain-os/incidents/` | 4 | move |
| `./SINA_MAINTAINER_EXTERNAL_CRITIC_PROCEDURE_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | external critic procedure | `brain-os/incidents/` | 4 | move |

**Post-batch 4 pointer follow-up:** update `scripts/hub_essentials_index.py` READ_CHAIN rows for `SINA_COMMAND_*` → `archive/legacy/sina-command/…` (7 paths).


## Batch 5a — manifest rows (`SOURCEA_*` → `brain-os/law/`)

**Theme:** Product/commercial/governance SOURCEA law · Option A + Path 2

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|
| `./SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md` | 4.0K | # SourceA 1000-Pack Audit Judge (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_1000_LOCKED_PROMPT_LIBRARY_NO_ASF_v1.md` | 4.0K | # SOURCEA 1000 LOCKED prompt library — PLAN WITH N | `brain-os/law/` | 5a | move |
| `./SOURCEA_ADVERSARIAL_PROBE_PACK_LOCKED_v1.md` | 8.0K | # SourceA — Adversarial Probe Pack (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md` | 8.0K | # SourceA Agency Product Demo Script — LOCKED v1 | `brain-os/law/` | 5a | move |
| `./SOURCEA_ANTI_STALENESS_AUTO_WIRE_LAYER_SYNC_LOCKED_v1.md` | 4.0K | # Anti-staleness auto wire — layer sync law (LOCKE | `brain-os/law/` | 5a | move |
| `./SOURCEA_ANTI_STALENESS_MACHINE_ENFORCEMENT_PLAN_LOCKED_v1.md` |  12K | # SourceA — Anti-staleness machine enforcement pla | `brain-os/law/` | 5a | move |
| `./SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md` | 8.0K | # Asset B — Governed Agentic Automation (DFY) — LO | `brain-os/law/` | 5a | move |
| `./SOURCEA_AUTHORITY_COVERAGE_AUDIT_2026-06-11_v1.md` |  12K | # SourceA Authority Coverage Audit — 2026-06-11 | `brain-os/law/` | 5a | move |
| `./SOURCEA_AUTHORITY_REGISTRY_GOV_UNIFY_BATCH_2026-06-11_LOCKED_v1.md` |  12K | # Authority Registry — GOV_UNIFY Batch 2026-06-11  | `brain-os/law/` | 5a | move |
| `./SOURCEA_BLUEPRINT_COMPARISON_POSTMORTEM_v1.md` |  40K | # SOURCEA BLUEPRINT COMPARISON — POST-MORTEM + PRE | `brain-os/law/` | 5a | move |
| `./SOURCEA_BRAIN_MONITOR_FIX_REPORT_LOCKED_v1.md` | 8.0K | # Brain Monitor Fix — Full Honest Report (LOCKED v | `brain-os/law/` | 5a | move |
| `./SOURCEA_CHAIN_TOOLS_PUBLISH_LOCKED_v1.md` | 4.0K | # SourceA Chain Tools — Publish Pattern (Graphify  | `brain-os/law/` | 5a | move |
| `./SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md` | 4.0K | # SourceA Commercial Sender — LOCKED v1.1 | `brain-os/law/` | 5a | move |
| `./SOURCEA_COMMERCIAL_VIDEO_HERO_PIPELINE_LOCKED_v1.md` | 8.0K | # SourceA Commercial Video — Hero Pipeline (LOCKED | `brain-os/law/` | 5a | move |
| `./SOURCEA_COMMERCIAL_WORKER_LOOP_LOCKED_v1.md` | 4.0K | # SourceA — Commercial Worker Loop (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_COMPANY_INFRA_BUYER_AND_POSITION_SSOT_LOCKED_v1.md` |  16K | # SourceA — Company, Infra, Buyer & Position SSOT  | `brain-os/law/` | 5a | move |
| `./SOURCEA_COMPLEX_SITUATION_FORK_MACHINE_LOCKED_v1.md` | 8.0K | # SourceA Complex Situation Fork Machine (LOCKED v | `brain-os/law/` | 5a | move |
| `./SOURCEA_CONTROL_PLANE_200_PLAN_BRANCH_INDEX_LOCKED_v1.md` | 8.0K | # SourceA Control Plane — 200 Plan Branch Index LO | `brain-os/law/` | 5a | move |
| `./SOURCEA_CONTROL_PLANE_200_PLAN_LOCKED_v1.md` |  24K | # SourceA Control Plane — 200 Plan LOCKED v1 | `brain-os/law/` | 5a | move |
| `./SOURCEA_CROSS_DOC_LINKAGE_AND_AUDIT_LOCKED_v1.md` |  28K | # SourceA Cross-Doc Linkage & Governance Audit (LO | `brain-os/law/` | 5a | move |
| `./SOURCEA_CURSOR_RULES_AND_SKILLS_MAP_LOCKED_v2.md` | 4.0K | # SourceA — Cursor rules & skills map (LOCKED v2) | `brain-os/law/` | 5a | move |
| `./SOURCEA_DISK_TRUTH_E2E_MATRIX_LOCKED_v1.md` | 8.0K | # SourceA — Disk truth E2E matrix (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md` |  12K | # SourceA E2E Debugger Playbook (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_ECOSYSTEM_MASTER_CATALOG_LOCKED_v1.md` |  12K | # SourceA Ecosystem Master Catalog — Everything on | `brain-os/law/` | 5a | move |
| `./SOURCEA_EXECUTOR_IN_CHARGE_NO_HANDOFF_LOCKED_v1.md` | 4.0K | # Executor in charge — no handoff (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_FAST_SYSTEM_LOAD_BUDGET_LOCKED_v1.md` | 4.0K | # SourceA — Fast System Load Budget (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_FINAL_RESOLUTION_GAP_ANALYSIS_v1.md` | 4.0K | # Final Resolution — Gap Analysis (working v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md` |  12K | # SourceA Five-Step Autonomous Progress Blueprint  | `brain-os/law/` | 5a | move |
| `./SOURCEA_FOUNDER_DIRECTION_TERMINOLOGY_LOCKED_v1.md` | 4.0K | # SourceA Founder Direction + Terminology (LOCKED  | `brain-os/law/` | 5a | move |
| `./SOURCEA_FOUNDER_MACHINE_TERMINOLOGY_DICTIONARY_LOCKED_v1.md` |  20K | # SourceA Founder ↔ Machine Terminology Dictionary | `brain-os/law/` | 5a | move |
| `./SOURCEA_FOUNDER_MESSAGE_NORMALIZATION_LOCKED_v1.md` | 4.0K | # SourceA Founder Message Normalization (LOCKED v1 | `brain-os/law/` | 5a | move |
| `./SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md` | 8.0K | # SourceA Founder Pinned Actions (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_FROZEN_ARCHIVE_REVIVAL_AUDIT_LOCKED_v1.md` | 8.0K | # Frozen & Archive Corpus — Revival Audit (LOCKED  | `brain-os/law/` | 5a | move |
| `./SOURCEA_GOVERNANCE_CENTER_SELF_GOVERN_LOCKED_v1.md` | 8.0K | # SourceA — Governance Center & Self-Govern (LOCKE | `brain-os/law/` | 5a | move |
| `./SOURCEA_GOVERNANCE_EVENT_SPINE_SCHEMA_LOCKED_v1.md` | 8.0K | # Governance Event Spine — schema & reference grap | `brain-os/law/` | 5a | move |
| `./SOURCEA_GOV_META_AUDIT_LOCKED_v1.md` | 4.0K | # Governance Meta-Audit — LOCKED v1 | `brain-os/law/` | 5a | move |
| `./SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md` |  12K | # SourceA — H2 Machine Hub Plan (LOCKED v1.1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_ICP_MARKET_IDENTITY_LOCKED_v1.md` |  24K | # SOURCEA_ICP_MARKET_IDENTITY_LOCKED_v1.md | `brain-os/law/` | 5a | move |
| `./SOURCEA_INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING_LOCKED_v1.md` |  12K | # SourceA — Incident Fix Ownership & Governance Ha | `brain-os/law/` | 5a | move |
| `./SOURCEA_INCIDENT_FIX_OWNERSHIP_REPORT_LOCKED_v1.md` | 4.0K | # INCIDENT fix ownership — report pointer | `brain-os/law/` | 5a | move |
| `./SOURCEA_INTEGRATION_LEVERAGE_STRATEGY_LOCKED_v1.md` |  12K | # SourceA Integration & Partnership Leverage Strat | `brain-os/law/` | 5a | move |
| `./SOURCEA_INTEGRITY_STACK_UNIFIED_BLUEPRINT_BATCH_2_LOCKED_v1.md` |  32K | # SourceA Integrity Stack — Unified Blueprint Batc | `brain-os/law/` | 5a | move |
| `./SOURCEA_INVARIANT_GATEKEEPER_REPORT_LOCKED_v1.md` | 4.0K | # Invariant Gatekeeper — root pointer (LOCKED) | `brain-os/law/` | 5a | move |
| `./SOURCEA_LAYERED_ADVISORY_DISK_DELTA_2026-06-12_v1.md` | 8.0K | # Layered Advisory — Disk Delta (2026-06-12) | `brain-os/law/` | 5a | move |
| `./SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md` |  12K | # SourceA Layered Advisory — Draft v1 (LOCKED) | `brain-os/law/` | 5a | move |
| `./SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` |  24K | # SourceA Live Founder Decision Form (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md` |  12K | # SourceA Live Governance — Big Picture (LOCKED v1 | `brain-os/law/` | 5a | move |
| `./SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md` | 4.0K | # Live ongoing prompts — machine order + Next step | `brain-os/law/` | 5a | move |
| `./SOURCEA_LOST_LINK_RECOVERY_ETHICS_LOCKED_v1.md` | 8.0K | # Lost Link Recovery Ethics — Practical + Philosop | `brain-os/law/` | 5a | move |
| `./SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md` |  16K | # SourceA — Machine test & upgrade ladder (LOCKED  | `brain-os/law/` | 5a | move |
| `./SOURCEA_MARKET_RECEIPT_ARCHITECTURE_LOCKED_v1.md` | 8.0K | # Architecture the Market Pays For — Receipt-Nativ | `brain-os/law/` | 5a | move |
| `./SOURCEA_MASTER_SESSION_MANIFEST_LOCKED_v1.md` |  12K | # Master Session Manifest — Full Thread & Subject  | `brain-os/law/` | 5a | move |
| `./SOURCEA_MONITOR_DISK_LIVE_WIRE_LOCKED_v1.md` | 4.0K | # Monitor disk live wire (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_OPENROUTER_ACTIVATION_QUEUE_LOCKED_v1.md` | 4.0K | # SourceA — OpenRouter Activation Queue (LOCKED v1 | `brain-os/law/` | 5a | move |
| `./SOURCEA_ORCHESTRATOR_PARTNER_INTEGRATION_LOCKED_v1.md` |  12K | # SourceA Orchestrator Partner Integration — LOCKE | `brain-os/law/` | 5a | move |
| `./SOURCEA_PHASE2_INTEGRITY_PICK_RECEIPT_2026-06-11_LOCKED_v1.md` | 4.0K | # Phase 2 Integrity Pick Receipt — 2026-06-11 (LOC | `brain-os/law/` | 5a | move |
| `./SOURCEA_PHASE_PACK_PINNED_SUMMARY_LOCKED_v1.md` | 4.0K | # Phase pack reorg — pinned very short summary (LO | `brain-os/law/` | 5a | move |
| `./SOURCEA_PHASE_STRICT_RUN_INBOX_LOCKED_v1.md` | 4.0K | # Phase-strict run inbox routing (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md` |  24K | # SourceA Reference Architecture Constellation (LO | `brain-os/law/` | 5a | move |
| `./SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md` |  12K | # SourceA Result-Driven Discussion Policy (LOCKED  | `brain-os/law/` | 5a | move |
| `./SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md` | 8.0K | # S10 — Eternal self-heal · disk-truth audit · 100 | `brain-os/law/` | 5a | move |
| `./SOURCEA_SESSION_20260609_COMPLETE_INDEX_LOCKED_v1.md` | 8.0K | # SourceA Session 2026-06-09 — Complete Index (LOC | `brain-os/law/` | 5a | move |
| `./SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` | 8.0K | # SourceA — Two-Hub Model + Super Fast Hub (LOCKED | `brain-os/law/` | 5a | move |
| `./SOURCEA_SYSTEM_INTEGRITY_100_STEP_PLAYBOOK_LOCKED_v1.md` |  16K | # SourceA System Integrity — 100-Step Playbook (LO | `brain-os/law/` | 5a | move |
| `./SOURCEA_SYSTEM_INTEGRITY_SESSION_LOG_v1.md` |  12K | # System Integrity Session Log — 2026-06-11 | `brain-os/law/` | 5a | move |
| `./SOURCEA_SYSTEM_MAP_TREE_LOCKED_v1.md` |  16K | # SourceA — System Map Tree (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md` | 4.0K | # SourceA — Three-Zone Hub Spine (LOCKED v1) | `brain-os/law/` | 5a | move |
| `./SOURCEA_TODAY_SESSION_UNIFIED_CLOSEOUT_RECEIPT_2026-06-11_LOCKED_v1.md` |  12K | # Today Session — Unified Closeout Receipt (LOCKED | `brain-os/law/` | 5a | move |
| `./SOURCEA_WORKER_E2E_POSTMORTEM_LOCKED_v1.md` |  12K | # Worker E2E Post-Mortem — Verdict, Permanent Fix, | `brain-os/law/` | 5a | move |

**Post-batch 5a pointer follow-up:** `governance_paths_v1.py` extended · ~20 scripts patched · `hub_essentials_index.py` READ_CHAIN SOURCEA paths → `brain-os/law/`.

## Batch 5b — manifest rows (`WORLD_*` root stubs → `archive/root-stubs/`)

**Theme:** Canonical SSOT already at `brain-os/wtm/` — retire root MOVED stubs only (action **archive**, not move).

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|
| `./WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5b | archive |
| `./WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5b | archive |
| `./WORLD_TARGET_MODEL_FULL_BLUEPRINT_FOR_REVIEW_v1.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5b | archive |
| `./WORLD_TARGET_MODEL_FULL_BLUEPRINT_FOR_REVIEW_v2.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5b | archive |
| `./WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5b | archive |
| `./WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5b | archive |
| `./WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5b | archive |
| `./WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5b | archive |
| `./WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5b | archive |
| `./WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5b | archive |

**Post-batch 5b pointer follow-up:** `governance_paths_v1.py` `wtm_doc()` + REL_WTM_* · `important_docs_index.py` · `agent_system_unified.py` · `ecosystem_incidents_index.py` · `agent_rules_in_charge.py` · `roadmaps_goals.py`.

## Batch 5c — manifest rows (`FOUNDER_*` → `brain-os/law/enforcement/` + pointer archive)

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|
| `./FOUNDER_AGENT_USE_GUIDE_LOCKED_v1.md` | 8.0K | # Founder — Agents Window use guide | `brain-os/law/enforcement/` | 5c | move |
| `./FOUNDER_BRAIN_MAINTAINER_STRATEGIC_EXTRACTION_100M_v2.md` | 24K | # Founder × Brain × Maintainer | `brain-os/law/enforcement/` | 5c | move |
| `./FOUNDER_BUSY_OPERATING_MODEL_REPORT_LOCKED_v1.md` | 4.0K | # Operating Model SSOT — root pointer | `archive/root-stubs/` | 5c | archive |
| `./FOUNDER_DAILY_PROMPT_PACK_LOCKED_v1.md` | 4.0K | # Founder daily prompt pack | `brain-os/law/enforcement/` | 5c | move |
| `./FOUNDER_FIRST_ASSISTANT_TRACKING_LAW_LOCKED_v1.md` | 4.0K | # Founder First Assistant — Tracking Law | `brain-os/law/enforcement/` | 5c | move |
| `./FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` | 4.0K | # Founder rule — NO credit card | `brain-os/law/enforcement/` | 5c | move |
| `./FOUNDER_SAVE_AND_LOCK_IMMEDIATE_APP_LAW_LOCKED_v1.md` | 4.0K | # Founder save & lock | `brain-os/law/enforcement/` | 5c | move |

**Post-batch 5c pointer follow-up:** `governance_paths_v1.py` `enforcement_doc()` · `founder_agent_use_guide.py` · `founder_request_tracker.py` · `founder_prompt_pack_build_v1.py` · hub/important docs indexes.

## Batch 5d — manifest rows (`CURSOR_*` → law + archive)

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|
| `./CURSOR_FIND_BUGS_AUTOMATION_LOCKED_v1.md` | 4.0K | # Cursor Find Bugs automation | `brain-os/law/` | 5d | move |
| `./CURSOR_FIX_OVERNIGHT.md` | 4.0K | # CURSOR FIX — Overnight Loop Reset | `docs/archive/cursor-tooling/` | 5d | move |
| `./CURSOR_REPO_AGENT_NOTICE_PROMPTS_v1.md` | 16K | # Cursor Repo Agent — Notice Prompts | `docs/archive/cursor-tooling/` | 5d | move |
| `./CURSOR_REPO_SPECIALIZED_NOTICES_v2.md` | 4.0K | # Five Specialized Repo Notice Prompts | `docs/archive/cursor-tooling/` | 5d | move |
| `./CURSOR_SYSTEM_EXECUTION_MODE_START_v1.md` | 8.0K | # START SYSTEM EXECUTION MODE | `docs/archive/cursor-tooling/` | 5d | move |

## Batch 5e — manifest rows (`SINA_*` → `brain-os/law/` + incidents + stub archive)

**Files:** 51 (33 law · 17 incidents · 1 stub archive)

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|
| `./SINA_ADVISOR_CURSOR_CONNECT_v1.md` | 1.0K | # Connect Cursor as Advisor in Sina Command | `brain-os/law/` | 5e | move |
| `./SINA_ADVISOR_TRACK_OPERATIONAL_POINTER_LOCKED_v1.md` | 1.0K | # Advisor track — operational pointer (LOCKED v1) | `brain-os/law/` | 5e | move |
| `./SINA_AGENT_WORKER_FACTORY_PLANE_CONFLATION_INCIDENT_038_REPORT_LOCKED_v1.md` | 1.0K | # INCIDENT-038 — Mac control vs cloud factory | `brain-os/incidents/` | 5e | move |
| `./SINA_APPS_GUIDE_FOR_SINA_v1.md` | 2.0K | # Sina apps — teacher guide (for Sina) | `brain-os/law/` | 5e | move |
| `./SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md` | 2.0K | # Automation spine + n8n (LOCKED) | `brain-os/law/` | 5e | move |
| `./SINA_BRAIN_JOB_TITLES_COMPREHENSIVE_LOCKED_v1.md` | 27.0K | # Sina Brain — Job Titles Comprehensive Manual | `brain-os/law/` | 5e | move |
| `./SINA_BRAIN_JOB_TITLES_DAILY_ONE_PAGE_LOCKED_v1.md` | 3.0K | # Brain Daily Card — One Page (LOCKED v1) | `brain-os/law/` | 5e | move |
| `./SINA_BRAIN_JOB_TITLES_LOCKED_v1.md` | 7.0K | # Sina Brain — Job Titles Catalog (LOCKED v1) | `brain-os/law/` | 5e | move |
| `./SINA_BRAIN_PLATFORM_UNIFICATION_LOCKED_v1.md` | 11.0K | # Sina Brain — Platform Unification (LOCKED v1) | `brain-os/law/` | 5e | move |
| `./SINA_CURSOR_PROMPT_QUEUE_ORDER_v1.md` | 4.0K | # Order for Cursor agents — Prompt queue (LOCKED) | `brain-os/law/` | 5e | move |
| `./SINA_DAILY_BOWL_LOCKED_v1.md` | 1.0K | # Sina Daily Bowl — unified morning read (LOCKED) | `brain-os/law/` | 5e | move |
| `./SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md` | 7.0K | # Execution Intelligence Stack | `brain-os/law/` | 5e | move |
| `./SINA_HUB_E2E_CANCELLED_LOCKED_v1.md` | 1.0K | # SINA Hub E2E — CANCELLED | `brain-os/law/` | 5e | move |
| `./SINA_HUB_ESSENTIALS_LOCKED_v1.md` | 1.0K | # Hub Essentials — locked unified map law | `brain-os/law/` | 5e | move |
| `./SINA_JUDGE_STACK_LOCKED_v1.md` | 2.0K | # Sina Judge Stack — LOCKED v1 | `brain-os/law/` | 5e | move |
| `./SINA_LOOP_PORTFOLIO_PACKS_v1.md` | 1.0K | # Sina Command — private agent loop packs | `brain-os/law/` | 5e | move |
| `./SINA_MAC_FOUNDER_SESSION_VALIDATOR_STUCK_INCIDENT_039_REPORT_LOCKED_v1.md` | 4.0K | # INCIDENT-039 — Mac stuck in validators | `brain-os/incidents/` | 5e | move |
| `./SINA_MAC_HEALTH_GUARD_LOCKED_v1.md` | 4.0K | # Mac Health Guard — locked mini app law | `brain-os/law/` | 5e | move |
| `./SINA_MAC_LAW_WIRING_VALIDATOR_MARATHON_INCIDENT_040_REPORT_LOCKED_v1.md` | 1.0K | # INCIDENT-040 — Mac Law wiring validator marathon | `brain-os/incidents/` | 5e | move |
| `./SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_REPORT_LOCKED_v1.md` | 1.0K | # INCIDENT-014 — Monitor Brain column PEND | `brain-os/incidents/` | 5e | move |
| `./SINA_MONITOR_FOUNDER_SCROLL_RESPECT_INCIDENT_018_REPORT_LOCKED_v1.md` | 1.0K | # INCIDENT-018 pointer — Monitor auto-scroll | `brain-os/incidents/` | 5e | move |
| `./SINA_MULTIDIMENSIONAL_ENGINE_MAP_LOCKED_v1.md` | 10.0K | # Sina Multidimensional Parallel Engine | `brain-os/law/` | 5e | move |
| `./SINA_P0_PORTFOLIO_AUTOMATION_AND_EVIDENCE_LAW_DRAFT_v1.md` | 15.0K | # Sina P0 Portfolio — Automation (DRAFT) | `brain-os/law/` | 5e | move |
| `./SINA_P0_PORTFOLIO_AUTOMATION_AND_EVIDENCE_LAW_LOCKED_v1.md` | 14.0K | # Sina P0 Portfolio — Automation (LOCKED) | `brain-os/law/` | 5e | move |
| `./SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md` | 2.0K | # Personal Database (Layer A) — locked law | `brain-os/law/` | 5e | move |
| `./SINA_POISON_TRACKING_METHOD_LOCKED_v1.md` | 12.0K | # Sina poison tracking method — PT-METHOD | `brain-os/law/` | 5e | move |
| `./SINA_POST_CLAUDE_ANALYSIS_SHIP_READY_COMPANION_v1.md` | 8.0K | # Post–Claude Analysis · Ship-Ready Companion | `brain-os/law/` | 5e | move |
| `./SINA_POST_CLOUD_ANALYSIS_SHIP_READY_COMPANION_v1.md` | 1.0K | # RENAMED — was mislabeled cloud | `brain-os/law/` | 5e | move |
| `./SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md` | 1.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5e | archive |
| `./SINA_PROHIBITION_INSTEAD_OF_DISK_WIRE_INCIDENT_034_REPORT_LOCKED_v1.md` | 1.0K | # INCIDENT-034 report | `brain-os/incidents/` | 5e | move |
| `./SINA_PROMPT_FAST_LOOP_LOCKED_v1.md` | 4.0K | # Sina Prompt-Fast Loop — Canonical 10 | `brain-os/law/` | 5e | move |
| `./SINA_PROMPT_OS_CORE_v1.md` | 1.0K | # Sina Prompt OS — Index (subordinate) | `brain-os/law/` | 5e | move |
| `./SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` | 12.0K | # Sina Prompt OS — System Definition (LOCKED) | `brain-os/law/` | 5e | move |
| `./SINA_REGISTRY_BATCH_FAKE_PROGRESS_INCIDENT_REPORT_LOCKED_v1.md` | 1.0K | # REGISTRY batch fake progress — incident | `brain-os/incidents/` | 5e | move |
| `./SINA_RUNTIME_STACK_LOCKED_v1.md` | 4.0K | # Runtime Stack — Locked Plan (Phase 2) | `brain-os/law/` | 5e | move |
| `./SINA_S10_WRONG_BASH_CWD_INCIDENT_019_REPORT_LOCKED_v1.md` | 1.0K | # SUPERSEDED — wrong topic S10/bash | `brain-os/incidents/` | 5e | move |
| `./SINA_SEMEJ_AGENT_v1.md` | 1.0K | # SEMEJ — multi-AI Chrome agent | `brain-os/law/` | 5e | move |
| `./SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md` | 3.0K | # Semi-separate Cursor lanes — agent notice | `brain-os/law/` | 5e | move |
| `./SINA_STATIC_PROMPT_FEED_STALE_LIST_INCIDENT_024_REPORT_LOCKED_v1.md` | 1.0K | # INCIDENT-024 pointer | `brain-os/incidents/` | 5e | move |
| `./SINA_THREAD_ACTIVATION_AND_READINESS_LOCKED_v1.md` | 10.0K | # Sina Thread Activation & Test Readiness | `brain-os/law/` | 5e | move |
| `./SINA_THREAD_ROOM_LOCKED_v1.md` | 2.0K | # Sina Thread Room — LOCKED v1 | `brain-os/law/` | 5e | move |
| `./SINA_THUNDERFIELD_VC_LEGAL_RELATIONSHIP_PLATFORM_LOCKED_v1.md` | 13.0K | # Thunderfield — VC Legal Platform | `brain-os/law/` | 5e | move |
| `./SINA_VOYAGE_P05_FAKE_GREEN_STALE_LABELS_INCIDENT_036_REPORT_LOCKED_v1.md` | 1.0K | # Voyage P05 fake-green stale labels | `brain-os/incidents/` | 5e | move |
| `./SINA_WORKER_AUTORUN_STALL_AND_TIMING_INCIDENT_REPORT_LOCKED_v1.md` | 1.0K | # Worker auto-run stall — incident report | `brain-os/incidents/` | 5e | move |
| `./SINA_WORKER_IGNORED_ASF_NO_HUB_STOP_STALE_STEERING_INCIDENT_031_REPORT_LOCKED_v1.md` | 1.0K | # INCIDENT-031 — Worker ignored ASF no-hub stop | `brain-os/incidents/` | 5e | move |
| `./SINA_WORKER_INCIDENT_028_REPEAT_REPORT_LOCKED_v1.md` | 1.0K | # INCIDENT-028-REPEAT | `brain-os/incidents/` | 5e | move |
| `./SINA_WORKER_SESSION_MISTAKES_CLOSEOUT_INCIDENT_REPORT_LOCKED_v1.md` | 1.0K | # Worker session mistakes — incident report | `brain-os/incidents/` | 5e | move |
| `./SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_012_REPORT_LOCKED_v1.md` | 1.0K | # SUPERSEDED — use INCIDENT-013 | `brain-os/incidents/` | 5e | move |
| `./SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_REPORT_LOCKED_v1.md` | 1.0K | # INCIDENT-013 — Worker stale goal_progress | `brain-os/incidents/` | 5e | move |
| `./SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_REPORT_INCIDENT_REPORT_LOCKED_v1.md` | 1.0K | # Worker chat stale goal_progress | `brain-os/incidents/` | 5e | move |
| `./SINA_WORKER_YAML_ONLY_CLOSEOUT_FAKE_GREEN_INCIDENT_030_REPORT_LOCKED_v1.md` | 1.0K | # INCIDENT-030 — YAML-only closeout fake green | `brain-os/incidents/` | 5e | move |

## Batch 5f — manifest rows (`OTHER` remainder → law / system / archive)

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|
| `./AI_INFRA_PARTNERSHIP_PROPOSALS_LOCKED_v1.md` | 8.0K | # AI infrastructure partnership proposals — LOCKED v1 | `brain-os/law/` | 5f | move |
| `./ASF_100_NEXT_PLANS_ENTERPRISE_SHIP_LOCKED_v1.md` |  12K | # ASF — 100 next plans · enterprise ship (LOCKED v1) | `brain-os/system/` | 5f | move |
| `./ASF_FIVE_REPOS_PLUS_COMMAND_CHAT_v1.md` | 4.0K | # Five product repos + Lane 0 command chat | `brain-os/system/` | 5f | move |
| `./ASF_PARALLEL_SIX_REPOS_OVERRIDE_v1.md` | 4.0K | # ASF override — parallel = 5 product repos + Lane 0 command | `brain-os/system/` | 5f | move |
| `./AUTO_CONFLICT_ENGINE_V3_LOCKED.md` | 8.0K | # Auto-Conflict Engine v3 — Layer Sovereignty (FINAL LOCKED) | `brain-os/law/` | 5f | move |
| `./AUTO_CONFLICT_EXAMPLE_AGENT_STACK_POLICY_v1_LOCKED.md` | 8.0K | # AUTO-CONFLICT Example — Agent Stack Policy v1 (LOCKED) | `brain-os/law/` | 5f | move |
| `./BRAIN_OS_POINTER_LOCKED_v1.md` | 4.0K | # Brain-OS — unified SSOT pointer (LOCKED v2) | `brain-os/law/entry/` | 5f | move |
| `./CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5f | archive |
| `./CHAT_EXTRACT_UNIFY_PROMPT.txt` | 4.0K | CHAT EXTRACT — this conversation only | `archive/root-sprawl/` | 5f | archive |
| `./CHAT_UNIFY_ROLLUP_PROMPT.txt` | 4.0K | CHAT UNIFY — merge extractions into one master brief | `archive/root-sprawl/` | 5f | archive |
| `./COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md` |  12K | # Council Brief — Strategic Slice (LOCKED v1) | `brain-os/law/` | 5f | move |
| `./CROSS_LANE_EDIT_FORBIDDEN_LOCKED_v1.md` | 4.0K | # Cross-lane edit forbidden — LOCKED v1 (stub) | `archive/root-stubs/` | 5f | archive |
| `./DEVBRIDGE_EXTENSION_NO_CODE_300_STEP_PLAN_LOCKED_v1.md` |  40K | # DevBridge for Cursor — Unified 300-Step Plan (LOCKED v2.1) | `brain-os/law/` | 5f | move |
| `./DISPATCH_POLICY_LOCKED_v1.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5f | archive |
| `./ECOSYSTEM_IMPORTANT_DOCS_INDEX_LOCKED_v1.md` | 4.0K | # Ecosystem important docs — index (LOCKED pointer) | `archive/root-stubs/` | 5f | archive |
| `./ECOSYSTEM_STATUS.md` | 8.0K | # Ecosystem Status (generated — do not edit by hand) | `brain-os/system/` | 5f | move |
| `./ENFORCEMENT-6MO-MASTER-PLAN-v1.md` |  24K | # ENFORCEMENT-6MO MASTER EXECUTION PLAN | `brain-os/law/` | 5f | move |
| `./ENFORCEMENT-6MO-VC-ROADMAP-v1.md` |  28K | # ENFORCEMENT-6MO — VC-GRADE EXECUTION ROADMAP | `brain-os/law/` | 5f | move |
| `./ENFORCE_BYPASS_MAP_LOCKED_v1.md` | 4.0K | # ENFORCE bypass map (LOCKED v1) | `brain-os/law/enforcement/` | 5f | move |
| `./FULL_STACK_ACTIVATION.md` | 4.0K | # Full Stack Activation — Brain/Worker Run This Once | `brain-os/law/` | 5f | move |
| `./GOVERNANCE_DRIFT_DETECTION_INSIGHTS_2026.md` | 4.0K | # MOVED — Canonical copy under Noetfield Runtime agent vault | `archive/root-stubs/` | 5f | archive |
| `./GOVERNANCE_DRIFT_ENGINE_LOCKED_v1.md` | 4.0K | # Governance Drift Engine (LOCKED) | `brain-os/law/` | 5f | move |
| `./GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md` |  12K | # Governance Unification Engine (LOCKED) | `brain-os/law/` | 5f | move |
| `./HONEST_P0_SCREEN_LOCKED_v1.md` | 4.0K | # Honest P0 screen (pointer) | `archive/root-stubs/` | 5f | archive |
| `./HUB_LITE_REBUILD_PHASE0_LOCKED_v1.md` | 4.0K | # HUB-LITE-REBUILD Phase 0 — LOCKED v1 | `brain-os/law/` | 5f | move |
| `./HUB_PROOF_UX_P0_LOCKED_v1.md` | 4.0K | # Hub proof UX P0 — LOCKED v1 | `brain-os/law/` | 5f | move |
| `./HUB_SOURCE_UI_ALIGNMENT_PROCEDURE_LOCKED_v1.md` | 8.0K | # Hub ↔ Source ↔ UI Alignment Procedure (LOCKED) | `brain-os/law/` | 5f | move |
| `./HUB_STABILIZATION_v5.1_FINAL.md` |  24K | # HUB_STABILIZATION_v5.1_FINAL | `brain-os/law/` | 5f | move |
| `./HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` | 4.0K | # Worker Hub only — monolith archived — LOCKED v1 | `brain-os/law/` | 5f | move |
| `./IPHONE_CLOUD_ORGANIZATION_SPEC_LOCKED_v1.md` |  12K | # iPhone Cloud — organization spec (LOCKED) | `brain-os/law/` | 5f | move |
| `./LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md` | 4.0K | # LLM Context Packet — Schema Contract (LOCKED v1) | `brain-os/law/` | 5f | move |
| `./MACHINE_THREE_PIPELINES_CALIBRATE_TUNE_FORGE_LOCKED_v1.md` | 4.0K | # Machine three pipelines — Calibrate · Tune · machine prove | `brain-os/law/` | 5f | move |
| `./MAC_GUARD_AGENCY_DEMO_SCRIPT_LOCKED_v1.md` | 4.0K | # Mac Guard Agency Demo Script — SUPERSEDED | `archive/root-stubs/` | 5f | archive |
| `./MAC_SNAPSHOT_PROMPT.txt` | 4.0K | MAC SNAPSHOT — run now | `archive/root-sprawl/` | 5f | archive |
| `./META_REASONING_POLICY_STACK_LOCKED_v1.md` |  24K | # Meta-Reasoning Policy Stack — Decision Governance Layer (L | `brain-os/law/` | 5f | move |
| `./N8N_AUTOMATION_EXECUTION_PLAN_LOCKED_v2.md` | 8.0K | # n8n Automation — Execution Plan (LOCKED) | `brain-os/law/` | 5f | move |
| `./N8N_COMMERCIAL_GRADE_LOCKED_v1.md` | 4.0K | # n8n Commercial Grade — LOCKED v1 | `brain-os/law/` | 5f | move |
| `./N8N_FOUNDER_MASTER_CARD_LOCKED_v1.md` | 4.0K | # N8N Founder Master Card (LOCKED) | `brain-os/law/` | 5f | move |
| `./NOETFIELD_CLOUD_GIT_AND_AGENT_ENTRY_UNIFIED_LOCKED_v1.md` | 8.0K | # Noetfield — cloud git, Mac hub, and agent entry (unified) | `brain-os/law/` | 5f | move |
| `./NOETFIELD_COMPLIANCE_DEMO_SCRIPT_LOCKED_v1.md` | 8.0K | # Noetfield Compliance Demo Script — LOCKED v1 | `brain-os/law/` | 5f | move |
| `./NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_LOCKED_v1.md` | 8.0K | # Noetfield — Founding Customer Pilot (NW1) | `brain-os/law/` | 5f | move |
| `./NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_MERGED_EXTERNAL_v1.md` | 4.0K | # Noetfield — Founding Customer Pilot (External Send) | `brain-os/law/` | 5f | move |
| `./NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md` | 8.0K | # Noetfield NW1 Battle Card — LOCKED v1 | `brain-os/law/` | 5f | move |
| `./ORDER_GUARDIAN_AGENT_LOCKED_v1.md` | 4.0K | # Order Guardian — in-app task orders agent (LOCKED) | `brain-os/law/` | 5f | move |
| `./PHASE1_UNIFIED_BLUEPRINT_v2_3.md` |  36K | > **INTERNAL ONLY — Phase 1 work plan — NOT SSOT.** | `docs/archive/` | 5f | move |
| `./PLAN_STATUS_VOCAB_LOCKED_v1.md` | 4.0K | # Plan status vocabulary + factory scoring vs growth (LOCKED | `brain-os/law/` | 5f | move |
| `./PORT_NOTICE_BOARD.md` | 4.0K | # PORT NOTICE BOARD (live — agents read this first) | `brain-os/system/` | 5f | move |
| `./PORT_NOTICE_BOARD_LOCKED_v1.md` | 4.0K | # Port Notice Board — LOCKED (agent entry point) | `brain-os/law/` | 5f | move |
| `./PORT_REGISTRY.md` | 8.0K | # Port Registry (live — do not edit by hand) | `brain-os/system/` | 5f | move |
| `./PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md` | 4.0K | # Product factory roadmap — LOCKED v1 | `brain-os/law/` | 5f | move |
| `./PROMPT_OS_CORE_MVP_BUILD_ORDER_LOCKED_v1.md` | 8.0K | # Prompt OS Core — MVP Build Order (LOCKED) | `brain-os/law/` | 5f | move |
| `./README_SOURCE_A.md` | 4.0K | # Source A — read this first | `brain-os/law/entry/` | 5f | move |
| `./REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md` | 8.0K | # Refinement unified — Agent · Machine · Founder (LOCKED v1) | `brain-os/law/` | 5f | move |
| `./RESEARCH_INTAKE_AND_SAVE_LOCK_LOCKED_v1.md` | 8.0K | # Research intake & save — LOCKED v1 | `brain-os/law/enforcement/` | 5f | move |
| `./RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md` | 4.0K | # Run inbox disk truth execution (LOCKED v1) | `brain-os/law/enforcement/` | 5f | move |
| `./SECRETS_VAULT.md` | 4.0K | # Sina Secret Vault (one place) | `brain-os/system/` | 5f | move |
| `./SINAAI_10X_AUTOMATION_ARCHITECTURE_LOCKED_v1.md` | 8.0K | # Sinaai — 10x Automation Architecture (LOCKED) | `brain-os/law/` | 5f | move |
| `./SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` |  24K | # Sinaai — Agents & Automation Unified Blueprint (LOCKED) | `brain-os/law/` | 5f | move |
| `./SINAAI_AGENT_STACK_POLICY_v1.md` | 8.0K | # Sinaai Agent Stack Policy — One Pager | `brain-os/law/` | 5f | move |
| `./SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md` | 8.0K | # Sinaai Agent YAML Ingest & Self-Healing Loop — FINAL LOCKE | `brain-os/law/` | 5f | move |
| `./SINAAI_ARCHITECT_V2_INDUSTRIAL_POLICY_LOCKED_v1.md` | 4.0K | # Architect v2 — Industrial System Cleaner (LOCKED) | `brain-os/law/` | 5f | move |
| `./SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` | 4.0K | # MOVED — canonical SSOT | `archive/root-stubs/` | 5f | archive |
| `./SINAAI_ECOSYSTEM_FINAL_STATE_AND_NEXT_PLAN_LOCKED_v1.md` | 8.0K | # Sinaai Ecosystem — Final State & Next Plan (LOCKED) | `brain-os/law/` | 5f | move |
| `./SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` | 8.0K | # Sinaai — Execution Truth Layer (LOCKED) | `brain-os/law/` | 5f | move |
| `./SINAAI_FAST_TRACK_FORCE_MAJEURE_LOCKED_v1.md` | 4.0K | # FAST TRACK — FORCE MAJEURE (LOCKED) | `brain-os/law/` | 5f | move |
| `./SINAAI_MASTER_BLUEPRINT_END_TO_END_v1.md` |  24K | # Sinaai — Master Blueprint (End-to-End) | `brain-os/law/` | 5f | move |
| `./SINAAI_MASTER_PLAN_FA_SHARE_v1.md` |  16K | # برنامهٔ جامع اکوسیستم سینا — نقشهٔ شهر، مراحل M، تلگرام، و | `brain-os/law/` | 5f | move |
| `./SINAAI_PARALLEL_LANES_NO_BLOCK_PROGRESS_LOCKED_v1.md` | 4.0K | # Parallel lanes — repo work MUST NOT block wire progress (L | `brain-os/law/` | 5f | move |
| `./SINAAI_PERMANENT_ARCHITECT_AGENT_LOCKED_v1.md` | 4.0K | # Permanent Architect Agent — LOCKED | `brain-os/law/` | 5f | move |
| `./SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md` | 4.0K | # Phase 1 stabilization ONLY — scope freeze (LOCKED) | `brain-os/law/` | 5f | move |
| `./SINAAI_PHASE2_AI_CONTROLLED_EXECUTION_LOCKED_v1.md` | 8.0K | # Sinaai — Phase 2: AI-Controlled Execution OS (LOCKED) | `brain-os/law/` | 5f | move |
| `./SINAAI_PORT_REGISTRY_LAW_LOCKED_v1.md` | 8.0K | # Sinaai — Port Registry Law (LOCKED) | `brain-os/law/` | 5f | move |
| `./SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md` | 8.0K | # Sinaai — Prompt OS Core Final Decision (LOCKED) | `brain-os/law/` | 5f | move |
| `./SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md` |  12K | # Source A — Document Sequence & Dating Registry (LOCKED) | `brain-os/system/` | 5f | move |
| `./STALE_ADVICE_RESULTS_POLICY_OWNERSHIP_TRACKING_LOCKED_v1.md` |  12K | # Stale advice — results policy · ownership · tracking (LOCK | `brain-os/law/` | 5f | move |
| `./STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` | 8.0K | # Strategic next steps — big picture synthesis (LOCKED v2) | `brain-os/law/` | 5f | move |
| `./TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md` | 4.0K | # Task orders — open register (LOCKED v1) | `brain-os/law/` | 5f | move |
| `./TRUSTFIELD_ENTITY_CORRECTION_v3_1.md` | 4.0K | # TrustField entity correction — APPLIED v3.1 | `brain-os/law/` | 5f | move |
| `./TRUST_LEDGER_SCHEMA_LOCKED_v1.md` | 4.0K | # Trust ledger schema (LOCKED v1) | `brain-os/law/` | 5f | move |
| `./UNDERSTANDING_ROLES_CURSOR_ECOSYSTEM_v1.md` |  12K | # Understanding roles — Cursor & agent ecosystem (ASF refere | `brain-os/law/` | 5f | move |
| `./VIRELUX_REPO_ALIGNMENT.md` | 4.0K | # VIRLUX repo alignment — DESIGN ↔ DELIVERY bridge | `docs/` | 5f | move |
| `./WIRE_LANE_PROGRESS.md` | 4.0K | # Wire lane progress — single checklist (ASF) | `brain-os/law/` | 5f | move |
| `./WORKER_FAST_ANTI_STALENESS_AUTO_HEAL_LOCKED_v1.md` | 4.0K | # Worker — Fast Anti-Staleness Auto-Heal (LOCKED v1) | `brain-os/law/enforcement/` | 5f | move |
| `./WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` | 4.0K | # Worker full-round evidence enforcement (pointer) | `archive/root-stubs/` | 5f | archive |
| `./WORKER_NO_SLOW_VERIFY_SHELL_LOCKED_v1.md` | 4.0K | # Worker — No Slow VERIFY Shell (LOCKED v1) | `brain-os/law/enforcement/` | 5f | move |
| `./sourcea-site-v1-QUARANTINE.md` | 4.0K | # SourceA Site v1 — QUARANTINED (UI experiment) | `docs/archive/` | 5f | move |

## Batch 3.5 — emergency (taxonomy + pointers)

**Cause:** Batch 3 moved tier-0 docs before path-grep; scripts still pointed at repo root.

**Taxonomy fix (no new top-level dirs):**
- `brain-os/entry/` → `brain-os/law/entry/` (5 files)
- `brain-os/enforcement/` → `brain-os/law/enforcement/` (39 files)
- Deleted empty `brain-os/entry/` and `brain-os/enforcement/` top-level folders

**Pointer SSOT:** `scripts/governance_paths_v1.py` · `scripts/governance-paths-v1.sh`

**Gate scripts verified (file resolve):** conduct gate, critic boot, stairlift, monitor, authority audit, ecosystem catalog, projection g3.

**Not in 3.5:** `ASF_RETIRE_SINA_COMMAND` archive move — defer to batch 4 triage with ASF.

## Batch 3 pointer fix (superseded by 3.5)

Tier-0 files moved in batch 3 broke root-relative script paths. Fixed via:

- `scripts/governance_paths_v1.py` — canonical `Path` constants
- `scripts/governance-paths-v1.sh` — shell source file
- Python: conduct gate, critic boot, brain wire, authority audit, stairlift, monitor, propagation cascade, founder signal, reference graph, projection g3, ecosystem catalog, hub essentials, orientation pipelines, important docs, agent system unified, system roadmap, audit hub alignment
- JSON: `data/sourcea_agentic_unified_bundle_v1.json` orientation + apex commercial paths
- Shell (sample): `validate-law-purity-ssot`, `validate-live-founder-decision-form`, `validate-disclosure-ladder`, `validate-governed-agentic-automation-offer`
- Self-ref: `brain-os/law/SINA_OS_SSOT_LOCKED.md` canonical location line

Remaining shell validators still using `$ROOT/SINA_*` at root should source `governance-paths-v1.sh` on next touch.



## Execute batch 5a (after APPROVED)

```bash
cd ~/Desktop/SourceA
bash infra/cleanup/scan-secrets-v1.sh
bash infra/cleanup/execute-batch-v1.sh --batch 5a --dry-run
bash infra/cleanup/execute-batch-v1.sh --batch 5a
bash infra/cleanup/generate-inventory-v1.sh
python3 scripts/cleanup_track_sync_v1.py --json
git add -A
git commit -m "cleanup: batch-5a sourcea law → brain-os"
```

**Critic packet:** `infra/cleanup/batch-5a-diff-for-critics.md`

## Execute batch 4 (after APPROVED)

```bash
cd ~/Desktop/sourceA
bash infra/cleanup/execute-batch-v1.sh --batch 4 --dry-run
bash infra/cleanup/execute-batch-v1.sh --batch 4
git add -A
git commit -m "cleanup: batch-4 command incidents → archive + brain-os"
bash infra/cleanup/generate-inventory-v1.sh
git add infra/cleanup/inventory-root.tsv
git commit -m "chore: inventory after batch 4"
```

**Critic packet:** `infra/cleanup/batch-4-diff-for-critics.md`

## Execute batch 3 (done)

```bash
cd ~/Desktop/sourceA
bash infra/cleanup/execute-batch-v1.sh --batch 3 --dry-run
bash infra/cleanup/execute-batch-v1.sh --batch 3
git add -A
git commit -m "cleanup: batch-3 portfolio law → brain-os"
bash infra/cleanup/generate-inventory-v1.sh
```

**Critic packet:** `infra/cleanup/batch-3-diff-for-critics.md`

## Execute batch 2 (done)

```bash
cd ~/Desktop/sourceA
bash infra/cleanup/execute-batch-v1.sh --batch 2 --dry-run
bash infra/cleanup/execute-batch-v1.sh --batch 2
git add -A
git commit -m "cleanup: batch-2 sina agent → brain-os"
bash infra/cleanup/generate-inventory-v1.sh
```

## Execute batch 1 (done)

```bash
cd ~/Desktop/sourceA
bash infra/cleanup/execute-batch-v1.sh --batch 1 --dry-run
bash infra/cleanup/execute-batch-v1.sh --batch 1
git status
git add -A
git commit -m "cleanup: batch-1 agent law → brain-os"
```

## Notes

- **Dupes:** `AGENT_RULES_IN_CHARGE` and `AGENT_VERBS` already exist in `brain-os/law/` and `brain-os/law/enforcement/` — root copies are stubs → archive only.
- Do not move `START_HERE.md`, `ACTIVE_NOW.md`, or `data/*.json` in batch 1.
- Virlux stays under `labs/virlux/`.


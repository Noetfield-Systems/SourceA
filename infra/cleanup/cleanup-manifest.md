# Cleanup manifest — SourceA root sprawl

**Status:** FROZEN — Batch 4 blocked until ASF approves  
**Generated:** 2026-06-20  
**Inventory:** `infra/cleanup/inventory-root.tsv` (252 files after batch 3)

## Approval

- [x] Secret scan clear
- [x] Batch 1 executed — commit `0cf364d8`
- [x] Batch 2 executed — commit `94c2dd2b`
- [x] Batch 3 executed — commit `0bb4a1b1` (premature — regression fixed in 3.5)
- [x] **Batch 3.5 emergency** — pointer sync + taxonomy consolidation (`law/entry`, `law/enforcement`)
- [ ] **Batch 4 FROZEN** — do not execute until ASF sets APPROVED below
- [ ] Critic packet: `infra/cleanup/batch-4-diff-for-critics.md`

## Batch plan


| Batch | Theme                                        | Files   | Commit prefix                    |
| ----- | -------------------------------------------- | ------- | -------------------------------- |
| **1** | `AGENT_*` → `brain-os/`                      | 26 ✅    | `cleanup: batch-1 agent law`     |
| **2** | `SINA_AGENT_*` + leftovers + incident reports | 25 ✅   | `cleanup: batch-2 sina agent`    |
| **3** | Tier-0 ASF + SINA + SOURCEA SSOT law           | 25 ✅   | `cleanup: batch-3 portfolio law` |
| **3.5** | Emergency pointer sync + taxonomy fix        | — ✅    | `chore(cleanup): batch 3.5`      |
| **4** | `SINA_COMMAND_*` legacy hub + incident reports | 25 FROZEN | `cleanup: batch-4 command incidents` |
| 5     | Remainder triage                             | per row | `cleanup: batch-5 …`             |


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
| `./SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_REPORT_LOCKED_v1.md` | 4.0K | INCIDENT-023 pointer | `brain-os/incidents/` | 4 | move |
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


## Batch 3.5 — emergency (taxonomy + pointers)

**Cause:** Batch 3 moved tier-0 docs before path-grep; scripts still pointed at repo root.

**Taxonomy fix (no new top-level dirs):**
- `brain-os/entry/` → `brain-os/law/entry/` (5 files)
- `brain-os/enforcement/` → `brain-os/law/enforcement/` (39 files)
- Deleted empty `brain-os/entry/` and `brain-os/enforcement/` top-level folders

**Pointer SSOT:** `scripts/governance_paths_v1.py` · `scripts/governance-paths-v1.sh`

**Gate scripts verified (file resolve):** conduct gate, critic boot, stairlift, monitor, authority audit, ecosystem catalog, projection g3.

**Not in 3.5:** `ASF_RETIRE_SINA_COMMAND` archive move — defer to batch 4 triage with ASF.

**Archive immutability (2026-06-20):** Batch 3.5 mass-replace touched 11 files under `archive/` (path strings only). Reverted to `0bb4a1b1` snapshot — live code uses `governance_paths_v1.py`; archive keeps historical paths. **Future batches: never bulk-replace inside `archive/`.**


## Batch 3 pointer fix (superseded by 3.5)

Tier-0 files moved in batch 3 broke root-relative script paths. Fixed via:

- `scripts/governance_paths_v1.py` — canonical `Path` constants
- `scripts/governance-paths-v1.sh` — shell source file
- Python: conduct gate, critic boot, brain wire, authority audit, stairlift, monitor, propagation cascade, founder signal, reference graph, projection g3, ecosystem catalog, hub essentials, orientation pipelines, important docs, agent system unified, system roadmap, audit hub alignment
- JSON: `data/sourcea_agentic_unified_bundle_v1.json` orientation + apex commercial paths
- Shell (sample): `validate-law-purity-ssot`, `validate-live-founder-decision-form`, `validate-disclosure-ladder`, `validate-controlled-agentic-automation-offer`
- Self-ref: `brain-os/law/SINA_OS_SSOT_LOCKED.md` canonical location line

Remaining shell validators still using `$ROOT/SINA_*` at root should source `governance-paths-v1.sh` on next touch.


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


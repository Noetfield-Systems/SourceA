# Cleanup manifest — SourceA root sprawl

**Status:** DRAFT — do not execute until ASF sets **APPROVED**  
**Generated:** 2026-06-20  
**Inventory:** `infra/cleanup/inventory-root.tsv` (328 files)

## Approval

- [x] Secret scan clear (`infra/cleanup/secret-scan-report.txt` — no live keys)
- [ ] ASF reviewed batch 1 destinations below
- [ ] Change line 3 to: **Status: APPROVED**

## Batch plan


| Batch | Theme                                        | Files   | Commit prefix                    |
| ----- | -------------------------------------------- | ------- | -------------------------------- |
| **1** | `AGENT_`* → `brain-os/`                      | 25      | `cleanup: batch-1 agent law`     |
| 2     | `SINA_AGENT_*` + `SOURCEA_AGENT*` → brain-os | 25      | `cleanup: batch-2 sina agent`    |
| 3     | Remaining `SINA_*` / `SOURCEA_*` LOCKED      | 25      | `cleanup: batch-3 portfolio law` |
| 4     | `.txt` prompts + entry pointers              | 3+      | `cleanup: batch-4 prompts`       |
| 5     | Remainder triage                             | per row | `cleanup: batch-5 …`             |


## Batch 1 — manifest rows (review these)


| source                                                           | size | first_heading                          | proposed_dest           | batch | action  |
| ---------------------------------------------------------------- | ---- | -------------------------------------- | ----------------------- | ----- | ------- |
| `./AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md`                 | 28K  | Agent Application Use Blueprint        | `brain-os/law/`         | 1     | move    |
| `./AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md`                       | 4.0K | Sina Command as unifying hub           | `brain-os/law/`         | 1     | move    |
| `./AGENT_CONTROL_PANEL_SPEC_LOCKED_v1.md`                        | 8.0K | Agent Control Panel spec               | `brain-os/law/`         | 1     | move    |
| `./AGENT_COUNCIL_ROOM_LOCKED_v1.md`                              | 8.0K | Agent Council Room                     | `brain-os/law/`         | 1     | move    |
| `./AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md`         | 12K  | Agent Decision Stack & Smart Judgment  | `brain-os/law/`         | 1     | move    |
| `./AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md`                      | 4.0K | Agent disk live wire first             | `brain-os/enforcement/` | 1     | move    |
| `./AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md`            | 16K  | Agent ecosystem sprint                 | `brain-os/law/`         | 1     | move    |
| `./AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md`              | 8.0K | Agent ecosystem unification policy     | `brain-os/law/`         | 1     | move    |
| `./AGENT_ESSAY_DISCOURSE_LOCKED_v1.md`                           | 4.0K | Agent essay discourse                  | `brain-os/law/`         | 1     | move    |
| `./AGENT_EXECUTOR_DAILY_DUTY_CARD_LOCKED_v1.md`                  | 8.0K | Agent executor daily duty card         | `brain-os/enforcement/` | 1     | move    |
| `./AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md`                | 4.0K | Agent → founder bash communication     | `brain-os/enforcement/` | 1     | move    |
| `./AGENT_GOVERNANCE_INDEX_LOCKED_v1.md`                          | 8.0K | Agent governance index                 | `brain-os/law/`         | 1     | move    |
| `./AGENT_INCIDENTS_REGISTRY_REPORT_LOCKED_v1.md`                 | 4.0K | Agent incidents registry report        | `brain-os/incidents/`   | 1     | move    |
| `./AGENT_DIAG_CLIPBOARD_PAIRING_HIJACK_2026-05-27_LOCKED.md`     | 4.0K | Clipboard hijack diag                  | `brain-os/incidents/`   | 1     | move    |
| `./AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md`                 | 4.0K | Agent memory mirror enforcement        | `brain-os/enforcement/` | 1     | move    |
| `./AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md`                    | 4.0K | MergePack is NOT an agent              | `brain-os/law/`         | 1     | move    |
| `./AGENT_MIND_SHARE_LOCKED_v1.md`                                | 4.0K | Agent Mind Share                       | `brain-os/law/`         | 1     | move    |
| `./AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md`                      | 4.0K | No Hub Rebuild Stuck Loop              | `brain-os/enforcement/` | 1     | move    |
| `./AGENT_OPERATING_ROLES_LOCKED_v1.md`                           | 4.0K | Agent operating roles                  | `brain-os/law/`         | 1     | move    |
| `./AGENT_SCOREBOARD_LOCKED_v1.md`                                | 4.0K | Agent session scoreboard               | `brain-os/law/`         | 1     | move    |
| `./AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md`              | 8.0K | Agent Skills & Research Pipeline       | `brain-os/law/`         | 1     | move    |
| `./AGENT_TERMINAL_CLOSEOUT_LOCKED_v1.md`                         | 4.0K | Agent terminal closeout                | `brain-os/enforcement/` | 1     | move    |
| `./AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md` | 12K  | Orientation · Hospital · Maze          | `brain-os/law/`         | 1     | move    |
| `./AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md`              | 4.0K | Workspace vault middle layer           | `brain-os/law/`         | 1     | move    |
| `./AGENT_RULES_IN_CHARGE_LOCKED_v1.md`                           | 4.0K | MOVED — canonical SSOT (root stub)     | `archive/root-stubs/`   | 1     | archive |
| `./AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md`                      | 4.0K | SAVE · WORK · EDIT ALLOWED (root stub) | `archive/root-stubs/`   | 1     | archive |


### Batch 1 — deferred to batch 2 (not in this commit)


| source                                        | note                                                                  |
| --------------------------------------------- | --------------------------------------------------------------------- |
| `./AGENT_DESK_START_HERE.md`                  | → `brain-os/entry/` (entry gate doc)                                  |
| `./AGENT_RULE_CONFLICT_*`                     | → `brain-os/incidents/` (may dupe files already there — verify first) |
| `./AGENT_SELF_AUDIT_ASF_REPORT_2026-06-04.md` | → `docs/archive/` (dated report, not law)                             |


## Execute batch 1 (after APPROVED)

```bash
cd ~/Desktop/sourceA
bash infra/cleanup/execute-batch-v1.sh --batch 1 --dry-run
bash infra/cleanup/execute-batch-v1.sh --batch 1
git status
git add -A
git commit -m "cleanup: batch-1 agent law → brain-os"
```

## Notes

- **Dupes:** `AGENT_RULES_IN_CHARGE` and `AGENT_VERBS` already exist in `brain-os/law/` and `brain-os/enforcement/` — root copies are stubs → archive only.
- Do not move `START_HERE.md`, `ACTIVE_NOW.md`, or `data/*.json` in batch 1.
- Virlux stays under `labs/virlux/`.


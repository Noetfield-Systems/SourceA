# SOURCEA_DISK_SNAPSHOT_TELEMETRY

**Saved:** 2026-06-13T09:46:05Z · **Retrofit:** doc-datetime-law batch retrofit
- generated: 2026-06-12T19:52:42Z
- workspace: `/Users/sinakazemnezhad/Desktop/SourceA`
- excludes: `.git`, `node_modules`, `__pycache__`, `.cursor`, heavy `receipts/` bulk
- note: **JudgeRoom** on disk = **Judge Center** (`judge_center_*`). **ThreadRoom** = `thread_room_*`.

## 1. Directory tree (depth 4, pruned)

```
SourceA/
├── agent-control-panel/
│   ├── assets/
│   │   ├── app.css
│   │   ├── app.js
│   │   ├── design-tokens-v1.css
│   │   ├── icon-system-v1.js
│   │   ├── journey-ui.js
│   │   ├── nav-registry-v1.js
│   │   ├── page-shell-v1.js
│   │   ├── pages-detail.js
│   │   ├── shell.html
│   │   ├── theme-duo.css
│   │   └── ui-shell-v1.css
│   ├── mini-apps/
│   │   ├── apple-health/
│   │   │   ├── app.css
│   │   │   ├── app.js
│   │   │   └── index.html
│   │   ├── chat-unify/
│   │   │   ├── app.css
│   │   │   ├── app.js
│   │   │   └── index.html
│   │   └── mac-health/
│   │       ├── app.css
│   │       ├── app.js
│   │       └── index.html
│   ├── command-data-canonical.json
│   ├── command-data-runtime.json
│   ├── command-data-shell.json
│   ├── command-data.json
│   └── index.html
├── agent-pro-v1/
│   ├── public/
│   │   ├── app.js
│   │   ├── index.html
│   │   └── style.css
│   ├── README.md
│   └── server.py
├── agent-skills/
│   ├── ai_dev_bridge_os/
│   │   └── SKILL.md
│   ├── drafts/
│   ├── noetfield_cloud/
│   │   └── SKILL.md
│   ├── noetfield_local/
│   │   └── SKILL.md
│   ├── semej/
│   │   └── SKILL.md
│   ├── seven77/
│   │   └── SKILL.md
│   ├── shared/
│   │   ├── advisor-external-critic/
│   │   │   └── SKILL.md
│   │   ├── agentic-commercial/
│   │   │   └── SKILL.md
│   │   ├── anti-staleness-machine/
│   │   │   └── SKILL.md
│   │   ├── conscious-recovery/
│   │   │   ├── reference.md
│   │   │   └── SKILL.md
│   │   ├── founder-freeze-conduct/
│   │   │   └── SKILL.md
│   │   ├── narrative-translator/
│   │   │   ├── reference.md
│   │   │   └── SKILL.md
│   │   ├── registry-drain/
│   │   │   └── SKILL.md
│   │   ├── research-intake/
│   │   │   └── SKILL.md
│   │   ├── s10-eternal-self-heal/
│   │   │   └── SKILL.md
│   │   └── truth-projection/
│   │       └── SKILL.md
│   ├── sinaai_maintainer/
│   │   └── SKILL.md
│   ├── sourcea_brain/
│   │   └── SKILL.md
│   ├── sourcea_worker/
│   │   ├── reference.md
│   │   └── SKILL.md
│   ├── trustfield/
│   │   └── SKILL.md
│   ├── virlux/
│   │   └── SKILL.md
│   └── REGISTRY_LOCKED_v1.json
├── architecture_audit/
│   ├── ACTION_TRACE.md
│   ├── API_MAP.md
│   ├── ARCHITECTURE_ENTRYPOINTS.md
│   ├── CALL_GRAPH.md
│   ├── DEPENDENCY_GRAPH.md
│   ├── DEPENDENCY_GRAPH.mmd
│   ├── DEPENDENCY_GRAPH.png
│   ├── DEPENDENCY_GRAPH.svg
│   ├── HOTSPOTS.md
│   ├── PANEL_BUILD_MAP.md
│   ├── README.md
│   ├── REBUILD_READINESS_SCORE.md
│   ├── REBUILD_TRIGGER_MAP.md
│   └── STATE_MAP.md
├── archive/
│   ├── attachments/
│   │   ├── 2026-06-05/
│   │   │   └── INCIDENT-029-archived-scratch-canvas/
│   │   │       ├── sourcea-100-agent-pov-form-v2.canvas.data.json
│   │   │       ├── sourcea-100-agent-pov-form-v2.canvas.status.json
│   │   │       └── sourcea-100-agent-pov-form-v2.canvas.tsx
│   │   ├── 2026-06-10/
│   │   │   ├── ANTI_STALENESS_V2_MACHINE_CLOSEOUT_2026-06-10.md
│   │   │   ├── hub-app-quality-research-report_LOCKED_v1.md
│   │   │   ├── INCIDENT-022-maintainer-2-stale-autorun-advice_LOCKED_REPORT_v1.md
│   │   │   ├── PHASE_PACK_REORG_DRAFT_s2-s9_ACHIEVABLE_v1.md
│   │   │   ├── PROGRAM_1000_SA_001_1000_MATRIX_LIVE_2026-06-10.csv
│   │   │   ├── PROGRAM_1000_STEP_MATRIX_LIVE_2026-06-10.json
│   │   │   ├── sa-0779-mind-share-act-patch-spec_LOCKED_v1.md
│   │   │   ├── SOURCEA_10_PHASE_100_STEP_FIX_PLAN_LOCKED_v1.md
│   │   │   ├── SOURCEA_BRAIN_IGNORANCE_AND_ONE_LINER_ANALYSIS_LOCKED_v1.md
│   │   │   ├── SOURCEA_BRAIN_REPAIR_AUDIT_AND_INCIDENT_014_COMPLETION_LOCKED_v1.md
│   │   │   ├── SOURCEA_CONDUCT_AND_POISONED_LOOP_AUDIT_PROMPT_LOCKED_v1.md
│   │   │   ├── SOURCEA_CONDUCT_AND_POISONED_LOOP_AUDIT_PROMPT_LOCKED_v2.md
│   │   │   ├── SOURCEA_CONVERSATION_FULL_INSIGHT_S10_SSOT_V2_LOCKED_v1.md
│   │   │   ├── SOURCEA_CURSOR_REVIEW_KEEP_ALL_GUIDE_LOCKED_v1.md
│   │   │   ├── SOURCEA_EXTERNAL_ADVISOR_BRIEF_AND_CHECKLISTS_LOCKED_v1.md
│   │   │   ├── SOURCEA_FOUNDER_ADVISOR_DISCUSSION_TRACK_LOCKED_v1.md
│   │   │   ├── SOURCEA_LAYERED_ADVISORY_FULL_CHAT_EXPORT_v1.md
│   │   │   ├── SOURCEA_MACHINE_ENFORCEMENT_REGISTRY_AND_AGENT_MAP_LOCKED_v1.md
│   │   │   ├── SOURCEA_MASTER_INDEX_ALL_SUBJECTS_LOCKED_v1.md
│   │   │   ├── SOURCEA_PERMANENT_CONDUCT_POISON_MACHINE_ENFORCEMENT_ESSAY_LOCKED_v1.md
│   │   │   ├── SOURCEA_ROOT_CAUSE_FACTORY_CONTROL_PLANE_ESSAY_LOCKED_v1.md
│   │   │   ├── SOURCEA_SMOOTH_PROGRESS_HISTORY_VS_NOW_LOCKED_v1.md
│   │   │   └── SOURCEA_WORKER_CONDUCT_AUDIT_DISPOSITION_GUIDE_LOCKED_v1.md
│   │   ├── 2026-06-11/
│   │   │   ├── INCIDENT-027-maintainer-2-drain-projection-staleness_LOCKED_REPORT_v1.md
│   │   │   ├── MAINTAINER_1_END_OF_SERVICE_HANDOFF_2026-06-11.md
│   │   │   ├── MAINTAINER_1_MEGA_CHAT_ANCHOR_REGISTER_2026-06-11.md
│   │   │   ├── pendings-p0-p11-task-orders-mapping-crosswalk_LOCKED_v1.md
│   │   │   ├── rt-live-gate-wall-time-maintainer-check_LOCKED_v1.md
│   │   │   ├── sa-0786-governance-moat-synthesis-lesson_LOCKED_v1.md
│   │   │   ├── sa-0787-paradox-mind-share-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0788-council-hero-unification-policy-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0789-council-topics-vote-post-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0790-important-docs-index-governance-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0791-governance-drift-essay-nudge-count-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0792-blueprint-navigator-scope-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0793-sprint-consolidation-hub-pendings-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0794-vault-log-activity-essay-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0795-asf-assigns-subject-founder-not-verify-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0796-council-strategic-slice-seed-on-build-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0797-task-orders-open-register-hub-todos-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0798-order-guardian-judgments-vs-pendings-crosswalk_LOCKED_v1.md
│   │   │   ├── sa-0798-to-008-to-009-fleet-reconcile-check-note_LOCKED_v1.md
│   │   │   ├── sa-0799-mark-best-post-without-asf-sole-actor-crosswalk_LOCKED_v1.md
│   │   │   ├── SOURCEA_LIVE_FOUNDER_DECISION_FORM_FIRST_FORM_LOCKED_v1.md
│   │   │   ├── SOURCEA_LIVE_FOUNDER_DECISION_FORM_V2_ANSWERS_RECEIPT_2026-06-11_LOCKED_v1.md
│   │   │   └── wire-g3-tailscale-proof-check-note_LOCKED_v1.md
│   │   ├── 2026-06-12/
│   │   │   ├── AGENTIC_REFERENCE_PLATFORM_BLUEPRINT_v1.md
│   │   │   ├── AGENTIC_REFERENCE_PLATFORM_FOUNDER_STATEMENT_DRAFT_v1.md
│   │   │   ├── AGENTIC_REFERENCE_PLATFORM_ONE_PAGER_v1.md
│   │   │   ├── AGENTIC_REFERENCE_PLATFORM_SSOT_DRAFT_v1.md
│   │   │   ├── AGENTIC_REFERENCE_PLATFORM_VC_SIGNAL_CATALOG_v1.md
│   │   │   ├── AGENTIC_REFERENCE_PLATFORM_WHITE_PAPER_v1.md
│   │   │   ├── AGENTIC_W3_OUTREACH_WORKFLOW_SPEC_v1.md
│   │   │   ├── ASF_FORM_OFFICIAL_HUMAN_MACHINE_CONV_ORDER_2026-06-12_LOCKED_v1.md
│   │   │   ├── ASF_FORM_OFFICIAL_ORDER_RECEIPT_2026-06-12_LOCKED_v1.md
│   │   │   ├── BRAIN_GOVERNANCE_TRIAGE_AND_COPY_AUDIT_v1.md
│   │   │   ├── CANVAS_PER_CHAT_ROLLOUT_LOCKED_v1.md
│   │   │   ├── CROSS_CHAT_TRUTH_ALARM_FORM_OFFICIAL_2026-06-12_LOCKED_v1.md
│   │   │   ├── enf-0303-W1-film-take-1-package_LOCKED_v1.md
│   │   │   ├── enf-0303-W1-film-take-1-receipt-snapshot.json
│   │   │   ├── enf-0303-W1-film-take-1-witness-log.txt
│   │   │   ├── ENFORCEMENT_6MO_COMPLETE_INVENTORY_AND_VERDICT_v1.md
│   │   │   ├── MAINTAINER_1_INTEGRITY_PACK_5_CONTINUITY_BRIDGE_v1.md
│   │   │   ├── MAINTAINER_2_CROSS_CHAT_GOV_COMMERCIAL_INCIDENT_SYNTHESIS_LOCKED_v1.md
│   │   │   ├── SINA_13_LAYER_AGENTIC_DIRECTION_MAP_v1.md
│   │   │   ├── SINA_24_7_PARALLEL_ENGINE_FULL_MODE_DESIGN_PLAN_LOCKED_v1.md
│   │   │   ├── SINA_BRAIN_FULL_CHAT_UNIFIED_ANALYSIS_AND_CANVAS_PER_CHAT_ORDER_v1.md
│   │   │   ├── SINA_BRAIN_INCIDENTS_FULL_SUMMARY_LOCKED_v1.md
│   │   │   ├── SINA_BRAIN_SELF_ANALYSIS_ESSAY_2026-06-11_12_LOCKED_v1.md
│   │   │   ├── SINA__AND_REFERENCE_MATRIX_v1.yaml
│   │   │   ├── SINA_FULL_CORRECTIONS_AND_FINDINGS_DEEP_RESEARCH_v1.md
│   │   │   ├── SINA_JUDGE_STACK_DRAFT_v1.md
│   │   │   ├── SINA_JUDGE_STACK_LOCKED_v1.md
│   │   │   ├── SINA_ROOMS_UNIFIED_BLUEPRINT_DRAFT_v1.md
│   │   │   ├── SINA_THREAD_ROOM_DRAFT_v1.md
│   │   │   ├── SINA_THREAD_ROOM_LOCKED_v1.md
│   │   │   ├── SOURCEA_FOUNDER_DIRECTION_LOCK_RECEIPT_2026-06-12_LOCKED_v1.md
│   │   │   ├── SOURCEA_FOUNDER_LANGUAGE_CORPUS_PROMOTE_RECEIPT_2026-06-12_LOCKED_v1.md
│   │   │   ├── SOURCEA_GOV_PICK_BATCH_2026-06-12_LOCKED_v1.md
│   │   │   ├── SOURCEA_INTEGRITY_PICK_BATCH_2026-06-12_LOCKED_v1.md
│   │   │   ├── SOURCEA_JUDGE_STACK_DRAFT_FILE_RECEIPT_2026-06-12_LOCKED_v1.md
│   │   │   ├── SOURCEA_LIVE_FOUNDER_DECISION_FORM_SECOND_FORM_LOCKED_v1.md
│   │   │   ├── SOURCEA_PACK5_ROOMS_PICK_BATCH_2026-06-12_LOCKED_v1.md
│   │   │   ├── SOURCEA_PHASE3_INTEGRITY_PICK_3_07_RECEIPT_2026-06-12_LOCKED_v1.md
│   │   │   ├── SOURCEA_ROOMS_UNIFIED_BLUEPRINT_FILE_RECEIPT_2026-06-12_LOCKED_v1.md
│   │   │   ├── SOURCEA_SHIP_ORDER_9_07_RECEIPT_2026-06-12_LOCKED_v1.md
│   │   │   └── SOURCEA_WHERE_TO_READ_FAST_PATH_v1.md
│   │   ├── examples/
│   │   │   └── wtm/
│   │   │       └── CHATGPT_13STEP_WTM_REVIEW_EXAMPLE_LOCKED_v1.md
│   │   ├── founder-language/
│   │   │   ├── FOUNDER_LANGUAGE_CORPUS_v3/
│   │   │   │   ├── dictionary.yaml
│   │   │   │   ├── evolution-timeline.yaml
│   │   │   │   ├── five-step-phrases.yaml
│   │   │   │   ├── forbidden.yaml
│   │   │   │   ├── FOUNDER_LANGUAGE_CORPUS_v3.md
│   │   │   │   ├── FOUNDER_LANGUAGE_PACK_v2.md
│   │   │   │   ├── INDEX.yaml
│   │   │   │   ├── integrity-pack-words.yaml
│   │   │   │   ├── intent-needs-scored.yaml
│   │   │   │   ├── MANIFEST.yaml
│   │   │   │   ├── parallel-tracks.yaml
│   │   │   │   ├── phrase-corpus.yaml
│   │   │   │   ├── picks-locked.yaml
│   │   │   │   ├── README.md
│   │   │   │   └── required-labels.yaml
│   │   │   ├── dictionary.yaml
│   │   │   ├── evolution-timeline.yaml
│   │   │   ├── five-step-phrases.yaml
│   │   │   ├── forbidden.yaml
│   │   │   ├── FOUNDER_LANGUAGE_CORPUS_v3.md
│   │   │   ├── FOUNDER_LANGUAGE_PACK_v2.md
│   │   │   ├── INDEX.yaml
│   │   │   ├── integrity-pack-words.yaml
│   │   │   ├── intent-needs-scored.yaml
│   │   │   ├── linkedin-voice.yaml
│   │   │   ├── MANIFEST.yaml
│   │   │   ├── parallel-tracks.yaml
│   │   │   ├── phrase-corpus.yaml
│   │   │   ├── picks-locked.yaml
│   │   │   ├── README.md
│   │   │   └── required-labels.yaml
│   │   ├── worker-auto/
│   │   ├── worker-dual-40/
│   │   │   └── AUTO_DOC_TAG_STANDARD_2026-06-08.md
│   │   └── wtm/
│   │       ├── CLAUDE_ANALYST_PRE_LLM_GATE_HARDENING_ATTACHMENT_v1.md
│   │       ├── CLOUD_ANALYST_PRE_LLM_GATE_HARDENING_ATTACHMENT_v1.md
│   │       ├── CURSOR_AGENT_POST_CLAUDE_SYNTHESIS_ATTACHMENT_v1.md
│   │       ├── GOLDEN_PRE_LLM_GATE_RESEARCH_REPORT_v1.md
│   │       └── SINA_AGENT_LESSONS_PRE_LLM_GATE_v1.md
│   └── superseded/
│       [200+ files omitted]
├── ASF_DECISIONS/
│   └── 2026-05-27-M8-UNLOCK.md
├── brain-os/
│   ├── contract/
│   │   ├── ALL_FILES_MAPPING_CLAUDE_PRO_MAIN_GOALS_LOCKED_v1.md
│   │   ├── ALL_FILES_MAPPING_CLAUDE_PRO_PARALLEL_ONLY_LOCKED_v1.md
│   │   ├── ALL_FILES_MAPPING_CLAUDE_PRO_SECONDARY_LANES_LOCKED_v1.md
│   │   ├── ALL_FILES_MAPPING_FOR_CLAUDE_PRO_LOCKED_v1.md
│   │   ├── AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md
│   │   ├── BRAIN_COMPLETE_TRANSFER_LOCKED_v1.md
│   │   ├── BRAIN_CORE_EXECUTOR_LOCKED_v1.md
│   │   ├── BRAIN_E2E_EXECUTOR_PASTE_LOCKED_v1.md
│   │   ├── BRAIN_END_TURN_NO_LEFTOVER_PROMPT_LOCKED_v1.md
│   │   ├── BRAIN_FULL_TRANSFER_PROMPT_LOCKED_v1.md
│   │   ├── BRAIN_HEAL_PROMPT_LOCKED_v1.md
│   │   ├── CLAUDE_ADVISOR_PROJECT_INSTRUCTIONS_LOCKED_v1.md
│   │   ├── CLAUDE_PRO_BOOT_PROMPT_LOCKED_v1.md
│   │   ├── CLAUDE_PRO_FULL_PICTURE_GUIDE_LOCKED_v1.md
│   │   ├── DOC_TRACE_TAG_FORMAT_LOCKED_v1.md
│   │   ├── FOUNDER_ADVISOR_PROFILE_LOCKED_v1.md
│   │   ├── MANDATORY_BRAIN_CHAT_LOCKED_v1.md
│   │   ├── SOURCEA_EXTERNAL_ADVISOR_CONTRACT_LOCKED_v3.md
│   │   ├── TODAY_AUTORUN_50_PLAN_LOCKED_v1.md
│   │   └── WORKER_PROMPT_PACK_FORMAT_LOCKED_v1.md
│   ├── cursor/
│   │   └── rules/
│   │       ├── 000-brain-unified.mdc
│   │       ├── 000-entry-gate.mdc
│   │       ├── 000-workspace-lock.mdc
│   │       ├── 099-worker-inbox-active.mdc
│   │       ├── agent-loop.mdc
│   │       ├── agent-smart-judgment.mdc
│   │       ├── chatgpt-external-critic.mdc
│   │       ├── sina-command-readonly.mdc
│   │       └── sina-governance-entry.mdc
│   ├── demo/
│   │   ├── DEMO_BYPASS_AUDIT_v1.md
│   │   ├── ENFORCEMENT_30DAY_BACKLOG_v1.md
│   │   ├── ENFORCEMENT_ARTIFACTS_INDEX_v1.md
│   │   ├── governance_demo_intents_v1.json
│   │   ├── governance_demo_policy_v1.json
│   │   ├── INVESTOR_DEMO_RUNBOOK_v1.md
│   │   └── SOURCEA_FLEET_THREAD_ANALYSIS_MAP_LOCKED_v1.md
│   ├── enforcement/
│   │   ├── AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md
│   │   ├── BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md
│   │   ├── BRAIN_ENFORCEMENT_AUDIT_PROMPT_LOCKED_v1.md
│   │   ├── BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md
│   │   ├── ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md
│   │   ├── ENFORCEMENT_6MO_WEEKLY_OPERATING_PLAN_LOCKED_v1.md
│   │   ├── FOUNDER_LANE_SEPARATION_LOCKED_v1.md
│   │   ├── FOUNDER_SAVE_ONLY_TEMPLATE_v1.md
│   │   ├── GOAL1_BATCH_CHECKPOINT_LOCKED_v1.md
│   │   ├── GOAL1_EXECUTION_SOLUTION_LOCKED_v1.md
│   │   ├── GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md
│   │   ├── MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md
│   │   ├── ONE_SA_PER_TURN_MECHANICAL_LOCKED_v1.md
│   │   ├── REGISTRY_DRAIN_RAIL_LOCKED_v1.md
│   │   ├── SINA_BRAIN_INBOX_PROCESS_LOCKED_v1.md
│   │   ├── SINA_GOAL1_OPERATING_MODEL_LOCKED_v1.md
│   │   └── WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md
│   ├── entry/
│   │   ├── LAW_ROOT_INDEX_LOCKED_v1.md
│   │   ├── MANDATORY_READ_BY_ROLE_LOCKED_v1.md
│   │   └── START_HERE_LOCKED_v1.md
│   ├── incidents/
│   │   ├── AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md
│   │   ├── AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md
│   │   ├── CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md
│   │   ├── CURSOR_FIX_OVERNIGHT_ARCHIVED_2026-06-09.md
│   │   ├── INCIDENT_SUBJECT_INDEX_LOCKED_v1.md
│   │   ├── NEAR_MISS_AND_UNFILED_INCIDENTS_INDEX_LOCKED_v1.md
│   │   ├── SINA_AGENT_FOUNDER_BASH_COMMUNICATION_INCIDENT_019_LOCKED_v1.md
│   │   ├── SINA_AGENT_HUB_NAME_FRAGMENTATION_ADVISOR_TRACK_INCIDENT_025_LOCKED_v1.md
│   │   ├── SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_LOCKED_v1.md
│   │   ├── SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md
│   │   ├── SINA_AGENT_INCIDENT_WRONG_FOLDER_FILING_INCIDENT_021_LOCKED_v1.md
│   │   ├── SINA_AGENT_PLAN_TODO_GHOST_REACTIVATION_INCIDENT_016_LOCKED_v1.md
│   │   ├── SINA_AGENT_REWRITE_UNAUTHORIZED_DISK_EDIT_INCIDENT_REPORT_v1.md
│   │   ├── SINA_AGENT_TOPIC_CONFLATION_INCIDENT_020_LOCKED_v1.md
│   │   ├── SINA_ARCHIVE_015_CONDUCT_DRAFT_SUPERSEDED_LOCKED_v1.md
│   │   ├── SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_LOCKED_v1.md
│   │   ├── SINA_BRAIN_E2E_RETRY_STORM_INCIDENT_026_LOCKED_v1.md
│   │   ├── SINA_BRAIN_REPAIR_INCIDENT_014_COMPLETION_ADJUNCT_LOCKED_v1.md
│   │   ├── SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md
│   │   ├── SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md
│   │   ├── SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md
│   │   ├── SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM_LOCKED_v1.md
│   │   ├── SINA_EXECUTOR_IGNORED_M1_INTEGRITY_FORM_CANVAS_INCIDENT_029_LOCKED_v1.md
│   │   ├── SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_LOCKED_v1.md
│   │   ├── SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_REPORT_LOCKED_v1.md
│   │   ├── SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_LOCKED_v1.md
│   │   ├── SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md
│   │   ├── SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_LOCKED_v1.md
│   │   ├── SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md
│   │   ├── SINA_HEALTHY_QUEUE_PHASE_ORDER_DRIFT_INCIDENT_017_LOCKED_v1.md
│   │   ├── SINA_MAINTAINER_2_DRAIN_PROJECTION_STALENESS_INCIDENT_027_LOCKED_v1.md
│   │   ├── SINA_MAINTAINER_2_STALE_AUTORUN_ADVICE_INCIDENT_022_LOCKED_v1.md
│   │   ├── SINA_MAINTAINER_EXTERNAL_CRITIC_PROCEDURE_INCIDENT_LOCKED_v1.md
│   │   ├── SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_LOCKED_v1.md
│   │   ├── SINA_MONITOR_FOUNDER_SCROLL_RESPECT_INCIDENT_018_LOCKED_v1.md
│   │   ├── SINA_REGISTRY_BATCH_FAKE_PROGRESS_INCIDENT_LOCKED_v1.md
│   │   ├── SINA_STATIC_PROMPT_FEED_STALE_LIST_INCIDENT_024_LOCKED_v1.md
│   │   ├── SINA_WORKER_AUTORUN_STALL_AND_TIMING_INCIDENT_LOCKED_v1.md
│   │   ├── SINA_WORKER_SESSION_MISTAKES_CLOSEOUT_INCIDENT_LOCKED_v1.md
│   │   ├── SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_012_LOCKED_v1.md
│   │   ├── SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_LOCKED_v1.md
│   │   ├── SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_REPORT_INCIDENT_LOCKED_v1.md
│   │   ├── SINA_WORKER_STALE_PROMPT_FEED_AUTOSEND_INCIDENT_028_LOCKED_v1.md
│   │   └── SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md
│   ├── lanes/
│   │   ├── CURSOR_OS_PRO_TWO_CHAT_POLICY_LOCKED_v1.md
│   │   ├── GOAL_SPECIALIST_CHAT_PACK_LOCKED_v1.md
│   │   ├── MANDATORY_777_FOUNDATION_CHAT_LOCKED_v1.md
│   │   ├── MANDATORY_CHAT_HANDOFF_INDEX_LOCKED_v1.md
│   │   ├── MANDATORY_CURSOR_OS_PRO_CHAT_LOCKED_v1.md
│   │   ├── MANDATORY_DEVBRIDGE_WIRE_CHAT_LOCKED_v1.md
│   │   ├── MANDATORY_NOETFIELD_CHAT_LOCKED_v1.md
│   │   ├── MANDATORY_SINAAI_MONOREPO_CHAT_LOCKED_v1.md
│   │   ├── MANDATORY_SINAPROMPTOS_CHAT_LOCKED_v1.md
│   │   ├── MANDATORY_TRUSTFIELD_CHAT_LOCKED_v1.md
│   │   └── MANDATORY_VIRLUX_CHAT_LOCKED_v1.md
│   ├── law/
│   │   ├── AGENT_RULES_IN_CHARGE_LOCKED_v1.md
│   │   ├── BRAIN_RULE_COLLISION_MATRIX_LOCKED_v1.md
│   │   ├── BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md
│   │   ├── BRAIN_UNIFIED_RULES_LOCKED_v1.md
│   │   ├── CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md
│   │   ├── DISPATCH_POLICY_LOCKED_v1.md
│   │   ├── GOVERNANCE_RUNTIME_GOLDEN_RULE_LOCKED_v1.md
│   │   ├── GOVERNANCE_SELF_HEAL_G7_LOCKED_v1.md
│   │   └── SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md
│   ├── laws/
│   │   ├── ACTIVE_NOW_HEARTBEAT_LOCKED_v1.md
│   │   ├── APPLE_HEALTH_SLEEP_SIGNAL_LOCKED_v1.md
│   │   ├── AUTO_RUN_FULLY_AUTOMATIC_LOCKED_v1.md
│   │   ├── AUTO_RUN_WINDOW_PREFLIGHT_LOCKED_v1.md
│   │   ├── BRAIN_NO_LEFTOVER_PROCESS_LOCKED_v1.md
│   │   ├── BRAIN_SELF_HEAL_STARTUP_LOCKED_v1.md
│   │   ├── COST_SMART_ENGINE_SSOT_LOCKED_v1.md
│   │   ├── FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md
│   │   ├── FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1.md
│   │   ├── HUB_LAUNCHD_SUPERVISOR_LOCKED_v1.md
│   │   ├── MONITOR_HONESTY_LOCKED_v1.md
│   │   ├── NO_DUPLICATE_INJECT_LOCKED_v1.md
│   │   ├── PRE_SLEEP_TRANSITION_LOCKED_v1.md
│   │   ├── PROOF_VALIDATION_CHAIN_LOCKED_v1.md
│   │   ├── QUEUE_STATE_TRANSITION_LOCKED_v1.md
│   │   ├── SLEEP_MAC_CARETAKER_LOCKED_v1.md
│   │   ├── SOURCEA_EXECUTION_LAW_LOCKED_v1.md
│   │   ├── SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1.md
│   │   ├── THREE_LANE_ENGINE_MODEL_LOCKED_v1.md
│   │   ├── WORKER_CHAT_INJECT_LOCKED_v1.md
│   │   └── WORKER_CLIPBOARD_INJECT_LOCKED_v1.md
│   ├── memory/
│   │   ├── BRAIN_FOUNDER_INTENT_REGISTRY_LOCKED_v1.md
│   │   ├── BRAIN_FULL_SYSTEM_MAP_LOCKED_v1.md
│   │   ├── BRAIN_KNOWLEDGE_INDEX_LOCKED_v1.md
│   │   ├── BRAIN_MASTER_MEMORY_LOCKED_v1.md
│   │   └── BRAIN_RESEARCH_LIBRARY_LOCKED_v1.md
│   ├── narrative-bridge/
│   │   ├── LATEST_TOUCH_BASE_LOCKED_v1.md
│   │   └── NARRATIVE_BRIDGE_TOUCH_BASE_LOCKED_v1.md
│   ├── plan-registry/
│   │   ├── automation-converge-1000/
│   │   │   ├── prompts/
│   │   │   │   ├── phase-ac1-loop-a-headless/
│   │   │   │   │   …
│   │   │   │   ├── phase-ac10-l3-exit/
│   │   │   │   │   …
│   │   │   │   ├── phase-ac2-inject-activate/
│   │   │   │   │   …
│   │   │   │   ├── phase-ac3-l2-dispatch/
│   │   │   │   │   …
│   │   │   │   ├── phase-ac4-s1-drain-fast/
│   │   │   │   │   …
│   │   │   │   ├── phase-ac5-loop-b-promptos/
│   │   │   │   │   …
│   │   │   │   ├── phase-ac6-loop-c-hub/
│   │   │   │   │   …
│   │   │   │   ├── phase-ac7-spine-s4/
│   │   │   │   │   …
│   │   │   │   ├── phase-ac8-ship-revenue/
│   │   │   │   │   …
│   │   │   │   └── phase-ac9-enforce-min/
│   │   │   │       …
│   │   │   ├── REGISTRY.json
│   │   │   └── RETIRED_DUPLICATION.md
│   │   ├── automation-fast-track-100/
│   │   │   ├── prompts/
│   │   │   │   ├── phase-ft1-loop-a/
│   │   │   │   │   …
│   │   │   │   ├── phase-ft10-l3-exit/
│   │   │   │   │   …
│   │   │   │   ├── phase-ft2-activate-chain/
│   │   │   │   │   …
│   │   │   │   ├── phase-ft3-dispatch-l2/
│   │   │   │   │   …
│   │   │   │   ├── phase-ft4-s1-drain/
│   │   │   │   │   …
│   │   │   │   ├── phase-ft5-loop-b/
│   │   │   │   │   …
│   │   │   │   ├── phase-ft6-loop-c/
│   │   │   │   │   …
│   │   │   │   ├── phase-ft7-spine-min/
│   │   │   │   │   …
│   │   │   │   ├── phase-ft8-ship/
│   │   │   │   │   …
│   │   │   │   └── phase-ft9-enforce/
│   │   │   │       …
│   │   │   └── REGISTRY.json
│   │   ├── broker-pack-1000/
│   │   │   ├── prompts/
│   │   │   │   ├── phase-br1-worker-submit/
│   │   │   │   │   …
│   │   │   │   ├── phase-br10-broker-e2e/
│   │   │   │   │   …
│   │   │   │   ├── phase-br2-brain-poll/
│   │   │   │   │   …
│   │   │   │   ├── phase-br3-sa-alignment/
│   │   │   │   │   …
│   │   │   │   ├── phase-br4-orchestrator/
│   │   │   │   │   …
│   │   │   │   ├── phase-br5-batch-log/
│   │   │   │   │   …
│   │   │   │   ├── phase-br6-activation/
│   │   │   │   │   …
│   │   │   │   ├── phase-br7-checkpoint/
│   │   │   │   │   …
│   │   │   │   ├── phase-br8-inbox/
│   │   │   │   │   …
│   │   │   │   └── phase-br9-run-loop/
│   │   │   │       …
│   │   │   └── REGISTRY.json
│   │   ├── enforcement-1000/
│   │   │   ├── prompts/
│   │   │   │   ├── phase-e0-commit-gate/
│   │   │   │   │   …
│   │   │   │   ├── phase-e1-receipt-integrity/
│   │   │   │   │   …
│   │   │   │   ├── phase-e2-validator-tamper/
│   │   │   │   │   …
│   │   │   │   ├── phase-e3-demo-live/
│   │   │   │   │   …
│   │   │   │   ├── phase-e4-commercial-w3/
│   │   │   │   │   …
│   │   │   │   ├── phase-e5-bypass-chaos/
│   │   │   │   │   …
│   │   │   │   ├── phase-e6-investor-pipeline/
│   │   │   │   │   …
│   │   │   │   ├── phase-e7-regulated-wedge/
│   │   │   │   │   …
│   │   │   │   ├── phase-e8-kernel-harden/
│   │   │   │   │   …
│   │   │   │   └── phase-e9-dec-closeout/
│   │   │   │       …
│   │   │   ├── AUDIT_REPORT_v1.json
│   │   │   └── REGISTRY.json
│   │   ├── healthy-prompt-pack-v1/
│   │   │   ├── prompts/
│   │   │   │   ├── hp-001.md
│   │   │   │   ├── hp-002.md
│   │   │   │   ├── hp-003.md
│   │   │   │   ├── hp-004.md
│   │   │   │   ├── hp-005.md
│   │   │   │   ├── hp-006.md
│   │   │   │   ├── hp-007.md
│   │   │   │   ├── hp-008.md
│   │   │   │   ├── hp-009.md
│   │   │   │   ├── hp-010.md
│   │   │   │   ├── hp-011.md
│   │   │   │   ├── hp-012.md
│   │   │   │   ├── hp-013.md
│   │   │   │   ├── hp-014.md
│   │   │   │   ├── hp-015.md
│   │   │   │   ├── hp-016.md
│   │   │   │   ├── hp-017.md
│   │   │   │   ├── hp-018.md
│   │   │   │   ├── hp-019.md
│   │   │   │   ├── hp-020.md
│   │   │   │   ├── hp-021.md
│   │   │   │   ├── hp-022.md
│   │   │   │   ├── hp-023.md
│   │   │   │   ├── hp-024.md
│   │   │   │   ├── hp-025.md
│   │   │   │   ├── hp-026.md
│   │   │   │   ├── hp-027.md
│   │   │   │   ├── hp-028.md
│   │   │   │   ├── hp-029.md
│   │   │   │   ├── hp-030.md
│   │   │   │   ├── hp-031.md
│   │   │   │   ├── hp-032.md
│   │   │   │   ├── hp-033.md
│   │   │   │   ├── hp-034.md
│   │   │   │   ├── hp-035.md
│   │   │   │   ├── hp-036.md
│   │   │   │   ├── hp-037.md
│   │   │   │   ├── hp-038.md
│   │   │   │   ├── hp-039.md
│   │   │   │   ├── hp-040.md
│   │   │   │   ├── hp-041.md
│   │   │   │   ├── hp-042.md
│   │   │   │   ├── hp-043.md
│   │   │   │   ├── hp-044.md
│   │   │   │   ├── hp-045.md
│   │   │   │   ├── hp-046.md
│   │   │   │   ├── hp-047.md
│   │   │   │   ├── hp-048.md
│   │   │   │   ├── hp-049.md
│   │   │   │   ├── hp-050.md
│   │   │   │   ├── hp-051.md
│   │   │   │   ├── hp-052.md
│   │   │   │   ├── hp-053.md
│   │   │   │   ├── hp-054.md
│   │   │   │   ├── hp-055.md
│   │   │   │   └── … +45 more files
│   │   │   ├── healthy-prompt-catalog-100.json
│   │   │   └── queue-pack-30-active.json
│   │   ├── sourcea-1000/
│   │   │   ├── prompts/
│   │   │   │   ├── phase-s0-ssot-alignment/
│   │   │   │   │   …
│   │   │   │   ├── phase-s1-eval-dispatch/
│   │   │   │   │   …
│   │   │   │   ├── phase-s2-hub-build-ci/
│   │   │   │   │   …
│   │   │   │   ├── phase-s3-scoreboard-fleet/
│   │   │   │   │   …
│   │   │   │   ├── phase-s4-spine-loop/
│   │   │   │   │   …
│   │   │   │   ├── phase-s5-commercial-lanes/
│   │   │   │   │   …
│   │   │   │   ├── phase-s6-wtm-pre-llm/
│   │   │   │   │   …
│   │   │   │   ├── phase-s7-council-governance/
│   │   │   │   │   …
│   │   │   │   ├── phase-s8-hub-ui-ux/
│   │   │   │   │   …
│   │   │   │   ├── phase-s9-research-models/
│   │   │   │   │   …
│   │   │   │   ├── healthy-prompt-pack-100.json
│   │   │   │   ├── healthy-queue-30-active.json
│   │   │   │   ├── healthy-queue-30-active.PARALLEL_COMMERCIAL_QUARANTINED_v1.json
│   │   │   │   └── healthy-queue-state-v1.json
│   │   │   ├── .REGISTRY.json.truncated-backup
│   │   │   ├── HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md
│   │   │   ├── REGISTRY.json
│   │   │   ├── REGISTRY_DRAIN_PROCESS_LOCKED_v1.md
│   │   │   └── VALIDATION.md
│   │   ├── worker-dual-40/
│   │   │   ├── REGISTRY.json
│   │   │   └── WORKER1_UNIFIED_CLOSEOUT_LOCKED_v1.md
│   │   ├── AUTOMATION-CONVERGE-1000-LOCK.md
│   │   ├── AUTOMATION-FAST-TRACK-100-LOCK.md
│   │   ├── BROKER-PACK-1000-LOCK.md
│   │   ├── CANADA_AI_FOR_ALL_FUNDING_ALIGNMENT_v1.md
│   │   ├── ENFORCEMENT-1000-CATEGORY-INDEX.md
│   │   ├── ENFORCEMENT-1000-LOCK.md
│   │   ├── SOURCEA-1000-LOCK.md
│   │   ├── SOURCEA-PRIORITY.md
│   │   └── WORKER-DUAL-40-LOCK.md
│   ├── remediation/
│   │   ├── INCIDENT-005_FIX_BATCH_PENDING_ASF_CONFIRMATION_v1.md
│   │   └── INCIDENT-CIR-COSPRO-RESEARCH-SAVE-2026-06-07_v1.md
│   ├── runtime/
│   │   ├── E2E_EXECUTOR_CHECKLIST_LOCKED_v1.md
│   │   └── RECEIPTS_INDEX_LOCKED_v1.md
│   ├── scripts/
│   │   ├── brain-session-start.sh
│   │   ├── brain_enforcement_audit_v1.py
│   │   ├── brain_execute_turn_v1.py
│   │   ├── brain_gather_rules_v1.py
│   │   ├── brain_intent_gate_v1.py
│   │   ├── brain_lane_guard.py
│   │   ├── brain_narrate_loop_v1.py
│   │   ├── brain_os_paths.py
│   │   ├── brain_research_register.py
│   │   ├── brain_run_loop_trace_v1.py
│   │   ├── brain_run_loop_v1.py
│   │   ├── brain_timing_enforce_v1.py
│   │   ├── brain_validate_goal1_v1.py
│   │   ├── brain_watch_loop_v1.py
│   │   ├── cursor_entry_gate.py
│   │   ├── phase2-unify-brain-os-v1.py
│   │   ├── reorganize-brain-os-v1.py
│   │   ├── sync-brain-pack.sh
│   │   ├── validate-brain-disk-before-chat-v1.sh
│   │   ├── validate-brain-enforcement-audit-v1.sh
│   │   ├── validate-brain-narrate-loop-v1.sh
│   │   ├── validate-brain-narrate-not-execute-v1.sh
│   │   ├── validate-brain-os-complete-v1.sh
│   │   ├── validate-brain-rules-narrate-v1.sh
│   │   ├── validate-brain-run-loop-v1.sh
│   │   ├── validate-brain-unified-rules-v1.sh
│   │   └── validate-goal1-brain-validation-v1.sh
│   ├── system/
│   │   ├── AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md
│   │   ├── AGENT_ONBOARDING_PROMPTS_v1.md
│   │   ├── authority.yaml
│   │   ├── AUTHORITY_RUNTIME_VERIFICATION_LOCKED_v1.md
│   │   ├── ECOSYSTEM_BRAIN_ROLLOUT_LOCKED_v1.md
│   │   ├── ENTRY_POINTER_LOCKED_v1.md
│   │   ├── EVENT_CONTRACT.yaml
│   │   ├── EXECUTION_AUTHORITY_MAP_LOCKED_v1.md
│   │   ├── FILE_STORAGE_GOVERNANCE_LOCKED_v1.md
│   │   ├── FOUNDER_DAILY_OPERATING_MODEL_LOCKED_v1.md
│   │   ├── GOAL_EXECUTION_ACTIVE_LOCKED_v1.md
│   │   ├── GOAL_HIERARCHY_LOCKED_v1.md
│   │   ├── GOVERNANCE_P1_LOOPS_LOCKED_v1.md
│   │   ├── GOVERNED_EXECUTION_OS_MASTER_LOCKED_v1.md
│   │   ├── HUB_HOME_REDESIGN_SPEC_LOCKED_v1.md
│   │   ├── README_INDEX_LOCKED_v1.md
│   │   ├── SINAAIDB_ARCHIVE_RETIREMENT_HANDOFF_LOCKED_v1.md
│   │   ├── SOURCEA_FULL_LAYERED_CONTROL_PLAN_LOCKED_v1.md
│   │   ├── SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md
│   │   ├── UNIFIED_RESEARCH_ROOT_LOCKED_v1.md
│   │   ├── WORKER1_UNIFIED_CLOSEOUT_LOCKED_v1.md
│   │   └── WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md
│   ├── wtm/
│   │   ├── SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md
│   │   ├── SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md
│   │   ├── WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md
│   │   ├── WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md
│   │   ├── WORLD_TARGET_MODEL_FULL_BLUEPRINT_FOR_REVIEW_v1.md
│   │   ├── WORLD_TARGET_MODEL_FULL_BLUEPRINT_FOR_REVIEW_v2.md
│   │   ├── WORLD_TARGET_MODEL_MAP_LOCKED_v5.md
│   │   ├── WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md
│   │   ├── WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md
│   │   ├── WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md
│   │   ├── WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md
│   │   └── WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md
│   ├── EXECUTION_ENGINE_STRATEGY_LOCKED_v1.md
│   ├── FOLDER_MAP_LOCKED_v1.md
│   └── INDEX_LOCKED_v1.md
├── brand/
│   ├── icons/
│   │   ├── icns/
│   │   │   ├── manifest.json
│   │   │   ├── sina-apple-health.icns
│   │   │   ├── sina-apple-health.png
│   │   │   ├── sina-chat-unify.icns
│   │   │   ├── sina-chat-unify.png
│   │   │   ├── sina-command.icns
│   │   │   ├── sina-command.png
│   │   │   ├── sina-decide.icns
│   │   │   ├── sina-decide.png
│   │   │   ├── sina-dispatch.icns
│   │   │   ├── sina-dispatch.png
│   │   │   ├── sina-execute.icns
│   │   │   ├── sina-execute.png
│   │   │   ├── sina-mac-health.icns
│   │   │   ├── sina-mac-health.png
│   │   │   ├── sina-promptos.icns
│   │   │   ├── sina-promptos.png
│   │   │   ├── sina-run.icns
│   │   │   ├── sina-run.png
│   │   │   ├── sina-status.icns
│   │   │   └── sina-status.png
│   │   ├── iconset/
│   │   │   ├── sina-apple-health.iconset/
│   │   │   │   ├── icon_1024x1024.png
│   │   │   │   ├── icon_128x128.png
│   │   │   │   ├── icon_128x128@2x.png
│   │   │   │   ├── icon_16x16.png
│   │   │   │   ├── icon_16x16@2x.png
│   │   │   │   ├── icon_256x256.png
│   │   │   │   ├── icon_256x256@2x.png
│   │   │   │   ├── icon_32x32.png
│   │   │   │   ├── icon_32x32@2x.png
│   │   │   │   ├── icon_512x512.png
│   │   │   │   ├── icon_512x512@2x.png
│   │   │   │   ├── icon_64x64.png
│   │   │   │   └── icon_64x64@2x.png
│   │   │   ├── sina-chat-unify.iconset/
│   │   │   │   ├── icon_1024x1024.png
│   │   │   │   ├── icon_128x128.png
│   │   │   │   ├── icon_128x128@2x.png
│   │   │   │   ├── icon_16x16.png
│   │   │   │   ├── icon_16x16@2x.png
│   │   │   │   ├── icon_256x256.png
│   │   │   │   ├── icon_256x256@2x.png
│   │   │   │   ├── icon_32x32.png
│   │   │   │   ├── icon_32x32@2x.png
│   │   │   │   ├── icon_512x512.png
│   │   │   │   ├── icon_512x512@2x.png
│   │   │   │   ├── icon_64x64.png
│   │   │   │   └── icon_64x64@2x.png
│   │   │   ├── sina-command.iconset/
│   │   │   │   ├── icon_1024x1024.png
│   │   │   │   ├── icon_128x128.png
│   │   │   │   ├── icon_128x128@2x.png
│   │   │   │   ├── icon_16x16.png
│   │   │   │   ├── icon_16x16@2x.png
│   │   │   │   ├── icon_256x256.png
│   │   │   │   ├── icon_256x256@2x.png
│   │   │   │   ├── icon_32x32.png
│   │   │   │   ├── icon_32x32@2x.png
│   │   │   │   ├── icon_512x512.png
│   │   │   │   ├── icon_512x512@2x.png
│   │   │   │   ├── icon_64x64.png
│   │   │   │   └── icon_64x64@2x.png
│   │   │   ├── sina-decide.iconset/
│   │   │   │   ├── icon_1024x1024.png
│   │   │   │   ├── icon_128x128.png
│   │   │   │   ├── icon_128x128@2x.png
│   │   │   │   ├── icon_16x16.png
│   │   │   │   ├── icon_16x16@2x.png
│   │   │   │   ├── icon_256x256.png
│   │   │   │   ├── icon_256x256@2x.png
│   │   │   │   ├── icon_32x32.png
│   │   │   │   ├── icon_32x32@2x.png
│   │   │   │   ├── icon_512x512.png
│   │   │   │   ├── icon_512x512@2x.png
│   │   │   │   ├── icon_64x64.png
│   │   │   │   └── icon_64x64@2x.png
│   │   │   ├── sina-dispatch.iconset/
│   │   │   │   ├── icon_1024x1024.png
│   │   │   │   ├── icon_128x128.png
│   │   │   │   ├── icon_128x128@2x.png
│   │   │   │   ├── icon_16x16.png
│   │   │   │   ├── icon_16x16@2x.png
│   │   │   │   ├── icon_256x256.png
│   │   │   │   ├── icon_256x256@2x.png
│   │   │   │   ├── icon_32x32.png
│   │   │   │   ├── icon_32x32@2x.png
│   │   │   │   ├── icon_512x512.png
│   │   │   │   ├── icon_512x512@2x.png
│   │   │   │   ├── icon_64x64.png
│   │   │   │   └── icon_64x64@2x.png
│   │   │   ├── sina-execute.iconset/
│   │   │   │   ├── icon_1024x1024.png
│   │   │   │   ├── icon_128x128.png
│   │   │   │   ├── icon_128x128@2x.png
│   │   │   │   ├── icon_16x16.png
│   │   │   │   ├── icon_16x16@2x.png
│   │   │   │   ├── icon_256x256.png
│   │   │   │   ├── icon_256x256@2x.png
│   │   │   │   ├── icon_32x32.png
│   │   │   │   ├── icon_32x32@2x.png
│   │   │   │   ├── icon_512x512.png
│   │   │   │   ├── icon_512x512@2x.png
│   │   │   │   ├── icon_64x64.png
│   │   │   │   └── icon_64x64@2x.png
│   │   │   ├── sina-mac-health.iconset/
│   │   │   │   ├── icon_1024x1024.png
│   │   │   │   ├── icon_128x128.png
│   │   │   │   ├── icon_128x128@2x.png
│   │   │   │   ├── icon_16x16.png
│   │   │   │   ├── icon_16x16@2x.png
│   │   │   │   ├── icon_256x256.png
│   │   │   │   ├── icon_256x256@2x.png
│   │   │   │   ├── icon_32x32.png
│   │   │   │   ├── icon_32x32@2x.png
│   │   │   │   ├── icon_512x512.png
│   │   │   │   ├── icon_512x512@2x.png
│   │   │   │   ├── icon_64x64.png
│   │   │   │   └── icon_64x64@2x.png
│   │   │   ├── sina-promptos.iconset/
│   │   │   │   ├── icon_1024x1024.png
│   │   │   │   ├── icon_128x128.png
│   │   │   │   ├── icon_128x128@2x.png
│   │   │   │   ├── icon_16x16.png
│   │   │   │   ├── icon_16x16@2x.png
│   │   │   │   ├── icon_256x256.png
│   │   │   │   ├── icon_256x256@2x.png
│   │   │   │   ├── icon_32x32.png
│   │   │   │   ├── icon_32x32@2x.png
│   │   │   │   ├── icon_512x512.png
│   │   │   │   ├── icon_512x512@2x.png
│   │   │   │   ├── icon_64x64.png
│   │   │   │   └── icon_64x64@2x.png
│   │   │   ├── sina-run.iconset/
│   │   │   │   ├── icon_1024x1024.png
│   │   │   │   ├── icon_128x128.png
│   │   │   │   ├── icon_128x128@2x.png
│   │   │   │   ├── icon_16x16.png
│   │   │   │   ├── icon_16x16@2x.png
│   │   │   │   ├── icon_256x256.png
│   │   │   │   ├── icon_256x256@2x.png
│   │   │   │   ├── icon_32x32.png
│   │   │   │   ├── icon_32x32@2x.png
│   │   │   │   ├── icon_512x512.png
│   │   │   │   ├── icon_512x512@2x.png
│   │   │   │   ├── icon_64x64.png
│   │   │   │   └── icon_64x64@2x.png
│   │   │   └── sina-status.iconset/
│   │   │       ├── icon_1024x1024.png
│   │   │       ├── icon_128x128.png
│   │   │       ├── icon_128x128@2x.png
│   │   │       ├── icon_16x16.png
│   │   │       ├── icon_16x16@2x.png
│   │   │       ├── icon_256x256.png
│   │   │       ├── icon_256x256@2x.png
│   │   │       ├── icon_32x32.png
│   │   │       ├── icon_32x32@2x.png
│   │   │       ├── icon_512x512.png
│   │   │       ├── icon_512x512@2x.png
│   │   │       ├── icon_64x64.png
│   │   │       └── icon_64x64@2x.png
│   │   └── source/
│   │       ├── sina-command.png
│   │       └── sina-promptos.png
│   └── macos-apps/
│       ├── Apple Health.app/
│       │   └── Contents/
│       │       ├── MacOS/
│       │       │   …
│       │       ├── Resources/
│       │       │   …
│       │       └── Info.plist
│       ├── Chat Unify.app/
│       │   └── Contents/
│       │       ├── MacOS/
│       │       │   …
│       │       ├── Resources/
│       │       │   …
│       │       └── Info.plist
│       ├── Mac Health Guard.app/
│       │   └── Contents/
│       │       ├── MacOS/
│       │       │   …
│       │       ├── Resources/
│       │       │   …
│       │       └── Info.plist
│       ├── Sina Command Apps.app/
│       │   └── Contents/
│       │       ├── MacOS/
│       │       │   …
│       │       ├── Resources/
│       │       │   …
│       │       └── Info.plist
│       ├── Sina Command.app/
│       │   └── Contents/
│       │       ├── MacOS/
│       │       │   …
│       │       ├── Resources/
│       │       │   …
│       │       └── Info.plist
│       ├── Sina Decide.app/
│       │   └── Contents/
│       │       ├── MacOS/
│       │       │   …
│       │       ├── Resources/
│       │       │   …
│       │       └── Info.plist
│       ├── Sina Dispatch.app/
│       │   └── Contents/
│       │       ├── MacOS/
│       │       │   …
│       │       ├── Resources/
│       │       │   …
│       │       └── Info.plist
│       ├── Sina Execute All.app/
│       │   └── Contents/
│       │       ├── MacOS/
│       │       │   …
│       │       ├── Resources/
│       │       │   …
│       │       └── Info.plist
│       ├── Sina Prompt OS.app/
│       │   └── Contents/
│       │       ├── MacOS/
│       │       │   …
│       │       ├── Resources/
│       │       │   …
│       │       └── Info.plist
│       ├── Sina Run Now.app/
│       │   └── Contents/
│       │       ├── MacOS/
│       │       │   …
│       │       ├── Resources/
│       │       │   …
│       │       └── Info.plist
│       └── Sina Status.app/
│           └── Contents/
│               ├── MacOS/
│               │   …
│               ├── Resources/
│               │   …
│               └── Info.plist
├── data/
│   └── agent_fleet/
│       ├── .gitkeep
│       └── AGENT_FLEET_REGISTRY.json
├── demo/
│   └── enforcement/
│       ├── intent-allow.json
│       └── intent-deny.json
├── docs/
│   ├── research-vault/
│   │   └── GOLDEN_REPORT_SOURCEA_SITE_POSITIONING_v1.md
│   ├── strategy/
│   ├── stress-test-layers-v1/
│   │   ├── SOURCEA_LAYERED_ADVISORY_13_LAYERS_v1.md
│   │   ├── STRESS_TEST_LAYER_1_ASF_DISK_GATE_v1.md
│   │   ├── STRESS_TEST_LAYER_2_THREAD_VERB_SCOPE_v1.md
│   │   └── STRESS_TEST_LAYER_3_GOAL_HIERARCHY_v1.md
│   ├── system-audits/
│   │   ├── ARCHITECTURE_SYNTHESIS_2026-06-06.md
│   │   ├── E2E_LIVE_AUDIT_2026-06-06.md
│   │   ├── FOUNDER_SUPPORT_PACK_2026-06-06.md
│   │   ├── GOVERNANCE_RULE_BREAKING_2026-06-06.md
│   │   ├── MASTER_SYSTEM_AUDIT_2026-06-06.md
│   │   ├── OLD_BRAIN_EXTRACTION_FULL_2026-06-06.yaml
│   │   ├── PRE_LLM_AND_WTM_EVIDENCE_2026-06-06.md
│   │   ├── PROMPT_OS_TWO_LAYER_MODEL_2026-06-06.md
│   │   ├── README_INDEX.md
│   │   ├── REPO_INVENTORY_2026-06-06.md
│   │   └── SYSTEM_SUMMARY_2026-06-06.md
│   ├── ARCHITECTURE.md
│   ├── DISPATCH_POLICY_INTERFACE_ERRATA_v1.md
│   ├── ENFORCEMENT-6MO-DEMO-SCRIPT_v1.md
│   ├── HUB_LIVE_SYSTEM_DESIGN_v1.md
│   ├── HUB_STATE_API_CONTRACT_v1.md
│   ├── HUB_UI_IA_UPGRADE_PROPOSAL_v3.md
│   ├── HUB_UI_NEXT_v4.md
│   ├── HUB_UNIFY_AND_PROOF_MASTER_v1.md
│   ├── HUB_UNIFY_RESEARCH_PROPOSAL_v2.md
│   ├── HUB_UNIFY_UPGRADE_PROPOSAL_v1.md
│   ├── ONBOARDING.md
│   └── RUNBOOK.md
├── EMERGENCY_STOP.app/
│   └── Contents/
│       ├── MacOS/
│       │   └── emergency-stop
│       ├── Resources/
│       └── Info.plist
├── entry/
│   ├── MOVED.md
│   └── README.md
├── founder/
│   ├── repo-agent-notices/
│   │   ├── AGENT_READ_LINKS_INDEX.md
│   │   ├── manifest.json
│   │   ├── README.md
│   │   ├── REPO_NOTICE_hq_v1.md
│   │   ├── REPO_NOTICE_mono_v1.md
│   │   ├── REPO_NOTICE_noetfield_v1.md
│   │   ├── REPO_NOTICE_seven77_v1.md
│   │   ├── REPO_NOTICE_trustfield_v1.md
│   │   ├── REPO_NOTICE_virlux_v1.md
│   │   ├── SEMI_NOTICE_cursor_os_pro_v1.md
│   │   ├── SEMI_NOTICE_mergepack_v1.md
│   │   ├── SEMI_NOTICE_noetfield_cloud_v1.md
│   │   ├── SEMI_NOTICE_promptos_v1.md
│   │   └── SEMI_NOTICE_wire_v1.md
│   ├── ASF_CURSOR_AND_M8.md
│   ├── ASF_DAILY_CARD.md
│   ├── ASF_FOUNDER_FAQ.md
│   ├── ASF_REPOS_AND_LANES.md
│   ├── ASF_SECRETS_AND_INFRA.md
│   ├── ASF_TWO_CHATS.md
│   ├── ASF_WEEKLY_SUNDAY.md
│   ├── ASF_WIRE_AND_PHONE.md
│   ├── NOETFIELD_CLOUD_FINAL_ACKNOWLEDGE_PROMPT_v1.md
│   └── README.md
├── founder-light-v1/
│   ├── public/
│   │   ├── app.js
│   │   ├── index.html
│   │   └── style.css
│   ├── scripts/
│   │   ├── founder_light_server_v1.py
│   │   └── run-founder-light-v1.sh
│   └── README.md
├── imports/
│   └── iphone-cloud/
│       ├── 777-consolidate-report.json
│       ├── iphone-cloud-inventory-20260604.csv
│       ├── iphone-cloud-manifest-20260604.jsonl
│       └── iphone-cloud-move-report.txt
├── internal/
│   └── agent-reference/
│       └── GOVERNANCE_DRIFT_DETECTION_ESSAY_2026.md
├── internal-reference/
│   └── GOVERNANCE_DRIFT_DETECTION_INSIGHT_ESSAY_v1.md
├── investor/
│   ├── _build_pdfs.py
│   ├── ADVISOR_SUMMARY_EN.md
│   ├── ADVISOR_SUMMARY_FA.md
│   ├── AGENTIC_INFRA_FUNDRAISE_PORTFOLIO_STRATEGY_v1.md
│   ├── CONNECTOR_BRIEF.md
│   ├── CONNECTOR_BRIEF.pdf
│   ├── CURRENT_SITUATION.md
│   ├── DEMO_SCRIPT.md
│   ├── ENFORCEMENT_3SLIDE_DECK_v1.md
│   ├── ENFORCEMENT_DEMO_5MIN.md
│   ├── ENFORCEMENT_OUTREACH_v1.md
│   ├── FAQ_INVESTORS.md
│   ├── ONE_PAGER.md
│   ├── PITCH_DECK.md
│   ├── PITCH_DECK_SPEAKER_SCRIPT_EN.md
│   ├── PITCH_DECK_SPEAKER_SCRIPT_FA.md
│   ├── README.md
│   ├── ROADMAP.md
│   ├── SEPARATE_PROGRAM_CURSOR_OS_PRO.md
│   ├── SYSTEM_OVERVIEW.md
│   ├── TRUSTFIELD_VC_TRUST_LEGAL_ANTI_MORTEM_v1.md
│   └── WHITEPAPER.md
├── knowledge-library/
│   ├── fields/
│   │   ├── agent-training-roles/
│   │   │   └── FIELD_INDEX.md
│   │   ├── context-engineering/
│   │   │   └── FIELD_INDEX.md
│   │   ├── execution-spine/
│   │   │   └── FIELD_INDEX.md
│   │   ├── governance-unification/
│   │   │   ├── 02-gathered/
│   │   │   │   └── GATHER_v1_GOLDEN_SITE_POSITIONING_2026-06-09.md
│   │   │   └── FIELD_INDEX.md
│   │   ├── hub-ux-quality/
│   │   │   └── 02-gathered/
│   │   │       └── GATHER_v1_DASHBOARD_UX_RESEARCH_2026-06-10.md
│   │   └── pre-llm-world-model/
│   │       ├── 01-extracts/
│   │       │   └── MANIFEST.md
│   │       ├── 02-gathered/
│   │       │   ├── GATHER_v1_GATE_RESEARCH.md
│   │       │   └── GATHER_v2_INDUSTRY_GATE_SYNTHESIS.md
│   │       ├── 03-merged/
│   │       │   └── MERGE_v1_PRE_LLM_GATE_SYNTHESIS.md
│   │       ├── 04-unified/
│   │       │   ├── ESSAY_v1_NO_MODEL_WITHOUT_PACKET.md
│   │       │   └── SHIP_PLAN_D5_AND_GATE_v1.md
│   │       ├── 05-books/
│   │       │   └── BOOK_OUTLINE_v1.md
│   │       └── FIELD_INDEX.md
│   ├── KNOWLEDGE_LIBRARY_INDEX.md
│   └── PIPELINE_LAW.md
├── launch/
│   ├── com.sourcea.autorun-worker.plist
│   └── com.sourcea.hub.plist
├── n8n/
│   └── workflows/
│       ├── wf-form-change-cascade.stub.json
│       └── wf-health-sweep-15m.stub.json
├── os/
│   ├── chat-handoffs/
│   │   ├── BRAIN_COMPLETE_TRANSFER_LOCKED_v1.md
│   │   ├── BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md
│   │   ├── BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md
│   │   ├── BRAIN_UNIFIED_RULES_LOCKED_v1.md
│   │   ├── GOAL1_BATCH_CHECKPOINT_LOCKED_v1.md
│   │   ├── GOAL1_EXECUTION_SOLUTION_LOCKED_v1.md
│   │   ├── GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md
│   │   ├── MANDATORY_BRAIN_CHAT_LOCKED_v1.md
│   │   ├── MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md
│   │   ├── ONE_SA_PER_TURN_MECHANICAL_LOCKED_v1.md
│   │   └── README_INDEX_LOCKED_v1.md
│   ├── plan-library/
│   │   ├── sourcea-1000/
│   │   │   ├── prompts/
│   │   │   │   ├── phase-s0-ssot-alignment/
│   │   │   │   │   …
│   │   │   │   ├── phase-s1-eval-dispatch/
│   │   │   │   │   …
│   │   │   │   ├── phase-s2-hub-build-ci/
│   │   │   │   │   …
│   │   │   │   ├── phase-s3-scoreboard-fleet/
│   │   │   │   │   …
│   │   │   │   ├── phase-s4-spine-loop/
│   │   │   │   │   …
│   │   │   │   ├── phase-s5-commercial-lanes/
│   │   │   │   │   …
│   │   │   │   ├── phase-s6-wtm-pre-llm/
│   │   │   │   │   …
│   │   │   │   ├── phase-s7-council-governance/
│   │   │   │   │   …
│   │   │   │   ├── phase-s8-hub-ui-ux/
│   │   │   │   │   …
│   │   │   │   ├── phase-s9-research-models/
│   │   │   │   │   …
│   │   │   │   ├── healthy-prompt-pack-100.json
│   │   │   │   ├── healthy-queue-30-active.json
│   │   │   │   ├── healthy-queue-30-active.PARALLEL_COMMERCIAL_QUARANTINED_v1.json
│   │   │   │   └── healthy-queue-state-v1.json
│   │   │   ├── .REGISTRY.json.truncated-backup
│   │   │   ├── HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md
│   │   │   ├── REGISTRY.json
│   │   │   ├── REGISTRY_DRAIN_PROCESS_LOCKED_v1.md
│   │   │   └── VALIDATION.md
│   │   ├── ENFORCEMENT-6MO-MASTER-PROMPT_LOCKED_v1.md
│   │   ├── MOVED.md
│   │   ├── NORTH-STAR-GOV-KERNEL-INVARIANT-OS.md
│   │   └── SOURCEA-PRIORITY.md
│   ├── MOVED.md
│   └── README_LOCKED_v1.md
├── product/
│   ├── ACQUISITION_STACK_LOCKED_v1.md
│   ├── EVIDENCE_FLYWHEEL_LOCKED_v1.md
│   ├── MERGEPACK_10K_7DAY_LOCKED_v1.md
│   ├── MERGEPACK_BUSINESS_DEFENSE_MEMO.md
│   ├── MERGEPACK_LOCKED_v1.md
│   ├── MERGEPACK_POST_MOAT_PATH_A_LOCKED_v1.md
│   ├── MERGEPACK_SEO_10K_LOCKED_v1.md
│   ├── MERGEPACK_SUITE_LOCKED_v1.md
│   ├── PARTICIPATION_HOOKS_LOCKED_v1.md
│   ├── PHASE1_MARKET_RESEARCH_2026.md
│   ├── PHASE1_OPPORTUNITIES_AND_30_RAW_IDEAS.md
│   ├── PHASE2_3_EVALUATION_AND_WINNER.md
│   ├── PRODUCT_FACTORY_RESCORE_NO_ADS_LOCKED_v1.md
│   ├── README.md
│   ├── RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md
│   └── SINA_AUDIENCE_HUB_FREE_TIER_SPEC.md
├── prompts/
│   ├── COMPLEX_SITUATION_FORK_SESSION_PROMPT_LOCKED_v1.md
│   ├── ENFORCEMENT_6MO_MASTER_CONTROL_PROMPT_v1.md
│   └── FIVE_STEP_SESSION_PROMPT_LOCKED_v1.md
├── receipts/
│   [800+ files omitted]
├── REPO_EXECUTION_LOGS/
│   ├── noetfield/
│   │   ├── 2026-06-02T1026_extract-top-5-mvp-requirements-from-existing-noe.yaml
│   │   ├── 2026-06-02T1200_nf-0101-implement-drift-contract-v0-fields-on-tl.yaml
│   │   ├── 2026-06-02T1200_nf-0202-harden-evidence-hash-on-ingest-in-connec.yaml
│   │   ├── 2026-06-02T1430_nf-0203-fix-workspace-connectors-oauth-redirect.yaml
│   │   ├── 2026-06-02T1500_nf-0204-add-verify-ui-e2e-check-for-connectors-p.yaml
│   │   ├── 2026-06-02T1600_nf-0205-document-3-evidence-types-in-copilot-dem.yaml
│   │   ├── 2026-06-02T1700_nf-0206-extend-seed-m365-evidence-stub-sh-idempo.yaml
│   │   ├── 2026-06-02T1800_nf-0207-validate-evidence-index-api-returns-tena.yaml
│   │   ├── 2026-06-02T1900_nf-0208-add-pytest-for-connector-connected-state.yaml
│   │   ├── 2026-06-02T2030_nf-0209-improve-connector-error-message-for-miss.yaml
│   │   ├── 2026-06-02T2200_plan-for-all-push-bank-grade-pr-handoff-nf-0210.yaml
│   │   ├── 2026-06-03T0915_fix-everything-tle-v1-2-stack-missing-reported-a.yaml
│   │   ├── 2026-06-04T0016_draft-tenant-append-only-audit-schema-outline-ma.yaml
│   │   ├── 2026-06-04T0027_draft-tenant-append-only-audit-schema-outline-ma.yaml
│   │   ├── 2026-06-04T0028_draft-tenant-append-only-audit-schema-outline-ma.yaml
│   │   ├── 2026-06-04T1230_wave-028-033-verify-pdf-oauth-json-fixes.yaml
│   │   ├── 2026-06-04T1731_trust-ledger-next-wave-closeout-pilot-e2e-pdf-ex.yaml
│   │   ├── 2026-06-04T1827_next-wave-agent-closeout-re-verify-023-027-verif.yaml
│   │   ├── 2026-06-04T1845_wave-028-033-m365-e2e-ingest-pdf-v2-rbac-chain-k.yaml
│   │   ├── 2026-06-05T1245_full-ui-e2e-audit-and-fixes.yaml
│   │   ├── 2026-06-05T1304_wave-034-036-gtm-tier-a-procurement-zip-demo-pag.yaml
│   │   ├── 2026-06-05T1307_wave-037-039-gtm-demo-polish-buyer-pack-workspac.yaml
│   │   ├── 2026-06-05T1309_wave-040-042-customer-acquisition-design-partner.yaml
│   │   ├── 2026-06-06T0030_wave-034-036-gtm-tier-a-procurement-zip-demo-pag.yaml
│   │   ├── 2026-06-06T0312_plan-with-no-asf-nf-0001-session-start-self-audi.yaml
│   │   ├── 2026-06-06T0315_noetfield-1000-locked-prompt-library-plan-with-n.yaml
│   │   ├── 2026-06-06T0315_plan-with-no-asf-nf-0003-add-agent-tag-to-report.yaml
│   │   ├── 2026-06-06T0421_draft-tenant-append-only-audit-schema-outline-ma.yaml
│   │   ├── 2026-06-06T0437_draft-tenant-append-only-audit-schema-outline-ma.yaml
│   │   ├── 2026-06-06T1200_plan-with-no-asf-nf-0001-session-start-self-audi.yaml
│   │   ├── 2026-06-07T1351_plan-with-no-asf-nf-0004-run-ingest-cursor-reply.yaml
│   │   ├── 2026-06-10T0059_phase-0-ship-ops-plan-nf-0001-through-nf-0100-co.yaml
│   │   ├── 2026-06-10T0250_nf-0102-add-evaluate-vs-last-tle-diff-helper-end.yaml
│   │   ├── 2026-06-10T1200_nf-0103-add-risk-summary-to-confidence-factors-i.yaml
│   │   ├── 2026-06-10T1400_phase-1-tle-core-complete-nf-0101-0200-t0-t3.yaml
│   │   ├── 2026-06-12T1659_draft-tenant-append-only-audit-schema-outline-ma.yaml
│   │   └── latest.yaml
│   ├── seven77/
│   │   ├── 2026-06-02T0055_review-docs-c1-ops-close-md-open-items-and-close.yaml
│   │   └── latest.yaml
│   ├── sinaai_mono/
│   │   ├── 2026-06-02T1035_declare-one-canonical-telegram-integration-path.yaml
│   │   ├── 2026-06-02T1056_create-committed-process-map-doc-8000-active-801.yaml
│   │   ├── 2026-06-03T0847_wire-human-approval-gate-test-on-sinaaiosbot-tel.yaml
│   │   ├── 2026-06-03T0930_wire-human-approval-gate-test-on-sinaaiosbot-tel.yaml
│   │   ├── 2026-06-04T1725_command-center-alignment-layer-a-p0-phase-0-veri.yaml
│   │   ├── 2026-06-04T1731_re-verify-command-center-alignment-verify-only.yaml
│   │   ├── 2026-06-04T1844_re-verify-command-center-alignment-verify-only.yaml
│   │   ├── 2026-06-04T1900_full-e2e-telegram-no-reply-fix-stack-verify.yaml
│   │   ├── 2026-06-04T1915_telegram-heavy-ux-menu-keyboards-no-start-requir.yaml
│   │   ├── 2026-06-05T1200_monorepo-no-asf-autonomous-plan-stack-verify-doc.yaml
│   │   ├── 2026-06-05T1400_sprint-2-demo-surface-consolidation-no-asf.yaml
│   │   ├── 2026-06-05T1600_sprint-3-stack-consolidation-spine-8000-no-asf.yaml
│   │   ├── 2026-06-05T1800_agent-auto-mono-2026-06-05-self-audit-loop-memo.yaml
│   │   ├── 2026-06-05T2000_mono-no-asf-autonomous-plan-stack-verify-docs-dr.yaml
│   │   ├── 2026-06-06T0030_agent-auto-mono-2026-06-06-mono-1000-locked-pro.yaml
│   │   ├── 2026-06-06T0100_plan-with-no-asf-mx-0001-full-e2e-mono-verify-ga.yaml
│   │   ├── 2026-06-06T0200_plan-with-no-asf-mx-0002-agent-auto-audit-full-e.yaml
│   │   ├── 2026-06-06T1200_plan-with-no-asf-mx-0003-check-stack-full-e2e-ve.yaml
│   │   ├── 2026-06-06T1230_plan-with-no-asf-mx-0004-validate-sina-registry.yaml
│   │   ├── 2026-06-06T1300_plan-with-no-asf-mx-0005-validate-mono-1000-pack.yaml
│   │   ├── 2026-06-06T1400_plan-with-no-asf-mx-0006-never-silent-gemini-pop.yaml
│   │   ├── 2026-06-08T0028_plan-with-no-asf-mx-0002-agent-auto-audit-full-e.yaml
│   │   ├── 2026-06-10T0325_five-item-governance-batch-mx-0007-incidents-mem.yaml
│   │   ├── 2026-06-10T0405_plan-with-no-asf-mx-0008-telegram-polling-full-e.yaml
│   │   ├── 2026-06-10T0454_plan-with-no-asf-mx-0009-telegram-inprocess-smok.yaml
│   │   ├── 2026-06-10T0501_plan-with-no-asf-mx-0010-demo-surface-full-e2e-v.yaml
│   │   ├── 2026-06-10T0514_plan-with-no-asf-mx-0011-stack-consolidation-ful.yaml
│   │   ├── 2026-06-10T0521_plan-with-no-asf-mx-0012-approval-gate-full-e2e.yaml
│   │   ├── 2026-06-10T0535_plan-with-no-asf-mx-0013-configure-telegram-ui-f.yaml
│   │   ├── 2026-06-11T1241_plan-with-no-asf-mx-0014-telegram-expect-usernam.yaml
│   │   ├── 2026-06-11T1254_plan-with-no-asf-mx-0016-verify-flake-incident.yaml
│   │   ├── 2026-06-11T1305_plan-with-no-asf-mx-0015-verify-output-guide.yaml
│   │   ├── 2026-06-11T1315_agent-auto-mono-category-index-filing-update.yaml
│   │   └── latest.yaml
│   ├── sourcea/
│   │   ├── QUARANTINE_BATCH_YAML/
│   │   │   ├── 2026-06-06T0335_sourcea-1000-locked-pack-plan-with-no-asf.yaml
│   │   │   ├── 2026-06-06T0348_plan-with-no-asf-sa-0101-eval-sustain.yaml
│   │   │   ├── 2026-06-06T0412_plan-with-no-asf-sa-0102-eval-wire.yaml
│   │   │   ├── 2026-06-06T0412_plan-with-no-asf-sa-0103-grounding.yaml
│   │   │   ├── 2026-06-06T0434_plan-with-no-asf-sa-0105-dispatch-lock.yaml
│   │   │   ├── 2026-06-06T0438_plan-with-no-asf-sa-0106-eval-capture.yaml
│   │   │   ├── 2026-06-06T1355_plan-with-no-asf-sa-0107-fleet-checks.yaml
│   │   │   ├── 2026-06-06T1430_plan-with-no-asf-sa-0108-dispatch-crosscheck.yaml
│   │   │   ├── 2026-06-06T1518_plan-with-no-asf-sa-0109-pos-dispatch-guard.yaml
│   │   │   ├── 2026-06-06T1530_plan-with-no-asf-sa-0110-eval-live-smoke.yaml
│   │   │   ├── 2026-06-06T1545_plan-with-no-asf-sa-0111-scorer-paths.yaml
│   │   │   ├── 2026-06-06T1554_plan-with-no-asf-sa-0112-retrieve-dispatch.yaml
│   │   │   ├── 2026-06-06T1600_plan-with-no-asf-sa-0113-factory-runreceipt.yaml
│   │   │   ├── 2026-06-06T1610_plan-with-no-asf-sa-0114-l8-hybrid.yaml
│   │   │   ├── 2026-06-06T1625_plan-with-no-asf-sa-0115-scaffold-arm.yaml
│   │   │   ├── 2026-06-06T1645_plan-with-no-asf-sa-0116-council-eval-compare.yaml
│   │   │   ├── 2026-06-06T1655_plan-with-no-asf-sa-0117-eval-ci-header.yaml
│   │   │   ├── 2026-06-06T1705_plan-with-no-asf-sa-0118-no-asf-eval-authority.yaml
│   │   │   ├── 2026-06-06T1715_plan-with-no-asf-sa-0119-eval-win-pct.yaml
│   │   │   ├── 2026-06-06T1725_plan-with-no-asf-sa-0120-council-eval-validators.yaml
│   │   │   ├── 2026-06-06T1729_plan-with-no-asf-sa-0124-governance-drift.yaml
│   │   │   ├── 2026-06-06T1735_plan-with-no-asf-sa-0121-eval-regression.yaml
│   │   │   ├── 2026-06-06T1735_plan-with-no-asf-sa-0125-eval-sustain.yaml
│   │   │   ├── 2026-06-06T1745_plan-with-no-asf-sa-0122-classifier-task-ids.yaml
│   │   │   ├── 2026-06-06T1754_plan-with-no-asf-sa-0201-run-audit-bash.yaml
│   │   │   ├── 2026-06-06T2023_plan-with-no-asf-sa-0202-strict-build.yaml
│   │   │   ├── 2026-06-06T2040_plan-with-no-asf-sa-0202-strict-build.yaml
│   │   │   ├── 2026-06-06T2047_plan-with-no-asf-sa-0203-critical-bugs.yaml
│   │   │   ├── 2026-06-06T2140_plan-with-no-asf-sa-0204-backend-e2e.yaml
│   │   │   ├── 2026-06-06T2355_plan-with-no-asf-sa-0206-skip-nested-bowl.yaml
│   │   │   ├── 2026-06-07T0030_plan-with-no-asf-sa-0208-fleet-snapshot.yaml
│   │   │   ├── 2026-06-07T0035_plan-with-no-asf-sa-0209-wire-validate.yaml
│   │   │   ├── 2026-06-07T0040_plan-with-no-asf-sa-0210-spine-bridge.yaml
│   │   │   ├── 2026-06-07T0048_plan-with-no-asf-sa-0211-governance-e2e.yaml
│   │   │   ├── 2026-06-07T0110_plan-with-no-asf-sa-0212-personal-db-audit.yaml
│   │   │   ├── 2026-06-07T0130_plan-with-no-asf-sa-0214-hub-health-e2e.yaml
│   │   │   ├── 2026-06-07T0145_plan-with-no-asf-sa-0215-hub-health-crosscheck.yaml
│   │   │   ├── 2026-06-07T0200_plan-with-no-asf-sa-0216-ic-refresh.yaml
│   │   │   ├── 2026-06-07T0215_plan-with-no-asf-sa-0217-refresh-perf-note.yaml
│   │   │   ├── 2026-06-07T0226_plan-with-no-asf-sa-0425.yaml
│   │   │   ├── 2026-06-07T0230_plan-with-no-asf-sa-0218-council-seed.yaml
│   │   │   ├── 2026-06-07T0232_plan-with-no-asf-sa-0226.yaml
│   │   │   ├── 2026-06-07T0238_plan-with-no-asf-sa-0307.yaml
│   │   │   ├── 2026-06-07T0240_plan-with-no-asf-sa-0308.yaml
│   │   │   ├── 2026-06-07T0243_plan-with-no-asf-sa-0309.yaml
│   │   │   ├── 2026-06-07T0245_plan-with-no-asf-sa-0219-founder-directives.yaml
│   │   │   ├── 2026-06-07T0245_plan-with-no-asf-sa-0310.yaml
│   │   │   ├── 2026-06-07T0247_plan-with-no-asf-sa-0311.yaml
│   │   │   ├── 2026-06-07T0249_plan-with-no-asf-sa-0312.yaml
│   │   │   ├── 2026-06-07T0251_plan-with-no-asf-sa-0313.yaml
│   │   │   ├── 2026-06-07T0253_plan-with-no-asf-sa-0314.yaml
│   │   │   ├── 2026-06-07T0255_plan-with-no-asf-sa-0315.yaml
│   │   │   ├── 2026-06-07T0257_plan-with-no-asf-sa-0316.yaml
│   │   │   ├── 2026-06-07T0259_plan-with-no-asf-sa-0317.yaml
│   │   │   ├── 2026-06-07T0300_plan-with-no-asf-sa-0220-command-data-atomic.yaml
│   │   │   └── … +459 more files
│   │   ├── 2026-06-06T0425_harden-eval-ci-structural.yaml
│   │   ├── 2026-06-06T1800_e2e-fix-sa-0123-gate-receipts.yaml
│   │   ├── 2026-06-06T2019_system-audits-mandatory-loop.yaml
│   │   ├── 2026-06-06T2045_sa-0202-closeout-fix.yaml
│   │   ├── 2026-06-07T0159_ci-pass.yaml
│   │   ├── 2026-06-07T0202_ci-pass.yaml
│   │   ├── 2026-06-07T0204_ci-pass.yaml
│   │   ├── 2026-06-07T0206_ci-pass.yaml
│   │   ├── 2026-06-07T0208_ci-pass.yaml
│   │   ├── 2026-06-07T0210_ci-pass.yaml
│   │   ├── 2026-06-07T0212_ci-pass.yaml
│   │   ├── 2026-06-07T0215_ci-pass.yaml
│   │   ├── 2026-06-07T0219_ci-pass.yaml
│   │   ├── 2026-06-07T0222_batch-sa-0318-0424-30task.yaml
│   │   ├── 2026-06-07T0222_ci-pass.yaml
│   │   ├── 2026-06-07T0224_ci-pass.yaml
│   │   ├── 2026-06-07T0226_ci-pass.yaml
│   │   ├── 2026-06-07T0229_ci-pass.yaml
│   │   ├── 2026-06-07T0232_ci-pass.yaml
│   │   ├── 2026-06-07T0238_ci-pass.yaml
│   │   ├── 2026-06-07T0239_ci-pass.yaml
│   │   ├── 2026-06-07T0240_ci-pass.yaml
│   │   ├── 2026-06-07T0243_ci-pass.yaml
│   │   ├── 2026-06-07T0245_ci-pass.yaml
│   │   ├── 2026-06-07T0247_ci-pass.yaml
│   │   ├── 2026-06-07T0249_ci-pass.yaml
│   │   ├── 2026-06-07T0251_ci-pass.yaml
│   │   ├── 2026-06-07T0253_ci-pass.yaml
│   │   ├── 2026-06-07T0255_ci-pass.yaml
│   │   ├── 2026-06-07T0257_ci-pass.yaml
│   │   ├── 2026-06-07T0259_ci-pass.yaml
│   │   ├── 2026-06-07T0301_ci-pass.yaml
│   │   ├── 2026-06-07T0302_ci-pass.yaml
│   │   ├── 2026-06-07T0303_ci-pass.yaml
│   │   ├── 2026-06-07T0304_ci-pass.yaml
│   │   ├── 2026-06-07T0305_ci-pass.yaml
│   │   ├── 2026-06-07T0307_ci-pass.yaml
│   │   ├── 2026-06-07T0308_ci-pass.yaml
│   │   ├── 2026-06-07T0309_ci-pass.yaml
│   │   ├── 2026-06-07T0311_ci-pass.yaml
│   │   ├── 2026-06-07T0313_ci-pass.yaml
│   │   ├── 2026-06-07T0315_ci-pass.yaml
│   │   ├── 2026-06-07T0316_ci-pass.yaml
│   │   ├── 2026-06-07T0317_ci-pass.yaml
│   │   ├── 2026-06-07T0319_ci-pass.yaml
│   │   ├── 2026-06-07T0320_ci-pass.yaml
│   │   ├── 2026-06-07T0321_ci-pass.yaml
│   │   ├── 2026-06-07T0323_ci-pass.yaml
│   │   ├── 2026-06-07T0325_ci-pass.yaml
│   │   ├── 2026-06-07T0326_ci-pass.yaml
│   │   ├── 2026-06-07T0328_ci-pass.yaml
│   │   ├── 2026-06-07T0329_ci-pass.yaml
│   │   ├── 2026-06-07T0331_ci-pass.yaml
│   │   ├── 2026-06-07T0336_ci-pass.yaml
│   │   ├── 2026-06-07T0339_ci-pass.yaml
│   │   └── … +1815 more files
│   ├── trustfield/
│   │   ├── 2026-06-02T0730_run-scripts-founder-free-auto-sh-until-founder-f.yaml
│   │   ├── 2026-06-02T0942_run-scripts-founder-free-auto-sh-until-founder-f.yaml
│   │   ├── 2026-06-02T1021_asf-submit-execution-log-publish-ecosystem-sh.yaml
│   │   ├── 2026-06-02T1059_create-or-refresh-os-plan-json-for-trustfield-wi.yaml
│   │   ├── 2026-06-03T0830_ui-e2e-quality-pass-readiness-showcase-nav-pilot.yaml
│   │   ├── 2026-06-04T0542_deploy-www-ui-e2e-fixes-to-vercel-then-verify-ui.yaml
│   │   ├── 2026-06-04T1215_lane-alignment-b-001-decision-doc-phase-1b-git-s.yaml
│   │   ├── 2026-06-04T1220_lane-alignment-b-001-decision-doc-phase-1b-git-s.yaml
│   │   ├── 2026-06-04T1220_lane-alignment-b-001-git-sync-plan-gtm.yaml
│   │   └── latest.yaml
│   └── virlux/
│       ├── 2026-06-02T0115_document-current-blockers-in-docs-live-deploy-ru.yaml
│       ├── 2026-06-02T0152_staging-smoke-test.yaml
│       ├── 2026-06-02T1200_create-or-refresh-os-plan-json-for-virlux-with-3.yaml
│       ├── 2026-06-02T1200_staging-smoke-test.yaml
│       └── latest.yaml
├── REPO_STATUS_REPORTS/
│   ├── noetfield.yaml
│   ├── seven77.yaml
│   ├── sinaai_mono.yaml
│   ├── trustfield.yaml
│   └── virlux.yaml
├── RESEARCH/
│   ├── _GOVERNANCE/
│   │   ├── RESEARCH_INTAKE_STANDARD_v1.md
│   │   ├── research_save_enforcer.py
│   │   ├── SUBJECTS_REGISTRY.yaml
│   │   ├── WORKER_NOTICE_RESEARCH_SAVE_MANDATORY_v1.md
│   │   └── WORKERS_REGISTRY.yaml
│   ├── _vault/
│   │   └── worker/
│   │       └── 2026-06-08/
│   │           └── AUTO-TRACE-WORKER-CLOSEOUT-RECEIPT-v1.0/
│   │               …
│   ├── by_date/
│   │   ├── 2026-05-29/
│   │   │   └── worker/
│   │   │       └── seven77/
│   │   │           …
│   │   ├── 2026-06-06/
│   │   │   ├── commercial_goal_specialist/
│   │   │   │   └── trustfield/
│   │   │   │       …
│   │   │   ├── governance_goal_specialist/
│   │   │   │   └── noetfield/
│   │   │   │       …
│   │   │   └── research_acquisitor/
│   │   │       ├── ai_dev/
│   │   │       │   …
│   │   │       ├── automation/
│   │   │       │   …
│   │   │       ├── ecosystem/
│   │   │       │   …
│   │   │       └── voice_ai/
│   │   │           …
│   │   ├── 2026-06-07/
│   │   │   ├── commercial_goal_specialist/
│   │   │   │   ├── dual_brand/
│   │   │   │   │   …
│   │   │   │   ├── ecosystem/
│   │   │   │   │   …
│   │   │   │   ├── noetfield/
│   │   │   │   │   …
│   │   │   │   ├── sina_os/
│   │   │   │   │   …
│   │   │   │   └── trustfield/
│   │   │   │       …
│   │   │   ├── research_acquisitor/
│   │   │   │   ├── dual_brand/
│   │   │   │   │   …
│   │   │   │   ├── ecosystem/
│   │   │   │   │   …
│   │   │   │   ├── noetfield/
│   │   │   │   │   …
│   │   │   │   └── voice_ai/
│   │   │   │       …
│   │   │   └── worker/
│   │   │       ├── sina_os/
│   │   │       │   …
│   │   │       └── virlux/
│   │   │           …
│   │   ├── 2026-06-08/
│   │   │   ├── commercial_goal_specialist/
│   │   │   │   ├── dual_brand/
│   │   │   │   │   …
│   │   │   │   └── trustfield/
│   │   │   │       …
│   │   │   ├── governance_goal_specialist/
│   │   │   │   ├── dual_brand/
│   │   │   │   │   …
│   │   │   │   ├── noetfield/
│   │   │   │   │   …
│   │   │   │   ├── sina_os/
│   │   │   │   │   …
│   │   │   │   └── trustfield/
│   │   │   │       …
│   │   │   ├── research_acquisitor/
│   │   │   │   ├── dual_brand/
│   │   │   │   │   …
│   │   │   │   ├── ecosystem/
│   │   │   │   │   …
│   │   │   │   ├── noetfield/
│   │   │   │   │   …
│   │   │   │   ├── sina_os/
│   │   │   │   │   …
│   │   │   │   └── trustfield/
│   │   │   │       …
│   │   │   └── worker/
│   │   │       └── sina_os/
│   │   │           …
│   │   ├── 2026-06-09/
│   │   │   ├── commercial_goal_specialist/
│   │   │   │   └── sina_os/
│   │   │   │       …
│   │   │   ├── governance_goal_specialist/
│   │   │   │   ├── sina_os/
│   │   │   │   │   …
│   │   │   │   └── virlux/
│   │   │   │       …
│   │   │   ├── research_acquisitor/
│   │   │   │   ├── ai_dev/
│   │   │   │   │   …
│   │   │   │   ├── dual_brand/
│   │   │   │   │   …
│   │   │   │   └── sina_os/
│   │   │   │       …
│   │   │   └── sourcea_worker/
│   │   │       └── sina_os/
│   │   │           …
│   │   ├── 2026-06-10/
│   │   │   ├── commercial_goal_specialist/
│   │   │   │   ├── ai_dev/
│   │   │   │   │   …
│   │   │   │   ├── dual_brand/
│   │   │   │   │   …
│   │   │   │   └── sina_os/
│   │   │   │       …
│   │   │   ├── research_acquisitor/
│   │   │   │   ├── ai_dev/
│   │   │   │   │   …
│   │   │   │   ├── ecosystem/
│   │   │   │   │   …
│   │   │   │   └── trustfield/
│   │   │   │       …
│   │   │   └── worker/
│   │   │       ├── dual_brand/
│   │   │       │   …
│   │   │       ├── seven77/
│   │   │       │   …
│   │   │       └── sina_os/
│   │   │           …
│   │   ├── 2026-06-11/
│   │   │   ├── commercial_goal_specialist/
│   │   │   │   ├── ai_dev/
│   │   │   │   │   …
│   │   │   │   ├── noetfield/
│   │   │   │   │   …
│   │   │   │   ├── sina_os/
│   │   │   │   │   …
│   │   │   │   └── trustfield/
│   │   │   │       …
│   │   │   └── governance_goal_specialist/
│   │   │       ├── enforcement/
│   │   │       │   …
│   │   │       └── sina_os/
│   │   │           …
│   │   └── 2026-06-12/
│   │       ├── commercial_goal_specialist/
│   │       │   ├── noetfield/
│   │       │   │   …
│   │       │   ├── sina_os/
│   │       │   │   …
│   │       │   └── trustfield/
│   │       │       …
│   │       ├── governance_goal_specialist/
│   │       │   ├── sina_os/
│   │       │   │   …
│   │       │   └── trustfield/
│   │       │       …
│   │       └── research_acquisitor/
│   │           ├── ecosystem/
│   │           │   …
│   │           └── sina_os/
│   │               …
│   ├── vault/
│   │   └── worker/
│   │       ├── AUTO-TRACE-AUTHORITY-CONVERGENCE-LOCK-2026-06-08_authority_unified_lock.md
│   │       ├── AUTO-TRACE-AUTHORITY-P0-LOCK-2026-06-08_authority_p0_shipped.md
│   │       ├── AUTO-TRACE-AUTHORITY-P1-LOOPS-2026-06-08_authority_p1_enforced.md
│   │       └── AUTO-TRACE-EXECUTION-KERNEL-CONVERGENCE-2026-06-07_execution_kernel_convergence.md
│   ├── INDEX.yaml
│   ├── README.md
│   ├── ROUTING_AI_DEV.yaml
│   ├── ROUTING_AUTOMATION.yaml
│   ├── ROUTING_DUAL_BRAND.yaml
│   ├── ROUTING_ECOSYSTEM.yaml
│   ├── ROUTING_NOETFIELD.yaml
│   ├── ROUTING_TRUSTFIELD.yaml
│   └── ROUTING_VOICE_AI.yaml
├── runreceipt/
│   └── out/
│       ├── evidence.snapshot.json
│       ├── receipt-pack.zip
│       ├── receipt.html
│       ├── run.jsonl
│       └── summary.json
├── runtime/
│   └── architect_reports/
│       ├── 2026-06-02.yaml
│       ├── 2026-06-03.yaml
│       ├── 2026-06-04.yaml
│       ├── 2026-06-05.yaml
│       ├── 2026-06-06.yaml
│       └── 2026-06-12.yaml
├── scripts/
│   ├── eval_packet_v1/
│   │   ├── __init__.py
│   │   ├── runner.py
│   │   └── tasks.json
│   ├── eval_packet_v1b/
│   │   ├── __init__.py
│   │   ├── grounding.py
│   │   ├── runner.py
│   │   ├── scorer.py
│   │   └── tasks.json
│   ├── execution_intelligence/
│   │   ├── context_intelligence/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── behavior_analyzer.py
│   │   │   ├── context_builder.py
│   │   │   ├── context_store.py
│   │   │   ├── relevance_ranker.py
│   │   │   ├── repo_analyzer.py
│   │   │   ├── retrieval_api.py
│   │   │   └── state_analyzer.py
│   │   ├── decision_memory/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── causality.py
│   │   │   ├── extractor.py
│   │   │   ├── fix_linker.py
│   │   │   └── reasoning.py
│   │   ├── feedback_loop/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── influence_mapper.py
│   │   │   ├── loop_engine.py
│   │   │   ├── priority_adjuster.py
│   │   │   └── signal_generator.py
│   │   ├── pattern_engine/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── classifier.py
│   │   │   ├── clustering.py
│   │   │   ├── extractor.py
│   │   │   ├── helpers.py
│   │   │   └── signatures.py
│   │   ├── planner_upgrade/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── history_ranker.py
│   │   │   ├── outcome_evaluator.py
│   │   │   ├── planner_adapter.py
│   │   │   ├── planner_context.py
│   │   │   └── signal_consumer.py
│   │   ├── self_optimization/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── optimization_engine.py
│   │   │   ├── optimization_memory.py
│   │   │   ├── performance_tracker.py
│   │   │   ├── recommendation_generator.py
│   │   │   ├── strategy_analyzer.py
│   │   │   └── trend_detector.py
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── planner_influence.py
│   │   ├── processor.py
│   │   ├── reader.py
│   │   └── types.py
│   ├── execution_intelligence_v2/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── causal_linker.py
│   │   ├── prediction_engine.py
│   │   ├── risk_scoring.py
│   │   ├── strategy_optimizer.py
│   │   ├── task_recommender.py
│   │   └── types.py
│   ├── execution_spine/
│   │   ├── __init__.py
│   │   ├── executor.py
│   │   ├── progress_sync.py
│   │   ├── queue.py
│   │   ├── schema.json
│   │   ├── spine.py
│   │   ├── types.py
│   │   ├── worker.py
│   │   └── writer.py
│   ├── fixtures/
│   │   └── n8n/
│   │       ├── starter_expected_steps.json
│   │       └── workflow_manifest.json
│   ├── pre_llm/
│   │   ├── code_intelligence/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── ast_parser.py
│   │   │   ├── file_discovery.py
│   │   │   ├── graph_builder.py
│   │   │   ├── import_resolver.py
│   │   │   ├── index_builder.py
│   │   │   ├── language_detector.py
│   │   │   ├── query_engine.py
│   │   │   ├── repo_walker.py
│   │   │   ├── store.py
│   │   │   └── symbol_extractor.py
│   │   ├── context_assembly/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── assembly_engine.py
│   │   │   ├── constraints_builder.py
│   │   │   ├── provenance_builder.py
│   │   │   ├── store.py
│   │   │   └── task_grounding.py
│   │   ├── context_compression/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── budget_policy.py
│   │   │   ├── compression_engine.py
│   │   │   ├── compressor.py
│   │   │   ├── store.py
│   │   │   └── token_estimator.py
│   │   ├── context_packet/
│   │   │   ├── __init__.py
│   │   │   └── schema.py
│   │   ├── context_ranking/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── evidence_collector.py
│   │   │   ├── ranker.py
│   │   │   ├── ranking_engine.py
│   │   │   └── store.py
│   │   ├── dependency_graph/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── graph_engine.py
│   │   │   ├── query_engine.py
│   │   │   └── store.py
│   │   ├── diff_intelligence/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── diff_engine.py
│   │   │   ├── focus_reader.py
│   │   │   ├── git_diff_reader.py
│   │   │   ├── impact_mapper.py
│   │   │   └── store.py
│   │   ├── graph_fusion/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── fusion_builder.py
│   │   │   ├── query_engine.py
│   │   │   └── store.py
│   │   ├── graph_reasoning/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── reasoning_engine.py
│   │   │   ├── seed_resolver.py
│   │   │   ├── store.py
│   │   │   └── traversal.py
│   │   ├── intent_engine/
│   │   │   ├── __init__.py
│   │   │   ├── ambiguity.py
│   │   │   ├── api.py
│   │   │   ├── classifier.py
│   │   │   ├── decomposition.py
│   │   │   ├── intent_engine.py
│   │   │   ├── query_engine.py
│   │   │   └── store.py
│   │   ├── memory_git_bridge/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── bridge_builder.py
│   │   │   ├── bridge_engine.py
│   │   │   ├── git_reader.py
│   │   │   ├── log_reader.py
│   │   │   ├── query_engine.py
│   │   │   └── store.py
│   │   ├── packet_memory_merge/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── budget_policy.py
│   │   │   ├── memory_collector.py
│   │   │   ├── merge_engine.py
│   │   │   └── store.py
│   │   ├── packet_readiness/
│   │   │   ├── __init__.py
│   │   │   └── hub_surface.py
│   │   ├── planning_engine/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── graph_builder.py
│   │   │   ├── planning_engine.py
│   │   │   └── store.py
│   │   ├── query_expansion/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── expansion_engine.py
│   │   │   ├── plan_builder.py
│   │   │   ├── query_templates.py
│   │   │   ├── store.py
│   │   │   └── symbol_expander.py
│   │   ├── semantic_history/
│   │   │   ├── __init__.py
│   │   │   └── history_bridge.py
│   │   ├── tool_router/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── capability_catalog.py
│   │   │   ├── policy_engine.py
│   │   │   ├── router_engine.py
│   │   │   └── store.py
│   │   ├── user_signals/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   └── store.py
│   │   ├── validation_layer/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── check_runner.py
│   │   │   ├── store.py
│   │   │   └── validation_engine.py
│   │   ├── vector_retrieval/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── chunk_builder.py
│   │   │   ├── embedding_provider.py
│   │   │   ├── index_builder.py
│   │   │   ├── query_engine.py
│   │   │   ├── retrieval_engine.py
│   │   │   └── store.py
│   │   └── __init__.py
│   ├── runreceipt/
│   │   ├── pack.sh
│   │   └── pack_v1.py
│   ├── runtime/
│   │   ├── context_fabric/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── fabric_engine.py
│   │   │   └── fabric_store.py
│   │   ├── dispatch_policy/
│   │   │   ├── __init__.py
│   │   │   ├── allowlist.py
│   │   │   ├── api.py
│   │   │   ├── classifier.py
│   │   │   ├── policy_engine.py
│   │   │   └── store.py
│   │   ├── event_bus/
│   │   │   └── bus_v1.py
│   │   ├── execution_router/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── execution_state.py
│   │   │   ├── policy_engine.py
│   │   │   ├── priority_resolver.py
│   │   │   ├── router_engine.py
│   │   │   ├── router_store.py
│   │   │   └── step_selector.py
│   │   ├── graph_executor/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── executor_engine.py
│   │   │   └── spine_bridge.py
│   │   ├── multi_step_planner/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── chain_builder.py
│   │   │   ├── fallback_paths.py
│   │   │   ├── planner_engine.py
│   │   │   └── planner_store.py
│   │   ├── orchestrator/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── orchestrator_engine.py
│   │   │   └── orchestrator_store.py
│   │   ├── repair_loop/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── failure_classifier.py
│   │   │   ├── recovery_graph.py
│   │   │   ├── repair_engine.py
│   │   │   └── repair_loop_store.py
│   │   ├── tool_graph/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── dependency_mapper.py
│   │   │   ├── execution_path.py
│   │   │   ├── graph_builder.py
│   │   │   └── graph_store.py
│   │   ├── tool_graph_verification/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── context_checker.py
│   │   │   ├── cycle_detector.py
│   │   │   ├── dependency_validator.py
│   │   │   ├── plan_scorer.py
│   │   │   ├── safety_checker.py
│   │   │   ├── validation_engine.py
│   │   │   └── verify_store.py
│   │   └── __init__.py
│   ├── samples/
│   ├── _debug_e2e_log_v1.py
│   ├── _ecosystem_safety_dual_pick_check_v1.py
│   ├── _ecosystem_safety_hub_api_check_v1.py
│   ├── _ecosystem_safety_monitor_check_v1.py
│   ├── _ecosystem_safety_orchestrator_check_v1.py
│   ├── _worker_turn_validate_restore.py
│   ├── activate-devbridge-loop.py
│   ├── activate-portfolio-loop.py
│   ├── active_now_sync_from_factory_now_v1.py
│   ├── active_now_v1.py
│   ├── advance-healthy-queue-v1.py
│   ├── advisor-cursor-reply.sh
│   ├── agent-loop-done.sh
│   ├── agent-queue-prompt.sh
│   ├── agent_command_reviews.py
│   ├── agent_conflict_room.py
│   ├── agent_council_room.py
│   ├── agent_doc_tags.py
│   ├── agent_essay_discourse.py
│   ├── agent_governance_events.py
│   ├── agent_governance_unification.py
│   ├── agent_incident_system.py
│   ├── agent_loop.py
│   ├── agent_memory_mirror_v1.py
│   ├── agent_private_workspaces.py
│   ├── agent_research_pipeline.py
│   ├── agent_rules_in_charge.py
│   ├── agent_rules_loop_orchestrator.py
│   ├── agent_scoreboard.py
│   ├── agent_session_gate_run_v1.py
│   ├── agent_skills_registry.py
│   ├── agent_smooth_truth_score_v1.py
│   ├── agent_system_unified.py
│   ├── agent_truth_bundle_v1.py
│   ├── agent_turn_context_v1.py
│   ├── agent_workspace_mirror.py
│   ├── agent_workspace_registry.py
│   ├── agent_workspace_vault.py
│   ├── align_command_data_sa_queue_v1.py
│   ├── align_command_data_ui_v1.py
│   ├── append_repo_execution_log_v1.py
│   ├── append_spine_proof_priority_v1.py
│   ├── append_ssot_alignment_priority_v1.py
│   ├── apple_health_mini.py
│   ├── apple_health_sleep_bridge_v1.py
│   ├── archive-superseded-wtm-doc.py
│   ├── archive_suppressed_docs_v1.py
│   ├── arm-sleep-mode-v1.sh
│   ├── audit-enforcement-1000-v1.py
│   ├── audit_agent_governance_e2e.py
│   ├── audit_backend_e2e.py
│   ├── audit_backend_e2e_light_v1.py
│   ├── audit_essentials_nav.py
│   ├── audit_hub_source_alignment.py
│   ├── audit_mergepack_ship_v1.py
│   └── … +678 more files
├── sina-bowl/
│   ├── brief.fa.txt
│   ├── brief.txt
│   ├── DAILY_BOWL.md
│   ├── DRIFT.json
│   ├── MASTER_ORDERS.json
│   └── state.json
├── SourceA Dashboard.app/
│   └── Contents/
│       ├── MacOS/
│       │   └── launcher
│       ├── Resources/
│       └── Info.plist
├── .cursorignore
├── ACTIVE_NOW.md
├── AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md
├── AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md
├── AGENT_CONTROL_PANEL_SPEC_LOCKED_v1.md
├── AGENT_COUNCIL_ROOM_LOCKED_v1.md
├── AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md
├── AGENT_DESK_START_HERE.md
├── AGENT_DIAG_CLIPBOARD_PAIRING_HIJACK_2026-05-27_LOCKED.md
├── AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md
├── AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md
├── AGENT_ESSAY_DISCOURSE_LOCKED_v1.md
├── AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md
├── AGENT_GOVERNANCE_INDEX_LOCKED_v1.md
├── AGENT_INCIDENTS_REGISTRY_REPORT_LOCKED_v1.md
├── AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md
├── AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md
├── AGENT_MIND_SHARE_LOCKED_v1.md
├── AGENT_OPERATING_ROLES_LOCKED_v1.md
├── AGENT_OUTPUT_CONTRACT_v1.yaml
├── AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md
├── AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_REPORT_LOCKED_v1.md
├── AGENT_RULES_IN_CHARGE_LOCKED_v1.md
├── AGENT_SCOREBOARD_LOCKED_v1.md
├── AGENT_SELF_AUDIT_ASF_REPORT_2026-06-04.md
├── AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md
├── AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md
├── AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md
├── AI_INFRA_PARTNERSHIP_PROPOSALS_LOCKED_v1.md
├── ARCHITECT_REPORT.yaml
├── ASF_FIVE_REPOS_PLUS_COMMAND_CHAT_v1.md
├── ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md
├── ASF_MASTER_ORDERS_ORGANIZED_LOCKED_v1.md
├── ASF_MILESTONE_GLOSSARY_LOCKED_v1.md
├── ASF_PARALLEL_SIX_REPOS_OVERRIDE_v1.md
├── ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md
├── ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md
├── AUTO_CONFLICT_ENGINE_V3_LOCKED.md
├── AUTO_CONFLICT_EXAMPLE_AGENT_STACK_POLICY_v1_LOCKED.md
├── BRAIN_OS_POINTER_LOCKED_v1.md
├── CHAT_EXTRACT_UNIFY_PROMPT.txt
├── CHAT_UNIFY_ROLLUP_PROMPT.txt
├── CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md
├── COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md
├── CROSS_LANE_EDIT_FORBIDDEN_LOCKED_v1.md
├── CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md
├── CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_REPORT_LOCKED_v1.md
├── CURSOR_FIND_BUGS_AUTOMATION_LOCKED_v1.md
├── CURSOR_FIX_OVERNIGHT.md
├── CURSOR_REPO_AGENT_NOTICE_PROMPTS_v1.md
├── CURSOR_REPO_SPECIALIZED_NOTICES_v2.md
├── CURSOR_SYSTEM_EXECUTION_MODE_START_v1.md
├── DISPATCH_POLICY_LOCKED_v1.md
├── ECOSYSTEM_GRAPH.json
├── ECOSYSTEM_IMPORTANT_DOCS_INDEX_LOCKED_v1.md
└── … +229 more files
```

## 2. Core component paths

### Hub

- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/index.html` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/assets/app.js` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/assets/app.css` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/assets/nav-registry-v1.js` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/assets/shell.html` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/command-data.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/command-data-runtime.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/command-data-canonical.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/command-data-shell.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/sina-command-server.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/sina-command-api.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/build-sina-command-panel.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/build-sina-command-panel.sh` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/serve-sina-command.sh` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/kill-sina-command.sh` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_home_founder_view_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_sync_slim_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_judge_alarm_strip_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_rebuild_worker_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_projection_canonical_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_projection_sync_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_state_service_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_surface_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_agent_runtime_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_queue_lib_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_essentials_index.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_live_events_lib_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_self_refresh_v1.py` ✓

### Forms

- `/Users/sinakazemnezhad/Desktop/SourceA/SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/live_founder_decision_form_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/canvas_form_submit_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/canvas_form_apply_picks_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/form_open_questions_reconcile_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/form_conflict_intake_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/generate_integrity_canvas_form_data_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/validate-live-founder-decision-form-v1.sh` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/validate-integrity-form-canvas-ssot-v1.sh` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/founder_voice_terminology_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/founder_voice_sources_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/sync_founder_linkedin_voice_v1.py` ✓
- `~/.sina/live-founder-decision-form-v1.json` ✓
- `~/.sina/canvas-form-picks-applied-v1.json` ✓
- `~/.sina/live-founder-decision-form-intake-v1.json` ✗ missing
- `~/.sina/form-open-questions-reconcile-v1.json` ✓
- `~/.sina/forms/thread-enforcement-forks-v1.yaml` ✓
- `/Users/sinakazemnezhad/.cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.tsx` ✓
- `/Users/sinakazemnezhad/.cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/integrity-open-row-spec.ts` ✓
- `/Users/sinakazemnezhad/.cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/integrity-form-data.generated.ts` ✓

### JudgeRoom (Judge Center)

- `/Users/sinakazemnezhad/Desktop/SourceA/SINA_JUDGE_STACK_LOCKED_v1.md` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/judge_center_run_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/judge_center_audit_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/judge_center_counsel_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/judge_center_bench_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/judge_center_patterns_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/judge_center_temporal_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/hub_judge_alarm_strip_v1.py` ✓
- `~/.sina/judge-center/last-audit-batch.json` ✓
- `~/.sina/judge-center/latest-counsel-v1.json` ✓
- `~/.sina/judge-center/latest-resolution-v1.json` ✓
- `~/.sina/judge-center/latest-run-receipt-v1.json` ✓

### ThreadRoom

- `/Users/sinakazemnezhad/Desktop/SourceA/SINA_THREAD_ROOM_LOCKED_v1.md` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/thread_room_run_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/thread_room_scout_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/thread_room_cartographer_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/thread_room_curator_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/thread_room_shared_v1.py` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/validate-thread-room-v1.sh` ✓
- `~/.sina/thread-room/latest-map-v1.json` ✓
- `~/.sina/thread-room/latest-curation-v1.json` ✓

### Active JSON schemas / SSOT

- `/Users/sinakazemnezhad/Desktop/SourceA/PROGRAM_PROGRESS.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/EXECUTION_TRUTH.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/FEEDBACK_AGGREGATE.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/PORT_REGISTRY.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/PORT_CATALOG.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/GLOBAL_BLOCKERS.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/GLOBAL_PRIORITY.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/ECOSYSTEM_GRAPH.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/VAULT_STATUS.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/scripts/execution_spine/schema.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/command-data.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/command-data-runtime.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/command-data-canonical.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/plan-registry/sourcea-1000/REGISTRY.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/plan-registry/enforcement-1000/REGISTRY.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/sina-bowl/MASTER_ORDERS.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/sina-bowl/state.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/data/agent_fleet/AGENT_FLEET_REGISTRY.json` ✓
- `/Users/sinakazemnezhad/Desktop/SourceA/agent-skills/REGISTRY_LOCKED_v1.json` ✓

## 3. Entry-point heads (first 15 lines)

### `scripts/sina-command-server.py`

```
#!/usr/bin/env python3
"""Sina Command — unified app server (UI + API on one port). Production default :13020."""
from __future__ import annotations

import json
import mimetypes
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

SOURCE_A = Path(__file__).resolve().parents[1]
```

### `scripts/build-sina-command-panel.py`

```
#!/usr/bin/env python3
"""Build Sina Command local UI — merges bowl state + fleet + KPI.

Refresh dedupe: ``SINA_SKIP_NESTED_BOWL`` in ``update-program-progress`` pipeline (sa-0230).

Eval CI (strict build — ``SINA_AUDIT_STRICT`` default on)
----------------------------------------------------------
Two eval layers run on every build; do not conflate them (council brief §Eval-1 vs Eval-1b).

**Eval-1 — structural** (no live LLM)
  - ``eval_packet_v1.runner.run_eval`` refreshes ``~/.sina/eval_packet_v1_report.json``
  - Metric: packet ``readiness_score`` / ``gate_eligible`` vs empty template (≥80% wins)
  - Hub: ``/api/eval-packet-v1`` · validator: ``validate-eval-packet-v1.sh`` (find_critical_bugs)

**Eval-1b — behavioral** (scaffold + optional live)
```

### `scripts/serve-sina-command.sh`

```
#!/usr/bin/env bash
# Sina Command — one production server (UI + API on :13020)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${SINA_COMMAND_PORT:-13020}"
PIDFILE="${HOME}/.sina/command-server.pid"
LOGFILE="${HOME}/.sina/command-server.log"
BUILDLOG="${HOME}/.sina/panel-build.log"
MODE="${1:-}"

export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}"

mkdir -p "${HOME}/.sina"
cd "$ROOT"

```

### `scripts/sina-command-app-runner.sh`

```
#!/usr/bin/zsh
# Sina Command.app runner — start hub, open UI, POST /shutdown on exit (normal quit).
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:/usr/bin:/bin:/usr/sbin:/sbin"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${SINA_COMMAND_PORT:-13020}"
CURL="${CURL:-/usr/bin/curl}"
if [[ -z "${SINA_GATE_MODE:-}" && -f "${HOME}/.sina/gate_mode_v1.txt" ]]; then
  export SINA_GATE_MODE="$(tr -d '[:space:]' < "${HOME}/.sina/gate_mode_v1.txt")"
fi

shutdown_hub() {
  "$CURL" -sf -X POST "http://127.0.0.1:${PORT}/shutdown" \
    -H "Content-Type: application/json" \
    -d '{}' >/dev/null 2>&1 || true
```

### `scripts/live_founder_decision_form_v1.py`

```
#!/usr/bin/env python3
"""Live founder decision form — machine mirror for pending/answered/open questions."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORM_MD = ROOT / "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md"
NORM_MD = ROOT / "SOURCEA_FOUNDER_MESSAGE_NORMALIZATION_LOCKED_v1.md"
FIRST_FORM_ARCHIVE = (
```

### `scripts/canvas_form_submit_v1.py`

```
#!/usr/bin/env python3
"""FORM_OFFICIAL batch submit — Canvas confirms → disk → hub (founder Submit only)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def submit(*, cascade_hub: bool = True, strict_hub: bool = True) -> dict:
```

### `scripts/canvas_form_apply_picks_v1.py`

```
#!/usr/bin/env python3
"""Apply M1 Canvas confirmed picks → form §ANSWERED (FORM_OFFICIAL wire)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORM_MD = ROOT / "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md"
CANVAS_DATA = (
    Path.home()
```

### `scripts/generate_integrity_canvas_form_data_v1.py`

```
#!/usr/bin/env python3
"""Generate integrity-form-data.generated.ts for M1 Canvas (100 agent POV + 43 open rows)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = Path.home() / ".sina/agent-workspaces/trustfield/commercial-goal/forms/SOURCEA_100_AGENT_POV_FORM_v2.yaml"
OUT_PATH = (
    Path.home()
    / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/integrity-form-data.generated.ts"
```

### `scripts/judge_center_run_v1.py`

```
#!/usr/bin/env python3
"""Judge Center — run full L1 Audit → L2 Counsel → L3 Bench pipeline.

Usage:
  python3 scripts/judge_center_run_v1.py --chats 6245d9dd,e54ddfa8,74f5ccab
  python3 scripts/judge_center_run_v1.py --chats 6245d9dd --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

```

### `scripts/judge_center_audit_v1.py`

```
#!/usr/bin/env python3
"""Judge Center L1 Audit — extract chat claims · alarm vs disk (no verdict).

TRACE: SINA_JUDGE_STACK_DRAFT_v1.md L1 · Q-JUDGE-STACK-v1
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
```

### `scripts/judge_center_counsel_v1.py`

```
#!/usr/bin/env python3
"""Judge Center L2 Counsel — settle alarms vs disk · draft form forks.

TRACE: SINA_JUDGE_STACK_DRAFT_v1.md L2 · Q-JUDGE-STACK-v1
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

```

### `scripts/judge_center_bench_v1.py`

```
#!/usr/bin/env python3
"""Judge Center L3 Bench — final resolution · form row drafts · remediation prompts.

TRACE: SINA_JUDGE_STACK_DRAFT_v1.md L3 · Q-JUDGE-STACK-v1
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

JUDGE_DIR = Path.home() / ".sina/judge-center"
```

### `scripts/thread_room_run_v1.py`

```
#!/usr/bin/env python3
"""Thread Room — Scout → Cartographer → Curator pipeline.

Usage:
  python3 scripts/thread_room_run_v1.py --chats 58148ac9,6245d9dd,e54ddfa8 --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
```

### `scripts/thread_room_scout_v1.py`

```
#!/usr/bin/env python3
"""Thread Room L1 Scout — extract chat anchors · candidate THREAD arcs.

TRACE: SINA_THREAD_ROOM_DRAFT_v1.md L1 · Q-THREAD-ROOM-v1
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
```

### `scripts/thread_room_cartographer_v1.py`

```
#!/usr/bin/env python3
"""Thread Room L2 Cartographer — T30/T20 map · gaps · judge cross-link.

TRACE: SINA_THREAD_ROOM_DRAFT_v1.md L2
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
```

### `scripts/thread_room_curator_v1.py`

```
#!/usr/bin/env python3
"""Thread Room L3 Curator — MERGE/SPLIT/DEFER plan · Form §THREAD row drafts.

TRACE: SINA_THREAD_ROOM_DRAFT_v1.md L3
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
```

### `scripts/hub_home_founder_view_v1.py`

```
#!/usr/bin/env python3
"""Plain-English Hub home payload — ASF HUB_HOME_REDESIGN_SPEC_LOCKED_v1.md."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
BROKER_EVENTS = Path.home() / ".sina" / "goal1-lane-broker-events.jsonl"
EVENT_BUS = Path.home() / ".sina" / "events_v1.jsonl"
SCHEMA = "hub-home-founder-v2-light"
```

### `scripts/hub_rebuild_worker_v1.py`

```
#!/usr/bin/env python3
"""
Single rebuild worker — SourceA hub.
ONE instance enforced via fcntl lock.
Dirty coalescing: N mutations in SETTLE seconds → 1 rebuild.
Standalone service on :13030 (health) + queue consumer thread.
"""
from __future__ import annotations

import fcntl
import json
import os
import sys
import threading
import time
```

### `scripts/agent_rules_loop_orchestrator.py`

```
#!/usr/bin/env python3
"""Rules-in-charge loop — agents MUST check existing laws before acting.

Supersession: a rule stays in charge until a newer LOCKED doc or .mdc explicitly supersedes it.
Never add parallel duplicate rules — extend or supersede the canonical one.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
```

### `scripts/system_roadmap.py`

```
#!/usr/bin/env python3
"""Big Picture System Roadmap — structured payload for hub UI."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
SINA_HOME = Path.home() / ".sina"

LAW_DOC = "brain-os/wtm/WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md"
UI_DOC = "brain-os/wtm/WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md"
MAP_DOC = "brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md"
```

### `agent-control-panel/assets/app.js`

```
/**
 * Sina Command v3 — live API, KPI, fleet groups, personal DB
 */
(function () {
  "use strict";

  // Same-origin unified server (sina-command-server.py on :13020)
  const API = window.location.protocol.startsWith("http")
    ? `${window.location.protocol}//${window.location.host}`
    : "http://127.0.0.1:13020";
  let D = window.COMMAND_DATA || {};
  let commandDataFullLoaded = !!(D.built_at && !window.__COMMAND_DATA_LAZY);
  let commandDataFullPromise = null;

  const HEAVY_TAB_KEYS = {
```


# Authority Registry — GOV_UNIFY Batch 2026-06-11 (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **sequence_id:** SA-2026-06-11-GOV-UNIFY-AUTHORITY  
**Parent:** `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md` · `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md`  
**Purpose:** Registry-only diff — no law body edits. One incident corpus row; agent-ecosystem parent + children; SourceA topic rows; T3 allowlist for pointers/reports/examples.

---

## Batch summary

| Action | Count | Notes |
|--------|-------|-------|
| `INCIDENT_CORPUS` parent | 1 | 31 root `*_REPORT_*` under `ecosystem_incidents_index.py` |
| Agent ecosystem family | 15 | `AGENT_ECOSYSTEM` parent + 14 high-traffic children |
| SourceA topic (T3) | 12 | E2E, constellation, execution law, etc. |
| Infrastructure / T2 uplift | 18 | Dispatch, Prompt OS, founder ops, gov infra |
| Allowlist (pointer/report/example) | 10 | Not topic law — indexed only |

**Validator:** `scripts/validate-authority-root-coverage-v1.sh` · `authority_root_coverage_audit.py`

---

## New authority registry rows (applied to index)

| ID | Canonical doc | Governs |
|----|---------------|---------|
| `INCIDENT_CORPUS` | `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` | All root incident reports — index + room, not per-report law rows |
| `AGENT_ECOSYSTEM` | `AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md` | Agent surface unification — children pointer-only |
| `AGENT_COUNCIL` | `AGENT_COUNCIL_ROOM_LOCKED_v1.md` | Council room protocol |
| `AGENT_MIND_SHARE` | `AGENT_MIND_SHARE_LOCKED_v1.md` | Cross-agent learning |
| `AGENT_APP_HUB` | `AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md` | App-as-hub pattern |
| `AGENT_APP_BLUEPRINT` | `AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md` | Application use blueprint |
| `AGENT_RULES_CHARGE` | `AGENT_RULES_IN_CHARGE_LOCKED_v1.md` | Rules-in-charge loop |
| `AGENT_SCOREBOARD` | `AGENT_SCOREBOARD_LOCKED_v1.md` | Agent scoreboard |
| `AGENT_CONTROL_PANEL` | `AGENT_CONTROL_PANEL_SPEC_LOCKED_v1.md` | Control panel spec |
| `AGENT_ESSAY` | `AGENT_ESSAY_DISCOURSE_LOCKED_v1.md` | Essay discourse |
| `AGENT_VAULT` | `AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md` | Workspace vault layer |
| `AGENT_SPRINT` | `AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md` | Sprint consolidation |
| `AGENT_OPERATING_ROLES` | `AGENT_OPERATING_ROLES_LOCKED_v1.md` | Operating roles |
| `AGENT_SKILLS` | `AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md` | Skills + research pipeline |
| `AGENT_MERGEPACK_NOTE` | `AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md` | MergePack is not an agent |
| `AGENT_INCIDENT_ROOM` | `SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md` | Incident room law |
| `SINA_COMMAND_FOUNDER` | `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` | No-terminal founder command |
| `SINA_COMMAND_GUIDE_ROW` | `SINA_COMMAND_GUIDE_LOCKED_v1.md` | Command guide |
| `PROMPT_OS_CORE` | `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md` | Prompt OS core decision |
| `PHASE1_FREEZE` | `SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md` | Phase 1 stabilization only |
| `EXECUTION_TRUTH` | `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` | Execution truth layer |
| `PARALLEL_LANES` | `SINAAI_PARALLEL_LANES_NO_BLOCK_PROGRESS_LOCKED_v1.md` | Parallel lanes |
| `PROMPT_OS_SYSTEM` | `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` | Prompt OS system |
| `DISPATCH_POLICY` | `DISPATCH_POLICY_LOCKED_v1.md` | Dispatch policy |
| `SINA_RUNTIME_STACK` | `SINA_RUNTIME_STACK_LOCKED_v1.md` | Runtime stack |
| `LLM_CONTEXT_PACKET` | `LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md` | LLM context packet schema |
| `GOV_DRIFT` | `GOVERNANCE_DRIFT_ENGINE_LOCKED_v1.md` | Governance drift engine |
| `DOC_SEQUENCE` | `SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md` | Document sequence (chronology) |
| `DOC_LIBRARY_INDEX` | `ECOSYSTEM_IMPORTANT_DOCS_INDEX_LOCKED_v1.md` | Important docs index |
| `ENFORCE_BYPASS` | `ENFORCE_BYPASS_MAP_LOCKED_v1.md` | Enforce bypass map |
| `TRUST_LEDGER` | `TRUST_LEDGER_SCHEMA_LOCKED_v1.md` | Trust ledger schema |
| `PLAN_STATUS_VOCAB` | `PLAN_STATUS_VOCAB_LOCKED_v1.md` | Plan status vocabulary |
| `ASF_PROGRESS` | `ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md` | Program progress command center |
| `ASF_THREADS` | `ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md` | Program threads registry |
| `FOUNDER_TRACKING` | `FOUNDER_FIRST_ASSISTANT_TRACKING_LAW_LOCKED_v1.md` | Founder request tracking |
| `FOUNDER_SAVE_LOCK` | `FOUNDER_SAVE_AND_LOCK_IMMEDIATE_APP_LAW_LOCKED_v1.md` | Save and lock immediate |
| `ASF_MILESTONE_GLOSSARY` | `ASF_MILESTONE_GLOSSARY_LOCKED_v1.md` | Milestone glossary |
| `E2E_DEBUGGER` | `SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md` | E2E debugger playbook |
| `REF_CONSTELLATION` | `SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md` | Reference architecture constellation |
| `EXECUTION_LAW` | `SOURCEA_EXECUTION_LAW_LOCKED_v1.md` | SourceA execution law |
| `CURSOR_RULES_MAP` | `SOURCEA_CURSOR_RULES_AND_SKILLS_MAP_LOCKED_v2.md` | Cursor rules and skills map |
| `GOLDEN_SAFETY` | `SOURCEA_GOLDEN_INSIGHT_AND_SAFETY_LOCKED_v1.md` | Golden insight and safety |
| `MARKET_RECEIPT_ARCH` | `SOURCEA_MARKET_RECEIPT_ARCHITECTURE_LOCKED_v1.md` | Market receipt architecture |
| `FOUNDER_PINNED` | `SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md` | Founder pinned actions |
| `MASTER_SESSION_MANIFEST` | `SOURCEA_MASTER_SESSION_MANIFEST_LOCKED_v1.md` | Master session manifest |
| `PHASE_STRICT_INBOX` | `SOURCEA_PHASE_STRICT_RUN_INBOX_LOCKED_v1.md` | Phase strict run inbox |
| `PHASE_PACK_SUMMARY` | `SOURCEA_PHASE_PACK_PINNED_SUMMARY_LOCKED_v1.md` | Phase pack pinned summary |
| `PACK_AUDIT_JUDGE` | `SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md` | 1000-pack audit judge |
| `WORKER_E2E_POSTMORTEM` | `SOURCEA_WORKER_E2E_POSTMORTEM_LOCKED_v1.md` | Worker E2E postmortem |
| `CROSS_LANE_EDIT` | `CROSS_LANE_EDIT_FORBIDDEN_LOCKED_v1.md` | Cross-lane edit forbidden |
| `LAYER_A` | `SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md` | Personal database Layer A |
| `NOETFIELD_CLOUD` | `NOETFIELD_CLOUD_GIT_AND_AGENT_ENTRY_UNIFIED_LOCKED_v1.md` | Noetfield cloud entry |
| `INCIDENT_LAW_BRAIN_WORKER` | `SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md` | Brain/worker lane cross incident law |
| `INCIDENT_LAW_CROSS_LANE` | `SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md` | Cross-lane incident law |
| `CURSOR_FIND_BUGS` | `CURSOR_FIND_BUGS_AUTOMATION_LOCKED_v1.md` | Find-bugs automation |
| `HUB_PROOF_UX` | `HUB_PROOF_UX_P0_LOCKED_v1.md` | Hub proof UX P0 |
| `IPHONE_CLOUD_SPEC` | `IPHONE_CLOUD_ORGANIZATION_SPEC_LOCKED_v1.md` | iPhone cloud organization |
| `AGENT_VERBS` | `AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md` | Agent verbs save/work/edit |
| `AGENT_FOUNDER_BASH` | `AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md` | Founder bash communication |
| `AGENT_RULE_CONFLICT_AUDIT` | `AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md` | Rule conflict audit law |
| `PROMPT_OS_MVP_ORDER` | `PROMPT_OS_CORE_MVP_BUILD_ORDER_LOCKED_v1.md` | Prompt OS MVP build order |
| `ARCHITECT_V2` | `SINAAI_ARCHITECT_V2_INDUSTRIAL_POLICY_LOCKED_v1.md` | Architect v2 industrial policy |
| `PERMANENT_ARCHITECT` | `SINAAI_PERMANENT_ARCHITECT_AGENT_LOCKED_v1.md` | Permanent architect agent |
| `PHASE2_AI_EXEC` | `SINAAI_PHASE2_AI_CONTROLLED_EXECUTION_LOCKED_v1.md` | Phase 2 AI-controlled execution |
| `ASF_MASTER_ORDERS` | `ASF_MASTER_ORDERS_ORGANIZED_LOCKED_v1.md` | ASF master orders |
| `FOUNDER_NO_CC` | `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` | Founder no credit card infra |
| `INCIDENT_LAW_GOAL1_PROOF` | `SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md` | Goal 1 unvalidated proof incident law |
| `HUB_E2E_CANCELLED` | `SINA_HUB_E2E_CANCELLED_LOCKED_v1.md` | Hub E2E cancelled |
| `COMMAND_UI_PLAYFUL` | `SINA_COMMAND_UI_PLAYFUL_LOCKED_v1.md` | Command UI playful layer |
| `SEMI_SEPARATE_NOTICE` | `SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md` | Semi-separate agent notice |
| `VIDEO_HERO_PIPELINE` | `SOURCEA_COMMERCIAL_VIDEO_HERO_PIPELINE_LOCKED_v1.md` | Commercial video hero pipeline |
| `INTEGRATION_LEVERAGE` | `SOURCEA_INTEGRATION_LEVERAGE_STRATEGY_LOCKED_v1.md` | Integration & partnership leverage strategy |

---

## Allowlist (T3_REGISTERED — not separate law rows)

| Path | Role |
|------|------|
| `AUTO_CONFLICT_EXAMPLE_AGENT_STACK_POLICY_v1_LOCKED.md` | ACE example only |
| `AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_REPORT_LOCKED_v1.md` | Audit report mirror |
| `FOUNDER_BUSY_OPERATING_MODEL_REPORT_LOCKED_v1.md` | Operating model report |
| `SOURCEA_BRAIN_MONITOR_FIX_REPORT_LOCKED_v1.md` | Fix report |
| `SOURCEA_INVARIANT_GATEKEEPER_REPORT_LOCKED_v1.md` | Invariant gatekeeper report |
| `BRAIN_OS_POINTER_LOCKED_v1.md` | brain-os pointer |
| `SINA_ADVISOR_TRACK_OPERATIONAL_POINTER_LOCKED_v1.md` | Advisor track pointer |
| `SOURCEA_SESSION_20260609_COMPLETE_INDEX_LOCKED_v1.md` | Session index mirror |
| `WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md` | WTM diagram companion |
| `WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md` | WTM UI research companion |
| `AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md` | Agent tier-1/2/3 pipelines (orientation · hospital · maze) |
| `FOUNDER_DAILY_PROMPT_PACK_LOCKED_v1.md` | Founder one-word prompt pack (orientation/hospital/maze/forge) |
| `MACHINE_THREE_PIPELINES_CALIBRATE_TUNE_FORGE_LOCKED_v1.md` | Machine tier pipelines (calibrate · tune · forge) |
| `REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md` | Unified refinement router — agent + machine tiers |
| `SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md` | Machine test ladder daily→monthly · upgrade loop |
| `SINA_COMMAND_DEACTIVATED_INCIDENT_READ_POLICY_LOCKED_v1.md` | Session-gate incident read policy · mirror ids only |
| `MAC_GUARD_AGENCY_DEMO_SCRIPT_LOCKED_v1.md` | Mac Health Guard agency demo script — commercial attach |
| `NOETFIELD_COMPLIANCE_DEMO_SCRIPT_LOCKED_v1.md` | Noetfield compliance demo script — pairs with NW1 battle card |
| `SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md` | SourceA agency product demo script — portfolio SKU |

---

## Incident corpus (31 root reports)

All paths in `scripts/ecosystem_incidents_index.py` → `LOCKED_ROOT_INCIDENT_REPORTS`.  
Authority wins: `INCIDENT_CORPUS` row · per-report bodies unchanged.

---

*End GOV_UNIFY authority batch*

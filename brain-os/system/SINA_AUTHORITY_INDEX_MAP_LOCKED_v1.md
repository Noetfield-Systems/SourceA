# Sina Authority Index Map (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.2 — LOCKED  
**sequence_id:** SA-2026-05-27-AUTHORITY-INDEX  
**Router:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md`  
**Purpose:** Single registry — what laws exist, what they govern, what they override, where archives live.

---

## LAW PURITY POLICY (SSOT — LOCKED)

**Alive here only.** `SINA_GOVERNANCE_ENTRY` §11 · `SINA_OS_SSOT` §2 · companions **pointer-only** — do not restate this table.

| # | Rule | Enforcement |
|---|------|-------------|
| **1** | **Law = law (100%)** | A root `*_LOCKED*.md` is **law** for its **one declared topic** — not essay, operating report, chronology index, or chat summary wearing a law filename |
| **2** | **No fragmentation** | One topic → one canonical active doc at root; indexes, hub, prompts, companions = **path + one-line pointer** |
| **3** | **No duplication** | Same rule prose in two active LOCKED files = **FAIL** — merge via `GOV_UNIFY` or archive superseded copy |
| **4** | **No mixing unrelated subjects** | Unrelated topics in one LOCKED doc = **FAIL** — split topic, child pointer row, or `INCIDENT_CORPUS` / allowlist — never blend conduct + product + WTM in one law body |
| **5** | **Ask if you don't know** | Before edit or cite: **ask ASF** which authority row governs — never guess, invent a tab name, or create a shadow law row |

**Registry lookup:** topic → row in **Active authority registry** below → edit **that** canonical doc only.

**Machine:** `validate-law-purity-ssot-v1.sh` · `validate-authority-index-coverage-v1.sh` · `authority_root_coverage_audit.py`

---

## Law (one sentence)

**Each topic has exactly one canonical active doc at root; all other surfaces point here — never restate.**

---
**Canonical WTM map:** `brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`


## Active authority registry

| ID | Canonical doc (root) | Ver | Governs | Overrides / wins over | Machine mirror | Superseded versions |
|----|----------------------|-----|---------|----------------------|----------------|---------------------|
| `ECOSYSTEM` | `SINA_OS_SSOT_LOCKED.md` | 3.0 | Mono structure, ports, phases | All ecosystem docs subordinate | — | — |
| `GOVERNANCE_ENTRY` | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | 1.0 | Routes agents to branch laws | Competing “read first” lists | `hub_essentials_index` row 2 | — |
| `AUTHORITY_INDEX` | `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` | 1.2 | Law registry + **LAW PURITY POLICY (SSOT)** | Duplicate law tables in companions | `system_roadmap.authorities.index_doc` · `validate-law-purity-ssot-v1.sh` | — |
| `ALIGNMENT` | `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` | 1.1 | Locked source vs suggestions; 12-order procedure | Chat/advisor input (rank 5) | — | — |
| `CRITIC` | `brain-os/law/CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` | 1.1 | GPT/ChatGPT paste = `EXTERNAL_CRITIC` | Subordinate to `ALIGNMENT`; never build steering | `authorities.critic_*` | root stub → `archive/superseded/pointers/` |
| `EDIT_LOCK` | `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` | 1.0 | Who edits SourceA / hub | Agent write attempts | `~/.sina/command-edit-lock.json` | — |
| `HUB_DEACTIVATED` | `SINA_COMMAND_DEACTIVATED_INCIDENT_READ_POLICY_LOCKED_v1.md` | 1.0 | Sina Command brand deactivated · Worker chat + session gate · no read-all-incidents | Legacy hub daily steering · incident compendium | `agent_memory_mirror_v1.py` F18–F22 · `000-dead-law-stubs.mdc` | — |
| `FLEET` | `AGENT_GOVERNANCE_INDEX_LOCKED_v1.md` | 1.0 | Eight private agents, forbidden paths | Per-agent scope | Private agent pages | — |
| `AGENT_JUDGMENT` | `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` | 1.0 | Decision inventory, hierarchy, beneficial line, self-healing | `EXTERNAL_CRITIC`; does not override `ALIGNMENT` or SOURCE | `authorities.agent_judgment_*` | — |
| `NO_FAKE_PROGRESS` | `SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md` | 1.1 | **No fake progress** — proven evidence · meaningful effect · result-driven acts/plans · enterprise-grade ship; UI green ≠ done; form 0 open requires §ANSWERED or SHIP receipt | Chat “done”; form 0 open without apply; batch done; hero green without receipt | `validate-no-fake-progress-form-v1.sh` · `.cursor/rules/no-fake-progress.mdc` | — |
| `INCIDENT_FIX_OWNERSHIP` | `SOURCEA_INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING_LOCKED_v1.md` | 1.0 | **Incident fix matrix** — law audit PASS/FAIL · role ship obligations · founder input cascade · no narrative remediated · stairlift propagation | Partial blame + move on; chat-only law sync; incident close without validator | `validate-incident-fix-ownership-v1.sh` · `validate-founder-input-cascade-v1.sh` · `founder_input_cascade_v1.py` · `.cursor/rules/governance-specialist-in-charge.mdc` | — |
| `INCIDENT_FIX_OWNERSHIP_REPORT` | `SOURCEA_INCIDENT_FIX_OWNERSHIP_REPORT_LOCKED_v1.md` | 1.0 | Report pointer — incident fix ownership body alias | Duplicate matrix prose | — | `INCIDENT_FIX_OWNERSHIP` |
| `OPENROUTER_ACTIVATION` | `SOURCEA_OPENROUTER_ACTIVATION_QUEUE_LOCKED_v1.md` | 1.0 | Phase-strict s1 OpenRouter activation queue — s1 then s7 then s9 | Hub dispatch_ready as activation proof | `build-phase-strict-queue-v1.py` · `phase-strict-drain-v1.json` | `PHASE_STRICT_INBOX` |
| `GOVERNANCE_CENTER` | `SOURCEA_GOVERNANCE_CENTER_SELF_GOVERN_LOCKED_v1.md` | 1.0 | **Self-govern office** — planner next-10 · judge · lawyer counsel · thread · G7 auto-heal · OpenRouter→specialist pipeline | Founder fights drift in chat; center without receipt | `governance_center_run_v1.py` · `validate-governance-center-v1.sh` · `governance_self_heal_daemon_v1.py` | `INCIDENT_FIX_OWNERSHIP` |
| `SUPER_FAST_HUB` | `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` | 1.1 | **Two hubs** — H1 Daily Necessities (zero mistakes) · H2 Machine `/machines/` · Archive frozen; cadence daily/3d/weekly/monthly · no wheel | Legacy as daily · full rebuild refresh · 9MB JSON hero · wheel builds | `validate-super-fast-hub-v1.sh` · `/api/worker-hub/v1` · `integration-fabric-registry-v1.yaml` `two_hub_model` | — |
| `H2_MACHINE_HUB_PLAN` | `SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md` | 1.1 | **phase-s8 backlog** — Hub 2 `/machines/` pending registry · scheduled receipts · **not** Sina Command archive | Sina Command = Hub 1 · patch `/legacy/` for daily · app.js as active plan | `validate-machine-hub-v1.sh` · `validate-h2-pending-honest-count-v1.sh` | `SUPER_FAST_HUB` |
| `NO_HUB_REBUILD_STUCK` | `AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md` | 1.0 | **Agent conduct** — no default strict build / full refresh; ship sa not panel | Worker closeout build-sina · Brain "rebuild hub" · `--full` without gate | `validate-agent-no-hub-rebuild-stuck-v1.sh` · `hub_self_refresh_v1.py --json` | `SUPER_FAST_HUB` |
| `ADVERSARIAL_PROBE` | `SOURCEA_ADVERSARIAL_PROBE_PACK_LOCKED_v1.md` | 1.1 | Hidden founder lines · weeks 8–10 · GAC→deterministic Critic wire | Conversational quizzes before W1 · LLM Critic as truth · SDK fuzz harness | `governance_critic_eval_v1.py` · `validate-governance-critic-v1.sh` | — |
| `RESULT_POLICY` | `SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md` | 1.1 | Hyper-active conduct — disk result, evidence/event-driven, option matrix, golden insight + founder next actions every session | Chat-only advice; passive “you should run”; **subordinate to `NO_FAKE_PROGRESS` on progress claims** | `hub_essentials_index` READ_CHAIN | — |
| `META_REASONING` | `META_REASONING_POLICY_STACK_LOCKED_v1.md` | 1.0 | L0–L12 decision sovereignty umbrella; policy→code map | Pointers only — does not replace topic laws | `authorities.meta_reasoning_stack` | — |
| `GOV_UNIFY` | `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md` | 1.0 | Batch intake: analyze, merge, archive, sync in-charge registry | Executes `ALIGNMENT` Orders 1–12 on batches | — | — |
| `WTM_SEPARATION` | `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md` | 2.0 | WTM vs factory/investor roadmaps | Parallel program roadmaps | `NOT_WTM_ROADMAPS` | v1 → `archive/superseded/wtm/v1/` |
| `WTM_MAP` | `brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` | 5.1 | 33 steps A1–D16 human map | Narrative roadmap drafts | `STEP_CATALOG` + payload | v1–v4 → `archive/superseded/wtm/` |
| `WTM_AUTHORITY` | `WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md` | 1.1 | Graph, memory, planning, packet, C5, B frozen | Step semantics in phase D | `SYSTEM_AUTHORITIES` | — |
| `WTM_HUB_UI` | `HUB_SOURCE_UI_ALIGNMENT_PROCEDURE_LOCKED_v1.md` | 1.0 | SSOT → build → UI alignment | Ad-hoc hub edits | `audit_hub_source_alignment.py` | — |
| `WTM_MIGRATION` | `WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md` | 1.0 | INCIDENT-004 ID history | Legacy D/C/B/A naming | — | — |
| `ACE` | `AUTO_CONFLICT_ENGINE_V3_LOCKED.md` | v3 | DESIGN / EXECUTION / DELIVERY planes | Informal conflict resolution | — | — |
| `HUB_ESSENTIALS` | `SINA_HUB_ESSENTIALS_LOCKED_v1.md` + `hub_essentials_index.py` | 1.1 / v2 | Hub tab map + maintainer read chain | Duplicate nav surfaces | `command-data.json` essentials | — |
| `VALID_YES_VERDICT` | `SOURCEA_VALID_YES_PROGRESS_VERDICT_LOCKED_v1.md` | 1.0 | Honest progress tiers, 57/1000 snapshot, INCIDENT-006 recovery verdict | Chat/monitor/receipt-count-only progress | `receipts/valid-yes-progress-verdict-lock-2026-06-09.json` | — |
| `SYSTEM_MAP_TREE` | `SOURCEA_SYSTEM_MAP_TREE_LOCKED_v1.md` | 1.0 | **Canonical navigation tree** — law/runtime/hub/incidents/lanes; archive = index only | Chat summaries; attachment essays as law | — | — |
| `RUN_INBOX_DISK_TRUTH` | `RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md` | 1.0 | Execution SSOT — run inbox; prompt feed live mirror | Hub snapshot as execution truth | `~/.sina/run-inbox-disk-truth-v1.json` | — |
| `LIVE_ONGOING_PROMPTS` | `SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md` | 1.0 | Live next-10 queue turns · machine delivery gate | Static OpenRouter 10-pack | `~/.sina/live-ongoing-prompts-next-10-v1.json` | — |
| `MONITOR_DISK_LIVE` | `SOURCEA_MONITOR_DISK_LIVE_WIRE_LOCKED_v1.md` | 1.0 | Monitor :13021 disk-wired · 5s sync | Agent refresh of monitor | `~/.sina/monitor-live-v1.json` | — |
| `FOUNDER_AGENTIC_POLICY` | `brain-os/laws/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md` | 1.0 | No Cursor AUTO-RUN P0; agentic commercial; founder never email/call | AUTO-RUN north star docs | `~/.sina/auto-run-disabled-v1.flag` | — |
| `S10_ETERNAL_AUDIT` | `SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md` | 1.0 | Third lane — eternal audit loop, not Cloud Forge Run | REGISTRY drain as S10 | `~/.sina/s10-eternal-manifest-v1.json` | — |
| `FACTORY_CONTROL` | `scripts/factory_control_v1.py` | 1.0 | Conduct machine — FREEZE · stop · spawn gate | Plan todo > ASF STOP | `factory_control` state in module | — |
| `DISK_TRUTH_E2E` | `SOURCEA_DISK_TRUTH_E2E_MATRIX_LOCKED_v1.md` | 1.0 | RT/LAG/GAP matrix · projection vs control · dual-pick FAIL | Archive insight §3 as law | `validate-ecosystem-safety-v1.sh` dual-pick | — |
| `ANTI_STALENESS` | `SOURCEA_ANTI_STALENESS_MACHINE_ENFORCEMENT_PLAN_LOCKED_v1.md` | 1.0 | Permanent anti-staleness latches AS-01..18 | Chat/hub without validator | `validate-anti-staleness-bundle-v1.sh` (Phase 1) | — |
| `SYS_INTEGRITY_100` | `SOURCEA_SYSTEM_INTEGRITY_100_STEP_PLAYBOOK_LOCKED_v1.md` | 1.0 | Whole-system 100-step audit — LAW/MACHINE/PROJECTION · 24 founder forks · conflict + agent governance | Ad-hoc fixes without playbook phase | Canvas `sourcea-system-integrity-100` · `PROGRAM_PROGRESS` `SYS-INTEGRITY-100` | — |
| `FORK_MACHINE` | `SOURCEA_COMPLEX_SITUATION_FORK_MACHINE_LOCKED_v1.md` | 1.0 | Complex/mega/Brain chats — fork inventory · Effect per option · ASF confirm · execute to disk | Vague “confirm recommended”; chat-only multi-fork | `prompts/COMPLEX_SITUATION_FORK_SESSION_PROMPT_LOCKED_v1.md` · `complex_situation_fork_machine_v1.py` | — |
| `FIVE_STEP_APEX` | `SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md` | 1.0 | Apex daily machine — SCAN SAY PICK PROVE SHIP · wraps Fork + 100-step + Layer A | 100-step daily cognitive load; chat-only progress | `prompts/FIVE_STEP_SESSION_PROMPT_LOCKED_v1.md` · `five_step_progress_machine_v1.py` | — |
| `INTEGRITY_BATCH_2` | `SOURCEA_INTEGRITY_STACK_UNIFIED_BLUEPRINT_BATCH_2_LOCKED_v1.md` | 1.0 | Unified integrity stack map — 4 artifacts · SSOT hierarchy · paradox resolutions · order · ASF prefix | Competing interpretations of integrity tools; duplicate prose in chat | `SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md` | — |
| `CROSS_DOC_LINKAGE` | `SOURCEA_CROSS_DOC_LINKAGE_AND_AUDIT_LOCKED_v1.md` | 1.0 | Cross-doc cluster audit — link 10 session docs across time · human vs machine channel · paradox/duplication/dual-language | Fragmented multi-era docs read as competing systems | `INTEGRITY_BATCH_2` · `SESSION-INTEGRITY-10` cluster | — |
| `INCIDENT_022` | `SINA_MAINTAINER_2_STALE_AUTORUN_ADVICE_INCIDENT_022_REPORT_LOCKED_v1.md` | 1.0 | Maintainer stale AUTO-RUN advice — hub latch gap | START AUTO RUN as founder P0 | `validate-hub-p0-no-autorun-v1.sh` | body: `brain-os/incidents/SINA_MAINTAINER_2_STALE_AUTORUN_ADVICE_INCIDENT_022_LOCKED_v1.md` |
| `INCIDENT_027` | `SINA_MAINTAINER_2_DRAIN_PROJECTION_STALENESS_INCIDENT_027_REPORT_LOCKED_v1.md` | 1.0 | Drain/projection staleness after form v2 — hub LAG | sa-XXXX / Valid YES on hero when RT LIVE open | `validate-maintainer-scan-p0-v1.sh` | body: `brain-os/incidents/SINA_MAINTAINER_2_DRAIN_PROJECTION_STALENESS_INCIDENT_027_LOCKED_v1.md` |
| `INCIDENT_030` | `SINA_WORKER_YAML_ONLY_CLOSEOUT_FAKE_GREEN_INCIDENT_030_REPORT_LOCKED_v1.md` | 1.0 | Worker YAML-only closeout fake green — broker receipt gap | REGISTRY done without receipt | `worker_verify_fast_v1.sh` · `validate-broker-receipt-cycle-v1.sh` · `worker_verify_closeout_v1.sh` | body: `brain-os/incidents/SINA_WORKER_YAML_ONLY_CLOSEOUT_FAKE_GREEN_INCIDENT_030_LOCKED_v1.md` |
| `INCIDENT_031` | `SINA_WORKER_IGNORED_ASF_NO_HUB_STOP_STALE_STEERING_INCIDENT_031_REPORT_LOCKED_v1.md` | 1.0 | Worker ignored ASF no-hub stop — stale hub steering | Continue hub lane after ASF stop | `worker_asf_directive_latch_v1.py` · `agent_turn_context_v1.py` | body: `brain-os/incidents/SINA_WORKER_IGNORED_ASF_NO_HUB_STOP_STALE_STEERING_INCIDENT_031_LOCKED_v1.md` |
| `FLEET_HEADLINE_READ` | `SOURCEA_FLEET_HEADLINE_READ_ORDER_LOCKED_v1.md` | 1.0 | Maintainer scan order — JSON before projection | Drain headline on hub hero | `SOURCEA_FLEET_THREAD_ANALYSIS_MAP_LOCKED_v1.md` | INCIDENT-027 |
| `BRAIN_PLATFORM` | `SINA_BRAIN_PLATFORM_UNIFICATION_LOCKED_v1.md` | 1.0 | Brain platform unification — one engine ten outcomes | Fragmented brain strategy docs | `sina_engine_registry_v1.yaml` | — |
| `BRAIN_DUTIES` | `SINA_BRAIN_JOB_TITLES_LOCKED_v1.md` | 1.0 | Brain job titles catalog — 73 DO + 10 NOT | Chat-only duty lists; duplicate title tables | `brain_job_titles_registry_v1.yaml` · companions: `SINA_BRAIN_JOB_TITLES_COMPREHENSIVE_LOCKED_v1.md` · `SINA_BRAIN_JOB_TITLES_DAILY_ONE_PAGE_LOCKED_v1.md` | — |
| `ENGINE_MAP` | `SINA_MULTIDIMENSIONAL_ENGINE_MAP_LOCKED_v1.md` | 1.0 | Multidimensional parallel engine master map | Chat-only architecture summaries | `sina_engine_registry_v1.yaml` | — |
| `THREAD_ACTIVATION` | `SINA_THREAD_ACTIVATION_AND_READINESS_LOCKED_v1.md` | 1.0 | Thread activation + test readiness registry | Lost / untested threads | `thread_activation_registry_v1.yaml` | — |
| `THUNDERFIELD` | `SINA_THUNDERFIELD_VC_LEGAL_RELATIONSHIP_PLATFORM_LOCKED_v1.md` | 1.0 | VC legal protection + relationship platform brand | Competing VC surface names | `thunderfield_phases_and_toolpack_v1.yaml` | — |
| `COMM_PARTNER` | `AI_INFRA_PARTNERSHIP_PROPOSALS_LOCKED_v1.md` | 1.0 | AI infra partner wedge · Phase A/B/C apply order · 10-partner matrix grades | v1/v2 chat apply order; critic reorder of P0 | `PROGRAM_PROGRESS.json` `COMM-PARTNER-BOOT` | — |
| `RESEARCH_SAVE` | `RESEARCH_INTAKE_AND_SAVE_LOCK_LOCKED_v1.md` | 1.0 | Mandatory RESEARCH mirror + enforcer before closeout | Chat-only research; `archive/attachments/` intake | `research_save_enforcer.py` | — |
| `INCIDENT_CORPUS` | `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` | 1.1 | All root incident reports — index + room; not per-report law rows | Duplicate incident law rows at root | `ecosystem_incidents_index.py` · `LOCKED_ROOT_INCIDENT_REPORTS` | — |
| `AGENT_ECOSYSTEM` | `AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md` | 1.0 | Agent surface unification — ecosystem parent | Per-agent duplicate policy prose | `agent_rules_in_charge.py` | — |
| `AGENT_COUNCIL` | `AGENT_COUNCIL_ROOM_LOCKED_v1.md` | 1.0 | Council room protocol | Ad-hoc council threads | — | — |
| `AGENT_MIND_SHARE` | `AGENT_MIND_SHARE_LOCKED_v1.md` | 1.0 | Cross-agent learning share | Duplicate mind-share essays | — | — |
| `AGENT_APP_HUB` | `AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md` | 1.0 | App-as-unifying-hub pattern | Fragmented app entry docs | — | — |
| `AGENT_APP_BLUEPRINT` | `AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md` | 1.0 | Application use blueprint | Competing app blueprints | — | — |
| `AGENT_RULES_CHARGE` | `AGENT_RULES_IN_CHARGE_LOCKED_v1.md` | 1.0 | Rules-in-charge loop | Stale rules tables in chat | `agent_rules_in_charge.py` | — |
| `AGENT_SCOREBOARD` | `AGENT_SCOREBOARD_LOCKED_v1.md` | 1.0 | Agent scoreboard law | Hub-only score guesses | `agent_scoreboard.py` | — |
| `AGENT_CONTROL_PANEL` | `AGENT_CONTROL_PANEL_SPEC_LOCKED_v1.md` | 1.0 | Agent control panel spec | Ad-hoc panel drafts | — | — |
| `AGENT_ESSAY` | `AGENT_ESSAY_DISCOURSE_LOCKED_v1.md` | 1.0 | Essay discourse surfaces | Chat-only discourse | `agent_essay_discourse.py` | — |
| `AGENT_VAULT` | `AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md` | 1.0 | Workspace vault middle layer | Duplicate vault prose | — | — |
| `AGENT_SPRINT` | `AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md` | 1.0 | Ecosystem sprint consolidation | Parallel sprint memos | — | — |
| `AGENT_OPERATING_ROLES` | `AGENT_OPERATING_ROLES_LOCKED_v1.md` | 1.0 | Agent operating roles | Role drift in chat | — | — |
| `AGENT_SKILLS` | `AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md` | 1.0 | Skills + research pipeline | Duplicate skill lists | — | — |
| `AGENT_MERGEPACK_NOTE` | `AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md` | 1.0 | MergePack is not an agent | Treating MergePack as agent | — | — |
| `AGENT_INCIDENT_ROOM` | `SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md` | 1.0 | Incident room weekly law | Chat-only incident summaries | `~/.sina/incident-room/` | — |
| `SINA_COMMAND_FOUNDER` | `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` | 1.0 | No-terminal founder command | Terminal-first founder flows | — | — |
| `SINA_COMMAND_GUIDE_ROW` | `SINA_COMMAND_GUIDE_LOCKED_v1.md` | 1.0 | Sina Command guide | Duplicate hub guides | — | — |
| `PROMPT_OS_CORE` | `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md` | 1.0 | Prompt OS core final decision | Competing Prompt OS drafts | — | — |
| `PHASE1_FREEZE` | `SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md` | 1.0 | Phase 1 stabilization only | Phase 2 scope creep | — | — |
| `EXECUTION_TRUTH` | `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` | 1.0 | Execution truth layer | Hub snapshot as truth | — | — |
| `PARALLEL_LANES` | `SINAAI_PARALLEL_LANES_NO_BLOCK_PROGRESS_LOCKED_v1.md` | 1.0 | Parallel lanes — no block progress | Serial lane blocking | — | — |
| `PROMPT_OS_SYSTEM` | `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` | 1.0 | Prompt OS system surface | Duplicate prompt OS tables | — | — |
| `DISPATCH_POLICY` | `DISPATCH_POLICY_LOCKED_v1.md` | 1.0 | Dispatch policy | Ad-hoc dispatch rules | — | — |
| `SINA_RUNTIME_STACK` | `SINA_RUNTIME_STACK_LOCKED_v1.md` | 1.0 | Runtime stack law | Chat runtime guesses | — | — |
| `LLM_CONTEXT_PACKET` | `LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md` | 1.0 | LLM context packet schema | Ad-hoc packet shapes | — | — |
| `GOV_DRIFT` | `GOVERNANCE_DRIFT_ENGINE_LOCKED_v1.md` | 1.0 | Governance drift detection | Manual drift audits only | `governance_drift_engine.py` | — |
| `DOC_SEQUENCE` | `SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md` | 1.0 | Document chronology registry | Chronology as authority | — | — |
| `DOC_LIBRARY_INDEX` | `ECOSYSTEM_IMPORTANT_DOCS_INDEX_LOCKED_v1.md` | 1.0 | Important docs library index | Duplicate doc lists | `important_docs_index.py` | — |
| `ENFORCE_BYPASS` | `ENFORCE_BYPASS_MAP_LOCKED_v1.md` | 1.0 | Enforce bypass map | Hidden bypass paths | — | — |
| `TRUST_LEDGER` | `TRUST_LEDGER_SCHEMA_LOCKED_v1.md` | 1.0 | Trust ledger schema | Ad-hoc event logs | — | — |
| `PLAN_STATUS_VOCAB` | `PLAN_STATUS_VOCAB_LOCKED_v1.md` | 1.0 | Plan status vocabulary | Ambiguous plan states | — | — |
| `ASF_PROGRESS` | `ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md` | 1.0 | Program progress command center | Chat-only progress | `PROGRAM_PROGRESS.json` | — |
| `ASF_THREADS` | `ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md` | 1.0 | Program threads registry | Parallel unnamed threads | — | — |
| `FOUNDER_TRACKING` | `FOUNDER_FIRST_ASSISTANT_TRACKING_LAW_LOCKED_v1.md` | 1.0 | Founder request tracking | Lost founder orders | `founder_request_tracker.py` | — |
| `FOUNDER_SAVE_LOCK` | `FOUNDER_SAVE_AND_LOCK_IMMEDIATE_APP_LAW_LOCKED_v1.md` | 1.0 | Save and lock immediate app law | Chat-only SAVE | — | — |
| `ASF_MILESTONE_GLOSSARY` | `ASF_MILESTONE_GLOSSARY_LOCKED_v1.md` | 1.0 | ASF milestone glossary | Ambiguous M8/M10 labels | — | — |
| `E2E_DEBUGGER` | `SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md` | 1.0 | E2E debugger playbook | Ad-hoc E2E steps | — | — |
| `REF_CONSTELLATION` | `SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md` | 1.0 | Reference architecture constellation | Chat architecture summaries | — | — |
| `EXECUTION_LAW` | `SOURCEA_EXECUTION_LAW_LOCKED_v1.md` | 1.0 | SourceA execution law | Competing execution memos | `ACTIVE_NOW.md` | — |
| `CURSOR_RULES_MAP` | `SOURCEA_CURSOR_RULES_AND_SKILLS_MAP_LOCKED_v2.md` | 1.0 | Cursor rules and skills map | Duplicate rules tables | — | — |
| `GOLDEN_SAFETY` | `SOURCEA_GOLDEN_INSIGHT_AND_SAFETY_LOCKED_v1.md` | 1.0 | Golden insight and safety | Chat-only safety tips | — | — |
| `MARKET_RECEIPT_ARCH` | `SOURCEA_MARKET_RECEIPT_ARCHITECTURE_LOCKED_v1.md` | 1.0 | Market receipt architecture | Ad-hoc receipt shapes | — | — |
| `FOUNDER_PINNED` | `SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md` | 1.0 | Founder pinned actions | Stale pinned lists | — | — |
| `MASTER_SESSION_MANIFEST` | `SOURCEA_MASTER_SESSION_MANIFEST_LOCKED_v1.md` | 1.0 | Master session manifest | Fragmented session indexes | — | — |
| `PHASE_STRICT_INBOX` | `SOURCEA_PHASE_STRICT_RUN_INBOX_LOCKED_v1.md` | 1.0 | Phase strict run inbox | Hub inbox as SSOT | `RUN_INBOX_DISK_TRUTH` | — |
| `PHASE_PACK_SUMMARY` | `SOURCEA_PHASE_PACK_PINNED_SUMMARY_LOCKED_v1.md` | 1.0 | Phase pack pinned summary | Duplicate phase packs | — | — |
| `PACK_AUDIT_JUDGE` | `SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md` | 1.0 | 1000-pack audit judge | Chat pack audits | — | — |
| `WORKER_E2E_POSTMORTEM` | `SOURCEA_WORKER_E2E_POSTMORTEM_LOCKED_v1.md` | 1.0 | Worker E2E postmortem | Ad-hoc worker retros | — | — |
| `CROSS_LANE_EDIT` | `CROSS_LANE_EDIT_FORBIDDEN_LOCKED_v1.md` | 1.0 | Cross-lane edit forbidden | Lane-cross edits | — | — |
| `LAYER_A` | `SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md` | 1.0 | Personal database Layer A | Cloud Layer A before SSOT | — | — |
| `NOETFIELD_CLOUD` | `NOETFIELD_CLOUD_GIT_AND_AGENT_ENTRY_UNIFIED_LOCKED_v1.md` | 1.1 | Noetfield cloud entry — **local-only until Layer A SSOT** (Phase 2 pick 2.07-B) | Premature cloud deploy | — | — |
| `INCIDENT_LAW_BRAIN_WORKER` | `SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md` | 1.0 | Brain/worker lane cross incident law | `INCIDENT_CORPUS` report only | — | — |
| `INCIDENT_LAW_CROSS_LANE` | `SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md` | 1.0 | Cross-lane edit incident law | Report-only handling | — | — |
| `INCIDENT_LAW_GOAL1_PROOF` | `SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md` | 1.0 | Goal 1 unvalidated proof incident law | Root report only (`INCIDENT_CORPUS`) | `brain-os/incidents/` body | — |
| `HUB_E2E_CANCELLED` | `SINA_HUB_E2E_CANCELLED_LOCKED_v1.md` | 1.0 | Hub E2E cancelled — quarantine posture | Live hub E2E as P0 | — | — |
| `HUB_LITE_REBUILD` | `HUB_LITE_REBUILD_PHASE0_LOCKED_v1.md` | 1.0 | Hub lite rebuild Phase 0 — light Refresh default · shell boot · tab slices | Full monolith prefetch · command-data.json fallback | `hub_self_refresh_v1.py` · `hub_light_refresh` | — |
| `HUB_WORKER_ONLY` | `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` | 1.0 | Worker Hub default · monolith archived at /legacy/ | Daily 9MB monolith · extending app.js | `worker_hub_v1.py` · `worker-hub/index.html` | — |
| `FAST_SYSTEM_LOAD` | `SOURCEA_FAST_SYSTEM_LOAD_BUDGET_LOCKED_v1.md` | 1.0 | Load tiers L0–L4 — wall-time budgets per lane | Full fleet verify every Worker turn | `worker_verify_ultra_v1.sh` · `worker_verify_fast_v1.sh` | `HUB_LITE_REBUILD` · `WORKER_VERIFY_FAST` |
| `DEVBRIDGE_EXT_300` | `DEVBRIDGE_EXTENSION_NO_CODE_300_STEP_PLAN_LOCKED_v1.md` | 2.1 | DevBridge 300-step unified plan — B+C Week 1 | Parallel extension plans | `pick-devbridge-ext-step.py` · `brain-os/plan-registry/devbridge-extension-300/` | — |
| `WORKER_VERIFY_FAST` | `WORKER_NO_SLOW_VERIFY_SHELL_LOCKED_v1.md` | 1.0 | Worker VERIFY fast lane — no default full FCB | Full `find_critical_bugs` on every sa closeout | `worker_verify_ultra_v1.sh` · `worker_verify_fast_v1.sh` | — |
| `WORKER_AS_HEAL` | `WORKER_FAST_ANTI_STALENESS_AUTO_HEAL_LOCKED_v1.md` | 1.0 | Worker fast anti-staleness auto-heal on loop | Full AS bundle every turn | `worker_anti_staleness_heal_v1.py` | — |
| `COMMERCIAL_WORKER` | `SOURCEA_COMMERCIAL_WORKER_LOOP_LOCKED_v1.md` | 1.0 | Commercial Worker hot path — thin broker + ultra verify | Full fleet every turn | `validate-commercial-worker-loop-v1.sh` | — |
| `COMMAND_UI_PLAYFUL` | `SINA_COMMAND_UI_PLAYFUL_LOCKED_v1.md` | 1.0 | Command UI playful layer | Competing UI law | — | — |
| `SEMI_SEPARATE_NOTICE` | `SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md` | 1.0 | Semi-separate agent notice | Full-merge agent policy | — | — |
| `CURSOR_FIND_BUGS` | `CURSOR_FIND_BUGS_AUTOMATION_LOCKED_v1.md` | 1.0 | Find-bugs automation law | Manual-only bug hunts | `find_critical_bugs.py` | — |
| `HUB_PROOF_UX` | `HUB_PROOF_UX_P0_LOCKED_v1.md` | 1.0 | Hub proof UX P0 | Ad-hoc proof flows | — | — |
| `IPHONE_CLOUD_SPEC` | `IPHONE_CLOUD_ORGANIZATION_SPEC_LOCKED_v1.md` | 1.0 | iPhone cloud organization spec | Duplicate cloud specs | — | — |
| `AGENT_VERBS` | `AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md` | 1.0 | Agent verbs — save/work/edit | Ad-hoc verb tables | — | — |
| `AGENT_FOUNDER_BASH` | `AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md` | 1.0 | Founder bash communication law | Terminal founder comms | — | — |
| `AGENT_RULE_CONFLICT_AUDIT` | `AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md` | 1.0 | Rule conflict and stale truth audit | Chat-only audits | — | — |
| `PROMPT_OS_MVP_ORDER` | `PROMPT_OS_CORE_MVP_BUILD_ORDER_LOCKED_v1.md` | 1.0 | Prompt OS MVP build order | Competing build orders | — | — |
| `ARCHITECT_V2` | `SINAAI_ARCHITECT_V2_INDUSTRIAL_POLICY_LOCKED_v1.md` | 1.0 | Architect v2 industrial policy | Legacy architect drafts | — | — |
| `PERMANENT_ARCHITECT` | `SINAAI_PERMANENT_ARCHITECT_AGENT_LOCKED_v1.md` | 1.0 | Permanent architect agent | Ad-hoc architect roles | — | — |
| `PHASE2_AI_EXEC` | `SINAAI_PHASE2_AI_CONTROLLED_EXECUTION_LOCKED_v1.md` | 1.0 | Phase 2 AI-controlled execution | Phase 1 scope bleed | — | — |
| `ASF_MASTER_ORDERS` | `ASF_MASTER_ORDERS_ORGANIZED_LOCKED_v1.md` | 1.0 | ASF master orders organized | Scattered order lists | — | — |
| `FOUNDER_NO_CC` | `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` | 1.0 | Founder no credit card infra | Credit-card-first infra | — | — |
| `GOV_UNIFY_BATCH` | `SOURCEA_AUTHORITY_REGISTRY_GOV_UNIFY_BATCH_2026-06-11_LOCKED_v1.md` | 1.0 | Authority registry batch manifest | Ad-hoc registry edits | `authority_root_coverage_audit.py` | — |
| `PHASE2_PICK_RECEIPT` | `SOURCEA_PHASE2_INTEGRITY_PICK_RECEIPT_2026-06-11_LOCKED_v1.md` | 1.0 | Phase 2 integrity founder pick receipt | Chat-only pick memory | `SYS_INTEGRITY_100` | — |
| `TERMINOLOGY_DICT` | `SOURCEA_FOUNDER_MACHINE_TERMINOLOGY_DICTIONARY_LOCKED_v1.md` | 1.0 | Founder ↔ machine dictionary · SSOT find algorithm · enforcer index | Duplicate glossaries in chat | `governance_completion_backlog_audit.py` | — |
| `FOUNDER_DIRECTION_TERMS` | `SOURCEA_FOUNDER_DIRECTION_TERMINOLOGY_LOCKED_v1.md` | 1.0 | Direction apex · 3.07 NO · forbidden copy FT-01..12 · parallel tracks | Chat refine-everything without PICK | `COPY_SAFETY` registry · DIRECTION-LOCK-040 | — |
| `FOUNDER_LANGUAGE_CORPUS` | `SOURCEA_FOUNDER_MACHINE_TERMINOLOGY_DICTIONARY_LOCKED_v1.md` | 3.0 | Founder language corpus §3.4 · vault `archive/attachments/founder-language/FOUNDER_LANGUAGE_CORPUS_v3/` · M1 research | Chat-only founder vocabulary · paste-ritual drift | `validate-copy-safety-hub-v1.sh` · `TERMINOLOGY_DICT` §3.4 | `FOUNDER_DIRECTION_TERMS` |
| `LIVE_GOV_BP` | `SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md` | 1.0 | P0–P7 tiers · need/don’t · propagation · zero-latency target | Chat big-picture without tiers | `governance_propagation_cascade_v1.py` | — |
| `FULL_LAYERED_PLAN` | `brain-os/system/SOURCEA_FULL_LAYERED_CONTROL_PLAN_LOCKED_v1.md` | 1.0 | **Unified big picture** — 9-layer control stack · central engines · parallel portfolio · ENFORCEMENT-6MO placement | Fragmented chat big-picture without layer glossary | `GOVERNED_EXECUTION_OS_MASTER` · `MASTER_OPERATING_TRACKER` §4 | — |
| `SSOT_FOUNDATION` | `SOURCEA_SSOT_FOUNDATION_WRITING_GUIDE_LOCKED_v1.md` | 1.0 | **Human** foundation — why hierarchies · subject→SSOT→blueprint · first-egg model | Duplicate META_REASONING L0–L12 prose | `META_REASONING` §9 pointer | — |
| `MASTER_CATALOG` | `SOURCEA_ECOSYSTEM_MASTER_CATALOG_LOCKED_v1.md` | 1.0 | Everything on one page — threads · rows · enforcers · live vs paper | Chat inventory without catalog | `ecosystem_master_catalog_v1.py` | — |
| `LOST_LINK_ETHICS` | `SOURCEA_LOST_LINK_RECOVERY_ETHICS_LOCKED_v1.md` | 1.0 | Lost-link recovery — transcript + disk search · FOUND report = complete reward | Tail-summary without message pass | `.cursor/rules/lost-link-recovery-reward.mdc` | — |
| `FROZEN_REVIVAL` | `SOURCEA_FROZEN_ARCHIVE_REVIVAL_AUDIT_LOCKED_v1.md` | 1.0 | Frozen/archive corpus — what to revive · what stays blocked | Injecting ARCHIVE as law | `002-sot-hierarchy-registry` · `validate-no-archive-as-law-v1.sh` | — |
| `CONSCIOUS_RECOVERY` | `agent-skills/shared/conscious-recovery/SKILL.md` | 1.0 | Cursor skill — lost-link routine · FOUND format · pairs self-audit | Chat-only recovery without skill | `sync-cursor-agent-skills.sh` · `MANDATORY_READ_BY_ROLE` v1.3 | `LOST_LINK_ETHICS` |
| `NARRATIVE_BRIDGE` | `brain-os/narrative-bridge/NARRATIVE_BRIDGE_TOUCH_BASE_LOCKED_v1.md` | 1.0 | **Human comfort** — megachat translator → `LATEST_TOUCH_BASE` · light chat bootstrap | Re-teaching narrative in every new chat | `validate-narrative-bridge-v1.sh` · `sina-narrative-translator` | `TERMINOLOGY_DICT` · `TODAY_CLOSEOUT` |
| `TODAY_CLOSEOUT` | `SOURCEA_TODAY_SESSION_UNIFIED_CLOSEOUT_RECEIPT_2026-06-11_LOCKED_v1.md` | 1.0 | **2026-06-11 unified receipt** — nothing left behind · full wire map · FOUND list | Chat-only session memory | `ecosystem_master_catalog_v1.py` | `MASTER_CATALOG` §2 |
| `LIVE_DECISION_FORM` | `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` | 1.0 | **Live founder form** — answered · Canvas open · pending ledger · open questions | Chat-only conflict memory | `live_founder_decision_form_v1.py` | `FOUNDER_MSG_NORM` |
| `JUDGE_CENTER` | `SINA_JUDGE_STACK_LOCKED_v1.md` | 1.0 | **Judge Center** — RIGHT/STALE/BAD · temporal law · alarm strip P0–P3 | Chat verdict tables as law | `judge_center_run_v1.py` · `~/.sina/judge-center/` | `SOURCEA_GOV_PICK_BATCH_2026-06-12` |
| `THREAD_ROOM` | `SINA_THREAD_ROOM_LOCKED_v1.md` | 1.0 | **Thread Room** — THREAD-* map · T30 continuity · scout/cartographer/curator | Judge Center thread duties | `thread_room_run_v1.py` · `~/.sina/thread-room/` | `SOURCEA_GOV_PICK_BATCH_2026-06-12` |
| `AGENT_MEMORY_MIRROR` | `AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md` | 1.0 | **Memory mirror** — session gate · disk before edit · mirror receipts | Chat memory as SSOT | `agent_session_gate_run_v1.py` · `~/.sina/agent-memory-mirror-v1.json` | `Q-AGENT-MEMORY-ENFORCE` |
| `AGENT_EXECUTOR_DAILY_DUTY` | `AGENT_EXECUTOR_DAILY_DUTY_CARD_LOCKED_v1.md` | 1.0 | **Daily duty card** — D01–D22 founder reminders · session inject · never re-remind | Chat-only standing orders | `agent_daily_duty_card_v1.py` · `~/.sina/agent-executor-daily-duty-card-v1.json` · `.cursor/rules/agent-daily-duty-card.mdc` | `AGENT_MEMORY_MIRROR` |
| `AGENTIC_ENFORCEMENT_V2` | `SOURCEA_AGENTIC_ENFORCEMENT_STACK_LOCKED_v2.md` | 2.0 | **Agentic enforcement v2** — conduct gate · read order · G7 discipline · spine `AGENT_SESSION_GATE` | Validator chains in chat · blind G7 heal | `agentic_conduct_gate_v1.py` · `validate-agentic-enforcement-stack-v2-v1.sh` | `AGENT_MEMORY_MIRROR` |
| `AGENTIC_LAYER_STACK` | `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md` | 2.0 | **Agentic layer stack** — L0 ASF+Hub · L1 Brain→Gov→Commercial→Brief · L2 Worker→R2→M2→M3 · L3 repos | Chat-only layer order · parallel stacks | `l1_agent_pipeline_wire_v1.py` · `brain_governance_wire_v1.py` · `validate-l1-agent-pipeline-v1.sh` | `AGENTIC_ENFORCEMENT_V2` |
| `FOUNDER_MSG_NORM` | `SOURCEA_FOUNDER_MESSAGE_NORMALIZATION_LOCKED_v1.md` | 1.0 | **CAPS = non-caps** · ASF order normalize | Case-sensitive reject of PICK | `live_founder_decision_form_v1.py` | `LIVE_DECISION_FORM` |
| `GOV_EVENT_SPINE` | `SOURCEA_GOVERNANCE_EVENT_SPINE_SCHEMA_LOCKED_v1.md` | 1.0 | **G1+G2 runtime kernel** — spine ledger · reference graph · impact scan | Chat-only state sync | `validate-governance-event-spine-v1.sh` | `LIVE_GOV_BP` |
| `ENFORCEMENT_6MO_SUPERSESSION` | `SINA_ENFORCEMENT_6MO_LAW_SUPERSESSION_LOCKED_v1.md` | 1.0 | **6mo conflict resolution** — void manual commercial · supersede stale plans | Citing MASTER-PLAN weeks 1–6 as execution | `ENFORCEMENT_6MO_INVESTOR_WIN` · weekly plan v1.1 | `ENFORCEMENT_6MO_PRESERVED_SPIRIT` |
| `ENFORCEMENT_6MO_PRESERVED_SPIRIT` | `SINA_ENFORCEMENT_6MO_PRESERVED_SPIRIT_AND_LINEAGE_LOCKED_v1.md` | 1.0 | **Lineage transfer** — spirit of superseded docs · effort preserved · distorted sentences only void | Deleting MASTER/VC/advisory as forgotten | `ENFORCEMENT_6MO_SUPERSESSION` · weekly Annex A | — |
| `P0_PORTFOLIO_AUTOMATION` | `SINA_P0_PORTFOLIO_AUTOMATION_AND_EVIDENCE_LAW_LOCKED_v1.md` | 1.0 | Agentic 24/7 surfaces · precedent-only · pillar A+B | Manual founder outreach default | `FOUNDER_AGENTIC_POLICY` · `SINA_AUTOMATION_SPINE_AND_N8N` | `ENFORCEMENT_6MO_SUPERSESSION` |
| `SOURCEA_PORTFOLIO_SSOT` | `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` | 3.2 | **Unified winner** — portfolio · **runs + sells governed agentic automation** · buyer · commercial · demo · energy · UI | Chat/backend-only · governance-only-without-agents · blueprint drafts | `ENFORCEMENT_6MO_INVESTOR_WIN` · `UNIFIED_ENGINE_STORY` · ENG-05 | `SOURCEA_COMPANY_INFRA_BUYER_AND_POSITION_SSOT_LOCKED_v1.md` |
| `UNIFIED_ENGINE_STORY` | `SINA_UNIFIED_ENGINE_STORY_LOCKED_v1.md` | 1.0 | **One narrative** — SourceA engine · Part 1/2/3 · lanes · references | Hundred parallel stories in chat | `SOURCEA_PORTFOLIO_SSOT` · `ENFORCEMENT_PORTFOLIO_DECISION_FORM` · PRESERVED_SPIRIT | — |
| `ENFORCEMENT_PORTFOLIO_FORM` | `SINA_ENFORCEMENT_PORTFOLIO_DECISION_FORM_LOCKED_v1.md` | 1.0 | Locked vs open decisions · priority formula · investigation index | Re-asking ENG-01..29 in chat | `LIVE_DECISION_FORM` · `UNIFIED_ENGINE_STORY` | — |
| `THREE_ZONE_HUB_SPINE` | `SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md` | 1.0 | Three-zone hub spine A daily · B maintainer · C museum | Unqualified Hub · command-data SSOT | `SUPER_FAST_HUB` · INCIDENT-032/033 | — |
| `DISK_LIVE_WIRE_FIRST` | `AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md` | 1.1 | Disk live wire first — factory_now_line · auto sync | Parallel prohibition vocabulary | `disk_live_wire_sync_v1.py` · `anti_staleness_auto_wire_v1.py` | — |
| `AS_AUTO_WIRE` | `SOURCEA_ANTI_STALENESS_AUTO_WIRE_LAYER_SYNC_LOCKED_v1.md` | 1.0 | Anti-staleness auto wire L0.5→L1→L2 orchestrator | Manual layer sync per session | `anti_staleness_auto_wire_v1.py` | `ANTI_STALENESS` |
| `AGENT_TERMINAL_CLOSEOUT` | `AGENT_TERMINAL_CLOSEOUT_LOCKED_v1.md` | 1.1 | Terminal CART closeout — Brain owns Mac health | Shell leaks without closeout | `background-terminal-cart-check.mdc` | — |
| `FOUNDER_MUSEUM` | `FOUNDER_MUSEUM_READ_ONLY_RESTORE_LOCKED_v1.md` | 1.0 | Museum ZONE C browse-only restore | Agent museum URL audits | INCIDENT-032 | `THREE_ZONE_HUB_SPINE` |
| `HONEST_P0_SCREEN` | `HONEST_P0_SCREEN_LOCKED_v1.md` | 1.0 | Honest P0 screen — ZONE A receipt pointer | command-data hero | `honest_p0_screen_v1.py` | `THREE_ZONE_HUB_SPINE` |
| `N8N_AUTOMATION_PLAN` | `N8N_AUTOMATION_EXECUTION_PLAN_LOCKED_v2.md` | 2.0 | N8N automation execution plan | Ad-hoc n8n wiring | — | — |
| `N8N_FOUNDER_CARD` | `N8N_FOUNDER_MASTER_CARD_LOCKED_v1.md` | 1.0 | N8N founder master card | Duplicate n8n founder cards | — | — |
| `EXECUTOR_IN_CHARGE` | `SOURCEA_EXECUTOR_IN_CHARGE_NO_HANDOFF_LOCKED_v1.md` | 1.0 | Executor in charge — no Terminal handoff to founder | Founder shell paste steps | — | `SINA_COMMAND_FOUNDER` |
| `GOV_META_AUDIT` | `SOURCEA_GOV_META_AUDIT_LOCKED_v1.md` | 1.0 | Governance meta audit | Chat-only gov audits | — | `GOVERNANCE_CENTER` |
| `ICP_MARKET_IDENTITY` | `SOURCEA_ICP_MARKET_IDENTITY_LOCKED_v1.md` | 1.0 | ICP market identity | Chat market positioning | `SOURCEA_PORTFOLIO_SSOT` | — |
| `STALE_ADVICE_POLICY` | `STALE_ADVICE_RESULTS_POLICY_OWNERSHIP_TRACKING_LOCKED_v1.md` | 1.0 | Stale advice results policy ownership | Chat-only stale advice tracking | `RESULT_POLICY` | — |
| `POISON_TRACKING` | `SINA_POISON_TRACKING_METHOD_LOCKED_v1.md` | 1.0 | PT-METHOD poison writer hunt + wire proof | Chat poison debate | INCIDENT-028 · 034 | `INCIDENT_FIX_OWNERSHIP` |
| `RETIRE_SINA_COMMAND` | `ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md` | 1.0 | **Retire Sina Command forever** — H1+H2 only · `/legacy/` not served · monolith `archive/` audit only | Daily museum · Sina Command brand · `/legacy/` founder path | `archive/hub-monolith-legacy-2026-06/README.md` | `HUB_DEACTIVATED` · `THREE_ZONE_HUB_SPINE` |
| `ASF_100_NEXT_PLANS` | `ASF_100_NEXT_PLANS_ENTERPRISE_SHIP_LOCKED_v1.md` | 1.0 | **100 next plans** enterprise ship queue — active Maintainer backlog | Archive copy as live queue | `NO_FAKE_PROGRESS` · H1 policy link | — |
| `N8N_COMMERCIAL_GRADE` | `N8N_COMMERCIAL_GRADE_LOCKED_v1.md` | 1.0 | n8n commercial grade — SKU outcome receipts not glue PASS | "automation PASS" as revenue proof | `n8n_commercial_grade_v1.py` · `SOURCEA_PORTFOLIO_SSOT` | `N8N_AUTOMATION_PLAN` |
| `CONTROL_PLANE_200` | `SOURCEA_CONTROL_PLANE_200_PLAN_LOCKED_v1.md` | 1.1 | Control plane 200 plan — governed execution OS market map | Scattered PLAN cards without branch index | `CONTROL_PLANE_200_BRANCH` · `SOURCEA_PORTFOLIO_SSOT` | — |
| `CONTROL_PLANE_200_BRANCH` | `SOURCEA_CONTROL_PLANE_200_PLAN_BRANCH_INDEX_LOCKED_v1.md` | 1.0 | 200-plan branch index → 14 buckets under `archive/attachments/commercial_goal_specialist/sina_os/branches/` | Duplicate plan tables at root | `CONTROL_PLANE_200` | — |
| `ORCHESTRATOR_PARTNER` | `SOURCEA_ORCHESTRATOR_PARTNER_INTEGRATION_LOCKED_v1.md` | 1.0 | Orchestrator partner policy — embed not compete | LangGraph/n8n as enemy framing | `REF_CONSTELLATION` · `SOURCEA_PORTFOLIO_SSOT` | — |
| `VIDEO_HERO_PIPELINE` | `SOURCEA_COMMERCIAL_VIDEO_HERO_PIPELINE_LOCKED_v1.md` | 1.0 | Commercial video hero — Screen Studio → polish → Remotion variants | Runway-only hero · Hormozi-text fiction | `w1_film_ingest_master_v1.py` · `skill-commercial-film-factory` | `MARKET_RECEIPT_ARCH` |
| `INTEGRATION_LEVERAGE` | `SOURCEA_INTEGRATION_LEVERAGE_STRATEGY_LOCKED_v1.md` | 1.0 | Integration & partnership leverage — GTM channel not second brain | Tool sprawl as execution SSOT | `data/integration-leverage-registry-v1.json` · Linear GOV SOURCEA | `ORCHESTRATOR_PARTNER` · `REF_CONSTELLATION` |
| `DISCLOSURE_LADDER` | `docs/SOURCEA_DISCLOSURE_LADDER_AND_PUBLIC_VOICE_LOCKED_v1.md` | 1.1 | Tiered public voice · outbound audit · ICP perimeter | Architecture dump in T0/T1 copy | `data/disclosure-ladder-v1.json` · `scripts/disclosure_ladder_v1.py` | `INTEGRATION_LEVERAGE` · `TIER_PRIORITY_COST` |
| `MCP_STACK_FREE_TIER` | `docs/SOURCEA_MCP_STACK_FREE_TIER_OPTIMIZATION_LOCKED_v1.md` | 1.1 | Free-tier MCP first — assist execution never replace RUN INBOX | Paid MCP before ROI gate | `data/mcp-stack-free-tier-v1.json` · `scripts/mcp_stack_free_tier_v1.py` | `INTEGRATION_LEVERAGE` · `DISCLOSURE_LADDER` · `FOUNDER_NO_CREDIT_CARD_INFRA` |
| `NW1_BATTLE_CARD` | `NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md` | 1.0 | NW1 outbound battle card — email + discovery | Chat-only pitch prose | `SOURCEA_PORTFOLIO_SSOT` §16 · `ONEPAGER_MERGED_EXTERNAL` | — |
| `ONEPAGER_MERGED_EXTERNAL` | `NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_MERGED_EXTERNAL_v1.md` | 1.0 | NW1 attach — merged 2 PAGER intake + locked NF-RD | Raw desktop v1 alone | `NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_LOCKED_v1.md` · `validate-noetfield-onepager-merge-v1.sh` | — |
| `ASSET_B_DFY` | `SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md` | 1.0 | Asset B — DFY governed agentic automation · fastest cash SKUs | Generic freelancer agent pitch | `governed_agentic_automation_offer_v1.py` · `SOURCEA_PORTFOLIO_SSOT` §2c | — |
| `COMMERCIAL_SENDER` | `SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md` | 1.0 | Outbound From addresses — hello@sourcea.app · no personal email | Founder Gmail on Asset B/SW1 | `send_ab1_single_v1.py` · `ASSET_B_DFY` | — |
| `CHAIN_TOOLS_PUBLISH` | `SOURCEA_CHAIN_TOOLS_PUBLISH_LOCKED_v1.md` | 1.0 | Graphify-class chain tools — sourcea-boot PyPI · SW1 unlock | "We built an agent" hero | `packages/sourcea-boot` · `validate-sourcea-boot-v1.sh` | — |
| `NW1_PILOT_ONEPAGER` | `NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_LOCKED_v1.md` | 1.0 | Founding customer pilot onepager — buyer attach | Ad-hoc PDF without SSOT row | `NW1_BATTLE_CARD` | — |
| `NF_INTELLIGENCE_613` | `docs/NOETFIELD_INTELLIGENCE_613_PLAN_LOCKED_v1.md` | 1.0 | Noetfield Intelligence 613 — vertical consulting + SaaS primary GTM | Copilot-only posture with zero clients | `NF_INTELLIGENCE_LANDING` · `SOURCEA_PORTFOLIO_SSOT` §7b · blueprint TSX | — |
| `NF_INTELLIGENCE_LANDING` | `docs/NOETFIELD_INTELLIGENCE_LANDING_ONEPAGER_v1.md` | 1.0 | Noetfield.com Intelligence hero + nav demotion copy | React blueprint shell as production homepage | `NF_INTELLIGENCE_613` | — |

---

## Topic → single canonical (no duplicate prose)

| Topic | Canonical only | Pointers allowed (no restate) |
|-------|----------------|------------------------------|
| Hub daily (H1+H2) | `SUPER_FAST_HUB` + `RETIRE_SINA_COMMAND` | `THREE_ZONE_HUB_SPINE` museum zone quarantined |
| Portfolio commercial | `SOURCEA_PORTFOLIO_SSOT` | `NW1_*` · `NF_INTELLIGENCE_613` · `NF_INTELLIGENCE_LANDING` · `ONEPAGER_MERGED_EXTERNAL` · `ASSET_B_DFY` · `COMMERCIAL_SENDER` · `CHAIN_TOOLS_PUBLISH` · `CONTROL_PLANE_200*` · `ORCHESTRATOR_PARTNER` |
| n8n revenue proof | `N8N_COMMERCIAL_GRADE` | `N8N_AUTOMATION_PLAN` execution only |
| Source vs chat suggestions | `ALIGNMENT` | `CRITIC` §4 step 6 |
| Memory B vs D | `WTM_AUTHORITY` §4 | `WTM_MAP` one-line, `STEP_CATALOG` fields |
| Planning B4/C6/D10 | `WTM_AUTHORITY` §5 | `WTM_MAP` one-line, `planning_matrix` |
| Graph taxonomy | `WTM_AUTHORITY` §2 | `graph_taxonomy` payload |
| WTM step truth | `WTM_MAP` + `system_roadmap.py` | Companions, diagram |
| Who edits code | `EDIT_LOCK` | `FLEET` |
| Agent decision / smart progress | `AGENT_JUDGMENT` | `META_REASONING`, `ALIGNMENT` §2, `CRITIC`, `FLEET` |
| Session closeout / founder clarity | `RESULT_POLICY` | `AGENT_JUDGMENT`, `VALID_YES_VERDICT`, Worker full-round evidence |
| Meta-reasoning / triple-loop governance | `META_REASONING` | `AGENT_JUDGMENT`, `ALIGNMENT`, `WTM_AUTHORITY` |
| Valid YES progress / proof tiers | `VALID_YES_VERDICT` | `MONITOR_HONESTY` (brain-os/laws), INCIDENT-006 docs |
| Worker factory evidence / full round | `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` | INCIDENT-007, `worker_factory_evidence_gate_v1.py`, `098-worker-full-round-evidence.mdc` |
| Worker auto-run timing / stall playbook | `SINA_WORKER_AUTORUN_STALL_AND_TIMING_INCIDENT_LOCKED_v1.md` | INCIDENT-008, sa-0009 session, batch log tail law |
| Full system navigation | `SYSTEM_MAP_TREE` | All topic rows above; `archive/attachments` = index only |
| Monitor live wire | `MONITOR_DISK_LIVE` | `MONITOR_HONESTY`, INCIDENT-014 |
| Run inbox disk truth | `RUN_INBOX_DISK_TRUTH` | `SOURCEA_PHASE_STRICT_RUN_INBOX`, Worker mandatory read |
| Live ongoing prompts / Next steps | `LIVE_ONGOING_PROMPTS` | `RUN_INBOX_DISK_TRUTH`, `validate-next-prompt-pack-live-v1` |
| Founder commercial + no autorun | `FOUNDER_AGENTIC_POLICY` | `AUTOMATION_CONVERGE`, `AUTO_RUN_FULLY_AUTOMATIC` (legacy) |
| S10 audit lane | `S10_ETERNAL_AUDIT` | Cloud Forge Run, AUTO-RUN |
| Conduct / FREEZE | `FACTORY_CONTROL` | INCIDENT-015 conduct, `factory-now` lane |
| Disk truth E2E / hub projection | `DISK_TRUTH_E2E` | `CONVERSATION_FULL_INSIGHT` archive §3 pointer only |
| AI infra partnerships / bootstrap credits | `COMM_PARTNER` | `investor/ROADMAP.md` Q2 row · Commercial Goal vault |
| Research intake & save | `RESEARCH_SAVE` | `RESEARCH/_GOVERNANCE/` · `.cursor/rules/research-save-mandatory.mdc` |
| Incident reports corpus | `INCIDENT_CORPUS` | Per-report `*_REPORT_*` bodies · `INCIDENT_022` row for 022 law |
| Agent ecosystem surfaces | `AGENT_ECOSYSTEM` | Children: `AGENT_COUNCIL`, `AGENT_MIND_SHARE`, `AGENT_APP_HUB`, `AGENT_RULES_CHARGE`, `FLEET` |
| SourceA execution / E2E | `EXECUTION_LAW` | `E2E_DEBUGGER`, `PHASE_STRICT_INBOX`, `RUN_INBOX_DISK_TRUTH` |
| SourceA portfolio · buyer · commercial · market position | `SOURCEA_PORTFOLIO_SSOT` | `UNIFIED_ENGINE_STORY`, `REF_CONSTELLATION`, `SOURCEA_BLUEPRINT_COMPARISON_POSTMORTEM_v1.md` (draft harvest · not law) |
| Reference architecture | `REF_CONSTELLATION` | `SOURCEA_PORTFOLIO_SSOT` · `COMM_PARTNER` §8 observability order |
| Hub founder P0 headline | `ASF_PROGRESS` + `GOAL_HIERARCHY` | **STRATEGIC-SLICE** — RunReceipt parallel only (`T2b`) |
| Prompt OS | `PROMPT_OS_CORE` | `PHASE1_FREEZE`, `EXECUTION_TRUTH`, `PARALLEL_LANES`, `PROMPT_OS_SYSTEM` |
| Noetfield / cloud | `NOETFIELD_CLOUD` | **Local-only** until `LAYER_A` SSOT stable |
| Conduct incident priority | `INCIDENT_022` | Before factory conduct evidence when AUTO-RUN latch gap |
| Founder ↔ machine words | `TERMINOLOGY_DICT` | Five-step §7 · Cross-doc §12 · specialized glossaries (pointer-only) |
| Founder language corpus / phrase map | `FOUNDER_LANGUAGE_CORPUS` | `TERMINOLOGY_DICT` §3.4 · `phrase-corpus.yaml` |
| Open forks not forgotten | `TERMINOLOGY_DICT` §5 · E4/E5 | `validate-governance-completion-backlog-v1.sh` |
| Governance stack P0–P7 · live cascade | `LIVE_GOV_BP` | `validate-governance-propagation-live-v1.sh` |

---

## Archive rule (LOCKED)

| Rule | Action |
|------|--------|
| Active law | Current `*_LOCKED_vN.md` at **SourceA root** only |
| Superseded | Move to `archive/superseded/<track>/vN/` + manifest row |
| Examples | `archive/attachments/examples/` — never canonical |
| Cite in build | **Active doc path only** — audit fails on stale map pointers |

**Manifests:** `archive/superseded/wtm/ARCHIVE_MANIFEST_LOCKED_v1.md` · `archive/superseded/ARCHIVE_MANIFEST_LOCKED_v1.md`

### Suppressed attachments (never canonical)

| Path | Role |
|------|------|
| `archive/attachments/2026-06-10/SOURCEA_CONDUCT_AND_POISONED_LOOP_AUDIT_PROMPT_LOCKED_v2.md` | Advisor audit prompt — superseded v1 |
| `archive/attachments/2026-06-10/INCIDENT-022-maintainer-2-stale-autorun-advice_LOCKED_REPORT_v1.md` | Mirror only — canonical `brain-os/incidents/…022…` |
| `archive/superseded/incidents/INCIDENT-015-agent-ignored-stop-resumed-drain-loop_LOCKED_REPORT_v1.md` | Pre-023 draft — **015** = ID collision · conduct = **023** |

---

## Maintainer sync checklist

When changing a governed topic:

1. Edit **one** canonical doc from table above.  
2. Update **machine mirror** if listed (usually `system_roadmap.py`).  
3. Update **this index** row version if bumped.  
4. Archive old version — do not leave two active copies at root.  
5. `python3 scripts/build-sina-command-panel.py` → `audit_hub_source_alignment.py` **OK**.

---

**LOCKED** — Index only. Laws remain in their canonical files.

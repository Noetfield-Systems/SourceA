#!/usr/bin/env python3
"""
Curated important docs for Sina Command — visibility for founder + agents.
Deep index of SourceA law, rooms, Prompt OS, ecosystem, product, repo incidents.
"""
from __future__ import annotations

from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
DESKTOP = Path.home() / "Desktop"

# (path, title, why, priority, audience, tags)
# path: relative to SourceA, or absolute for repo/external
_RAW_SECTIONS: list[tuple[str, list[tuple[str, str, str, str, str, str]]]] = [
    (
        "agent_session",
        "Agents — read every session (P0)",
        "agent",
        [
            ("entry/START_HERE_LOCKED_v1.md", "START HERE — role picker", "Brain/Worker/Founder/Research — read your row only.", "P0", "both", "entry"),
            ("entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md", "Mandatory read by role", "Exact read chains per Cursor chat role.", "P0", "agent", "entry"),
            ("SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md", "Result-driven discussion policy", "Hyper-active v1.1 — disk goals/pain, evidence+events, option matrix, golden insight + founder next actions; not passive chat.", "P0", "agent", "governance"),
            ("AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md", "Agent decision stack & smart judgment", "Smart, honest, diligent judgment — beneficial progress for founder goals; self-heal; never fake progress.", "P0", "agent", "governance"),
            ("entry/FOLDER_MAP_LOCKED_v1.md", "Folder map", "What each SourceA directory is for.", "P0", "both", "entry"),
            ("entry/LAW_ROOT_INDEX_LOCKED_v1.md", "Root law index", "102 *_LOCKED*.md at repo root by topic — do not move files.", "P1", "agent", "entry"),
            ("os/chat-handoffs/README_INDEX_LOCKED_v1.md", "Handoffs index", "30 chat-handoff files by category.", "P0", "agent", "entry"),
            ("os/chat-handoffs/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md", "Worker assignment", "One worker · RA L1/L2 · archive no jobs.", "P0", "agent", "entry"),
            ("os/README_LOCKED_v1.md", "os/ folder map", "chat-handoffs + plan-library.", "P1", "agent", "entry"),
            ("README_SOURCE_A.md", "Source A entry (30 min)", "Legacy path — STEP 0 points to entry/START_HERE.", "P0", "agent", "entry"),
            ("docs/ONBOARDING.md", "Onboarding guide", "≤30 min — founder, maintainer, lane roles.", "P0", "both", "entry"),
            ("docs/ARCHITECTURE.md", "Architecture", "Hub stack, four planes, C1–C7, dispatch, SSOT.", "P1", "both", "map"),
            ("docs/RUNBOOK.md", "Runbook", "Start/stop, build, validators, incidents.", "P1", "maintainer", "ops"),
            ("docs/DISPATCH_POLICY_INTERFACE_ERRATA_v1.md", "Dispatch spec errata", "Claude interface vs shipped law — Phase 2a/3 delta.", "P1", "maintainer", "dispatch"),
            ("SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md", "Auto-paste incident", "Critical — never re-enable inject without ASF.", "P0", "agent", "incident"),
            ("CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md", "Context memory incident", "Session-start + session-close — chat is not SSOT.", "P0", "agent", "incident"),
            ("SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md", "Maintainer self-audit incident", "Repeat mistakes / Mac lag — run maintainer_self_audit_loop.py.", "P0", "agent", "incident"),
            ("SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md", "Incident Room law", "Weekly share + certify; always report in storage.", "P0", "agent", "room"),
            ("SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md", "Conflict Room law", "Report clash → ACE → keep working.", "P0", "agent", "room"),
            ("SINA_PROMPT_FAST_LOOP_LOCKED_v1.md", "Prompt-fast loop", "Meta / factory / repo — one 10-pack per session.", "P0", "agent", "loop"),
            ("SINA_AGENT_LOOP_ORDER_v1.md", "Loop order", "Founder clicks; rounds in app only.", "P0", "agent", "loop"),
            ("SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md", "Edit lock", "Who may edit SourceA hub.", "P0", "agent", "governance"),
            ("AGENT_GOVERNANCE_INDEX_LOCKED_v1.md", "Governance index", "8 private agents, forbidden roots, logs.", "P0", "agent", "governance"),
            ("SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md", "Private workspaces", "Per-agent page = workspace.", "P1", "agent", "governance"),
            ("AUTO_CONFLICT_ENGINE_V3_LOCKED.md", "ACE v3", "DESIGN / EXECUTION / DELIVERY planes.", "P1", "agent", "conflict"),
            ("SINAAI_PARALLEL_LANES_NO_BLOCK_PROGRESS_LOCKED_v1.md", "Never block lanes", "Repo blockers ≠ stop all progress.", "P1", "agent", "conflict"),
            ("AGENT_DESK_START_HERE.md", "Agent desk", "Desk routing for Cursor chats.", "P2", "agent", "entry"),
        ],
    ),
    (
        "council_governance",
        "Council Room — ecosystem governance (P0)",
        "agent",
        [
            ("AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md", "Agent unification policy", "Roles, edit lock, workspaces, Council Room phases — parent law for all 8 private agents.", "P0", "agent", "governance"),
            ("AGENT_COUNCIL_ROOM_LOCKED_v1.md", "Council Room law", "Report channels, mind share, Phase 2 votes — one room for all agent opinions.", "P0", "agent", "governance"),
            ("AGENT_MIND_SHARE_LOCKED_v1.md", "Mind Share law", "All agents see rules; learn from repo lens; paradox board — shared awareness.", "P0", "agent", "governance"),
            ("brain-os/law/AGENT_RULES_IN_CHARGE_LOCKED_v1.md", "Rules in charge", "Which laws govern NOW — highlighted for all agents before every act.", "P0", "agent", "governance"),
            ("AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md", "App as unifying hub", "Start every agent session in Council Room — one brief for all.", "P0", "agent", "governance"),
            ("AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md", "Agent application use blueprint", "End-to-end manual — roles, tasks, access, APIs, every agent.", "P0", "agent", "governance"),
            ("AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md", "Workspace vault middle layer", "Deposit all documents + activity via app — never chat-only work.", "P0", "agent", "governance"),
            ("AGENT_SCOREBOARD_LOCKED_v1.md", "Agent scoreboard", "Session reports + auto-checks green column for all 8 agent chats.", "P0", "agent", "governance"),
            ("AGENT_ESSAY_DISCOURSE_LOCKED_v1.md", "Essay discourse", "Same subject — all agents write essays — compare — mark best.", "P0", "agent", "governance"),
            ("GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md", "Governance unification engine", "ASF batch intake — score vs mission, merge into LOCKED SSOT, archive duplicates, sync authority index; one truth for founder + business.", "P0", "agent", "governance"),
        ],
    ),
    (
        "founder_daily",
        "Founder — daily (no Terminal)",
        "founder",
        [
            ("founder/ASF_DAILY_CARD.md", "ASF daily card", "5 commands every work day.", "P0", "founder", "daily"),
            ("SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md", "No Terminal law", "One-tap Actions only.", "P0", "founder", "command"),
            ("SINA_COMMAND_GUIDE_LOCKED_v1.md", "Command guide", "Teacher walkthrough for app.", "P1", "founder", "command"),
            ("SINA_APPS_GUIDE_FOR_SINA_v1.md", "Apps guide", "Desktop icons + roles.", "P1", "founder", "command"),
            ("ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md", "Progress center", "P0 + open todos daily.", "P0", "founder", "progress"),
            ("ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md", "Threads registry", "14 threads — pick one per chat.", "P1", "founder", "map"),
            ("founder/ASF_FOUNDER_FAQ.md", "Founder FAQ", "Repeated questions answered.", "P2", "founder", "faq"),
            ("founder/ASF_WIRE_AND_PHONE.md", "Wire + phone", "G3, Tailscale, run ids.", "P1", "founder", "wire"),
            ("founder/ASF_CURSOR_AND_M8.md", "Cursor + M8", "Silver vs purple app.", "P1", "founder", "m8"),
            ("WIRE_LANE_PROGRESS.md", "Wire lane progress", "G1/G2/G3 checklist.", "P1", "founder", "wire"),
            ("FOUNDER_FIRST_ASSISTANT_TRACKING_LAW_LOCKED_v1.md", "Founder request tracking", "Never lose ideas/orders — Today + Track.", "P0", "founder", "tracking"),
            ("ORDER_GUARDIAN_AGENT_LOCKED_v1.md", "Order Guardian agent", "Task orders + smart advisor in hub.", "P0", "founder", "tracking"),
            ("TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md", "Task orders register", "All open/partial/deferred orders — LOCKED.", "P0", "founder", "tracking"),
            ("FOUNDER_SAVE_AND_LOCK_IMMEDIATE_APP_LAW_LOCKED_v1.md", "Save & lock → app", "Every save/lock → file + hub same session.", "P0", "founder", "tracking"),
            ("FOUNDER_AGENT_USE_GUIDE_LOCKED_v1.md", "Agents Window guide", "100 tasks · Agents vs Editor · hub reminders.", "P0", "founder", "agents"),
            (
                "archive/attachments/2026-06-10/SOURCEA_FOUNDER_ADVISOR_DISCUSSION_TRACK_LOCKED_v1.md",
                "Advisor discussion track (PINNED)",
                "Crisis table D1–D4 · live factory-now + S10 · Hub Advisor track tab.",
                "P0",
                "founder",
                "crisis",
            ),
        ],
    ),
    (
        "command_app",
        "Sina Command app",
        "both",
        [
            ("SINA_COMMAND_CENTER_VISION_LOCKED_v1.md", "Command vision", "Why the hub exists.", "P1", "both", "command"),
            ("AGENT_CONTROL_PANEL_SPEC_LOCKED_v1.md", "Panel spec", "UI contract for hub.", "P2", "maintainer", "command"),
            ("SINA_COMMAND_UI_PLAYFUL_LOCKED_v1.md", "UI playful law", "Tone and layout rules.", "P2", "maintainer", "command"),
            ("UNDERSTANDING_ROLES_CURSOR_ECOSYSTEM_v1.md", "Roles map", "ASF, lanes, Cursor chats.", "P1", "both", "map"),
            ("AGENT_OPERATING_ROLES_LOCKED_v1.md", "Operating roles", "Role definitions locked.", "P2", "both", "map"),
            ("SINA_CURSOR_PROMPT_QUEUE_ORDER_v1.md", "Prompt queue", "Manual queue order (legacy path).", "P2", "both", "command"),
            ("SINA_SEMEJ_AGENT_v1.md", "SEMEJ agent", "Multi-AI Chrome chain law.", "P2", "both", "semej"),
            ("SINA_ADVISOR_CURSOR_CONNECT_v1.md", "AI Advisory", "Golden links + coach.", "P2", "founder", "command"),
            ("SINA_MAC_HEALTH_GUARD_LOCKED_v1.md", "Mac Health Guard", "Mini app law — local Mac security agents.", "P1", "founder", "security"),
            ("SINA_HUB_ESSENTIALS_LOCKED_v1.md", "Hub Essentials map", "Unified app index — one non-repetitive map.", "P1", "both", "command"),
            ("SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md", "Personal DB Layer A", "L0–L4 SSOT — copy agents train here.", "P0", "both", "personal-db"),
            ("ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md", "All incidents index", "Locked reports + weekly room + storage.", "P1", "both", "incident"),
            ("SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md", "System update notice", "Every Cursor agent — Essentials + per-repo tasks.", "P0", "agent", "command"),
            ("SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md", "Semi-separate lanes", "Wire, Cursor OS Pro, MergePack, Prompt OS — not five repos.", "P0", "agent", "command"),
            ("SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md", "Automation spine + n8n", "Hub Actions · starter test · n8n is glue only.", "P0", "both", "automation"),
            ("brain-os/law/entry/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md", "Governance entry router", "START — branch to laws; anti-fragmentation; active vs archive.", "P0", "agent", "roadmap"),
            ("META_REASONING_POLICY_STACK_LOCKED_v1.md", "Meta-reasoning policy stack", "L0–L12 decision governance — SSOT wins; critic isolated; policy→code map.", "P0", "agent", "roadmap"),
            ("brain-os/system/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md", "Authority index map", "Registry of canonical laws — one topic one doc.", "P0", "agent", "roadmap"),
            ("SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md", "Source alignment law", "Whole system — locked source wins; analyze; attach extras only.", "P0", "agent", "roadmap"),
            ("CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md", "ChatGPT / external critic law", "Paste = critic only; ASF order separate; never steer build from ChatGPT.", "P0", "agent", "roadmap"),
            ("brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md", "World Target Model map (FINAL)", "Master WTM v5.1 — 33 steps, authority law, hub v5.1.", "P0", "both", "roadmap"),
            ("WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md", "WTM authority law", "Graph/memory/planning boundaries — zero ambiguity.", "P0", "both", "roadmap"),
            ("WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md", "Step ID migration v4", "INCIDENT-004 — old D/C/B/A IDs → phase-aligned.", "P1", "both", "roadmap"),
            ("WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md", "WTM separation law", "Major upgrade tab only — not factory/investor.", "P1", "both", "roadmap"),
            ("HUB_SOURCE_UI_ALIGNMENT_PROCEDURE_LOCKED_v1.md", "Hub source/UI alignment", "SSOT → build → payload → UI; audit on every rebuild.", "P0", "agent", "roadmap"),
            ("STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md", "Strategic next steps (LOCKED v2)", "Big picture goals, pendings, phase plan — WTM panel.", "P0", "both", "roadmap"),
            ("COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md", "Council brief · strategic slice", "Founder build order — Eval-1/L0/ENFORCE; lane law.", "P0", "both", "roadmap"),
            ("ENFORCE_BYPASS_MAP_LOCKED_v1.md", "ENFORCE bypass map", "Which ingress paths are gated vs bypassed — hub gate receipts panel.", "P0", "agent", "roadmap"),
            ("DISPATCH_POLICY_LOCKED_v1.md", "Dispatch policy", "Auto-execution classes — gated on Eval-1b live pass.", "P0", "agent", "roadmap"),
            ("TRUST_LEDGER_SCHEMA_LOCKED_v1.md", "Trust ledger schema", "agent-governance-events.jsonl row schema v1.", "P1", "agent", "governance"),
            ("SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md", "GPT + Claude WTM synthesis", "Critic vs live results — compare only.", "P1", "both", "roadmap"),
            ("SOURCEA_1000_LOCKED_PROMPT_LIBRARY_NO_ASF_v1.md", "SourceA 1000 LOCKED prompts", "PLAN WITH NO ASF — sa-0001…1000 · pick/verify/closeout.", "P0", "agent", "roadmap"),
            ("brain-os/plan-registry/SOURCEA-1000-LOCK.md", "SourceA 1000 index", "Machine REGISTRY + phase map + founder-only pins.", "P0", "agent", "roadmap"),
        ],
    ),
    (
        "personal_db",
        "Personal database (Layer A)",
        "both",
        [
            ("SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md", "Layer A law", "Frontmatter, access, ingestion path.", "P0", "both", "layer-a"),
            ("SINA_COMMAND_CENTER_VISION_LOCKED_v1.md", "Command vision", "Personal DB is home face; Command reads Layer A.", "P1", "founder", "layer-a"),
        ],
    ),
    (
        "prompt_os",
        "Prompt OS & execution",
        "agent",
        [
            ("SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md", "SA-019 Phase 1", "Wins daily — ops freeze.", "P0", "agent", "promptos"),
            ("SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md", "Prompt OS decision", "Operating model — read #2 after SSOT.", "P0", "agent", "promptos"),
            ("SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md", "Execution truth", "Evidence + re-rank Phase 2.", "P1", "agent", "promptos"),
            ("SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md", "YAML ingest", "Ingest contract after Cursor.", "P1", "agent", "promptos"),
            ("ASF_FIVE_REPOS_PLUS_COMMAND_CHAT_v1.md", "Five repos + Lane 0", "Dispatch + ingest map.", "P1", "both", "promptos"),
            ("SINAAI_ARCHITECT_V2_INDUSTRIAL_POLICY_LOCKED_v1.md", "Architect v2", "Max 5 blockers — not doc police.", "P1", "agent", "promptos"),
            ("ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md", "Full day playbook", "Long Prompt OS day.", "P2", "agent", "promptos"),
            ("PROMPT_OS_CORE_MVP_BUILD_ORDER_LOCKED_v1.md", "MVP build order", "9 deliverables reference.", "P2", "maintainer", "promptos"),
            ("SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md", "Agents blueprint", "Canonical automation map.", "P1", "agent", "promptos"),
        ],
    ),
    (
        "ecosystem_law",
        "Ecosystem law & registry",
        "both",
        [
            ("brain-os/law/SINA_OS_SSOT_LOCKED.md", "Sina OS SSOT", "Master ecosystem law.", "P0", "both", "ssot"),
            ("SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md", "Document registry", "Chronology + authority order.", "P1", "both", "registry"),
            ("AUTO_CONFLICT_EXAMPLE_AGENT_STACK_POLICY_v1_LOCKED.md", "ACE example", "Worked stack policy example.", "P2", "agent", "conflict"),
            ("SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md", "E2E debugger playbook", "Rules 0–7 · sa-0042 · Worker/Brain process SSOT.", "P0", "both", "factory"),
            ("SINAAI_ECOSYSTEM_FINAL_STATE_AND_NEXT_PLAN_LOCKED_v1.md", "When lost", "Handoff + next plan.", "P2", "both", "map"),
            ("SINAAI_MASTER_BLUEPRINT_END_TO_END_v1.md", "End-to-end blueprint", "Roadmap narrative.", "P3", "both", "map"),
            ("ASF_MILESTONE_GLOSSARY_LOCKED_v1.md", "M8 glossary", "M8 vs Cursor vs wire terms.", "P2", "founder", "map"),
            ("PLAN_STATUS_VOCAB_LOCKED_v1.md", "Plan status vocab", "Parked vs ship language.", "P2", "agent", "map"),
            ("FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md", "No credit card", "Infra rule for deploy.", "P2", "founder", "infra"),
            ("SINAAI_FAST_TRACK_FORCE_MAJEURE_LOCKED_v1.md", "Fast track F8", "Fail forward per repo.", "P2", "agent", "blockers"),
        ],
    ),
    (
        "noetfield_lanes",
        "Noetfield — local vs cloud",
        "both",
        [
            (
                "NOETFIELD_CLOUD_GIT_AND_AGENT_ENTRY_UNIFIED_LOCKED_v1.md",
                "Noetfield unified guide",
                "Git vs Mac · share/do not share · cloud entry without hub.",
                "P0",
                "both",
                "noetfield",
            ),
            (
                str(DESKTOP / "Noetfield/docs/ops/AGENT_READ_LINKS_LOCKED_v1.md"),
                "Noetfield in-repo link index",
                "Cloud VM entry — mirror of SourceA index.",
                "P0",
                "agent",
                "noetfield",
            ),
            (
                str(DESKTOP / "Noetfield/docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md"),
                "Noetfield agent context",
                "Two workspaces — read before implement.",
                "P0",
                "agent",
                "noetfield",
            ),
            (
                "founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md",
                "Noetfield cloud notice",
                "Semi-separate ship chat.",
                "P0",
                "agent",
                "noetfield",
            ),
            (
                "founder/repo-agent-notices/REPO_NOTICE_noetfield_v1.md",
                "Noetfield local notice",
                "All-Documents chat only.",
                "P0",
                "agent",
                "noetfield",
            ),
        ],
    ),
    (
        "product_factory",
        "Product factory & MergePack",
        "agent",
        [
            ("product/PRODUCT_FACTORY_RESCORE_NO_ADS_LOCKED_v1.md", "Factory P0 RunReceipt", "Current factory P0.", "P0", "both", "factory"),
            ("product/ACQUISITION_STACK_LOCKED_v1.md", "Acquisition stack", "MergePack acquisition stack law.", "P0", "both", "mergepack"),
            ("product/EVIDENCE_FLYWHEEL_LOCKED_v1.md", "Evidence flywheel", "MergePack ecosystem flywheel.", "P1", "both", "mergepack"),
            ("product/PARTICIPATION_HOOKS_LOCKED_v1.md", "Participation hooks", "MergePack participation hooks.", "P1", "both", "mergepack"),
            ("product/MERGEPACK_SUITE_LOCKED_v1.md", "MergePack suite", "MergePack suite law.", "P1", "both", "mergepack"),
            ("PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md", "Factory roadmap", "Utility factory path.", "P2", "both", "factory"),
            ("product/MERGEPACK_10K_7DAY_LOCKED_v1.md", "MergePack 10K 7-day", "Active parallel lane.", "P1", "both", "mergepack"),
            ("product/MERGEPACK_POST_MOAT_PATH_A_LOCKED_v1.md", "MergePack post-moat", "Path A after moat.", "P2", "both", "mergepack"),
            ("product/MERGEPACK_LOCKED_v1.md", "MergePack parked", "When not active.", "P3", "both", "mergepack"),
        ],
    ),
    (
        "system_audits_evidence",
        "System audits (evidence — not law)",
        "both",
        [
            (
                "docs/system-audits/README_INDEX.md",
                "System audits index",
                "11 saved audit files — vault entry; PRIORITY + pick win over dates.",
                "P1",
                "both",
                "audit",
            ),
            (
                "docs/system-audits/SYSTEM_SUMMARY_2026-06-06.md",
                "System summary audit",
                "Executive orientation — open before deep CTO audit.",
                "P2",
                "both",
                "audit",
            ),
            (
                "docs/system-audits/MASTER_SYSTEM_AUDIT_2026-06-06.md",
                "Master system audit",
                "Parts 1–17 evidence-only CTO report.",
                "P2",
                "both",
                "audit",
            ),
            (
                "docs/system-audits/GOVERNANCE_RULE_BREAKING_2026-06-06.md",
                "Governance rule-breaking audit",
                "Why rules break + T0+T1 enforcement status.",
                "P2",
                "both",
                "audit",
            ),
        ],
    ),
    (
        "reference_constellation",
        "Market reference — architecture constellation",
        "both",
        [
            (
                "SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md",
                "Reference architecture constellation (LOCKED)",
                "29 external refs mapped L0–L7 — Temporal, ThinkFleet, Notenic, Frontier, Canada agentic guide, full market picture + SourceA status + golden insights.",
                "P0",
                "both",
                "roadmap",
            ),
        ],
    ),
    (
        "system_integrity",
        "System integrity — 100-step playbook",
        "both",
        [
            (
                "SOURCEA_SYSTEM_INTEGRITY_100_STEP_PLAYBOOK_LOCKED_v1.md",
                "System integrity 100-step playbook (LOCKED)",
                "10 phases × 10 steps — Founder decisive forks + Maintainer validators — LAW/MACHINE/PROJECTION audit, conflicts, agents, governance. Canvas tick-check.",
                "P0",
                "both",
                "governance",
            ),
            (
                "SOURCEA_COMPLEX_SITUATION_FORK_MACHINE_LOCKED_v1.md",
                "Complex situation fork machine (LOCKED)",
                "Mega/Brain/multi-fork protocol — 7-step pipeline, Effect lines, ASF order format, Canvas live form.",
                "P0",
                "both",
                "governance",
            ),
            (
                "prompts/COMPLEX_SITUATION_FORK_SESSION_PROMPT_LOCKED_v1.md",
                "Fork Machine session prompt (LOCKED)",
                "Copy-paste prompt for complex sessions — triage, inventory, clarify, confirm, execute.",
                "P0",
                "agent",
                "governance",
            ),
            (
                "SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md",
                "Five-step autonomous progress apex (LOCKED)",
                "Daily machine SCAN→SAY→PICK→PROVE→SHIP — wraps Fork + 100-step + Canvas.",
                "P0",
                "both",
                "governance",
            ),
            (
                "prompts/FIVE_STEP_SESSION_PROMPT_LOCKED_v1.md",
                "Five-step session prompt (LOCKED)",
                "Paste every chat — ignition for daily apex machine.",
                "P0",
                "agent",
                "governance",
            ),
            (
                "SOURCEA_INTEGRITY_STACK_UNIFIED_BLUEPRINT_BATCH_2_LOCKED_v1.md",
                "Integrity stack — Batch 2 unified map (LOCKED)",
                "Four artifacts compared · hierarchy · paradoxes · order · one ASF prefix.",
                "P0",
                "both",
                "governance",
            ),
            (
                "SOURCEA_CROSS_DOC_LINKAGE_AND_AUDIT_LOCKED_v1.md",
                "Cross-doc linkage & audit (LOCKED)",
                "SESSION-INTEGRITY-10 + EXPAND-11 · human vs machine channel · paradox · duplication.",
                "P0",
                "both",
                "governance",
            ),
            (
                "SOURCEA_TODAY_SESSION_UNIFIED_CLOSEOUT_RECEIPT_2026-06-11_LOCKED_v1.md",
                "Today session unified closeout (LOCKED)",
                "2026-06-11 nothing-left-behind receipt · full wire · FOUND list · machine proof.",
                "P0",
                "both",
                "governance",
            ),
            (
                "SOURCEA_ECOSYSTEM_MASTER_CATALOG_LOCKED_v1.md",
                "Ecosystem master catalog (LOCKED)",
                "T0–T12 threads · counts · live vs paper — one page inventory.",
                "P0",
                "both",
                "governance",
            ),
            (
                "SOURCEA_SSOT_FOUNDATION_WRITING_GUIDE_LOCKED_v1.md",
                "SSOT foundation writing guide (LOCKED)",
                "Human epistemic foundation · 018 egg · subject→SSOT→hatch.",
                "P0",
                "both",
                "governance",
            ),
            (
                "SOURCEA_LOST_LINK_RECOVERY_ETHICS_LOCKED_v1.md",
                "Lost link recovery ethics (LOCKED)",
                "FOUND = complete reward · transcript + disk · truth tree.",
                "P0",
                "both",
                "governance",
            ),
            (
                "SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md",
                "Live governance big picture (LOCKED)",
                "P0–P7 tiers · truth tree §2b · propagation · need vs noise.",
                "P0",
                "both",
                "governance",
            ),
        ],
    ),
    (
        "runtime_live",
        "Live state (refresh often)",
        "both",
        [
            ("sina-bowl/DAILY_BOWL.md", "Daily bowl", "Morning brief source.", "P0", "founder", "runtime"),
            ("GLOBAL_BLOCKERS.json", "GLOBAL_BLOCKERS", "Cross-repo blockers graph.", "P0", "both", "runtime"),
            ("PROGRAM_PROGRESS.json", "Program progress", "P0 % and phases.", "P0", "founder", "runtime"),
            ("ARCHITECT_REPORT.yaml", "Architect report", "Morning blockers (generated).", "P1", "agent", "runtime"),
            ("sina-bowl/DRIFT.json", "Drift register", "SSOT vs runtime drift.", "P2", "both", "runtime"),
        ],
    ),
    (
        "repo_incidents",
        "Repo incident reports (outside SourceA)",
        "agent",
        [
            (
                str(DESKTOP / "SinaPromptOS/docs/M8_INCIDENT_2026-06-03_LOCKED.md"),
                "M8 UI incident (2026-06-03)",
                "Wrong Cursor app paste blast.",
                "P0",
                "agent",
                "incident",
            ),
            (
                str(DESKTOP / "AI Dev Bridge OS/docs/INCIDENT_2026-06-04_AGENT_PLACEHOLDER_RUN_ID.md"),
                "Bridge placeholder run id",
                "Never paste run_<from-phone>.",
                "P1",
                "agent",
                "incident",
            ),
            (
                str(DESKTOP / "mergepack/docs/_TOPICS/05-incidents/INCIDENT_2026-06-03_AGENT_PLACEHOLDER_DEPLOY.md"),
                "MergePack deploy placeholders",
                "Railway init paste hazard.",
                "P1",
                "agent",
                "incident",
            ),
        ],
    ),
    (
        "investor_reference",
        "Investor materials (founder only)",
        "founder",
        [
            ("investor/README.md", "Investor package index", "Deck, FAQ — not agent daily law.", "P3", "founder", "investor"),
            ("investor/WHITEPAPER.md", "White paper", "External narrative.", "P3", "founder", "investor"),
        ],
    ),
]


def _resolve_item(path: str) -> dict:
    from sina_command_lib import resolve_doc_path  # noqa: WPS433

    external = path.startswith("/") or path.startswith("~")
    if external:
        p = Path(path).expanduser().resolve()
        exists = p.is_file()
        key = str(p)
        editable = False
    else:
        resolved = resolve_doc_path(path)
        if resolved:
            p, key = resolved
            exists = p.is_file()
            editable = True
        else:
            p = (SOURCE_A / path).resolve()
            exists = p.is_file()
            key = path
            editable = False
    return {
        "path": key,
        "path_display": path if not external else key,
        "title": "",
        "exists": exists,
        "external": external,
        "editable": editable and not external,
    }


def important_docs_payload() -> dict:
    from hub_essentials_index import READ_CHAIN  # noqa: WPS433

    sections = []
    total = 0
    missing = 0
    seen_paths: set[str] = set()
    deduped_count = 0
    for sec_id, title, audience, items in _RAW_SECTIONS:
        rows = []
        for path, doc_title, why, pri, aud, tags in items:
            norm = path if not path.startswith("/") else path
            if norm in seen_paths:
                deduped_count += 1
                continue
            seen_paths.add(norm)
            meta = _resolve_item(path)
            if not meta["exists"]:
                missing += 1
            total += 1
            rows.append(
                {
                    **meta,
                    "title": doc_title,
                    "why": why,
                    "priority": pri,
                    "audience": aud,
                    "tags": tags.split() if isinstance(tags, str) else list(tags),
                }
            )
        sections.append(
            {
                "id": sec_id,
                "title": title,
                "audience": audience,
                "count": len(rows),
                "items": rows,
            }
        )
    read_order_hint = [r["path"] for r in READ_CHAIN[:6]]
    return {
        "ok": True,
        "source_a_root": str(SOURCE_A),
        "sections": sections,
        "total_count": total,
        "missing_count": missing,
        "deduped_count": deduped_count,
        "read_order_hint": read_order_hint,
        "tagline": "Curated index — duplicates removed. Read chain lives on Essentials tab.",
    }

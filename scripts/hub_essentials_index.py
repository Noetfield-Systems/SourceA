#!/usr/bin/env python3
"""
Unified hub essentials — one non-repetitive map of everything important in Sina Command.
Feeds: Home quick tiles, Essentials tab, mandatory read chain, doc library dedupe hints.
"""
from __future__ import annotations

from typing import Any

SOURCE_A_NAME = "SourceA"

# P0 read chain — single ordered list (mandatory_reads derives from this).
READ_CHAIN: list[dict[str, str]] = [
    {"path": "brain-os/law/entry/README_SOURCE_A.md", "title": "Source A entry (30 min)", "why": "Step 0 router + five core laws — then branch by task."},
    {"path": "docs/ONBOARDING.md", "title": "Onboarding guide", "why": "≤30 min path — founder, maintainer, lane roles."},
    {"path": "docs/ARCHITECTURE.md", "title": "Project architecture", "why": "Hub stack, C1–C7 runtime, dispatch policy, SSOT layout."},
    {"path": "docs/RUNBOOK.md", "title": "Project runbook", "why": "Start/stop hub, build, validators, incidents."},
    {"path": "brain-os/law/entry/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md", "title": "Governance entry router", "why": "Single entry — pick branch; no duplicate law reading."},
    {"path": "brain-os/law/SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md", "title": "Result-driven discussion policy", "why": "Hyper-active conduct — understand pain/goals from disk, evidence+event-driven, option matrix, act+verify, golden insight + founder next actions every session. Not chat-only."},
    {"path": "AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md", "title": "Agent decision stack & smart judgment", "why": "Smart, honest, diligent agents — seek beneficial progress for founder + business; self-heal repeats; never fake progress or invert SSOT authority."},
    {"path": "brain-os/system/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md", "title": "Authority index map", "why": "Which law governs what; active vs archive/superseded."},
    {"path": "SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md", "title": "Auto-paste incident", "why": "Never re-enable Cursor inject without ASF."},
    {"path": "brain-os/law/SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md", "title": "No Terminal (founder)", "why": "Founder one-tap Actions only — agents run shell."},
    {"path": "brain-os/law/enforcement/GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md", "title": "Goal 1 activation chain", "why": "INJECT → VALIDATE → ACTIVATE — deliver alone ≠ running."},
    {"path": "brain-os/law/SINA_OS_SSOT_LOCKED.md", "title": "Sina OS SSOT", "why": "Master ecosystem law."},
    {"path": "brain-os/law/SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md", "title": "SA-019 Phase 1", "why": "Daily ops freeze."},
    {"path": "brain-os/law/SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md", "title": "Prompt OS decision", "why": "Operating model after SSOT."},
    {"path": "SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md", "title": "Incident Room law", "why": "Weekly share + certify."},
    {"path": "SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md", "title": "Conflict Room law", "why": "ACE triage — never block work."},
    {"path": "brain-os/law/SINA_PROMPT_FAST_LOOP_LOCKED_v1.md", "title": "Prompt-fast loop", "why": "Meta / factory / repo layers."},
    {"path": "SINA_AGENT_LOOP_ORDER_v1.md", "title": "Loop order", "why": "Rounds in app only."},
    {"path": "brain-os/law/AGENT_RULES_IN_CHARGE_LOCKED_v1.md", "title": "Edit lock", "why": "Who may edit SourceA."},
    {"path": "AGENT_GOVERNANCE_INDEX_LOCKED_v1.md", "title": "Governance index", "why": "Eight private agents + forbidden paths."},
    {"path": "brain-os/law/AGENT_RULES_IN_CHARGE_LOCKED_v1.md", "title": "Rules in charge", "why": "Which laws govern NOW — highlighted for all agents."},
    {"path": "AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md", "title": "Agent unification policy", "why": "Roles, edit lock, workspaces, Council Room phases."},
    {"path": "AGENT_COUNCIL_ROOM_LOCKED_v1.md", "title": "Council Room law", "why": "Report channels; mind share; Phase 2 votes."},
    {"path": "AGENT_MIND_SHARE_LOCKED_v1.md", "title": "Mind Share law", "why": "All agents see rules; learn from repo lens; paradox board."},
    {"path": "AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md", "title": "App as unifying hub", "why": "Start every agent session in Council Room — one brief for all."},
    {"path": "AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md", "title": "Agent application use blueprint", "why": "End-to-end manual — roles, tasks, access, APIs, every agent."},
    {"path": "AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md", "title": "Workspace vault middle layer", "why": "Deposit all documents + activity via app — never chat-only work."},
    {"path": "AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md", "title": "MergePack not an agent", "why": "MergePack = semi-separate product lane — not private agent registry."},
    {"path": "AGENT_SCOREBOARD_LOCKED_v1.md", "title": "Agent scoreboard", "why": "Session reports + auto-checks green column for all 8 agent chats."},
    {"path": "AGENT_ESSAY_DISCOURSE_LOCKED_v1.md", "title": "Essay discourse", "why": "Same subject — all agents write essays — compare — mark best."},
    {"path": "brain-os/law/GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md", "title": "Governance unification engine", "why": "When ASF sends new rules or docs — one pass: score vs mission, merge into canonical LOCKED files, archive superseded, sync authority index. Stops law sprawl; one SSOT for founder orders and the business system."},
    {"path": "brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md", "title": "Brain unified rules", "why": "Entry law spine — one read instead of scattered root LOCKED files."},
    {"path": "AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md", "title": "Sprint consolidation manifest", "why": "Preserve all conclusions, open decisions, reserved builds — path to final locked v2."},
    {"path": "brain-os/law/GOVERNANCE_DRIFT_ENGINE_LOCKED_v1.md", "title": "Governance drift engine", "why": "Aggregate audit score — Today tab + drift sensors."},
    {"path": "brain-os/law/enforcement/FOUNDER_FIRST_ASSISTANT_TRACKING_LAW_LOCKED_v1.md", "title": "Founder request tracking", "why": "Never lose ASF ideas/orders — registry + Today + Track."},
    {"path": "brain-os/law/ORDER_GUARDIAN_AGENT_LOCKED_v1.md", "title": "Order Guardian agent", "why": "Task orders register + smart advisor — what to do now from live state."},
    {"path": "brain-os/law/TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md", "title": "Task orders open register", "why": "All open/partial/deferred orders — machine mirror in ~/.sina/task-orders/."},
    {"path": "brain-os/law/enforcement/FOUNDER_SAVE_AND_LOCK_IMMEDIATE_APP_LAW_LOCKED_v1.md", "title": "Save & lock → app immediately", "why": "Every save/lock goes to file + hub same session — no chat-only memory."},
    {"path": "brain-os/law/enforcement/FOUNDER_AGENT_USE_GUIDE_LOCKED_v1.md", "title": "Agents Window use guide", "why": "100 tasks · when to use Agents vs Editor · hub reminders + copy prompts."},
    {"path": "brain-os/law/SINA_MAC_HEALTH_GUARD_LOCKED_v1.md", "title": "Mac Health Guard", "why": "Local Mac security mini app law."},
    {"path": "brain-os/law/SINA_HUB_ESSENTIALS_LOCKED_v1.md", "title": "Hub Essentials map", "why": "How to add tabs/apps once — no duplicate surfaces."},
    {"path": "brain-os/law/META_REASONING_POLICY_STACK_LOCKED_v1.md", "title": "Meta-reasoning policy stack", "why": "L0–L12 decision governance umbrella — SSOT wins; critic isolated; validate before execute."},
    {"path": "AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md", "title": "Agent skills & research pipeline", "why": "Per-agent Cursor skills + Agent Hub intake → brainstorm → evaluate → promote."},
    {"path": "brain-os/law/SINA_POST_CLAUDE_ANALYSIS_SHIP_READY_COMPANION_v1.md", "title": "Post-Claude ship-ready companion", "why": "Everything after Claude AI chat analysis — gate, D5 ship, checklist, agent start map."},
    {"path": "knowledge-library/KNOWLEDGE_LIBRARY_INDEX.md", "title": "Knowledge library index", "why": "Extract→book by field — train agents without fragmenting locked source."},
    {"path": "SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md", "title": "Source alignment law", "why": "Whole system — locked source wins; analyze suggestions; attach extras only; no drift."},
    {"path": "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md", "title": "ChatGPT / external critic law", "why": "When ASF pastes ChatGPT — critic input only; distinguish from ASF orders; never steer build."},
    {"path": "brain-os/law/STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md", "title": "Strategic next steps (LOCKED v2)", "why": "Big picture goals, pendings, phase plan — hub WTM panel."},
    {"path": "brain-os/law/SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md", "title": "Reference architecture constellation", "why": "Full external market map (29 refs) — layers, categories, SourceA place/status, golden build vs buy insights. ThinkFleet tone · Temporal spine · Stripe docs."},
    {"path": "brain-os/law/SOURCEA_SYSTEM_INTEGRITY_100_STEP_PLAYBOOK_LOCKED_v1.md", "title": "System integrity 100-step playbook", "why": "10 phases · Founder + Maintainer — law/machine/projection audit, 24 decisive forks, conflict governance, agents. Tick in Canvas sidebar."},
    {"path": "brain-os/law/SOURCEA_COMPLEX_SITUATION_FORK_MACHINE_LOCKED_v1.md", "title": "Complex situation fork machine", "why": "Mega chat · Brain · multi-fork — inventory forks, Effect per option, ASF confirm format, execute to disk. Prompt + script + Canvas."},
    {"path": "prompts/COMPLEX_SITUATION_FORK_SESSION_PROMPT_LOCKED_v1.md", "title": "Fork Machine session prompt", "why": "Copy-paste at start of complex Brain/governance/mega chats — stable 7-step pipeline."},
    {"path": "brain-os/law/SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md", "title": "Five-step autonomous progress (APEX)", "why": "Daily machine SCAN→SAY→PICK→PROVE→SHIP — 2026–2027 autonomous agentic path. Wraps Fork + 100-step + Layer A."},
    {"path": "prompts/FIVE_STEP_SESSION_PROMPT_LOCKED_v1.md", "title": "Five-step session prompt", "why": "Copy-paste every session — simplest repeatable progress machine."},
    {"path": "brain-os/law/SOURCEA_INTEGRITY_STACK_UNIFIED_BLUEPRINT_BATCH_2_LOCKED_v1.md", "title": "Integrity stack — Batch 2 unified map", "why": "One doc: 4 artifacts compared · hierarchy · paradoxes · duplicates · order · canonical ASF prefix."},
    {"path": "brain-os/law/SOURCEA_CROSS_DOC_LINKAGE_AND_AUDIT_LOCKED_v1.md", "title": "Cross-doc linkage & audit", "why": "Link 10 session docs across time · human vs machine channel · paradox · duplication · dual-language audit."},
    {"path": "brain-os/law/SOURCEA_LOST_LINK_RECOVERY_ETHICS_LOCKED_v1.md", "title": "Lost link recovery ethics", "why": "Transcript + disk search · FOUND = complete reward · truth tree down-only · @sina-conscious-recovery skill."},
    {"path": "brain-os/law/SOURCEA_SSOT_FOUNDATION_WRITING_GUIDE_LOCKED_v1.md", "title": "SSOT foundation (human)", "why": "018 egg · subject→SSOT→blueprint→hatch · why hierarchies exist."},
    {"path": "brain-os/law/SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md", "title": "Live governance big picture", "why": "P0–P7 tiers · truth tree §2b · propagation cascade · need vs noise."},
    {"path": "brain-os/law/SOURCEA_FROZEN_ARCHIVE_REVIVAL_AUDIT_LOCKED_v1.md", "title": "Frozen archive revival", "why": "MonoRepo 002 tiers · what to revive · 024 AUTO-RUN blocked."},
    {"path": "brain-os/law/SOURCEA_ECOSYSTEM_MASTER_CATALOG_LOCKED_v1.md", "title": "Ecosystem master catalog", "why": "T0–T12 thread chain · counts · live vs paper · one page inventory."},
    {"path": "agent-skills/shared/conscious-recovery/SKILL.md", "title": "Skill: conscious recovery", "why": "Mandatory routine — lost links · big picture · FOUND format (@sina-conscious-recovery)."},
    {"path": "brain-os/law/SOURCEA_TODAY_SESSION_UNIFIED_CLOSEOUT_RECEIPT_2026-06-11_LOCKED_v1.md", "title": "Today session closeout 2026-06-11", "why": "Unified receipt — nothing left behind · full wire · FOUND list · machine proof · founder next 3."},
    {"path": "brain-os/law/SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md", "title": "Live founder decision form", "why": "ANSWERED · Canvas open · pending ledger · open questions — every SCAN until RT cascade."},
    {"path": "START_HERE_COMPACT_v1.md", "title": "Living center", "why": "Compact entry — archive broker is SinaaiDataBase only."},
    {"path": "brain-os/law/SOURCEA_FOUNDER_MESSAGE_NORMALIZATION_LOCKED_v1.md", "title": "Founder message normalization", "why": "CAPS = non-caps for ASF orders · PICK keys · Track titles."},
    {"path": "brain-os/law/SOURCEA_GOVERNANCE_EVENT_SPINE_SCHEMA_LOCKED_v1.md", "title": "Governance event spine G1+G2", "why": "Runtime kernel — spine ledger · reference graph · impact scan · projection-only hub."},
    {"path": "brain-os/law/COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md", "title": "Council brief · strategic slice", "why": "Founder build order — not L8 primary; lane law."},
    {"path": "brain-os/law/enforcement/law/enforcement/ENFORCE_BYPASS_MAP_LOCKED_v1.md", "title": "ENFORCE bypass map", "why": "Gate receipts panel — what ENFORCE covers vs bypasses."},
    {"path": "brain-os/law/SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md", "title": "Execution intelligence stack", "why": "Locked build order: spine → memory → patterns → self-optimization."},
    {"path": "brain-os/law/SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md", "title": "Personal DB Layer A", "why": "SSOT for copy agents — L0–L4, ingestion, access."},
    {"path": "brain-os/law/entry/START_HERE_LOCKED_v1.md", "title": "System update notice", "why": "All agents — read before work; per-repo tasks inside."},
    {"path": "brain-os/law/SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md", "title": "Semi-separate lanes", "why": "Wire · Cursor OS Pro · MergePack · Prompt OS boundaries."},
]

# Sidebar tabs — coverage check ensures every NAV id appears once in pillars.
NAV_TABS: list[str] = [
    "command",
    "prompt-feed",
    "advisor-discussion",
    "essentials",
    "track",
    "order-guardian",
    "agent-window",
    "backlog",
    "today",
    "sa-queue",
    "goal1-auto-run",
    "roadmaps",
    "system-roadmap",
    "knowledge-library",
    "decision-governance",
    "actions",
    "council-room",
    "agent-scoreboard",
    "agent-loop",
    "incident-room",
    "conflict-room",
    "intelligence",
    "semej",
    "threads",
    "work",
    "apps",
    "notes",
    "ai-advisory",
    "guide",
    "agents",
    "repos",
    "daily",
    "audio",
    "products",
    "ecosystem",
    "personal-db",
    "orders",
    "hq",
    "fleet",
    "roles",
    "plans",
    "prompt-os",
    "runtime",
    "doc-library",
    "sources",
]

# Extra routes (not in sidebar) still linked from Essentials.
EXTRA_TABS: list[str] = ["rules", "branches"]

# Tab aliases — branches renders same as apps; no duplicate pillar entry.
TAB_ALIASES: dict[str, str] = {
    "branches": "apps",
    "world-target-model": "system-roadmap",
    "wtm": "system-roadmap",
    "meta-reasoning": "decision-governance",
    "meta_reasoning": "decision-governance",
    "decision_governance": "decision-governance",
    "personal_db": "personal-db",
    "doc_library": "doc-library",
    "ai_advisory": "ai-advisory",
}

# Pillars — each item appears once globally (enforced at build).
_PILLAR_DEFS: list[dict[str, Any]] = [
    {
        "id": "daily",
        "title": "Daily founder loop",
        "icon": "☀",
        "accent": "gold",
        "lead": "P0, bowl, actions — no Terminal.",
        "items": [
            {"kind": "tab", "tab": "command", "title": "Home", "desc": "P0 hero, Track banner, quick tiles"},
            {"kind": "tab", "tab": "advisor-discussion", "title": "Advisor track", "desc": "PINNED · D1–D4 · crisis subjects · live factory/S10"},
            {"kind": "tab", "tab": "prompt-feed", "title": "Next steps", "desc": "Live next 10 queue turns — optional commentary stamp"},
            {"kind": "tab", "tab": "today", "title": "Today", "desc": "P0, KPI, drift, todos"},
            {"kind": "tab", "tab": "sa-queue", "title": "SA queue", "desc": "sourcea-1000 live pick · backlog · prompt path"},
            {"kind": "tab", "tab": "goal1-auto-run", "title": "Factory drain log", "desc": "Batch log = truth · RUN INBOX when Brain routes"},
            {"kind": "action", "action_id": "founder-execute-turn", "title": "▶ EXECUTE TURN", "desc": "One tap from anywhere — deliver/execute/ack"},
            {"kind": "tab", "tab": "roadmaps", "title": "Roadmaps & goals", "desc": "Products & parallel plans — NOT World Target Model"},
            {"kind": "tab", "tab": "system-roadmap", "title": "World Target Model", "desc": "Major upgrade roadmap — after “major upgrade today”"},
            {"kind": "tab", "tab": "knowledge-library", "title": "Knowledge Library", "desc": "Extract→book by field · essays · ship plans · agent training"},
            {"kind": "doc", "path": "brain-os/law/SINA_POST_CLAUDE_ANALYSIS_SHIP_READY_COMPANION_v1.md", "title": "Ship-ready companion", "desc": "Post-Claude analysis — full checklist"},
            {"kind": "tab", "tab": "decision-governance", "title": "Decision governance", "desc": "L0–L12 meta-reasoning stack — SSOT wins · critic isolated"},
            {"kind": "doc", "path": "brain-os/law/META_REASONING_POLICY_STACK_LOCKED_v1.md", "title": "Meta-reasoning policy stack", "desc": "LOCKED umbrella — decision sovereignty"},
            {"kind": "tab", "tab": "daily", "title": "Daily rhythm", "desc": "ASF card, bowl, paste prompts"},
            {"kind": "tab", "tab": "actions", "title": "Actions", "desc": "Dispatch, ingest, brief — one tap"},
            {"kind": "tab", "tab": "track", "title": "Track", "desc": "Open commitments — nothing missed"},
            {"kind": "tab", "tab": "order-guardian", "title": "Order Guardian", "desc": "Task orders — smart advisor · what to do now"},
            {"kind": "tab", "tab": "agent-window", "title": "Agents Window", "desc": "100 tasks · wanted list · copy prompt for Cursor Agents"},
            {"kind": "doc", "path": "brain-os/law/TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md", "title": "Task orders register", "desc": "All open/partial/deferred — LOCKED doc"},
            {"kind": "tab", "tab": "audio", "title": "Audio brief", "desc": "Morning brief EN / FA"},
            {"kind": "doc", "path": "founder/ASF_DAILY_CARD.md", "title": "ASF daily card", "desc": "Five commands every work day"},
            {"kind": "doc", "path": "sina-bowl/DAILY_BOWL.md", "title": "Daily bowl", "desc": "Morning brief source"},
            {"kind": "runtime", "path": "PROGRAM_PROGRESS.json", "title": "Program progress", "desc": "Live P0 % — refresh hub"},
        ],
    },
    {
        "id": "noetfield",
        "title": "Noetfield lanes",
        "icon": "◇",
        "accent": "gold",
        "lead": "Local docs vs cloud ship — git boundary, Mac hub, cloud entry without your Mac.",
        "items": [
            {"kind": "doc", "path": "brain-os/law/NOETFIELD_CLOUD_GIT_AND_AGENT_ENTRY_UNIFIED_LOCKED_v1.md", "title": "Unified guide (app + law)", "desc": "Share vs not · 3 layers · read orders"},
            {"kind": "doc", "path": "founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md", "title": "Cloud ship notice", "desc": "Semi-separate — Desktop/Noetfield"},
            {"kind": "doc", "path": "founder/repo-agent-notices/REPO_NOTICE_noetfield_v1.md", "title": "Local docs notice", "desc": "Mainstream — All-Documents only"},
            {"kind": "tab", "tab": "repos", "title": "Repos", "desc": "Copy lane brief per chat"},
            {"kind": "tab", "tab": "agent-loop", "title": "Agent hub", "desc": "noetfield_local · noetfield_cloud packs"},
            {"kind": "doc", "path": "brain-os/law/SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md", "title": "Semi-separate lanes", "desc": "Wire · Cursor OS Pro · cloud Noetfield"},
        ],
    },
    {
        "id": "automation",
        "title": "Automation & n8n",
        "icon": "⚙",
        "accent": "green",
        "lead": "n8n = external glue only. Hub + Prompt OS + Runtime stay brain.",
        "items": [
            {"kind": "tab", "tab": "apps", "title": "Connected Apps", "desc": "n8n card · start · test"},
            {"kind": "tab", "tab": "actions", "title": "Actions", "desc": "Automation & n8n group"},
            {"kind": "doc", "path": "brain-os/law/SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md", "title": "Automation spine law", "desc": "Locked policy + starter test steps"},
            {"kind": "action", "action_id": "founder-n8n-test-flow", "title": "Run n8n starter test", "desc": "Hub → Runtime → n8n → workflow path"},
            {"kind": "action", "action_id": "founder-n8n-start", "title": "Start n8n", "desc": ":5678 UI"},
            {"kind": "mini_app", "app_id": "n8n", "title": "n8n Workflows", "desc": "Optional Telegram glue"},
        ],
    },
    {
        "id": "execute",
        "title": "Execute & programs",
        "icon": "⚡",
        "accent": "blue",
        "lead": "Threads, repos, products, Prompt OS.",
        "items": [
            {"kind": "tab", "tab": "threads", "title": "Ecosystem map", "desc": "Threads, docs, chats connected"},
            {"kind": "tab", "tab": "repos", "title": "Repos", "desc": "Plans, blockers, next task"},
            {"kind": "tab", "tab": "products", "title": "Live products", "desc": "Form to PDF, MergePack, VIRLUX"},
            {"kind": "doc", "path": "product/EVIDENCE_FLYWHEEL_LOCKED_v1.md", "title": "Evidence flywheel", "desc": "MergePack ecosystem flywheel law"},
            {"kind": "tab", "tab": "prompt-os", "title": "Prompt OS", "desc": "Five-repo dispatch snapshot"},
            {"kind": "tab", "tab": "plans", "title": "Program path", "desc": "Duolingo-style steps"},
            {"kind": "tab", "tab": "work", "title": "Recent work", "desc": "Quick product & repo cards"},
            {"kind": "tab", "tab": "backlog", "title": "Backlog", "desc": "Audit gaps & fixes"},
            {"kind": "doc", "path": "ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md", "title": "Threads registry", "desc": "One thread per Cursor chat"},
        ],
    },
    {
        "id": "agents",
        "title": "Agents & loops",
        "icon": "⟳",
        "accent": "blue",
        "lead": "Private pages, live agents, SEMEJ, advisory.",
        "items": [
            {"kind": "tab", "tab": "goal1-auto-run", "title": "Factory drain log", "desc": "REGISTRY drain — Brain+Worker+broker PEV"},
            {"kind": "tab", "tab": "agent-loop", "title": "Agent hub", "desc": "Index — one page per private agent (NOT Goal 1 drain)"},
            {"kind": "tab", "tab": "order-guardian", "title": "Order Guardian", "desc": "Task orders advisor — fleet + hub builds"},
            {"kind": "tab", "tab": "agent-window", "title": "Agents Window guide", "desc": "When to use Agents vs Editor — 100 tasks"},
            {"kind": "tab", "tab": "agent-scoreboard", "title": "Agent scoreboard", "desc": "Session reports · auto-checks green · not ASF verify"},
            {"kind": "tab", "tab": "decision-governance", "title": "Decision governance", "desc": "L0–L12 policy stack — build · verify · govern"},
            {"kind": "tab", "tab": "council-room", "title": "Council Room", "desc": "Integration readiness · report channels · Phase 1 votes"},
            {"kind": "tab", "tab": "agents", "title": "Agents registry", "desc": "Workspaces + activity"},
            {"kind": "tab", "tab": "intelligence", "title": "Live agents", "desc": "OpenRouter · Cursor maintainer · cloud"},
            {"kind": "tab", "tab": "semej", "title": "SEMEJ", "desc": "Chrome AI chain to artifact"},
            {"kind": "tab", "tab": "ai-advisory", "title": "AI Advisory", "desc": "Coach — connections & focus"},
            {"kind": "tab", "tab": "prompt-feed", "title": "Next steps", "desc": "Manual paste queue (legacy archive tab slug)"},
            {"kind": "tab", "tab": "notes", "title": "Your notes", "desc": "Fixes & ideas for Cursor"},
        ],
    },
    {
        "id": "safety",
        "title": "Safety & incidents",
        "icon": "⛔",
        "accent": "red",
        "lead": "Incidents, conflicts, emergency, Mac posture. Top bar Stop only on Home.",
        "items": [
            {"kind": "tab", "tab": "council-room", "title": "Council Room", "desc": "Unification policy · where agents report (not SourceA edits)"},
            {"kind": "tab", "tab": "incident-room", "title": "Incident Room", "desc": "Weekly share · certify"},
            {"kind": "tab", "tab": "conflict-room", "title": "Conflict Room", "desc": "ACE v3 — report & continue"},
            {"kind": "action", "action_id": "founder-emergency-stop", "title": "Emergency stop", "desc": "Kill hub · block auto-paste"},
            {
                "kind": "doc",
                "path": "brain-os/law/SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md",
                "title": "Resume remote_ops",
                "desc": "Set paused:false only after ASF approval — never during auto-paste incidents",
            },
            {"kind": "tab", "tab": "apps", "title": "Connected Apps", "desc": "Open Mac Health + all engines"},
            {"kind": "doc", "path": "SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md", "title": "Auto-paste incident", "desc": "2026-06-04 locked report"},
            {"kind": "doc", "path": "brain-os/law/AUTO_CONFLICT_ENGINE_V3_LOCKED.md", "title": "ACE v3", "desc": "DESIGN / EXECUTION / DELIVERY"},
            {"kind": "doc", "path": "ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md", "title": "All incidents index", "desc": "Locked reports + weekly room + storage paths"},
            {"kind": "doc", "path": "brain-os/incidents/NEAR_MISS_AND_UNFILED_INCIDENTS_INDEX_LOCKED_v1.md", "title": "Near-miss index", "desc": "Archive mirrors · audit C/S rows · adjunct bodies"},
            {"kind": "tab", "tab": "advisor-discussion", "title": "Advisor track", "desc": "Founder crisis table — not AI Advisory"},
        ],
    },
    {
        "id": "personal",
        "title": "Personal database (Layer A)",
        "icon": "▤",
        "accent": "violet",
        "lead": "SSOT for agents that copy you — P0 foundation project.",
        "items": [
            {"kind": "tab", "tab": "personal-db", "title": "Personal DB", "desc": "L0–L4 entries · ingestion · agent templates"},
            {"kind": "doc", "path": "brain-os/law/SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md", "title": "Layer A law", "desc": "Frontmatter, access, ingestion — SSOT rules"},
            {"kind": "doc", "path": "data/sourcea-living-center-v1.json", "title": "Living center", "desc": "Compact SourceA planes — archive in SinaaiDataBase"},
            {"kind": "doc", "path": "ASF_MASTER_ORDERS_ORGANIZED_LOCKED_v1.md", "title": "Master orders", "desc": "Active focus: build personal database"},
            {"kind": "doc", "path": "brain-os/law/SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md", "title": "Agents blueprint", "desc": "PAIOS · Layer A binding · automation"},
        ],
    },
    {
        "id": "law",
        "title": "Law & documentation",
        "icon": "📚",
        "accent": "violet",
        "lead": "One library — curated docs, not 50 random files.",
        "items": [
            {"kind": "tab", "tab": "decision-governance", "title": "Decision governance", "desc": "L0–L12 meta-reasoning — locked in app"},
            {"kind": "tab", "tab": "essentials", "title": "Essentials map", "desc": "This page — full non-repetitive index"},
            {"kind": "tab", "tab": "doc-library", "title": "Doc library", "desc": "Curated searchable index"},
            {"kind": "tab", "tab": "rules", "title": "Rules editor", "desc": "Read & edit Source A law"},
            {"kind": "tab", "tab": "sources", "title": "Sources tier-1", "desc": "Quick links + edit"},
            {"kind": "tab", "tab": "guide", "title": "Guide", "desc": "Teacher lessons — tap to learn"},
            {"kind": "doc", "path": "brain-os/system/SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md", "title": "Document registry", "desc": "Authority order"},
            {"kind": "doc", "path": "brain-os/law/SINA_HUB_ESSENTIALS_LOCKED_v1.md", "title": "Hub Essentials law", "desc": "SSOT rules for this map"},
        ],
    },
    {
        "id": "system",
        "title": "System & apps",
        "icon": "⎇",
        "accent": "green",
        "lead": "Connected apps, fleet, runtime, ecosystem KPI.",
        "items": [
            {"kind": "tab", "tab": "apps", "title": "Connected Apps", "desc": "Launch Prompt OS, engines, Mac Health"},
            {"kind": "tab", "tab": "roles", "title": "Roles", "desc": "ASF, lanes, PAIOS, Runtime map"},
            {"kind": "tab", "tab": "ecosystem", "title": "Ecosystem", "desc": "Flywheel, L1–L5, KPI trio"},
            {"kind": "tab", "tab": "fleet", "title": "Fleet", "desc": "Workspaces by lane"},
            {"kind": "tab", "tab": "runtime", "title": "Runtime", "desc": "Telegram workers health"},
            {"kind": "tab", "tab": "hq", "title": "HQ & team", "desc": "Duties & supervision"},
            {"kind": "tab", "tab": "orders", "title": "Your orders", "desc": "Organized founder messages"},
            {"kind": "mini_app", "app_id": "mac-health-guard", "title": "Mac Health Guard", "desc": "Local scan · Apple guides only · ~/.sina/mac-health"},
            {"kind": "mini_app", "app_id": "apple-health", "title": "Apple Health", "desc": "Wellness goals · link to roadmaps · ~/.sina/apple-health"},
            {"kind": "mini_app", "app_id": "chat-unify", "title": "Chat Unify", "desc": "Standalone :13023 · merge chats · ~/.sina/chat-unify · Desktop app"},
            {"kind": "mini_app", "app_id": "promptos-ui", "title": "Prompt OS UI", "desc": "Streamlit :8765"},
            {"kind": "mini_app", "app_id": "promptos-remote", "title": "Prompt OS Remote", "desc": "iPhone one-click · :8899"},
            {"kind": "mini_app", "app_id": "mono-next", "title": "Mono Command", "desc": "Next.js panel · :13022"},
            {"kind": "mini_app", "app_id": "sina-dispatch", "title": "Sina Dispatch", "desc": "Engine: 5-repo paste prompts"},
            {"kind": "mini_app", "app_id": "sina-execute", "title": "Sina Execute All", "desc": "Engine: full execute cycle"},
            {"kind": "mini_app", "app_id": "sina-decide", "title": "Sina Decide", "desc": "Engine: decision pass"},
            {"kind": "mini_app", "app_id": "sina-run", "title": "Sina Run Now", "desc": "Engine: run cycle"},
            {"kind": "mini_app", "app_id": "sina-status", "title": "Sina Status", "desc": "Engine: status report"},
            {"kind": "mini_app", "app_id": "sina-command", "title": "Sina Command hub", "desc": "This control center :13020"},
        ],
    },
]

# Home quick tiles — subset, no overlap with pillar titles.
QUICK_TILES: list[dict[str, str]] = [
    {"tab": "prompt-feed", "icon": "➡", "title": "Next steps", "desc": "Big picture → optional follow-up commentary", "accent": "violet"},
    {"tab": "essentials", "icon": "◈", "title": "Essentials map", "desc": "Everything important — organized", "accent": "violet"},
    {"tab": "personal-db", "icon": "▤", "title": "Personal DB", "desc": "Layer A SSOT for agents", "accent": "violet"},
    {"tab": "track", "icon": "◎", "title": "Track", "desc": "Open commitments", "accent": "red"},
    {"tab": "today", "icon": "◆", "title": "Today", "desc": "P0 · KPI · todos", "accent": "gold"},
    {"tab": "sa-queue", "icon": "▣", "title": "SA queue", "desc": "Live sa pick · backlog count", "accent": "gold"},
    {"tab": "goal1-auto-run", "icon": "▶", "title": "Factory drain log", "desc": "Batch log · RUN INBOX when Brain routes", "accent": "gold"},
    {"tab": "roadmaps", "icon": "🗺", "title": "Roadmaps", "desc": "Products · parallel — not WTM", "accent": "gold"},
    {"tab": "actions", "icon": "⚡", "title": "Actions", "desc": "One-tap commands", "accent": "blue"},
    {"tab": "agent-loop", "icon": "⟳", "title": "Agent hub", "desc": "Private agent pages", "accent": "blue"},
    {"tab": "apps", "icon": "⎇", "title": "Apps", "desc": "Engines · Mac Health · Prompt OS", "accent": "green"},
    {"tab": "incident-room", "icon": "⛔", "title": "Incidents", "desc": "Weekly room", "accent": "red"},
]


def _item_key(item: dict) -> str:
    kind = item.get("kind", "tab")
    if kind == "tab":
        return f"tab:{item.get('tab')}"
    if kind == "doc":
        return f"doc:{item.get('path')}"
    if kind == "mini_app":
        return f"app:{item.get('app_id')}"
    if kind == "action":
        return f"action:{item.get('action_id')}"
    if kind == "runtime":
        return f"runtime:{item.get('path')}"
    return f"{kind}:{item.get('title')}"


def _indexed_tabs(pillars: list[dict]) -> set[str]:
    tabs: set[str] = set()
    for p in pillars:
        for it in p.get("items", []):
            if it.get("kind", "tab") == "tab" and it.get("tab"):
                tabs.add(it["tab"])
    return tabs


def _nav_coverage(pillars: list[dict]) -> dict[str, Any]:
    indexed = _indexed_tabs(pillars)
    missing_nav = [t for t in NAV_TABS if t not in indexed]
    missing_extra = []
    for t in EXTRA_TABS:
        alias = TAB_ALIASES.get(t)
        if t in indexed or (alias and alias in indexed):
            continue
        missing_extra.append(t)
    return {
        "nav_total": len(NAV_TABS),
        "indexed_tab_count": len(indexed),
        "missing_nav_tabs": missing_nav,
        "missing_extra_tabs": missing_extra,
        "complete": not missing_nav and not missing_extra,
    }


def _dedupe_pillars() -> list[dict]:
    seen: set[str] = set()
    pillars = []
    for p in _PILLAR_DEFS:
        items = []
        for it in p.get("items", []):
            key = _item_key(it)
            if key in seen:
                continue
            seen.add(key)
            items.append({**it, "kind": it.get("kind", "tab")})
        pillars.append({**p, "items": items, "count": len(items)})
    return pillars


def mandatory_reads_from_chain() -> dict:
    """Thin wrapper — same paths as READ_CHAIN, plus emergency metadata."""
    items = []
    for i, row in enumerate(READ_CHAIN):
        items.append(
            {
                "id": row["path"].replace(".md", "").replace("/", "_")[:40],
                "priority": "P0" if i < 6 else "P1",
                "required": i < 10,
                "path": row["path"],
                "title": row["title"],
                "why": row["why"],
            }
        )
    items.append(
        {
            "id": "doc_library",
            "priority": "P1",
            "required": False,
            "path": "brain-os/system/SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md",
            "title": "Full doc library",
            "why": "Essentials + Doc library tabs — all curated docs.",
        }
    )
    return {
        "title": "Mandatory reading — agents coding this app",
        "subtitle": "Same list as Essentials → Read chain. Open in Rules or Doc library.",
        "law": "Never re-enable auto-paste into Cursor without ASF + new incident report version.",
        "emergency": {
            "label": "Emergency stop",
            "script": "scripts/emergency-stop.sh",
            "action_id": "founder-emergency-stop",
            "api": "POST /api/emergency-stop",
            "hint": "Safety: top bar ⛔ Stop only. Also Actions → Emergency and Essentials → Safety.",
        },
        "items": items,
        "essentials_tab": "essentials",
    }


def hub_essentials_payload(*, hub_port: int = 13020) -> dict:
    pillars = _dedupe_pillars()
    coverage = _nav_coverage(pillars)
    tab_count = sum(1 for p in pillars for it in p["items"] if it.get("kind") == "tab")
    app_count = sum(1 for p in pillars for it in p["items"] if it.get("kind") == "mini_app")
    try:
        from noetfield_unified_guide import noetfield_unified_guide_payload  # noqa: WPS433

        nf_guide = noetfield_unified_guide_payload()
    except Exception as e:
        nf_guide = {"ok": False, "error": str(e)}
    return {
        "ok": True,
        "version": 2,
        "noetfield_guide": nf_guide,
        "tagline": "One map for the whole app — pillars, read chain, quick tiles. No duplicate entries.",
        "hub_url": f"http://127.0.0.1:{hub_port}/",
        "essentials_url": f"http://127.0.0.1:{hub_port}/?tab=essentials",
        "read_chain": READ_CHAIN,
        "pillars": pillars,
        "quick_tiles": QUICK_TILES,
        "pillar_count": len(pillars),
        "item_count": sum(p["count"] for p in pillars),
        "tab_count": tab_count,
        "mini_app_count": app_count,
        "nav_coverage": coverage,
        "roles": {
            "command": "Home — P0 hero, Track banner, compact mandatory reads",
            "essentials": "Master map — all pillars (use this when lost)",
            "personal_db": "Layer A SSOT — train copy agents here first",
            "noetfield": "Two workspaces — local vs cloud ship (Essentials → Noetfield lanes)",
            "doc_library": "Search all curated docs by section",
            "rules": "Edit any SourceA markdown law",
            "sources": "Tier-1 quick edit links only",
            "apps": "Launch engines + Mac Health + Prompt OS UIs",
        },
    }

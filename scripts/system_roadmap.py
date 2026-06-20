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
ARCHITECTURE_DIAGRAM_DOC = "brain-os/wtm/WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md"
MASTER_DOC = MAP_DOC  # canonical WTM map — not other roadmaps
PAYLOAD_VERSION = "5.2"
CLAUDE_ANALYST_ATTACHMENT = (
    "archive/attachments/wtm/CLAUDE_ANALYST_PRE_LLM_GATE_HARDENING_ATTACHMENT_v1.md"
)
CURSOR_AGENT_SYNTHESIS = (
    "archive/attachments/wtm/CURSOR_AGENT_POST_CLAUDE_SYNTHESIS_ATTACHMENT_v1.md"
)
GOLDEN_RESEARCH_REPORT = (
    "archive/attachments/wtm/GOLDEN_PRE_LLM_GATE_RESEARCH_REPORT_v1.md"
)
AGENT_LESSONS_PRE_LLM = (
    "archive/attachments/wtm/SINA_AGENT_LESSONS_PRE_LLM_GATE_v1.md"
)
KNOWLEDGE_LIBRARY_INDEX = "knowledge-library/KNOWLEDGE_LIBRARY_INDEX.md"
KNOWLEDGE_LIBRARY_PIPELINE = "knowledge-library/PIPELINE_LAW.md"
KNOWLEDGE_FIELD_PRE_LLM = "knowledge-library/fields/pre-llm-world-model/FIELD_INDEX.md"
KNOWLEDGE_ESSAY_PRE_LLM = (
    "knowledge-library/fields/pre-llm-world-model/04-unified/ESSAY_v1_NO_MODEL_WITHOUT_PACKET.md"
)
SHIP_READY_COMPANION = "SINA_POST_CLAUDE_ANALYSIS_SHIP_READY_COMPANION_v1.md"
SHIP_PLAN_D5 = (
    "knowledge-library/fields/pre-llm-world-model/04-unified/SHIP_PLAN_D5_AND_GATE_v1.md"
)
AUTHORITY_DOC = "brain-os/wtm/WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md"
CRITIC_LAW_DOC = "brain-os/law/CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md"
GOVERNANCE_ENTRY_DOC = "brain-os/law/entry/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md"
AUTHORITY_INDEX_DOC = "brain-os/system/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md"
AGENT_JUDGMENT_DOC = "AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md"
META_REASONING_DOC = "META_REASONING_POLICY_STACK_LOCKED_v1.md"
GOV_UNIFY_DOC = "GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md"
HUB_UI_PROCEDURE_DOC = "HUB_SOURCE_UI_ALIGNMENT_PROCEDURE_LOCKED_v1.md"

# All locked docs that belong to World Target Model (major upgrade session)
WTM_LOCKED_DOCS: list[dict[str, str]] = [
    {"path": MAP_DOC, "title": "World Target Model Map (master)", "role": "master"},
    {"path": "brain-os/wtm/WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md", "title": "Step ID migration v4", "role": "migration"},
    {"path": LAW_DOC, "title": "WTM separation law", "role": "law"},
    {"path": AUTHORITY_DOC, "title": "WTM authority & boundary law", "role": "authority_law"},
    {"path": GOVERNANCE_ENTRY_DOC, "title": "Governance entry router", "role": "governance_entry"},
    {"path": AUTHORITY_INDEX_DOC, "title": "Authority index map", "role": "authority_index"},
    {"path": META_REASONING_DOC, "title": "Meta-reasoning policy stack (L0–L12)", "role": "meta_reasoning"},
    {"path": AGENT_JUDGMENT_DOC, "title": "Agent decision stack & smart judgment", "role": "agent_judgment"},
    {"path": GOV_UNIFY_DOC, "title": "Governance unification engine", "role": "gov_unify"},
    {"path": "SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md", "title": "Source alignment law (whole system)", "role": "alignment_law"},
    {"path": CRITIC_LAW_DOC, "title": "ChatGPT / external critic law", "role": "critic_law"},
    {"path": "archive/attachments/examples/wtm/CHATGPT_13STEP_WTM_REVIEW_EXAMPLE_LOCKED_v1.md", "title": "Example: ChatGPT 13-step review", "role": "example"},
    {"path": CLAUDE_ANALYST_ATTACHMENT, "title": "Claude AI · pre-LLM gate hardening (trigger)", "role": "attachment"},
    {"path": CURSOR_AGENT_SYNTHESIS, "title": "Cursor agent · post-Claude synthesis", "role": "agent_synthesis"},
    {"path": GOLDEN_RESEARCH_REPORT, "title": "Golden pre-LLM gate · research report", "role": "attachment"},
    {"path": AGENT_LESSONS_PRE_LLM, "title": "Agent lessons · pre-LLM gate", "role": "lessons"},
    {"path": KNOWLEDGE_LIBRARY_INDEX, "title": "Knowledge library · master index", "role": "knowledge_library"},
    {"path": KNOWLEDGE_ESSAY_PRE_LLM, "title": "Essay · No model without a packet", "role": "essay"},
    {"path": SHIP_READY_COMPANION, "title": "Post-Claude analysis · ship-ready companion", "role": "ship_ready"},
    {"path": SHIP_PLAN_D5, "title": "Ship plan · D5 + gate shadow", "role": "ship_plan"},
    {"path": ARCHITECTURE_DIAGRAM_DOC, "title": "Architecture diagram (locked)", "role": "architecture"},
    {"path": UI_DOC, "title": "WTM UI research (P0 spec)", "role": "ui"},
    {"path": "SINA_BIG_PICTURE_ROADMAP_LOCKED_v2.md", "title": "Phases A→B→C→D", "role": "companion"},
    {"path": "SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md", "title": "Phase B detail", "role": "companion"},
    {"path": "SINA_RUNTIME_STACK_LOCKED_v1.md", "title": "Phase C detail", "role": "companion"},
    {"path": "brain-os/wtm/SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md", "title": "Phase D detail", "role": "companion"},
    {"path": "archive/superseded/wtm/ARCHIVE_MANIFEST_LOCKED_v1.md", "title": "Superseded docs archive", "role": "archive"},
    {"path": HUB_UI_PROCEDURE_DOC, "title": "Hub ↔ source UI alignment procedure", "role": "procedure"},
    {"path": "STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md", "title": "Strategic next steps synthesis (LOCKED v2)", "role": "synthesis"},
    {"path": "COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md", "title": "Council brief · strategic slice", "role": "council"},
]

# Explicitly NOT World Target Model — other hub roadmaps
NOT_WTM_ROADMAPS: list[dict[str, str]] = [
    {"id": "roadmaps-tab", "title": "Roadmaps & goals tab", "where": "Parallel programs · factory · investor"},
    {"id": "factory", "title": "Product factory roadmap", "where": "PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md"},
    {"id": "investor", "title": "Investor roadmap", "where": "investor/ROADMAP.md"},
    {"id": "products", "title": "RunReceipt / MergePack", "where": "Today tab · THREAD-FACTORY"},
]
PHASE_ORDER = ("A", "B", "C", "D")
CURRENT_RUNTIME_STEP = "C7"
CURRENT_STRATEGIC_STEP = "D16"
RUNTIME_STACK_COMPLETE = True


def _live_gate_mode() -> str:
    try:
        import model_dispatch  # noqa: WPS433

        return model_dispatch.current_gate_mode()
    except Exception:
        return "shadow"


def _gate_is_enforce() -> bool:
    return _live_gate_mode() == "enforce"

# Rich step catalog — goals, features, achievements per step (major system upgrade track)
STEP_CATALOG: dict[str, dict[str, Any]] = {
    "A1": {
        "title": "Execution queue",
        "goal": "Single durable queue for all spine tasks — no lost runs.",
        "features": ["SQLite queue", "Task enqueue/dequeue", "Status lifecycle", "Spine SSOT for pending work"],
        "achievements": ["Queue DB at ~/.sina/execution-queue.db", "All spine dispatches flow through queue", "Foundation for worker + memory writeback"],
        "unlocks": "Worker can pull tasks reliably",
        "artifact": "~/.sina/execution-queue.db",
        "live_key": "execution-queue.db",
    },
    "A2": {
        "title": "Worker + executor",
        "goal": "Run queued tasks and produce structured run outcomes.",
        "features": ["Spine worker loop", "Runner integration", "PASS/FAIL capture", "Artifact paths logged"],
        "achievements": ["scripts/execution_spine/ shipped", "validate-execution-spine.sh green", "Hub can dispatch without Terminal"],
        "unlocks": "Every action can append to execution memory",
        "artifact": "scripts/execution_spine/",
        "live_key": "scripts/execution_spine",
    },
    "A3": {
        "title": "Memory writeback",
        "goal": "Append-only SSOT of what happened on every run.",
        "features": ["execution_memory.jsonl", "Per-task records", "Timestamps + outcomes", "Feeds intelligence stack"],
        "achievements": ["Post-action learning substrate live", "Pattern/decision/feedback layers read this file", "No bypass — spine-only writes"],
        "unlocks": "Phase B intelligence (patterns, why, signals)",
        "artifact": "~/.sina/execution_memory.jsonl",
        "live_key": "execution_memory.jsonl",
    },
    "A4": {
        "title": "Execution artifact store",
        "goal": "Persist run artifacts (logs, outputs) per spine execution — infrastructure, not a product SKU.",
        "features": ["~/.sina/execution-artifacts/", "Per-run folders", "Wire for downstream intelligence"],
        "achievements": ["Artifact storage path standardized", "Spine runs leave inspectable evidence"],
        "unlocks": "Decision memory + context snapshots can reference run outputs",
        "artifact": "~/.sina/execution-artifacts/",
        "live_key": "execution-artifacts",
        "note": "",
    },
    "B1": {
        "title": "Pattern Extraction Engine v1",
        "goal": "Deterministic success/failure/repeat-error patterns from execution history.",
        "features": ["Pattern extraction from memory", "execution_patterns_v1.json", "Success/failure signatures", "Hub /api exposure"],
        "achievements": ["Post-exec learning loop started", "validate-execution-intelligence.sh PASS", "Patterns influence downstream without new modules"],
        "unlocks": "Decision memory + feedback loop",
        "artifact": "execution_patterns_v1.json",
        "live_key": "execution_patterns_v1.json",
    },
    "B2": {
        "title": "Decision Memory v1",
        "goal": "Capture WHY runs passed/failed and map causes to fixes.",
        "memory_role": "historical truth — frozen causality (B-layer); D6 may read, never override",
        "features": ["execution_decisions_v1.jsonl", "Cause/fix mapping", "WHY layer on patterns", "Read-only for planners"],
        "achievements": ["Reasoning layer above patterns", "Decisions grow per new spine runs", "Feeds feedback + planner bias"],
        "unlocks": "Feedback loop influence signals",
        "artifact": "execution_decisions_v1.jsonl",
        "live_key": "execution_decisions_v1.jsonl",
    },
    "B3": {
        "title": "Feedback Loop v1",
        "goal": "Turn patterns + decisions into influence signals for planning.",
        "features": ["execution_feedback_signals.jsonl", "Influence weights", "Signal aggregation", "validate-feedback-loop-v1.sh"],
        "achievements": ["Closed loop: memory → patterns → decisions → signals", "Planner can bias recommendations"],
        "unlocks": "Memory-aware planner upgrade",
        "artifact": "execution_feedback_signals.jsonl",
        "live_key": "execution_feedback_signals.jsonl",
    },
    "B4": {
        "title": "Planner Upgrade v1",
        "goal": "Rank next actions using history + feedback signals.",
        "planning_authority": "learning signal only — NOT planning truth; may bias D10, never replace",
        "features": ["planner_context_v1.json", "Ranked recommendations", "agent_loop + prompt_direction wiring", "best_next_action surface"],
        "achievements": ["Hub planners consume ranked context", "validate-planner-upgrade-v1.sh PASS", "Actions tab can show best next"],
        "unlocks": "Context intelligence unified snapshot",
        "artifact": "planner_context_v1.json",
        "live_key": "planner_context_v1.json",
    },
    "B5": {
        "title": "Context Intelligence v1",
        "goal": "Unified snapshot: state + repo + behavior + planner for matters_now.",
        "memory_role": "historical truth snapshot — frozen matters_now; D6 indexes for retrieval only",
        "features": ["context_intelligence_v1.json", "GET /api/execution-context", "planner_context_block()", "matters_now subset"],
        "achievements": ["Single context object for agents", "validate-context-intelligence-v1.sh PASS", "Pre-LLM track can read (not write) later"],
        "unlocks": "Self-optimization + runtime router inputs",
        "artifact": "context_intelligence_v1.json",
        "live_key": "context_intelligence_v1.json",
    },
    "B6": {
        "title": "Self-Optimization v1",
        "goal": "Observe → measure → compare → suggest optimizations — never auto-execute.",
        "features": ["self_optimization_v1.json", "Strategy suggestions", "Founder confirm only", "Frozen intelligence capstone"],
        "achievements": ["Major upgrade: post-exec intelligence stack COMPLETE", "validate-self-optimization-v1.sh PASS", "Phase B frozen — no new intel modules"],
        "unlocks": "Runtime stack can read SSOT; strategic pre-LLM track opens",
        "artifact": "self_optimization_v1.json",
        "live_key": "self_optimization_v1.json",
    },
    "C1": {
        "title": "Tool Graph Engine v1",
        "goal": "Map task + goal → ordered tool dependency graph.",
        "features": ["tool_graph_v1.json", "Dependency mapper", "Execution path builder", "GET /api/tool-graph-v1"],
        "achievements": ["brain → structured graph (not just text)", "validate-tool-graph-v1.sh PASS", "Runtime track Step 1 done"],
        "unlocks": "Graph verification layer",
        "artifact": "/api/tool-graph-v1",
        "live_key": "tool_graph_v1.json",
    },
    "C2": {
        "title": "Tool Graph Verification v1",
        "goal": "Score graphs for cycles, deps, context, safety before dispatch.",
        "features": ["tool_graph_verified_v1.json", "Cycle detection", "plan_score + recommendation", "GET /api/tool-graph-verify-v1"],
        "achievements": ["Unsafe graphs blocked (needs_fix)", "validate-tool-graph-verify-v1.sh PASS", "Router has verified input only"],
        "unlocks": "Execution router v1",
        "artifact": "/api/tool-graph-verify-v1",
        "live_key": "tool_graph_verified_v1.json",
    },
    "C3": {
        "title": "Execution Router v1",
        "goal": "Policy + priority → next_step instruction only — no auto-execute.",
        "features": ["execution_router_v1.json", "dispatch_ready flag", "Founder confirm gate", "GET /api/execution-router-v1"],
        "achievements": ["Last shipped step on primary path", "Waits when verification needs_fix", "Major upgrade runtime slice 3/7 done"],
        "unlocks": "C4 repair loop + spine dispatch wiring",
        "artifact": "/api/execution-router-v1",
        "live_key": "execution_router_v1.json",
    },
    "C4": {
        "title": "Autonomous Repair Loop v1",
        "goal": "Failure → recovery suggestions — still no auto-execute.",
        "features": ["Failure classification", "Recovery suggestion graph", "Links to decisions/patterns", "repair_loop_v1.json"],
        "achievements": [
            "validate-repair-loop-v1.sh PASS",
            "GET /api/repair-loop-v1",
            "Recovery graph links B2/B3 — no spine auto-execute",
        ],
        "unlocks": "C5 Semantic Context Fabric",
        "artifact": "/api/repair-loop-v1",
        "live_key": "repair_loop_v1.json",
        "gate": "validate-repair-loop-v1.sh",
    },
    "C5": {
        "title": "Semantic Context Fabric v1",
        "goal": "Bridge runtime stack ↔ pre-LLM context without merging tracks.",
        "stateless": True,
        "features": ["Runtime-readable context fabric", "Pre-LLM packet hooks", "No duplicate intelligence"],
        "scope_law": "Stateless mapping layer — handles/pointers to D1/D5 only; no AST, retrieval, ranking, or inference",
        "achievements": [
            "validate-semantic-context-fabric-v1.sh PASS",
            "GET /api/semantic-context-fabric-v1",
            "D1/D5 handles only — runtime C1–C4 index for bridge visibility",
        ],
        "unlocks": "C6 Multi-Step Execution Planner",
        "artifact": "/api/semantic-context-fabric-v1",
        "live_key": "semantic_context_fabric_v1.json",
        "gate": "validate-semantic-context-fabric-v1.sh",
    },
    "C6": {
        "title": "Multi-Step Execution Planner v1",
        "goal": "Multi-step runtime plans from verified graphs.",
        "planning_authority": "execution-time sequencing only — NOT pre-LLM plan SSOT (D10 owns that)",
        "features": ["Step chains", "Fallback paths", "Spine-ready sequences"],
        "achievements": [
            "validate-multi-step-planner-v1.sh PASS",
            "GET /api/multi-step-planner-v1",
            "primary_chain + fallback_paths from C1/C4 — dispatch_ready false",
        ],
        "unlocks": "C7 Runtime Orchestrator",
        "artifact": "/api/multi-step-planner-v1",
        "live_key": "multi_step_planner_v1.json",
        "gate": "validate-multi-step-planner-v1.sh",
    },
    "C7": {
        "title": "Runtime Orchestrator v1",
        "goal": "Coordinated runtime control across graph → verify → route → repair.",
        "features": ["Orchestrated runtime control", "Founder confirm preserved", "Full runtime stack complete"],
        "achievements": [
            "validate-runtime-orchestrator-v1.sh PASS",
            "GET /api/runtime-orchestrator-v1",
            "C1→C6 pipeline coordinated — Phase C complete",
        ],
        "unlocks": "Pre-LLM world model (D1–D16) — runtime stack frozen at C7",
        "artifact": "/api/runtime-orchestrator-v1",
        "live_key": "runtime_orchestrator_v1.json",
        "gate": "validate-runtime-orchestrator-v1.sh",
    },
    "D1": {
        "title": "Code Intelligence Layer v1",
        "goal": "AST, symbols, import graph — repo understanding before LLM.",
        "bootstrap_inside_step": [
            "repo walker first pass (file tree scan)",
            "file discovery engine",
            "language detection layer",
            "module discovery seed index",
        ],
        "features": ["repo_graph", "symbol_index", "ast_index", "Query: who calls what, what breaks"],
        "achievements": [
            "code_intelligence_v1.json",
            "repo walker + AST + symbol + import graph",
            "/api/code-intelligence-v1",
        ],
        "unlocks": "D2 fusion + D3 dependency (bootstrap must complete before AST indexes)",
        "artifact": "/api/code-intelligence-v1",
        "gate": "validate-code-intelligence-v1.sh",
        "live_key": "code_intelligence_v1.json",
    },
    "D2": {
        "title": "Graph Fusion Layer v1",
        "goal": "Fuse AST + call + import + execution + error edges into one unified semantic code graph.",
        "domain": "unified semantic graph — integrates indexes from D1",
        "not": "structural dependency-only graph (that is D3)",
        "features": ["Unified graph SSOT", "AST+call+import fusion", "Error edge attachment", "Feeds D3 impact edges"],
        "achievements": [
            "graph_fusion_v1.json",
            "pre_llm/graph_fusion fusion_builder",
            "GET /api/graph-fusion-v1",
        ],
        "unlocks": "Dependency graph on fused substrate — not scattered indexes",
        "gate": "validate-graph-fusion-v1.sh",
        "artifact": "/api/graph-fusion-v1",
        "live_key": "graph_fusion_v1.json",
        "parent_step": "D1",
        "source": "alignment law v3 — architecture zone → sub-step",
    },
    "D3": {
        "title": "Dependency Graph Engine v1",
        "goal": "File/call/module graphs with impact edges — not tool graph.",
        "domain": "structural dependency graph — impact simulation on fused substrate",
        "not": "unified fusion layer (that is D2)",
        "features": ["File graph", "Call graph", "Module graph", "Impact simulation"],
        "achievements": [
            "dependency_graph_v1.json",
            "file + call + module graphs on D2 substrate",
            "GET /api/dependency-graph-v1",
        ],
        "unlocks": "Intent + retrieval grounded in code structure",
        "gate": "validate-dependency-graph-v1.sh",
        "artifact": "/api/dependency-graph-v1",
        "live_key": "dependency_graph_v1.json",
        "parent_step": "D2",
    },
    "D4": {
        "title": "Intent Inference Engine v1",
        "goal": "Classify user goal BEFORE execution runs.",
        "features": ["Goal classification", "Ambiguity detection", "Decomposition tree"],
        "achievements": [
            "intent_engine_v1.json",
            "rule-based goal_class + ambiguity tree (no LLM)",
            "GET /api/intent-engine-v1",
        ],
        "unlocks": "Pre-LLM planning (L2 critical gap closed)",
        "gate": "validate-intent-engine-v1.sh",
        "artifact": "/api/intent-engine-v1",
        "live_key": "intent_engine_v1.json",
        "parent_step": "D3",
    },
    "D5": {
        "title": "Vector Retrieval Engine v1",
        "goal": "Embeddings + AST-aware chunking — local index first (no Ollama; optional single embed API).",
        "features": [
            "Similarity search",
            "AST-aware chunks",
            "Local index SSOT ~/.sina/vector_index_v1",
            "No pgvector until allowed",
            "Fills packet.retrieval for gate path",
        ],
        "achievements": [
            "vector_index_v1.json",
            "token_overlap_v1 local retrieval (no Ollama)",
            "GET /api/vector-retrieval-v1",
            "packet.retrieval hydrates from D5",
        ],
        "unlocks": "Graph reasoning with semantic retrieval",
        "gate": "validate-vector-retrieval-v1.sh",
        "artifact": "/api/vector-retrieval-v1",
        "live_key": "vector_index_v1.json",
        "hardening_ref": CLAUDE_ANALYST_ATTACHMENT,
    },
    "D6": {
        "title": "Memory + Logs + Git read bridge v1",
        "goal": "Read-only bridge: execution_memory + git lineage into retrieval substrate.",
        "memory_role": "retrieval substrate only — NOT historical truth (B2/B5 own causality)",
        "features": [
            "execution_memory.jsonl read",
            "Git commit lineage + diff stat",
            "Gate shadow + artifact log hooks",
            "No spine writeback",
            "Fills packet.memory.slots",
        ],
        "achievements": [
            "memory_git_bridge_v1.json",
            "read-only B-layer bridge (never overrides truth)",
            "GET /api/memory-git-bridge-v1",
            "packet.memory hydrates from D6",
            "retrieval feed enriched from memory/git slots",
        ],
        "unlocks": "Retrieval grounded in history — not vectors only",
        "gate": "validate-memory-git-bridge-v1.sh",
        "artifact": "/api/memory-git-bridge-v1",
        "live_key": "memory_git_bridge_v1.json",
        "parent_step": "D5",
        "source": "alignment law v3 — ChatGPT extra",
    },
    "D7": {
        "title": "Query Expansion Layer v1",
        "goal": "Intent → search queries · symbol expansion · multi-query · declarative retrieval plan.",
        "features": [
            "Intent→queries from D4 goal_class",
            "Symbol expansion from D1",
            "Multi-query generation",
            "Declarative retrieval-plan-v1 (RRF fuse + cap)",
        ],
        "achievements": [
            "query_expansion_v1.json",
            "rule-based expansion (no LLM)",
            "GET /api/query-expansion-v1",
            "packet.retrieval.queries hydrates from D7",
            "retrieval_plan JSON per task",
        ],
        "unlocks": "Graph reasoning with expanded evidence set",
        "gate": "validate-query-expansion-v1.sh",
        "artifact": "/api/query-expansion-v1",
        "live_key": "query_expansion_v1.json",
        "parent_step": "D5",
        "source": "alignment law v3 — ChatGPT step 5 → D7",
    },
    "D8": {
        "title": "Graph Reasoning Engine v1",
        "goal": "Traversal, root-cause trace, impact simulation on code graph.",
        "features": [
            "Forward file traversal (D3 adjacency)",
            "Root-cause reverse trace",
            "Impact simulation (D3 simulate_impact)",
            "Seed resolution from text + D1 symbols",
        ],
        "achievements": [
            "graph_reasoning_v1.json",
            "rule-based paths (no LLM)",
            "GET /api/graph-reasoning-v1",
            "packet.reasoning.paths hydrates from D8",
            "impact + root_cause + traversal path kinds",
        ],
        "unlocks": "Pre-LLM ranking + planning",
        "gate": "validate-graph-reasoning-v1.sh",
        "artifact": "/api/graph-reasoning-v1",
        "live_key": "graph_reasoning_v1.json",
        "parent_step": "D3",
    },
    "D9": {
        "title": "Context Ranking System v1",
        "goal": "Pre-LLM relevance + intent alignment + noise filter.",
        "features": [
            "Rule-based scoring (intent + overlap + retrieval + graph)",
            "Evidence fusion from D5/D6/D8/D1",
            "Noise filter + dedupe by path",
            "Fills packet.ranking.ranked_evidence",
        ],
        "achievements": [
            "context_ranking_v1.json",
            "GET /api/context-ranking-v1",
            "packet.ranking hydrates from D9",
            "intent-aligned rank signals (no LLM)",
            "shadow gate path now has ranking section",
        ],
        "unlocks": "Semantic planning engine",
        "gate": "validate-context-ranking-v1.sh",
        "artifact": "/api/context-ranking-v1",
        "live_key": "context_ranking_v1.json",
        "parent_step": "D8",
    },
    "D10": {
        "title": "Planning Engine v1 (semantic)",
        "goal": "Task decomposition BEFORE execution — plan graph, not tool order only.",
        "planning_authority": "ONLY SSOT for LLM-bound pre-exec plan; B4=soft signal, C6=runtime sequence only",
        "features": [
            "D4 decomposition → plan nodes",
            "D9 evidence refs per step",
            "Sequential + fallback edges",
            "Fills packet.plan.graph",
        ],
        "achievements": [
            "planning_engine_v1.json",
            "GET /api/planning-engine-v1",
            "packet.plan hydrates from D10",
            "fallback_on_fail branch to D9 re-rank",
            "Month 2 rank+plan rule-based stack complete",
        ],
        "unlocks": "Execution preparation (D11–D12)",
        "gate": "validate-planning-engine-v1.sh",
        "artifact": "/api/planning-engine-v1",
        "live_key": "planning_engine_v1.json",
        "parent_step": "D9",
    },
    "D11": {
        "title": "Tool Router v1 (upgrade)",
        "goal": "Capability + policy + cost-aware tool selection for D10 plan steps.",
        "features": [
            "Plan-node → capability catalog",
            "Permission model (read/write/execute)",
            "Cost estimate per selection",
            "Policy gates (pre-LLM advisory — not C3 execute)",
        ],
        "achievements": [
            "tool_router_v1.json",
            "GET /api/tool-router-v1",
            "packet.tools.selection hydrates from D11",
            "execute tools blocked until D15 gate",
            "total_cost_estimate on selection",
        ],
        "unlocks": "Full validation layer",
        "gate": "validate-tool-router-v1.sh",
        "artifact": "/api/tool-router-v1",
        "live_key": "tool_router_v1.json",
        "parent_step": "D10",
    },
    "D12": {
        "title": "Validation Layer v1 (full)",
        "goal": "Dry-run, compile sim, code + graph safety beyond C2.",
        "features": [
            "Substrate checks D1–D11",
            "Graph + plan integrity safety",
            "D11 policy review",
            "py_compile sim on top evidence",
            "Packet schema dry-run",
        ],
        "achievements": [
            "validation_layer_v1.json",
            "GET /api/validation-layer-v1",
            "packet.validation.checks hydrates from D12",
            "required checks pass with zero fails",
            "prep phase D11+D12 complete",
        ],
        "unlocks": "Diff + compression + assembly",
        "gate": "validate-validation-layer-v1.sh",
        "artifact": "/api/validation-layer-v1",
        "live_key": "validation_layer_v1.json",
        "parent_step": "D11",
    },
    "D13": {
        "title": "Diff Intelligence Engine v1",
        "goal": "Semantic diff and change impact before LLM sees code.",
        "features": [
            "Git name-status + numstat (read-only)",
            "D3 file impact map per change",
            "D9 ranked-evidence focus overlap",
            "Working tree + recent commit scope",
        ],
        "achievements": [
            "diff_intelligence_v1.json",
            "GET /api/diff-intelligence-v1",
            "packet.diff.changes hydrates from D13",
            "impact_map with severity per file",
            "D12 validation chain before diff build",
        ],
        "unlocks": "Token-budget compression (D14)",
        "gate": "validate-diff-intelligence-v1.sh",
        "artifact": "/api/diff-intelligence-v1",
        "live_key": "diff_intelligence_v1.json",
        "parent_step": "D12",
    },
    "D14": {
        "title": "Context Compression Engine v1",
        "goal": "Token budget + summarization hierarchy for LLM packet.",
        "pipeline_order": "MUST run before D15 assembly — compress ranked evidence, do not re-rank",
        "features": [
            "Goal-class token budget policy",
            "Greedy pack of D9 ranked evidence (no re-rank)",
            "Hierarchical layers: intent, plan, ranking, diff, validation",
            "compressed_context.narrative within budget",
        ],
        "achievements": [
            "context_compression_v1.json",
            "GET /api/context-compression-v1",
            "packet.compression.budget hydrates from D14",
            "packet.compressed_context.narrative hydrates from D14",
            "within_budget enforced on every build",
        ],
        "unlocks": "Final context assembly (D15)",
        "gate": "validate-context-compression-v1.sh",
        "artifact": "/api/context-compression-v1",
        "live_key": "context_compression_v1.json",
        "parent_step": "D13",
    },
    "D15": {
        "title": "Context Assembly Engine v1",
        "goal": "Merge + rank + prune → llm_context_packet_v1.json — world model complete.",
        "pipeline_order": "Assembles D14-compressed evidence; schema validation gate before D16 writeback",
        "features": [
            "assemble_packet() compiles D1–D14 substrates",
            "constraints + provenance for gate eligibility",
            "Writes ~/.sina/llm_context_packet_v1.json",
            "model_dispatch.prepare_packet uses D15 assembly",
        ],
        "achievements": [
            "llm_context_packet_v1.json",
            "GET /api/context-assembly-v1",
            "validate_packet gate_eligible true on fresh assemble",
            "constraints.policy_refs + provenance.artifacts",
            "D15.1 shadow wired via model_dispatch",
        ],
        "unlocks": "Unified memory merge (D16) + ENFORCE gate",
        "gate": "validate-context-assembly-v1.sh",
        "artifact": "/api/context-assembly-v1",
        "live_key": "llm_context_packet_v1.json",
        "validations": ["validate-context-assembly-v1.sh", "validate-llm-context-packet-v1.sh"],
        "implementation_substeps": ["D15.1", "D15.2"],
        "hardening_ref": CLAUDE_ANALYST_ATTACHMENT,
        "parent_step": "D14",
    },
    "D15.1": {
        "title": "Model dispatch gate v1",
        "goal": "Single OpenRouter choke point — assemble → validate_packet → dispatch (shadow then enforce).",
        "parent_step": "D15",
        "features": [
            "scripts/model_dispatch.py — only hub-side model entry",
            "Gate modes: OFF → SHADOW → ENFORCE",
            "agent_loop._planner_chat wired (not Cursor executor)",
            "gate_shadow_v1.jsonl + gate_enforce_v1.jsonl receipts",
            "GET /api/model-dispatch-gate-v1 status probe",
        ],
        "achievements": [
            "model_dispatch_gate_v1.json SSOT",
            "GET /api/model-dispatch-gate-v1",
            "validate-model-gate-shadow-v1.sh PASS",
            "validate-model-gate-enforced-v1.sh PASS",
            "agent_loop planner uses dispatch_chat with D15 assembly",
        ],
        "unlocks": "D15.2 readiness UI + production ENFORCE flip",
        "gate": "validate-model-gate-shadow-v1.sh + validate-model-gate-enforced-v1.sh",
        "artifact": "/api/model-dispatch-gate-v1",
        "live_key": "model_dispatch_gate_v1.json",
        "source": CLAUDE_ANALYST_ATTACHMENT,
    },
    "D15.2": {
        "title": "Packet readiness hub surface v1",
        "goal": "Founder sees gate_eligible % and missing sections before any model call.",
        "parent_step": "D15",
        "features": [
            "Agent loop + WTM show validate_packet readiness",
            "Missing gate sections listed plain-English",
            "No Terminal — Refresh hub only",
            "GET /api/packet-readiness-v1",
            "system_roadmap.packet_readiness on hub refresh",
        ],
        "achievements": [
            "pre_llm/packet_readiness/hub_surface.py",
            "GET /api/packet-readiness-v1",
            "WTM + Agent hub readiness panel",
            "validate-packet-readiness-v1.sh",
        ],
        "unlocks": "ENFORCE flip with visible founder status",
        "gate": "validate-packet-readiness-v1.sh",
        "artifact": "/api/packet-readiness-v1",
        "live_key": "model_dispatch_gate_v1.json",
        "source": CLAUDE_ANALYST_ATTACHMENT,
    },
    "D16": {
        "title": "Unified memory merge into packet v1",
        "goal": "Merge long/short memory + git + logs into final LLM packet under budget.",
        "pipeline_order": "Strict writeback into packet only — no recomputation of D14/D15 ranking or compression",
        "features": [
            "D6 + B-layer slots merged under memory budget",
            "packet.memory.merge_ready writeback",
            "D15 assembly chains D16 automatically",
            "GET /api/packet-memory-merge-v1",
        ],
        "achievements": [
            "packet_memory_merge_v1.json",
            "pre_llm/packet_memory_merge/ module",
            "packet.memory unified slots (D6,B1,B2,B3)",
            "validate-packet-memory-merge-v1.sh PASS",
        ],
        "unlocks": "Complete pre-LLM world model packet — ENFORCE gate flip",
        "gate": "validate-packet-memory-merge-v1.sh",
        "artifact": "/api/packet-memory-merge-v1",
        "live_key": "packet_memory_merge_v1.json",
        "parent_step": "D15",
        "source": "alignment law v3 — ChatGPT memory step → assembly hook",
    },
}

# What was built TODAY in session order (after "major upgrade today") — not locked phase order
UPGRADE_CHRONOLOGY: list[dict[str, Any]] = [
    {"order": 0, "id": "trigger", "title": "Major upgrade declared", "status": "done", "achievements": [
        "World Target Model upgrade started",
        "Gap: living execution + memory fabric + closed loop",
        "Built SQLite spine (queue → worker → memory → artifacts)",
    ]},
    {"order": 1, "id": "A", "title": "Execution Spine (Phase A)", "status": "done", "achievements": [
        "Queue + worker + memory writeback + artifact store",
        "validate-execution-spine.sh green",
        "Foundation for all intelligence + runtime layers",
    ]},
    {"order": 2, "id": "B1", "title": "Pattern Extraction Engine v1", "status": "done", "achievements": [
        "execution_patterns_v1.json SSOT",
        "Mining from execution_memory — no prediction layer yet",
    ]},
    {"order": 3, "id": "intel_v2", "title": "Intelligence v2 (supplemental)", "status": "done", "achievements": [
        "prediction_engine, risk_scoring, task_recommender, causal_linker, strategy_optimizer",
        "Read-only — NOT part of locked Phase C sequence",
        "validate-execution-intelligence-v2.sh",
    ]},
    {"order": 4, "id": "B5", "title": "Context Intelligence v1", "status": "done", "achievements": [
        "Unified matters_now snapshot",
        "GET /api/execution-context",
    ]},
    {"order": 5, "id": "B2", "title": "Decision Memory v1 (WHY layer)", "status": "done", "achievements": [
        "execution_decisions_v1.jsonl",
        "Cause → effect → fix mapping",
    ]},
    {"order": 6, "id": "B3", "title": "Feedback Loop v1", "status": "done", "achievements": [
        "execution_feedback_signals.jsonl",
        "Patterns + decisions → influence signals",
    ]},
    {"order": 7, "id": "B4", "title": "Planner Upgrade v1", "status": "done", "achievements": [
        "planner_context_v1.json",
        "Ranked recommendations to agent_loop + prompt_direction",
    ]},
    {"order": 8, "id": "B6", "title": "Self-Optimization v1", "status": "done", "achievements": [
        "self_optimization_v1.json — suggestions only",
        "Phase C intelligence stack FROZEN",
    ]},
    {"order": 9, "id": "C1", "title": "Tool Graph Engine v1", "status": "done", "achievements": ["tool_graph_v1.json", "/api/tool-graph-v1"]},
    {"order": 10, "id": "C2", "title": "Tool Graph Verification v1", "status": "done", "achievements": ["tool_graph_verified_v1.json", "plan_score + needs_fix gate"]},
    {"order": 11, "id": "C3", "title": "Execution Router v1", "status": "done", "achievements": ["execution_router_v1.json", "instruction only — no auto-execute"]},
    {"order": 12, "id": "docs", "title": "Locked strategic roadmaps", "status": "done", "achievements": [
        "SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md",
        "SINA_RUNTIME_STACK_LOCKED_v1.md",
        "SINA_BIG_PICTURE_ROADMAP_LOCKED_v2.md",
    ]},
    {"order": 13, "id": "hub_ui", "title": "Hub System Roadmap tab", "status": "done", "achievements": ["Live map, journey, per-step achievements in app"]},
    {"order": 14, "id": "C4", "title": "Autonomous Repair Loop v1", "status": "done", "achievements": [
        "repair_loop_v1.json",
        "failure_class + recovery_suggestions",
        "/api/repair-loop-v1",
    ]},
    {"order": 15, "id": "C5", "title": "Semantic Context Fabric v1", "status": "done", "achievements": [
        "semantic_context_fabric_v1.json",
        "stateless D1/D5 handle bridge",
        "/api/semantic-context-fabric-v1",
    ]},
    {"order": 16, "id": "C6", "title": "Multi-Step Execution Planner v1", "status": "done", "achievements": [
        "multi_step_planner_v1.json",
        "spine-ready sequences",
        "/api/multi-step-planner-v1",
    ]},
    {"order": 17, "id": "C7", "title": "Runtime Orchestrator v1", "status": "done", "achievements": [
        "runtime_orchestrator_v1.json",
        "Phase C runtime stack complete",
        "/api/runtime-orchestrator-v1",
    ]},
    {"order": 18, "id": "D1", "title": "Code Intelligence Layer v1", "status": "done", "achievements": [
        "code_intelligence_v1.json",
        "repo walker + AST + symbol + import graph",
        "/api/code-intelligence-v1",
    ]},
    {"order": 19, "id": "D2", "title": "Graph Fusion Layer v1", "status": "done", "achievements": [
        "graph_fusion_v1.json",
        "unified AST+call+import+execution+error graph",
        "/api/graph-fusion-v1",
    ]},
    {"order": 20, "id": "D3", "title": "Dependency Graph Engine v1", "status": "done", "achievements": [
        "dependency_graph_v1.json",
        "file/call/module graphs + impact simulation",
        "/api/dependency-graph-v1",
    ]},
    {"order": 21, "id": "D4", "title": "Intent Inference Engine v1", "status": "done", "achievements": [
        "intent_engine_v1.json",
        "goal_class + ambiguity + decomposition tree",
        "/api/intent-engine-v1",
    ]},
]

MISCONCEPTIONS: list[dict[str, str]] = [
    {"wrong": "Spine / Layer 1 = RunReceipt product", "right": "Phase A Execution Spine (queue, worker, memory, artifact store) is 100% system roadmap. RunReceipt is a separate Factory product — zero overlap."},
    {"wrong": "ChatGPT 'RunReceipt system' in Layer 1 was founder intent", "right": "ChatGPT mirrored a partial assistant answer. After 'major upgrade today', Layer 1 means Execution Spine — not the RunReceipt SKU."},
    {"wrong": "RunReceipt P0 = this upgrade tab", "right": "RunReceipt ships on Today tab / THREAD-FACTORY (like MergePack). This tab is Phases A→B→C→D only."},
    {"wrong": "ChatGPT Layer 1–3 is a different project", "right": "All layers map to this roadmap: A (spine) → B (intelligence OS) → C (runtime stack) → D (pre-LLM world model). Step IDs match phases (A1, B4, C4, D1) stay stable."},
    {"wrong": "Tool graph = code dependency graph", "right": "Tool graph = execution tool order. Code graph is Phase D3."},
    {"wrong": "More post-exec intelligence modules", "right": "Phase B is FROZEN at B6. Next learning is Phase D (pre-LLM)."},
    {"wrong": "Personal DB Layer A = this upgrade", "right": "Layer A is constitution/knowledge — separate. This upgrade is execution + world model runtime."},
]

STEP_MODULES: dict[str, list[str]] = {
    "A1": ["scripts/execution_spine/queue.py"],
    "A2": ["scripts/execution_spine/worker.py", "scripts/execution_spine/executor.py"],
    "A3": ["scripts/execution_spine/writer.py"],
    "A4": ["~/.sina/execution-artifacts/"],
    "B1": ["scripts/execution_intelligence/pattern_engine/"],
    "B2": ["scripts/execution_intelligence/decision_memory/"],
    "B3": ["scripts/execution_intelligence/feedback_loop/"],
    "B4": ["scripts/execution_intelligence/planner_upgrade/"],
    "B5": ["scripts/execution_intelligence/context_intelligence/"],
    "B6": ["scripts/execution_intelligence/self_optimization/"],
    "C1": ["scripts/runtime/tool_graph/"],
    "C2": ["scripts/runtime/tool_graph_verification/"],
    "C3": ["scripts/runtime/execution_router/"],
    "C4": ["scripts/runtime/repair_loop/"],
    "C5": ["scripts/runtime/context_fabric/"],
    "C6": ["scripts/runtime/multi_step_planner/"],
    "C7": ["scripts/runtime/orchestrator/"],
        "D1": [
        "scripts/pre_llm/code_intelligence/repo_walker.py",
        "scripts/pre_llm/code_intelligence/file_discovery.py",
        "scripts/pre_llm/code_intelligence/language_detector.py",
        "scripts/pre_llm/code_intelligence/ast_parser.py",
        "scripts/pre_llm/code_intelligence/symbol_extractor.py",
        "scripts/pre_llm/code_intelligence/import_resolver.py",
        "scripts/pre_llm/code_intelligence/graph_builder.py",
        "scripts/pre_llm/code_intelligence/index_builder.py",
        "scripts/pre_llm/code_intelligence/store.py",
        "scripts/pre_llm/code_intelligence/api.py",
    ],
    "D2": [
        "scripts/pre_llm/graph_fusion/store.py",
        "scripts/pre_llm/graph_fusion/fusion_builder.py",
        "scripts/pre_llm/graph_fusion/query_engine.py",
        "scripts/pre_llm/graph_fusion/api.py",
    ],
    "D3": [
        "scripts/pre_llm/dependency_graph/store.py",
        "scripts/pre_llm/dependency_graph/graph_engine.py",
        "scripts/pre_llm/dependency_graph/query_engine.py",
        "scripts/pre_llm/dependency_graph/api.py",
    ],
    "D4": [
        "scripts/pre_llm/intent_engine/store.py",
        "scripts/pre_llm/intent_engine/classifier.py",
        "scripts/pre_llm/intent_engine/ambiguity.py",
        "scripts/pre_llm/intent_engine/decomposition.py",
        "scripts/pre_llm/intent_engine/intent_engine.py",
        "scripts/pre_llm/intent_engine/query_engine.py",
        "scripts/pre_llm/intent_engine/api.py",
    ],
    "D5": [
        "scripts/pre_llm/vector_retrieval/store.py",
        "scripts/pre_llm/vector_retrieval/chunk_builder.py",
        "scripts/pre_llm/vector_retrieval/index_builder.py",
        "scripts/pre_llm/vector_retrieval/query_engine.py",
        "scripts/pre_llm/vector_retrieval/retrieval_engine.py",
        "scripts/pre_llm/vector_retrieval/api.py",
        "scripts/model_dispatch.py",
    ],
}

STEP_APIS: dict[str, list[str]] = {
    "B1": ["/api/execution-patterns-v1"],
    "B2": ["/api/execution-decisions-v1"],
    "B3": ["/api/execution-feedback-v1"],
    "B4": ["/api/planner-upgrade-v1"],
    "B5": ["/api/context-intelligence-v1", "/api/execution-context"],
    "B6": ["/api/self-optimization-v1"],
    "C1": ["/api/tool-graph-v1"],
    "C2": ["/api/tool-graph-verify-v1"],
    "C3": ["/api/execution-router-v1"],
    "C4": ["/api/repair-loop-v1"],
    "C5": ["/api/semantic-context-fabric-v1"],
    "C6": ["/api/multi-step-planner-v1"],
    "C7": ["/api/runtime-orchestrator-v1"],
    "D1": ["/api/code-intelligence-v1"],
    "D2": ["/api/graph-fusion-v1"],
    "D3": ["/api/dependency-graph-v1"],
    "D4": ["/api/intent-engine-v1"],
    "D5": ["/api/vector-retrieval-v1"],
    "D6": ["/api/memory-git-bridge-v1"],
    "D7": ["/api/query-expansion-v1"],
    "D8": ["/api/graph-reasoning-v1"],
    "D9": ["/api/context-ranking-v1"],
    "D10": ["/api/planning-engine-v1"],
    "D11": ["/api/tool-router-v1"],
    "D12": ["/api/validation-layer-v1"],
    "D13": ["/api/diff-intelligence-v1"],
    "D14": ["/api/context-compression-v1"],
    "D15": ["/api/context-assembly-v1"],
    "D15.1": ["/api/model-dispatch-gate-v1"],
    "D15.2": ["/api/packet-readiness-v1"],
    "D16": ["/api/packet-memory-merge-v1"],
}

# §1 Big picture — current system vs target (founder blueprint 2026-06-05)
CURRENT_SYSTEM_BUILT: list[dict[str, str]] = [
    {"layer": "Execution Spine", "status": "done", "what": "task → queue → worker → execution"},
    {"layer": "Memory Writeback", "status": "done", "what": "execution logs (jsonl)"},
    {"layer": "Pattern Engine", "status": "done", "what": "extract behavior from history"},
    {"layer": "Decision Memory", "status": "done", "what": "WHY layer (causal outcomes)"},
    {"layer": "Feedback Loop", "status": "done", "what": "signals (prefer / avoid / reinforce)"},
    {"layer": "Planner Upgrade", "status": "done", "what": "history-aware ranking"},
    {"layer": "Context Intelligence", "status": "done", "what": "system snapshot (matters_now)"},
    {"layer": "Self-Optimization", "status": "done", "what": "suggestion-only improvement layer"},
    {"layer": "Tool Graph Engine", "status": "done", "what": "execution dependency graphs"},
    {"layer": "Graph Verification", "status": "done", "what": "validate execution plans (B2)"},
    {"layer": "Execution Router", "status": "done", "what": "verified graph → step instruction (C3, no auto-execute)"},
    {"layer": "Autonomous Repair Loop", "status": "done", "what": "failure class → recovery suggestions (C4, no auto-execute)"},
    {"layer": "Semantic Context Fabric", "status": "done", "what": "stateless D1/D5 handle bridge (C5, no semantic build)"},
    {"layer": "Multi-Step Execution Planner", "status": "done", "what": "verified graph → chain + fallbacks (C6, runtime plan only)"},
    {"layer": "Runtime Orchestrator", "status": "done", "what": "C1→C6 pipeline coordination (C7, Phase C complete)"},
    {"layer": "Code Intelligence", "status": "done", "what": "repo walker + AST + symbols + import graph (D1, pre-LLM)"},
    {"layer": "Graph Fusion", "status": "done", "what": "unified semantic code graph SSOT (D2, fuses D1 indexes)"},
    {"layer": "Dependency Graph", "status": "done", "what": "file/call/module deps + impact on D2 (D3)"},
    {"layer": "Intent Engine", "status": "done", "what": "goal_class + ambiguity + decomposition tree before LLM (D4)"},
    {"layer": "Vector Retrieval", "status": "done", "what": "local index + token retrieval + packet.retrieval (D5)"},
    {"layer": "Memory Git Bridge", "status": "done", "what": "execution_memory + git + logs → packet.memory (D6, read-only)"},
    {"layer": "Query Expansion", "status": "done", "what": "D4 intent → multi-query + retrieval plan JSON (D7)"},
    {"layer": "Graph Reasoning", "status": "done", "what": "D3 traversal + root-cause + impact paths (D8)"},
    {"layer": "Context Ranking", "status": "done", "what": "rule-based ranked evidence before LLM (D9)"},
    {"layer": "Semantic Planning", "status": "done", "what": "pre-exec plan graph SSOT from D4+D9 (D10)"},
    {"layer": "Tool Router", "status": "done", "what": "policy + cost-aware capability selection per plan step (D11)"},
    {"layer": "Validation Layer", "status": "done", "what": "dry-run + graph safety + compile sim (D12)"},
    {"layer": "Diff Intelligence", "status": "done", "what": "git semantic diff + D3 impact map before LLM (D13)"},
    {"layer": "Context Compression", "status": "done", "what": "token budget + hierarchical narrative from ranked evidence (D14)"},
    {"layer": "Context Assembly", "status": "done", "what": "full llm_context_packet_v1.json compiler + gate eligibility (D15)"},
    {"layer": "Model Dispatch Gate", "status": "done", "what": "OFF/SHADOW/ENFORCE choke on agent_loop planner (D15.1)"},
    {"layer": "Packet Readiness Hub", "status": "done", "what": "gate % + missing sections on WTM + Agent hub (D15.2)"},
    {"layer": "Unified Memory Merge", "status": "done", "what": "D6 + B-layer → packet.memory under budget (D16 writeback)"},
]

CURRENT_VS_TARGET: dict[str, Any] = {
    "built_summary": "After-execution learning system — powerful but reactive",
    "missing_summary": "Before-execution understanding system — repo + intent + semantics before LLM",
    "current_flow": "execute → observe → store → learn → improve",
    "target_flow": "understand → structure → plan → validate → execute",
    "current_nature": "learning-after-action",
    "target_nature": "understanding-before-action",
    "fundamental_problem": "System learns after execution; no real pre-exec understanding of code and goal",
    "why_feels_powerful": "History, patterns, decisions, feedback, planner ranking — all AFTER execution",
    "strategic_gap": "System learns from outcomes → target: system understands before action",
    "final_definition": "Pre-execution intelligence that structures code, intent, dependencies, history, constraints BEFORE the model is called",
}

LAYER_BLUEPRINT: list[dict[str, Any]] = [
    {"layer": "L0", "name": "Signal layer", "status": "missing", "gap": "High",
     "capabilities": ["user input (commands, prompts)", "file actions", "CLI + UI events"]},
    {"layer": "L1", "name": "Workspace state", "status": "partial", "gap": "Medium",
     "capabilities": ["open files", "active buffers", "session state", "project focus tracking"]},
    {"layer": "L2", "name": "Intent understanding", "status": "partial", "gap": "Medium",
     "capabilities": ["classify goal (fix/build/refactor)", "ambiguity detection", "multi-step goal tree", "missing context detection"]},
    {"layer": "L3", "name": "Code understanding", "status": "missing", "gap": "Critical",
     "capabilities": ["AST parsing", "function/class index", "symbol registry", "import/export map", "semantic tagging"]},
    {"layer": "L4", "name": "Dependency graph", "status": "partial", "gap": "Critical",
     "capabilities": ["file dependency graph", "function call graph", "module relationships", "change impact graph"],
     "note": "Tool graph = execution tools only — NOT code dependency graph"},
    {"layer": "L5", "name": "Change history", "status": "missing", "gap": "High",
     "capabilities": ["git history tracking", "diff lineage", "edit evolution map"]},
    {"layer": "L6", "name": "Execution signals", "status": "partial", "gap": "Medium",
     "capabilities": ["logs", "errors", "stack traces", "test results"],
     "note": "Backend exists (execution_memory.jsonl) — not wired pre-LLM"},
    {"layer": "L7", "name": "Memory system", "status": "partial", "gap": "High",
     "capabilities": ["session memory", "long-term memory", "bug/fix history", "pattern memory"],
     "note": "Fragmented JSONL/JSON SSOT — not unified retrieval"},
    {"layer": "L8", "name": "Semantic retrieval", "status": "hybrid", "gap": "Low",
     "capabilities": ["embeddings (code + text)", "similarity search", "AST-aware chunking", "hybrid symbol + semantic"],
     "note": "Hash-local embed + D9 blend shipped — not full cloud embeddings"},
    {"layer": "L9", "name": "Graph reasoning", "status": "missing", "gap": "High",
     "capabilities": ["dependency traversal", "root cause tracing", "impact simulation", "execution path reasoning"]},
    {"layer": "L10", "name": "Context ranking", "status": "partial", "gap": "High",
     "capabilities": ["relevance scoring", "intent alignment", "noise filtering", "priority weighting"],
     "note": "planner_upgrade = post-exec bias, not pre-LLM ranking"},
    {"layer": "L11", "name": "Planning engine (pre-exec)", "status": "partial", "gap": "High",
     "capabilities": ["task decomposition BEFORE execution", "dependency ordering", "fallback plans", "execution graph"],
     "note": "tool_graph = tool order, not semantic plan"},
    {"layer": "L12", "name": "Tool selection", "status": "partial", "gap": "Medium",
     "capabilities": ["tool registry", "capability matching", "execution constraints", "cost estimation"]},
    {"layer": "L13", "name": "Validation system", "status": "partial", "gap": "Medium",
     "capabilities": ["dry-run", "syntax validation", "type checking", "safety constraints"],
     "note": "C2 validates graphs only — not full code validation"},
    {"layer": "L14", "name": "Semantic diff", "status": "partial", "gap": "Medium",
     "capabilities": ["intelligent diff understanding", "change impact analysis", "patch validation"],
     "note": "D13 git diff + D3 impact — no LLM patch validation yet"},
    {"layer": "L15", "name": "Compression engine", "status": "partial", "gap": "Low",
     "capabilities": ["token budgeting", "context summarization", "redundancy removal", "hierarchical compression"],
     "note": "D14 rule-based budget + narrative — no LLM summarizer yet"},
    {"layer": "L16", "name": "Context assembly", "status": "partial", "gap": "Low",
     "capabilities": ["merge all signals", "rank + filter", "compress to token limit", "final LLM input package"],
     "note": "D15 assemble_packet + gate validate — D16 writeback pending"},
]

SHIP_READY: dict[str, Any] = {
    "companion_doc": SHIP_READY_COMPANION,
    "ship_plan_d5": SHIP_PLAN_D5,
    "status": "d16_shipped_phase_d_complete",
    "current_step": "ENFORCE",
    "last_shipped": "D16",
    "next_step_after_d5": "D16",
    "gate_mode": "shadow",
    "validators": [
        "validate-vector-retrieval-v1.sh",
        "validate-model-gate-shadow-v1.sh",
    ],
    "checklist_done": [
        "claude_analyst_attachment",
        "cursor_agent_synthesis_attachment",
        "golden_research_report",
        "agent_lessons",
        "knowledge_library_pipeline",
        "hub_knowledge_library_tab",
        "d5_module_scaffold",
        "model_dispatch_shadow",
        "d5_validator_pass",
        "wire_agent_loop_planner_shadow",
        "d6_memory_git_bridge",
        "d6_validator_pass",
        "packet_memory_hydrate",
        "d7_query_expansion",
        "d7_validator_pass",
        "packet_retrieval_queries_hydrate",
        "d8_graph_reasoning",
        "d8_validator_pass",
        "packet_reasoning_paths_hydrate",
        "d9_context_ranking",
        "d9_validator_pass",
        "packet_ranking_hydrate",
        "d10_planning_engine",
        "d10_validator_pass",
        "packet_plan_hydrate",
        "month2_d9_d10_rule_based_complete",
        "d11_tool_router",
        "d11_validator_pass",
        "packet_tools_selection_hydrate",
        "d12_validation_layer",
        "d12_validator_pass",
        "packet_validation_checks_hydrate",
        "prep_phase_d11_d12_complete",
        "d13_diff_intelligence",
        "d13_validator_pass",
        "packet_diff_changes_hydrate",
        "d14_context_compression",
        "d14_validator_pass",
        "packet_compression_narrative_hydrate",
        "d15_context_assembly",
        "d15_validator_pass",
        "gate_eligible_assembled_packet",
        "model_dispatch_uses_d15_assembly",
        "d15_1_model_dispatch_gate",
        "d15_1_shadow_enforce_validators",
        "agent_loop_planner_dispatch_wire",
        "d15_2_packet_readiness_hub",
        "hub_packet_readiness_pct",
        "validate_packet_readiness_v1",
        "d16_packet_memory_merge",
        "validate_packet_memory_merge_v1",
    ],
    "checklist_next": [
        "enforce_gate_flip",
        "l0_user_signals",
    ],
    "one_line_law": "No model call until intent, retrieval, ranking, and plan are assembled and validated.",
}

SESSION_LINEAGE: dict[str, Any] = {
    "law": "Claude = trigger (Layer A). Cursor agent = synthesis (Layer B). Both kept — never collapse.",
    "layer_a_trigger": {
        "source": "Claude AI / Claude chat",
        "attachment": CLAUDE_ANALYST_ATTACHMENT,
        "contributed": ["gate modes OFF/SHADOW/ENFORCE", "model_dispatch choke", "D15.1/D15.2", "90-day order"],
    },
    "layer_b_synthesis": {
        "source": "Cursor HQ agent",
        "attachment": CURSOR_AGENT_SYNTHESIS,
        "contributed": [
            "golden research report",
            "agent lessons",
            "knowledge library pipeline",
            "essay + book outline",
            "D5 ship + validators",
            "model_dispatch shadow + planner wire",
            "hub Knowledge Library tab",
            "ship-ready companion",
        ],
    },
}

IMPLEMENTATION_HARDENING: dict[str, Any] = {
    "attachment": CLAUDE_ANALYST_ATTACHMENT,
    "agent_synthesis": CURSOR_AGENT_SYNTHESIS,
    "session_lineage": SESSION_LINEAGE,
    "alignment_law": "SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md",
    "critic_law": CRITIC_LAW_DOC,
    "lesson_one_liner": "Spine is strong; system does not yet force structured context before every hub model call.",
    "lessons_file": AGENT_LESSONS_PRE_LLM,
    "research_report": GOLDEN_RESEARCH_REPORT,
    "agent_skill": "~/.cursor/skills/sina-research-lessons/SKILL.md",
    "knowledge_library": {
        "index": KNOWLEDGE_LIBRARY_INDEX,
        "pipeline_law": KNOWLEDGE_LIBRARY_PIPELINE,
        "fields": {
            "pre-llm-world-model": {
                "field_index": KNOWLEDGE_FIELD_PRE_LLM,
                "first_essay": KNOWLEDGE_ESSAY_PRE_LLM,
                "book_outline": "knowledge-library/fields/pre-llm-world-model/05-books/BOOK_OUTLINE_v1.md",
                "pipeline_stages": ["extract", "gather", "merge", "unify", "book"],
            },
        },
    },
    "core_gap_clarified": "Not founder thinking — missing mandatory assembly + gate on OpenRouter entry.",
    "substrate_vs_projection": {
        "substrate": ["~/.sina/* SSOT", "D1–D3 graphs", "intent_engine_v1.json"],
        "projection": "llm_context_packet_v1.json per task (assembled, validated, then model)",
        "compiler_step": "D15",
    },
    "gate_modes": [
        {"id": "off", "label": "OFF", "when": "Until D5 PASS", "behavior": "Models run as today"},
        {"id": "shadow", "label": "SHADOW", "when": "D5 + partial D9/D10", "behavior": "Assemble + log gate_eligible; model still runs"},
        {"id": "enforce", "label": "ENFORCE", "when": "D14 + D15 PASS", "behavior": "Block hub OpenRouter if gate_eligible false"},
    ],
    "current_gate_mode": "shadow",
    "choke_point": {
        "module": "scripts/model_dispatch.py",
        "wire_order": ["agent_loop planner", "live agents", "advisor"],
        "do_not_gate": ["Cursor executing agent", "execution spine subprocess worker"],
    },
    "golden_research_highlights": {
        "mantra": "No model call until intent, retrieval, ranking, and plan are assembled and validated.",
        "top_five": [
            "Harness > prompt — wrap model, don't enlarge prompt",
            "Retrieval plan is code — declarative, diffable, testable",
            "Plan before compress — D14 after D10 (PAACE)",
            "Golden-set CI gate — structural runtime + quality release",
            "Minimum sufficient context — scoped packet per call",
        ],
        "seven_suggestions": [
            "D15 compiler + D15.1 model_dispatch choke",
            "Declarative retrieval plan D5+D7 hybrid+RRF+cap",
            "Rule-based D9/D10 before LLM polish",
            "Two-layer validation structural + golden-set quality",
            "Conditional retrieval in GATE_REQUIRED_SECTIONS",
            "Gate modes OFF SHADOW ENFORCE",
            "Replay envelope in gate_shadow_v1.jsonl",
        ],
        "replay_envelope_fields": [
            "packet_id", "task_id", "readiness_score", "gate_eligible",
            "missing_for_gate", "producer_steps", "retrieval_query_id",
            "policy_version", "trace_id",
        ],
        "open_items": [
            "retrieval conditional in GATE_REQUIRED_SECTIONS",
            "validate-pre-llm-golden-v1.sh",
            "~/.sina/golden/pre_llm_v1/",
        ],
    },
    "ninety_day": [
        {"month": 1, "ship": "D5 + D15.1 shadow stub", "receipt": "validate-vector-retrieval-v1.sh", "mode": "shadow_start", "status": "done"},
        {"month": 2, "ship": "D6–D10 rule-based rank + plan", "receipt": "D9/D10 validators + golden recall", "mode": "shadow", "status": "in_progress"},
        {"month": 3, "ship": "D14 + D15 + ENFORCE planner gate", "receipt": "validate-model-gate-enforced-v1.sh", "mode": "enforce", "status": "pending"},
    ],
    "do_not_touch": [
        "Execution spine A1–A4",
        "Intelligence B1–B6 frozen",
        "Runtime C1–C7 complete",
        "C5 stateless handle bridge",
    ],
    "implementation_substeps": {
        "D15.1": "Model dispatch gate",
        "D15.2": "Packet readiness hub UI",
    },
}

LLM_PACKET_SCHEMA: dict[str, Any] = {
    "description": "Final structured package to model — world model output gate",
    "law_doc": "LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md",
    "schema_module": "scripts/pre_llm/context_packet/schema.py",
    "schema_validation_script": "validate-llm-context-packet-schema-v1.sh",
    "pre_llm_steps_shipped": "4/16",
    "shipped_producers": ["D1", "D2", "D3", "D4"],
    "implementation_hardening_ref": CLAUDE_ANALYST_ATTACHMENT,
    "fields": {
        "intent": "classified user goal (D4)",
        "code": "files + symbols (D1,D2)",
        "dependencies": "impact graph (D3)",
        "retrieval": "chunks + queries (D5,D7)",
        "reasoning": "paths (D8)",
        "ranking": "ranked evidence (D9)",
        "plan": "semantic plan graph SSOT (D10)",
        "tools": "capability selection (D11)",
        "validation": "safety checks (D12)",
        "diff": "semantic change (D13)",
        "compression": "token budget (D14)",
        "memory": "slots (D6,D16)",
        "constraints": "policy limits",
        "compressed_context": "token-budgeted narrative (D14)",
        "provenance": "producer steps (D15)",
    },
    "gate_artifact": "llm_context_packet_v1.json",
    "validation_script": "validate-llm-context-packet-v1.sh",
    "gate_required_sections": [
        "intent", "code", "dependencies", "ranking", "plan",
        "compression", "compressed_context", "constraints", "provenance",
    ],
    "bypass_today": [
        "agent_loop._planner_chat → OpenRouter (no validate_packet)",
        "Live agents / Advisor → OpenRouter direct",
    ],
    "gate_law_month_3": "Hub planners must not call model unless validate_packet passes on fresh task packet",
}

STRATEGIC_BUILD_PHASES: list[dict[str, Any]] = [
    {"phase": 1, "title": "Core missing foundation", "steps": [
        {"order": 1, "title": "Code Intelligence Layer", "critical": True, "roadmap_id": "D1",
         "items": ["AST parser", "symbol index", "import/export graph", "query API"]},
        {"order": "1.1", "title": "Graph Fusion Layer", "critical": True, "roadmap_id": "D2", "sub_step": True,
         "items": ["unified AST+call+import+error graph", "single graph SSOT"]},
        {"order": 2, "title": "Dependency Graph System", "critical": False, "roadmap_id": "D3",
         "items": ["module graph", "call graph", "change impact graph"]},
        {"order": 3, "title": "Intent Engine", "critical": False, "roadmap_id": "D4",
         "items": ["classify goal BEFORE execution", "ambiguity", "goal tree"]},
    ]},
    {"phase": 2, "title": "Semantic understanding", "steps": [
        {"order": 4, "title": "Vector Retrieval System", "roadmap_id": "D5",
         "items": ["embeddings (code + logs)", "similarity search", "AST-aware chunking"]},
        {"order": "4.1", "title": "Memory + Logs + Git bridge", "roadmap_id": "D6", "sub_step": True,
         "items": ["execution_memory read", "git lineage", "log/trace feed"]},
        {"order": "4b", "title": "Query Expansion Layer", "roadmap_id": "D7", "sub_step": True,
         "items": ["intent→queries", "symbol expansion", "multi-query", "semantic rewrite"]},
        {"order": 5, "title": "Graph Reasoning Engine", "roadmap_id": "D8",
         "items": ["root cause tracing", "dependency traversal", "impact simulation"]},
    ]},
    {"phase": 3, "title": "Pre-LLM decision system", "steps": [
        {"order": 6, "title": "Context Ranking Engine", "roadmap_id": "D9",
         "items": ["relevance scoring", "intent alignment", "noise filtering"]},
        {"order": 7, "title": "Planning Engine (semantic)", "roadmap_id": "D10",
         "items": ["decomposition BEFORE execution", "plan graph", "fallback strategies"]},
    ]},
    {"phase": 4, "title": "Execution preparation", "steps": [
        {"order": 8, "title": "Tool Router (upgrade)", "roadmap_id": "D11",
         "items": ["capability routing", "permissions", "cost estimation"]},
        {"order": 9, "title": "Validation Layer (full)", "roadmap_id": "D12",
         "items": ["dry run", "compile sim", "full safety"]},
    ]},
    {"phase": 5, "title": "Final context system", "steps": [
        {"order": 10, "title": "Diff Intelligence", "roadmap_id": "D13",
         "items": ["semantic diff", "change impact"]},
        {"order": 11, "title": "Compression Engine", "roadmap_id": "D14",
         "items": ["token budget manager", "summarization hierarchy"]},
        {"order": 12, "title": "Context Assembly Engine", "roadmap_id": "D15",
         "items": ["structured LLM packet", "merge + rank + prune"]},
        {"order": "12.1", "title": "Memory merge into packet", "roadmap_id": "D16", "sub_step": True,
         "items": ["unified memory in packet", "budget-aware merge"]},
    ]},
]

STEP_VALIDATIONS: dict[str, list[str]] = {
    "A1": ["validate-execution-spine.sh"], "A2": ["validate-execution-spine.sh"],
    "A3": ["validate-execution-spine.sh"], "A4": ["validate-execution-spine.sh"],
    "B1": ["validate-pattern-engine-v1.sh", "validate-execution-intelligence.sh"],
    "B2": ["validate-execution-decisions.sh"],
    "B3": ["validate-feedback-loop-v1.sh"],
    "B4": ["validate-planner-upgrade-v1.sh"],
    "B5": ["validate-context-intelligence-v1.sh"],
    "B6": ["validate-self-optimization-v1.sh"],
    "C1": ["validate-tool-graph-v1.sh"],
    "C2": ["validate-tool-graph-verify-v1.sh"],
    "C3": ["validate-execution-router-v1.sh"],
    "C4": ["validate-repair-loop-v1.sh"],
    "C5": ["validate-semantic-context-fabric-v1.sh"],
    "C6": ["validate-multi-step-planner-v1.sh"],
    "C7": ["validate-runtime-orchestrator-v1.sh"],
    "D1": ["validate-code-intelligence-v1.sh"],
    "D2": ["validate-graph-fusion-v1.sh"],
    "D3": ["validate-dependency-graph-v1.sh"],
    "D4": ["validate-intent-engine-v1.sh"],
    "D5": ["validate-vector-retrieval-v1.sh"],
    "D6": ["validate-memory-git-bridge-v1.sh"],
    "D7": ["validate-query-expansion-v1.sh"],
    "D8": ["validate-graph-reasoning-v1.sh"],
    "D9": ["validate-context-ranking-v1.sh"],
    "D10": ["validate-planning-engine-v1.sh"],
    "D11": ["validate-tool-router-v1.sh"],
    "D12": ["validate-validation-layer-v1.sh"],
    "D13": ["validate-diff-intelligence-v1.sh"],
    "D14": ["validate-context-compression-v1.sh"],
    "D15": ["validate-context-assembly-v1.sh", "validate-llm-context-packet-v1.sh"],
    "D15.1": ["validate-model-gate-shadow-v1.sh", "validate-model-gate-enforced-v1.sh"],
    "D15.2": ["validate-packet-readiness-v1.sh"],
    "D16": ["validate-packet-memory-merge-v1.sh"],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _artifact_exists(name: str) -> bool:
    p = SINA_HOME / name
    if p.exists():
        return True
    if name.startswith("scripts/"):
        return (SOURCE_A / name).exists()
    return False


def _l8_hybrid_live() -> bool:
    embed = (
        SOURCE_A / "scripts" / "pre_llm" / "vector_retrieval" / "embedding_provider.py"
    ).is_file()
    return embed and _artifact_exists("vector_index_v1.json")


def _layer_row(
    layer: str,
    name: str,
    target: str,
    *,
    status: str,
    gap: str,
) -> dict[str, str]:
    return {"layer": layer, "name": name, "target": target, "your_status": status, "gap": gap}


def _build_layer_comparison() -> list[dict[str, str]]:
    """Derive L0–L16 table from live ~/.sina SSOT — not static LAYER_COMPARISON."""
    has = _artifact_exists

    l2 = "done" if has("intent_engine_v1.json") else "missing"
    l3 = "done" if has("code_intelligence_v1.json") else "missing"
    l4_fusion = has("graph_fusion_v1.json")
    l4_dep = has("dependency_graph_v1.json")
    if l4_fusion and l4_dep:
        l4_status, l4_gap = "done", "D2+D3 shipped"
    elif l4_fusion or l4_dep:
        l4_status, l4_gap = "partial", "incomplete fusion or deps"
    else:
        l4_status, l4_gap = "partial", "tool graph only"

    if has("diff_intelligence_v1.json"):
        l5_status, l5_gap = "partial", "D13+D6 git lineage (read-only)"
    elif has("memory_git_bridge_v1.json"):
        l5_status, l5_gap = "partial", "D6 bridge only"
    else:
        l5_status, l5_gap = "missing", "missing"

    l6_status = "partial" if has("execution_memory.jsonl") else "missing"
    l6_gap = "D6 backend bridge" if l6_status == "partial" else "missing"

    if has("packet_memory_merge_v1.json"):
        l7_status, l7_gap = "done", "D16 unified merge shipped"
    elif has("llm_context_packet_v1.json"):
        l7_status, l7_gap = "partial", "packet.memory · D16 unified merge next"
    elif has("memory_git_bridge_v1.json"):
        l7_status, l7_gap = "partial", "fragmented jsonl · D16 next"
    else:
        l7_status, l7_gap = "partial", "no unified brain"

    embed_provider = (SOURCE_A / "scripts" / "pre_llm" / "vector_retrieval" / "embedding_provider.py").is_file()
    if embed_provider and has("vector_index_v1.json"):
        l8_status, l8_gap = "hybrid", "D5 token + L8 hash hybrid (local embed)"
    elif has("vector_index_v1.json"):
        l8_status, l8_gap = "partial", "D5 token index · embeddings later"
    else:
        l8_status, l8_gap = "missing", "missing"

    l0_status = "done" if _artifact_exists("user_signals_v1.json") else "missing"
    l0_gap = (
        "L0 hub touch SSOT · L0-full editor telemetry partial"
        if l0_status == "done"
        else "missing"
    )
    l1_status = "done" if _artifact_exists("workspace_state_v1.json") else "partial"
    l1_gap = "L1 hub-fed working set" if l1_status == "done" else "hub mirror only"

    rows = [
        _layer_row("L0", "User Signals", "keystrokes, CLI, editor events", status=l0_status, gap=l0_gap),
        _layer_row("L1", "Workspace State", "active buffers + session state", status=l1_status, gap=l1_gap),
        _layer_row("L2", "Intent Engine", "classify goal BEFORE execution", status=l2, gap="D4 shipped" if l2 == "done" else "missing"),
        _layer_row(
            "L3",
            "Code Intelligence",
            "AST + symbol graph",
            status=l3,
            gap="D1 shipped" if l3 == "done" else "critical missing",
        ),
        _layer_row("L4", "Dependency Graph", "call graph + module graph", status=l4_status, gap=l4_gap),
        _layer_row("L5", "Change History", "git diff lineage", status=l5_status, gap=l5_gap),
        _layer_row("L6", "Execution Signals", "logs / errors / tests", status=l6_status, gap=l6_gap),
        _layer_row("L7", "Memory System", "unified long/short memory", status=l7_status, gap=l7_gap),
        _layer_row("L8", "Vector Retrieval", "embeddings + semantic search", status=l8_status, gap=l8_gap),
        _layer_row(
            "L9",
            "Graph Reasoning",
            "impact / root cause graph",
            status="done" if has("graph_reasoning_v1.json") else "missing",
            gap="D8 shipped" if has("graph_reasoning_v1.json") else "missing",
        ),
        _layer_row(
            "L10",
            "Ranking System",
            "relevance scoring pre-LLM",
            status="done" if has("context_ranking_v1.json") else "partial",
            gap="D9 pre-LLM ranking" if has("context_ranking_v1.json") else "post-exec bias",
        ),
        _layer_row(
            "L11",
            "Planning Engine",
            "task decomposition BEFORE execution",
            status="done" if has("planning_engine_v1.json") else "partial",
            gap="D10 semantic plan" if has("planning_engine_v1.json") else "not semantic",
        ),
        _layer_row(
            "L12",
            "Tool Router",
            "capability-based selection",
            status="done" if has("tool_router_v1.json") else "partial",
            gap="D11 shipped" if has("tool_router_v1.json") else "weak policy layer",
        ),
        _layer_row(
            "L13",
            "Validation Layer",
            "dry-run + safety gates",
            status="done" if has("validation_layer_v1.json") else "partial",
            gap="D12 shipped" if has("validation_layer_v1.json") else "not full",
        ),
        _layer_row(
            "L14",
            "Diff Intelligence",
            "semantic diff engine",
            status="done" if has("diff_intelligence_v1.json") else "missing",
            gap="D13 shipped" if has("diff_intelligence_v1.json") else "missing",
        ),
        _layer_row(
            "L15",
            "Compression Engine",
            "token optimization",
            status="done" if has("context_compression_v1.json") else "missing",
            gap="D14 shipped" if has("context_compression_v1.json") else "missing",
        ),
    ]
    if has("packet_memory_merge_v1.json"):
        l16_status, l16_gap = "done", "D15+D16 packet complete"
    elif has("llm_context_packet_v1.json"):
        l16_status, l16_gap = "partial", "D15 packet · D16 writeback next"
    else:
        l16_status, l16_gap = "missing", "missing"
    rows.append(
        _layer_row("L16", "Context Assembly", "final LLM packet builder", status=l16_status, gap=l16_gap)
    )
    return rows


def _build_layer_blueprint() -> list[dict[str, Any]]:
    """Sync founder blueprint status fields from live layer comparison."""
    by_layer = {r["layer"]: r for r in _build_layer_comparison()}
    out: list[dict[str, Any]] = []
    for row in LAYER_BLUEPRINT:
        entry = dict(row)
        live = by_layer.get(entry["layer"])
        if not live:
            out.append(entry)
            continue
        status = live["your_status"]
        entry["status"] = status
        gap_text = live["gap"]
        if status in ("done", "hybrid"):
            entry["gap"] = "Low"
        elif "critical" in gap_text.lower():
            entry["gap"] = "Critical"
        elif status == "missing":
            entry["gap"] = "High"
        else:
            entry["gap"] = "Medium"
        out.append(entry)
    return out


def _pre_llm_shipped_count() -> int:
    keys = [
        "code_intelligence_v1.json",
        "graph_fusion_v1.json",
        "dependency_graph_v1.json",
        "intent_engine_v1.json",
        "vector_index_v1.json",
        "memory_git_bridge_v1.json",
        "query_expansion_v1.json",
        "graph_reasoning_v1.json",
        "context_ranking_v1.json",
        "planning_engine_v1.json",
        "tool_router_v1.json",
        "validation_layer_v1.json",
        "diff_intelligence_v1.json",
        "context_compression_v1.json",
        "llm_context_packet_v1.json",
        "packet_memory_merge_v1.json",
    ]
    return sum(1 for k in keys if _artifact_exists(k))


def _phase_d_complete() -> bool:
    """True when all D1–D16 pre-LLM SSOT artifacts exist locally (sa-0012)."""
    return _pre_llm_shipped_count() == 16


def _phase_d_column_status(steps: list[dict]) -> str:
    """Live Phase D column status — done when D16 artifact + all 16 journey steps past."""
    if _phase_d_complete() and steps and all(s.get("position") == "past" for s in steps):
        return "done"
    if steps and any(s.get("position") in ("past", "current") for s in steps):
        return "partial"
    return "not_built"


def _build_world_target_map() -> dict[str, Any]:
    """Live projection of WORLD_TARGET_MAP — layer table + next-move synced to SSOT."""
    out = copy.deepcopy(WORLD_TARGET_MAP)
    out["layer_comparison"] = _build_layer_comparison()
    d16 = STEP_CATALOG[CURRENT_STRATEGIC_STEP]
    shipped = _pre_llm_shipped_count()
    if _phase_d_complete():
        if _gate_is_enforce():
            out["core_gap"] = (
                f"Pre-LLM world model complete (D1–D16, {shipped}/16 SSOT artifacts). "
                "ENFORCE gate live — remaining: L0/L1 live signals + embeddings + outcome benchmarks."
            )
        else:
            out["core_gap"] = (
                f"Pre-LLM world model complete (D1–D16, {shipped}/16 SSOT artifacts). "
                "Remaining: ENFORCE gate flip + L0/L1 live signals + embeddings."
            )
    else:
        out["core_gap"] = (
            f"Pre-LLM packet pipeline shipped (D1–D15, {shipped}/16 SSOT artifacts live). "
            f"Remaining: unified memory merge ({CURRENT_STRATEGIC_STEP}) + L0/L1 live signals."
        )
    out["honest_score"] = {
        "here": [
            "Execution Spine",
            "Execution OS (post-action world)",
            "Memory → Patterns → Decisions → Feedback → Planner → Context snapshot",
            "Pre-LLM world model D1–D15 (code, graph, retrieval, plan, packet)",
            "Model dispatch gate (D15.1 shadow)",
        ],
        "not_here": [] if _phase_d_complete() else (
            [
                "Unified memory writeback into packet (D16)",
                "Live L0 user signals (keystrokes, editor events)",
            ]
            + (
                []
                if _l8_hybrid_live()
                else ["Embedding index (D5 is token retrieval today)"]
            )
        ),
    }
    if _phase_d_complete():
        not_here: list[str] = []
        if not _artifact_exists("user_signals_v1.json"):
            not_here.append("Live L0 user signals (hub touch SSOT — extend to editor)")
        if not _artifact_exists("eval_packet_v1_report.json"):
            not_here.append("Eval-1 outcome benchmarks (structural packet vs raw)")
        else:
            try:
                import json as _json
                from pathlib import Path as _P

                rep = _json.loads((_P.home() / ".sina" / "eval_packet_v1_report.json").read_text())
                if not rep.get("ok"):
                    not_here.append("Eval-1 below threshold — improve packet assembly")
            except Exception:
                not_here.append("Eval-1 report unreadable")
        if not _artifact_exists("eval_packet_v1b_report.json"):
            not_here.append("Eval-1b behavioral proof (packet vs raw LLM)")
        else:
            try:
                import json as _json
                from pathlib import Path as _P

                rep1b = _json.loads((_P.home() / ".sina" / "eval_packet_v1b_report.json").read_text())
                if rep1b.get("mode") == "scaffold":
                    not_here.append("Eval-1b live LLM A/B (scaffold proxy only)")
                elif not rep1b.get("ok"):
                    not_here.append("Eval-1b below threshold — improve packet behavioral proof")
            except Exception:
                not_here.append("Eval-1b report unreadable")
        if not _l8_hybrid_live():
            not_here.append("Embedding index (D5 token · full L8 embeddings later)")
        out["honest_score"]["not_here"] = not_here
        if not _gate_is_enforce():
            out["honest_score"]["not_here"].insert(
                0, "ENFORCE gate in production (shadow today)"
            )
    out["reality_alignment"] = {
        "built": [
            "Execution Spine",
            "Post-execution Intelligence",
            "Patterns / Decisions / Feedback / Context snapshot",
            "Tool Graph + Verification (+ Router)",
            "Pre-LLM D1–D16 complete packet + shadow gate",
        ],
        "target": (
            [
                "Live workspace + user signal capture (L0–L1)",
                "Embedding-backed semantic retrieval",
                "Outcome evaluation — packet-driven vs raw LLM",
            ]
            if _gate_is_enforce()
            else [
                "ENFORCE gate flip",
                "Live workspace + user signal capture (L0–L1)",
                "Embedding-backed semantic retrieval",
            ]
        ),
    }
    out["strategic_conclusion"] = (
        (
            "D1–D16 + ENFORCE shipped. STRATEGIC-SLICE: Eval-1 sustain, L0/L1 deepen, ENFORCE bypass map. "
            "Next engineering: Eval-1b → dispatch policy — not L8 primary. "
            "See STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md."
            if _gate_is_enforce()
            else "Pre-LLM world model complete — packet assembles with unified memory before the model. "
            "Next: ENFORCE gate when founder ready."
        )
        if _phase_d_complete()
        else (
            "Pre-LLM understanding pipeline is live — packet assembles before the model. "
            "Next: merge memory into the packet (D16), then ENFORCE gate."
        )
    )
    out["architecture_next_build"] = (
        {
            "after": "STRATEGIC-SLICE",
            "step": "Eval-1b",
            "layer": "Behavioral packet proof (live LLM A/B)",
            "why": "Highest ROI — unlocks dispatch policy; not new D-module",
        }
        if _phase_d_complete() and _gate_is_enforce()
        else {
            "after": "D16",
            "step": "ENFORCE",
            "layer": "Model dispatch ENFORCE mode",
            "why": "Block hub OpenRouter when gate_eligible false — validators already pass",
        }
        if _phase_d_complete()
        else {
            "after": "D15",
            "step": CURRENT_STRATEGIC_STEP,
            "layer": d16["title"],
            "why": d16.get("goal", "Unified memory writeback into packet under budget"),
        }
    )
    semantic_status = "done" if _artifact_exists("vector_index_v1.json") else "not_built"
    pre_llm_status = "partial" if shipped >= 14 else "partial" if shipped > 0 else "not_built"
    out["system_status"] = [
        {"name": "Execution Intelligence OS", "status": "done"},
        {"name": "Tool Graph System", "status": "done"},
        {"name": "Self-optimization loop", "status": "done"},
        {"name": "Context snapshot system", "status": "done"},
        {"name": "Pre-LLM intelligence system", "status": pre_llm_status},
        {"name": "Graph fusion layer", "status": "done" if _artifact_exists("graph_fusion_v1.json") else "partial"},
        {"name": "Dependency graph engine", "status": "done" if _artifact_exists("dependency_graph_v1.json") else "partial"},
        {"name": "Code understanding engine", "status": "done" if _artifact_exists("code_intelligence_v1.json") else "not_built"},
        {"name": "Intent inference engine", "status": "done" if _artifact_exists("intent_engine_v1.json") else "not_built"},
        {"name": "Semantic retrieval system", "status": semantic_status},
    ]
    out["next_move"] = (
        {
            "step": "STRATEGIC-SLICE",
            "title": "Eval-1 + L0/L1 + ENFORCE transparency",
            "priority": "Sustain slice; Phase 2b spine Action; lane P0 parallel",
            "items": [
                "Eval-1 + Eval-1b live sustain on build",
                "Founder Action: enqueue-eval-spine-bridge",
                "RunReceipt pack + verify:wire (Wire lane)",
                "Lane Scoreboard + vault attests",
            ],
            "then_queue": ["L8 hybrid embeddings", "Learning loop + event bus"],
            "runtime_parallel": None,
            "runtime_stack_complete": RUNTIME_STACK_COMPLETE,
        }
        if _phase_d_complete() and _gate_is_enforce()
        else {
            "step": "ENFORCE",
            "title": "Flip model dispatch gate to ENFORCE",
            "priority": "Hub Actions or maintainer — no founder Terminal",
            "items": [
                "Shadow receipts in gate_shadow_v1.jsonl",
                "validate-model-gate-enforced-v1.sh PASS",
                "Packet readiness 100% on hub",
            ],
            "then_queue": [],
            "runtime_parallel": None,
            "runtime_stack_complete": RUNTIME_STACK_COMPLETE,
        }
        if _phase_d_complete()
        else {
            "step": CURRENT_STRATEGIC_STEP,
            "title": d16["title"],
            "priority": "NON-NEGOTIABLE — completes packet memory slots",
            "items": list(d16.get("features") or [])[:4],
            "then_queue": [],
            "runtime_parallel": None,
            "runtime_stack_complete": RUNTIME_STACK_COMPLETE,
        }
    )
    return out


def _build_llm_packet_schema() -> dict[str, Any]:
    """Live projection — shipped producers + gate bypass list."""
    from pre_llm.context_packet.schema import SHIPPED_PRODUCERS  # noqa: WPS433

    out = copy.deepcopy(LLM_PACKET_SCHEMA)
    shipped = sorted(SHIPPED_PRODUCERS)
    out["pre_llm_steps_shipped"] = f"{len(shipped)}/16"
    out["shipped_producers"] = shipped
    if _gate_is_enforce():
        out["bypass_today"] = [
            "Live agents / Advisor → OpenRouter direct (not agent_loop planner)",
            "ENFORCE blocks agent_loop planner when gate_eligible false",
            "Cursor IDE chats bypass hub dispatch — packet not injected there yet",
        ]
    else:
        out["bypass_today"] = [
            "Live agents / Advisor → OpenRouter direct (not agent_loop planner)",
            "ENFORCE blocks planner only — shadow is active today",
        ]
    return out


def _build_packet_readiness() -> dict[str, Any]:
    from pre_llm.packet_readiness.hub_surface import packet_readiness_hub_payload  # noqa: WPS433

    return packet_readiness_hub_payload(task_id="wtm-readiness")


def _build_eval_packet() -> dict[str, Any]:
    try:
        from eval_packet_v1.runner import hub_payload  # noqa: WPS433

        return hub_payload()
    except Exception as e:
        return {"ok": False, "error": str(e), "producer": "Eval-1"}


def _build_eval_packet_v1b() -> dict[str, Any]:
    try:
        from eval_packet_v1b.runner import hub_payload  # noqa: WPS433

        return hub_payload()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "producer": "Eval-1b"}


def _build_dispatch_policy() -> dict[str, Any]:
    try:
        from runtime.dispatch_policy.policy_engine import dispatch_policy_payload  # noqa: WPS433

        return dispatch_policy_payload()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "producer": "dispatch-policy"}


def _build_graph_executor() -> dict[str, Any]:
    try:
        from runtime.graph_executor.api import graph_executor_v1_payload  # noqa: WPS433

        return graph_executor_v1_payload()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "producer": "graph-executor"}


def _build_user_workspace_signals() -> dict[str, Any]:
    try:
        from pre_llm.user_signals.store import hub_payload  # noqa: WPS433

        return hub_payload()
    except Exception as e:
        return {"ok": False, "error": str(e), "producer": "L0+L1"}


def _build_strategic_synthesis() -> dict[str, Any]:
    try:
        from strategic_synthesis_hub import strategic_synthesis_payload  # noqa: WPS433

        return strategic_synthesis_payload()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "schema": "strategic-synthesis-v1"}


def _build_gate_receipts() -> dict[str, Any]:
    try:
        from gate_receipts_hub import gate_receipts_hub_payload  # noqa: WPS433

        return gate_receipts_hub_payload()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _build_event_bus() -> dict[str, Any]:
    try:
        from runtime.event_bus.bus_v1 import event_bus_payload  # noqa: WPS433

        return event_bus_payload()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "schema": "event-bus-v1"}


def _build_implementation_hardening() -> dict[str, Any]:
    out = copy.deepcopy(IMPLEMENTATION_HARDENING)
    try:
        import model_dispatch  # noqa: WPS433

        out["current_gate_mode"] = model_dispatch.current_gate_mode()
        out["gate_mode_pref"] = str(model_dispatch.GATE_MODE_PREF_PATH)
    except Exception:
        pass
    return out


def _enrich_step(step_id: str, base: dict[str, Any]) -> dict[str, Any]:
    cat = STEP_CATALOG.get(step_id, {})
    out = {**base, **{k: v for k, v in cat.items() if k not in base or base.get(k) in (None, "—", "")}}
    out.setdefault("title", cat.get("title", step_id))
    out.setdefault("goal", "")
    out.setdefault("features", [])
    out.setdefault("achievements", [])
    out.setdefault("unlocks", "")
    out.setdefault("modules", STEP_MODULES.get(step_id, []))
    out.setdefault("apis", STEP_APIS.get(step_id, []))
    out.setdefault("validations", STEP_VALIDATIONS.get(step_id, []))
    return out


def _phases_def() -> list[dict[str, Any]]:
    raw = [
        {
            "id": "A",
            "title": "Execution Spine",
            "status": "done",
            "purpose": "Runtime execution substrate — single source of execution truth.",
            "doc": None,
            "build_order": 1,
            "track": "major_upgrade",
            "steps": ["A1", "A2", "A3", "A4"],
        },
        {
            "id": "B",
            "title": "Execution Intelligence OS",
            "status": "frozen",
            "purpose": "Post-execution learning — frozen after major upgrade intelligence wave.",
            "doc": "SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md",
            "build_order": 2,
            "track": "major_upgrade",
            "steps": ["B1", "B2", "B3", "B4", "B5", "B6"],
        },
        {
            "id": "C",
            "title": "Runtime Stack",
            "status": "done",
            "purpose": "Verified plan → dispatch instruction → confirm → spine.",
            "doc": "SINA_RUNTIME_STACK_LOCKED_v1.md",
            "build_order": 3,
            "track": "major_upgrade",
            "steps": ["C1", "C2", "C3", "C4", "C5", "C6", "C7"],
        },
        {
            "id": "D",
            "title": "Pre-LLM World Model",
            "status": "not_built",
            "purpose": "Repo understanding before execution → LLM context packet (target world model).",
            "doc": "SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md",
            "build_order": 4,
            "track": "major_upgrade",
            "subphases": [
                {"id": "core", "title": "Core foundation", "steps": ["D1", "D2", "D3", "D4"]},
                {"id": "semantic", "title": "Semantic understanding", "steps": ["D5", "D6", "D7", "D8"]},
                {"id": "decision", "title": "Pre-LLM decision system", "steps": ["D9", "D10"]},
                {"id": "prep", "title": "Execution preparation", "steps": ["D11", "D12"]},
                {"id": "packet", "title": "Final context system", "steps": ["D13", "D14", "D15", "D16"]},
            ],
        },
    ]
    phases: list[dict[str, Any]] = []
    for ph in raw:
        entry = {k: v for k, v in ph.items() if k not in ("steps", "subphases")}
        if ph.get("steps"):
            entry["steps"] = [_enrich_step(sid, {"id": sid, "status": _default_status(sid)}) for sid in ph["steps"]]
        if ph.get("subphases"):
            entry["subphases"] = []
            for sp in ph["subphases"]:
                entry["subphases"].append(
                    {
                        **sp,
                        "steps": [_enrich_step(sid, {"id": sid, "status": _default_status(sid)}) for sid in sp["steps"]],
                    }
                )
        phases.append(entry)
    return phases


def _default_status(step_id: str) -> str:
    if step_id == CURRENT_STRATEGIC_STEP:
        return "next"
    if step_id == CURRENT_RUNTIME_STEP and not RUNTIME_STACK_COMPLETE:
        return "next"
    done_ids = {
        "A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "B5", "B6", "C1", "C2", "C3", "C4", "C5", "C6", "C7",
        "D1", "D2", "D3", "D4", "D5",
    }
    if step_id in done_ids:
        return "done"
    return "not_started"


def _iter_phase_steps(phases: list[dict[str, Any]]):
    for ph in sorted(phases, key=lambda p: p.get("build_order", 99)):
        if ph.get("steps"):
            for st in ph["steps"]:
                yield ph, None, st
        for sp in ph.get("subphases") or []:
            for st in sp["steps"]:
                yield ph, sp, st


def _resolve_live_status(step: dict[str, Any]) -> str:
    key = step.get("live_key")
    if key and _artifact_exists(key):
        return "done"
    return str(step.get("status") or "not_started")


def _build_journey(phases: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    journey: list[dict[str, Any]] = []
    order = 0
    current_ids: set[str] = set()
    if not _phase_d_complete():
        current_ids.add(CURRENT_STRATEGIC_STEP)
    if not RUNTIME_STACK_COMPLETE:
        current_ids.add(CURRENT_RUNTIME_STEP)

    for ph, sp, st in _iter_phase_steps(phases):
        order += 1
        live_status = _resolve_live_status(st)
        locked_status = str(st.get("status") or "not_started")

        if st["id"] in current_ids:
            position = "current"
        elif live_status == "done" or locked_status in ("done", "frozen"):
            position = "past"
        elif locked_status == "next":
            position = "current"
        else:
            position = "future"

        track = "runtime" if ph["id"] == "C" else "strategic" if ph["id"] == "D" else "foundation"

        journey.append(
            {
                "order": order,
                "phase_id": ph["id"],
                "phase_title": ph["title"],
                "phase_status": ph.get("status"),
                "subphase_id": sp["id"] if sp else None,
                "subphase_title": sp["title"] if sp else None,
                "id": st["id"],
                "title": st.get("title", ""),
                "goal": st.get("goal", ""),
                "features": st.get("features", []),
                "achievements": st.get("achievements", []),
                "unlocks": st.get("unlocks", ""),
                "status": live_status if live_status == "done" else locked_status,
                "position": position,
                "track": track,
                "artifact": st.get("artifact") or st.get("gate") or "—",
                "live_verified": live_status == "done",
                "modules": st.get("modules", []),
                "apis": st.get("apis", []),
                "validations": st.get("validations", []),
                "note": st.get("note", ""),
            }
        )

    past = [j for j in journey if j["position"] == "past"]
    current = [j for j in journey if j["position"] == "current"]
    future = [j for j in journey if j["position"] == "future"]
    last_done = past[-1] if past else None

    phase_a_steps = [j for j in journey if j["phase_id"] == "A"]
    phase_b_steps = [j for j in journey if j["phase_id"] == "B"]
    phase_c_steps = [j for j in journey if j["phase_id"] == "C"]
    phase_d_steps = [j for j in journey if j["phase_id"] == "D"]

    def _phase_column(phase_id: str, title: str, status: str, steps: list[dict]) -> dict:
        done_n = len([s for s in steps if s["position"] == "past" or s.get("live_verified")])
        return {
            "id": phase_id,
            "title": title,
            "status": status,
            "steps": steps,
            "steps_done": done_n,
            "steps_total": len(steps),
        }

    phase_columns = [
        _phase_column("A", "Execution Spine", "done", phase_a_steps),
        _phase_column("B", "Execution Intelligence OS", "frozen", phase_b_steps),
        _phase_column(
            "C",
            "Runtime Stack",
            "done" if RUNTIME_STACK_COMPLETE else "partial",
            phase_c_steps,
        ),
        _phase_column(
            "D",
            "Pre-LLM World Model",
            _phase_d_column_status(phase_d_steps),
            phase_d_steps,
        ),
    ]

    done_n = len(past)
    total_n = len(journey)
    pct = round(100.0 * done_n / total_n, 1) if total_n else 0.0

    live = {
        "headline": "Major system upgrade — World Target Model build",
        "summary": (
            f"{done_n} of {total_n} upgrade steps shipped · Phase C complete (C1–C7) · Pre-LLM {CURRENT_STRATEGIC_STEP} next"
            if RUNTIME_STACK_COMPLETE
            else f"{done_n} of {total_n} upgrade steps shipped · Phase C in progress · Pre-LLM world model not started"
        ),
        "last_completed_step": last_done,
        "last_completed_phase": {
            "id": "B",
            "title": "Execution Intelligence OS",
            "status": "frozen",
            "steps": phase_b_steps,
            "steps_done": len(phase_b_steps),
        },
        "current_phase": (
            {
                # Founder law: LIVE NOW columns are always B | C | D — never B | D | D
                "id": "C",
                "title": "Runtime Stack",
                "status": "done",
                "steps": phase_c_steps,
                "steps_done": len(phase_c_steps),
                "steps_total": len(phase_c_steps),
            }
            if RUNTIME_STACK_COMPLETE
            else {
                "id": "C",
                "title": "Runtime Stack",
                "status": "partial",
                "steps": phase_c_steps,
                "steps_done": len([s for s in phase_c_steps if s["position"] == "past"]),
                "steps_total": len(phase_c_steps),
            }
        ),
        "future_phase": (
            {
                "id": "D",
                "title": "Pre-LLM World Model",
                "status": _phase_d_column_status(phase_d_steps),
                "steps": phase_d_steps,
                "steps_done": len([s for s in phase_d_steps if s["position"] == "past"]),
                "steps_total": len(phase_d_steps),
            }
            if RUNTIME_STACK_COMPLETE
            else {
                "id": "D",
                "title": "Pre-LLM World Model",
                "status": "not_built",
                "steps": phase_d_steps,
                "steps_total": len(phase_d_steps),
            }
        ),
        "runtime_phase": {
            "id": "C",
            "title": "Runtime Stack",
            "status": "done" if RUNTIME_STACK_COMPLETE else "partial",
            "steps": phase_c_steps,
            "steps_done": len(phase_c_steps) if RUNTIME_STACK_COMPLETE else len([s for s in phase_c_steps if s["position"] == "past"]),
            "steps_total": len(phase_c_steps),
        },
        "current_steps": (
            [
                {
                    "id": CURRENT_STRATEGIC_STEP,
                    "title": STEP_CATALOG.get(CURRENT_STRATEGIC_STEP, {}).get("title", "Code Intelligence Layer v1"),
                    "track": "Strategic (Pre-LLM world model)",
                    "phase_id": "D",
                    "priority": 1,
                    "goal": STEP_CATALOG.get(CURRENT_STRATEGIC_STEP, {}).get("goal", ""),
                },
            ]
            if RUNTIME_STACK_COMPLETE
            else [
                {
                    "id": CURRENT_RUNTIME_STEP,
                    "title": STEP_CATALOG.get(CURRENT_RUNTIME_STEP, {}).get("title", "Autonomous Repair Loop v1"),
                    "track": "Runtime continuity",
                    "phase_id": "C",
                    "priority": 1,
                    "goal": STEP_CATALOG.get(CURRENT_RUNTIME_STEP, {}).get("goal", ""),
                },
                {
                    "id": CURRENT_STRATEGIC_STEP,
                    "title": STEP_CATALOG.get(CURRENT_STRATEGIC_STEP, {}).get("title", "Code Intelligence Layer v1"),
                    "track": "Strategic (Pre-LLM world model)",
                    "phase_id": "D",
                    "priority": 2,
                    "goal": STEP_CATALOG.get(CURRENT_STRATEGIC_STEP, {}).get("goal", ""),
                },
            ]
        ),
        "you_are_here": {
            "between": (
                f"Phase A done → B frozen → C complete (C1–C7) → Phase D all in one column · {CURRENT_STRATEGIC_STEP} now"
                if RUNTIME_STACK_COMPLETE
                else (
                    f"Phase {phase_b_steps[0]['phase_id'] if phase_b_steps else 'B'} (frozen)"
                    f" → Phase {phase_c_steps[0]['phase_id'] if phase_c_steps else 'C'} step {CURRENT_RUNTIME_STEP}"
                    f" → Phase {phase_d_steps[0]['phase_id'] if phase_d_steps else 'D'} step {CURRENT_STRATEGIC_STEP}"
                )
            ),
            "primary_path_last_done": last_done["id"] if last_done else None,
            "runtime_next": CURRENT_RUNTIME_STEP,
            "strategic_next": CURRENT_STRATEGIC_STEP,
        },
        "layout": "abcd_four_column_v1",
        "phase_columns": phase_columns,
        "progress": {"done": done_n, "current": len(current), "future": len(future), "total": total_n, "pct": pct},
        "segments": {"past": past, "current": current, "future": future},
    }
    return journey, live


# Founder tab law — ONLY content from after "major upgrade today" (2026-06-05 session)
SESSION_SCOPE = {
    "date": "2026-06-05",
    "trigger": "we have major upgrade today",
    "law": "Roadmap or locked plan after this line = World Target Model only — never Roadmaps & goals tab, factory, or products.",
    "hub_tab": "system-roadmap",
    "hub_tab_label": "World Target Model",
    "not_mix_with": [x["title"] for x in NOT_WTM_ROADMAPS],
}

LAYER_COMPARISON: list[dict[str, str]] = [
    {"layer": "L0", "name": "User Signals", "target": "keystrokes, CLI, editor events", "your_status": "missing", "gap": "missing"},
    {"layer": "L1", "name": "Workspace State", "target": "active buffers + session state", "your_status": "partial", "gap": "weak"},
    {"layer": "L2", "name": "Intent Engine", "target": "classify goal BEFORE execution", "your_status": "missing", "gap": "missing"},
    {"layer": "L3", "name": "Code Intelligence", "target": "AST + symbol graph", "your_status": "missing", "gap": "critical missing"},
    {"layer": "L4", "name": "Dependency Graph", "target": "call graph + module graph", "your_status": "partial (tool graph only)", "gap": "incomplete"},
    {"layer": "L5", "name": "Change History", "target": "git diff lineage", "your_status": "missing", "gap": "missing"},
    {"layer": "L6", "name": "Execution Signals", "target": "logs / errors / tests", "your_status": "partial (execution_memory)", "gap": "backend-only"},
    {"layer": "L7", "name": "Memory System", "target": "unified long/short memory", "your_status": "partial (fragmented jsonl)", "gap": "no unified brain"},
    {"layer": "L8", "name": "Vector Retrieval", "target": "embeddings + semantic search", "your_status": "hybrid", "gap": "D5 token + L8 hash hybrid (local embed)"},
    {"layer": "L9", "name": "Graph Reasoning", "target": "impact / root cause graph", "your_status": "missing", "gap": "missing"},
    {"layer": "L10", "name": "Ranking System", "target": "relevance scoring pre-LLM", "your_status": "partial (planner upgrade)", "gap": "post-exec bias"},
    {"layer": "L11", "name": "Planning Engine", "target": "task decomposition BEFORE execution", "your_status": "partial (tool graph)", "gap": "not semantic"},
    {"layer": "L12", "name": "Tool Router", "target": "capability-based selection", "your_status": "partial", "gap": "weak policy layer"},
    {"layer": "L13", "name": "Validation Layer", "target": "dry-run + safety gates", "your_status": "partial", "gap": "not full"},
    {"layer": "L14", "name": "Diff Intelligence", "target": "semantic diff engine", "your_status": "missing", "gap": "missing"},
    {"layer": "L15", "name": "Compression Engine", "target": "token optimization", "your_status": "missing", "gap": "missing"},
    {"layer": "L16", "name": "Context Assembly", "target": "final LLM packet builder", "your_status": "missing", "gap": "missing"},
]


ARCHITECTURE_BLUEPRINT: dict[str, Any] = {
    "locked_version": "1.0",
    "locked_doc": ARCHITECTURE_DIAGRAM_DOC,
    "title": "Target System Architecture",
    "tagline": "How understanding is built BEFORE the LLM runs",
    "human_summary": "Your intent flows through a unified world model, gets retrieved and ranked under a token budget, then becomes a structured packet — not a raw prompt.",
    "zones": [
        {
            "id": "input",
            "order": 1,
            "label": "Input",
            "short": "What you want",
            "accent": "green",
            "nodes": [
                {"id": "user", "title": "USER", "desc": "You — goal, question, or command", "critical": False},
                {"id": "intent", "title": "Intent Engine", "desc": "Classify what you want before anything runs", "critical": False},
                {"id": "workspace", "title": "Workspace State", "desc": "Open files, buffers, live session", "critical": False},
            ],
        },
        {
            "id": "world",
            "order": 2,
            "label": "World Model",
            "short": "What the system knows",
            "accent": "violet",
            "nodes": [
                {"id": "code_intel", "title": "Code Intelligence (AST + Symbols)", "desc": "Parse structure, symbols, references", "critical": False},
                {"id": "graph_fusion", "title": "Graph Fusion Layer", "desc": "One graph: AST + calls + imports + errors", "critical": True},
                {"id": "memory", "title": "Memory + Logs + Git", "desc": "History, traces, version lineage", "critical": False},
            ],
        },
        {
            "id": "retrieve",
            "order": 3,
            "label": "Retrieve & Reason",
            "short": "Find the right evidence",
            "accent": "blue",
            "nodes": [
                {"id": "vector", "title": "Vector Retrieval", "desc": "Semantic search over code & logs", "critical": False},
                {"id": "orchestrator", "title": "Retrieval Orchestrator", "desc": "Hybrid symbol + vector + graph queries", "critical": True},
                {"id": "graph_reason", "title": "Graph Reasoning", "desc": "Impact paths, root cause, dependency walks", "critical": False},
                {"id": "ranking", "title": "Ranking System", "desc": "Score what matters for this intent", "critical": False},
            ],
        },
        {
            "id": "decide",
            "order": 4,
            "label": "Decide & Validate",
            "short": "Plan safely under budget",
            "accent": "gold",
            "nodes": [
                {"id": "budget", "title": "Context Budget Manager", "desc": "Token slots per subsystem", "critical": True},
                {"id": "planning", "title": "Planning Engine", "desc": "Step plan before execution", "critical": False},
                {"id": "router", "title": "Tool Router", "desc": "Pick the right capability", "critical": False},
                {"id": "validation", "title": "Validation Layer", "desc": "Dry-run and safety gates", "critical": False},
            ],
        },
        {
            "id": "output",
            "order": 5,
            "label": "Output",
            "short": "Packet then LLM",
            "accent": "cyan",
            "nodes": [
                {"id": "compression", "title": "Compression Engine", "desc": "Shrink without losing meaning", "critical": False},
                {"id": "assembly", "title": "Context Assembly Engine", "desc": "Merge, rank, prune into structure", "critical": True},
                {"id": "packet", "title": "LLM CONTEXT PACKET", "desc": "Structured input — not a raw prompt", "critical": False, "kind": "packet"},
                {"id": "llm", "title": "LLM", "desc": "Final reasoning step only", "critical": False, "kind": "llm"},
            ],
        },
    ],
    "pipeline_states": [
        {"id": "init", "label": "INIT", "desc": "Request received"},
        {"id": "intent", "label": "INTENT_PARSED", "desc": "Goal classified"},
        {"id": "context", "label": "CONTEXT_LOADED", "desc": "Workspace ready"},
        {"id": "graph", "label": "GRAPH_BUILT", "desc": "Unified graph ready"},
        {"id": "retrieval", "label": "RETRIEVAL_DONE", "desc": "Evidence gathered"},
        {"id": "ranked", "label": "RANKED", "desc": "Relevance scored"},
        {"id": "compressed", "label": "COMPRESSED", "desc": "Within token budget"},
        {"id": "ready", "label": "PACKET_READY", "desc": "Safe to call LLM"},
    ],
    "principles": [
        {"icon": "◈", "title": "Graph-first", "desc": "Unified relationships — not scattered files"},
        {"icon": "◎", "title": "Multi-source retrieval", "desc": "Symbol + vector + graph — not vector-only"},
        {"icon": "▣", "title": "Budget-controlled", "desc": "Token slots per layer — not blind compression"},
        {"icon": "⟳", "title": "State-driven", "desc": "Pipeline states — not a dumb linear script"},
    ],
    "legend": [
        {"key": "critical", "label": "Core gap layer (★)"},
        {"key": "packet", "label": "Structured LLM input"},
        {"key": "llm", "label": "Final reasoning only"},
    ],
}


SYSTEM_AUTHORITIES: dict[str, Any] = {
    "doc": AUTHORITY_DOC,
    "governance_entry_doc": GOVERNANCE_ENTRY_DOC,
    "index_doc": AUTHORITY_INDEX_DOC,
    "unification_law": "One topic → one canonical LOCKED doc; pointers only elsewhere; superseded in archive/superseded/ only.",
    "focus": "Understanding before action — pre-LLM world model (D) while completing safe runtime (C).",
    "external_review_policy": "ChatGPT and external audits are critics only — never direct build steering.",
    "critic_law_doc": CRITIC_LAW_DOC,
    "critic_input_class": "EXTERNAL_CRITIC",
    "critic_name_aliases": ["GPT", "Chat GPT", "ChatGPT", "OpenAI chat"],
    "critic_label_rule": "First agent reply line must be INPUT CLASS: EXTERNAL_CRITIC when critic paste detected.",
    "asf_order_class": "ASF_ORDER",
    "meta_reasoning_doc": META_REASONING_DOC,
    "meta_reasoning_law": "L0–L12 decision sovereignty — SSOT wins; critic isolated; validate before state change; hub is projection.",
    "meta_reasoning_stack": [
        {"layer": "L0", "id": "source_authority", "effect": "If not in SSOT, not a directive"},
        {"layer": "L1", "id": "input_classification", "effect": "No raw execution from external text"},
        {"layer": "L2", "id": "step_order", "effect": "Order is structural, not negotiable"},
        {"layer": "L3", "id": "build_authority", "effect": "Only current step(s) are real"},
        {"layer": "L4", "id": "critic_isolation", "effect": "Critic = lens, not controller"},
        {"layer": "L5", "id": "architecture_stability", "effect": "Evolve vertically, not structurally"},
        {"layer": "L6", "id": "memory_authority", "effect": "B = truth; D6 = retrieval only"},
        {"layer": "L7", "id": "graph_separation", "effect": "Graphs in different dimensions"},
        {"layer": "L8", "id": "planning_authority", "effect": "D10 wins pre-exec planning"},
        {"layer": "L9", "id": "pipeline_validation", "effect": "Nothing moves without gate"},
        {"layer": "L10", "id": "handoff_contract", "effect": "C5 passes handles only"},
        {"layer": "L11", "id": "version_immutability", "effect": "No invisible evolution"},
        {"layer": "L12", "id": "execution_safety", "effect": "No act without explicit gate"},
    ],
    "agent_judgment_doc": AGENT_JUDGMENT_DOC,
    "agent_judgment_law": "Smart judgment rank 3 — contract harden, quality, incident prevention; never invert SOURCE or critic-driven reorder.",
    "authority_hierarchy": [
        {"rank": 0, "class": "ASF_ORDER", "role": "explicit founder imperative"},
        {"rank": 1, "class": "LOCKED_SOURCE", "role": "*_LOCKED_vN.md at root"},
        {"rank": 2, "class": "MACHINE_SSOT", "role": "system_roadmap.py, validators, audits"},
        {"rank": 3, "class": "SMART_JUDGMENT", "role": "beneficial line under AGENT_JUDGMENT doc"},
        {"rank": 4, "class": "BLUEPRINT", "role": "companions inform only"},
        {"rank": 5, "class": "ATTACHMENT", "role": "archive/attachments staging"},
        {"rank": 6, "class": "EXTERNAL_CRITIC", "role": "GPT paste compare only"},
    ],
    "self_healing_loop": ["detect", "classify", "remediate", "harden", "verify", "record"],
    "gov_unify_doc": GOV_UNIFY_DOC,
    "gov_unify_pipeline": ["intake", "inventory", "score", "map", "merge", "archive", "sync", "verify"],
    "graph_taxonomy": [
        {"type": "execution_tool_graph", "owner": "C1", "models": "tool/capability dispatch order", "not": "code AST"},
        {"type": "semantic_code_graph", "owner": "D1-D3", "models": "repo structure, calls, impact", "not": "tool routing"},
        {"type": "recovery_graph", "owner": "C4", "models": "failure → recovery suggestions", "not": "pre-LLM reasoning"},
    ],
    "d1_bootstrap_law": "D1 includes repo walker, file discovery, language detection, module seed — no new step ID.",
    "d2_d3_split": "D2 = unified semantic fusion graph; D3 = structural dependency + impact graph.",
    "memory_matrix": [
        {"class": "causal", "step": "B2", "plane": "B", "role": "historical truth (frozen causality)", "writes": True, "pre_llm_authority": False},
        {"class": "snapshot", "step": "B5", "plane": "B", "role": "historical truth snapshot (matters_now)", "writes": True, "pre_llm_authority": False},
        {"class": "retrieval_feed", "step": "D6", "plane": "D", "role": "retrieval substrate only — reads B, never defines truth", "writes": False, "pre_llm_authority": False},
        {"class": "runtime_trace", "step": "C4", "plane": "C", "role": "this-run repair trace", "writes": True, "pre_llm_authority": False},
        {"class": "packet_export", "step": "D16", "plane": "D", "role": "budget-aware memory writeback into packet", "writes": True, "pre_llm_authority": True},
    ],
    "memory_enforcement_law": "B-layer = historical truth (frozen causality). D-layer = queryable retrieval substrate. D6 reads B — never overrides.",
    "planning_matrix": [
        {"class": "learned_ranking", "step": "B4", "authority": "learning signal only — NOT planning truth"},
        {"class": "runtime_chain", "step": "C6", "authority": "execution-time sequencing only — NOT pre-LLM plan"},
        {"class": "semantic_plan", "step": "D10", "authority": "ONLY SSOT for LLM-bound pre-exec plan"},
    ],
    "planning_enforcement_law": "D10 wins for pre-execution plan truth. B4 may inform as soft bias. C6 sequences tools at runtime only.",
    "retrieval_pipeline": ["D4", "D7", "D5", "D6", "D3", "D8"],
    "retrieval_pipeline_note": "D7 = query formulation + source router (no separate step ID).",
    "c5_bridge_law": "C5 is stateless mapping only — passes handles to D1/D5; no AST, retrieval, ranking, or inference.",
    "b_frozen_law": "B1–B6 frozen; read-only upstream for C and D.",
    "packet_pipeline_law": "D14 compress → D15 assemble+validate → D16 writeback only (no recomputation).",
    "token_budget": {"policy_step": "D14", "assembly_step": "D15", "writeback_step": "D16", "validation": "validate-llm-context-packet-v1.sh"},
}



WORLD_TARGET_MAP: dict[str, Any] = {
    "title": "World Target Model Map — FINAL v5.2",
    "authorities": SYSTEM_AUTHORITIES,
    "reality_alignment": {
        "built": [
            "Execution Spine",
            "Post-execution Intelligence",
            "Patterns / Decisions / Feedback / Context snapshot",
            "Tool Graph + Verification (+ Router)",
        ],
        "target": [
            "Pre-LLM world model",
            "Repo understanding BEFORE execution",
            "Intent → structured plan BEFORE runtime",
            "Semantic + graph + retrieval BEFORE LLM",
        ],
    },
    "core_gap": "You have a learning system after action. The target is an understanding system before action.",
    "layer_comparison": LAYER_COMPARISON,
    "honest_score": {
        "here": [
            "Execution OS (post-action world)",
            "Memory → Patterns → Decisions → Feedback → Planner → Context snapshot",
        ],
        "not_here": [
            "Pre-LLM intelligence system",
            "Repo understanding BEFORE decision",
            "Intent BEFORE execution",
            "Graph BEFORE reasoning",
        ],
    },
    "architecture_blueprint": ARCHITECTURE_BLUEPRINT,
    "strategic_conclusion": "You built a brain that learns from execution — not a brain that understands before execution.",
    "architecture_flow": [
        "USER",
        "Intent Engine",
        "Workspace State",
        "Code Intelligence (AST + Symbols)",
        "Graph Fusion Layer",
        "Memory + Logs + Git",
        "Vector Retrieval",
        "Retrieval Orchestrator",
        "Graph Reasoning",
        "Ranking System",
        "Context Budget Manager",
        "Planning Engine",
        "Tool Router",
        "Validation Layer",
        "Compression Engine",
        "Context Assembly Engine",
        "LLM CONTEXT PACKET",
        "LLM",
    ],
    "architecture_pipeline_states": [
        "INIT",
        "INTENT_PARSED",
        "CONTEXT_LOADED",
        "GRAPH_BUILT",
        "RETRIEVAL_DONE",
        "RANKED",
        "COMPRESSED",
        "PACKET_READY",
    ],
    "architecture_principles": [
        "Graph-first — not file-first",
        "Multi-source retrieval — not vector-only",
        "Budget-controlled context — not compress-only",
        "State-driven pipeline — not linear script",
    ],
    "architecture_next_build": {
        "after": "D3",
        "step": "D5",
        "layer": "Vector Retrieval Engine v1",
        "why": "Local embedding index + AST chunks — fixes C5 dead pointer",
    },
    "critical_truth": "The LLM is NOT the intelligence. The LLM is the final reasoning step on a pre-built world model.",
    "system_status": [
        {"name": "Execution Intelligence OS", "status": "done"},
        {"name": "Tool Graph System", "status": "done"},
        {"name": "Self-optimization loop", "status": "done"},
        {"name": "Context snapshot system", "status": "done"},
        {"name": "Pre-LLM intelligence system", "status": "partial"},
        {"name": "Graph fusion layer", "status": "done"},
        {"name": "Dependency graph engine", "status": "done"},
        {"name": "Code understanding engine", "status": "done"},
        {"name": "Intent inference engine", "status": "done"},
        {"name": "Semantic retrieval system", "status": "not_built"},
    ],
    "next_move": {
        "step": "D5",
        "title": "Vector Retrieval Engine v1",
        "priority": "NON-NEGOTIABLE — semantic retrieval substrate",
        "items": ["local embedding index", "AST-aware chunks", "live /api/vector-retrieval-v1"],
        "then_queue": ["D6", "D7", "D8", "D9", "D10"],
        "runtime_parallel": None,
        "runtime_stack_complete": True,
    },
}

SESSION_BUILT: list[dict[str, str]] = [
    {"id": "A", "title": "Execution Spine", "status": "done"},
    {"id": "B", "title": "Intelligence B1–B6", "status": "done"},
    {"id": "C1-C3", "title": "Runtime — Tool Graph, Verification, Router", "status": "done"},
    {"id": "roadmap", "title": "Locked big-picture + pre-LLM roadmap docs", "status": "done"},
    {"id": "hub", "title": "World Target Model hub tab + live map", "status": "done"},
    {"id": "C4", "title": "Autonomous Repair Loop", "status": "done"},
    {"id": "C5", "title": "Semantic Context Fabric", "status": "done"},
    {"id": "C6", "title": "Multi-Step Execution Planner", "status": "done"},
    {"id": "C7", "title": "Runtime Orchestrator", "status": "done"},
    {"id": "D1", "title": "Code Intelligence Layer v1", "status": "done"},
    {"id": "D2", "title": "Graph Fusion Layer v1", "status": "done"},
    {"id": "D3", "title": "Dependency Graph Engine v1", "status": "done"},
    {"id": "D4", "title": "Intent Inference Engine v1", "status": "done"},
    {"id": "D5", "title": "Vector Retrieval Engine v1", "status": "done"},
    {"id": "D6", "title": "Memory Git Bridge v1", "status": "done"},
    {"id": "D7", "title": "Query Expansion v1", "status": "done"},
    {"id": "D8", "title": "Graph Reasoning Engine v1", "status": "done"},
    {"id": "D9", "title": "Context Ranking Engine v1", "status": "done"},
    {"id": "D10", "title": "Semantic Planning Engine v1", "status": "done"},
    {"id": "D11", "title": "Tool Router v1", "status": "done"},
    {"id": "D12", "title": "Validation Layer v1", "status": "done"},
    {"id": "D13", "title": "Diff Intelligence v1", "status": "done"},
    {"id": "D14", "title": "Context Compression v1", "status": "done"},
    {"id": "D15", "title": "Context Assembly v1", "status": "done"},
    {"id": "D15.1", "title": "Model dispatch gate v1", "status": "done"},
    {"id": "D15.2", "title": "Packet readiness hub surface v1", "status": "done"},
    {"id": "D16", "title": "Unified memory merge into packet v1", "status": "done"},
]


def _phase_d_step_ids(phases: list[dict[str, Any]]) -> list[str]:
    for ph in phases:
        if ph.get("id") != "D":
            continue
        ids: list[str] = []
        for sp in ph.get("subphases") or []:
            for step in sp.get("steps") or []:
                ids.append(step["id"])
        return ids
    return []


def _strategic_build_step_count() -> int:
    return sum(len(ph.get("steps") or []) for ph in STRATEGIC_BUILD_PHASES)


def _build_do_now() -> dict[str, Any]:
    if RUNTIME_STACK_COMPLETE and _phase_d_complete():
        if _gate_is_enforce():
            primary_step, primary_title, primary_jump = (
                "STRATEGIC-SLICE",
                "Eval-1 + L0/L1 + ENFORCE transparency",
                "eval-packet-panel",
            )
            return {
                "label": "PHASE D COMPLETE — Strategic slice (founder verdict)",
                "naming_note": (
                    "D1–D16 shipped. NOT new D-module. Slice: Eval-1 sustain + L0/L1 deepen + "
                    "ENFORCE bypass map. Rules-in-charge loop mandatory. L8 deferred."
                ),
                "primary": {
                    "step": primary_step,
                    "title": primary_title,
                    "track": "strategic",
                    "hub_phase": "D",
                    "jump": primary_jump,
                },
                "parallel": {
                    "step": CURRENT_RUNTIME_STEP,
                    "title": "Runtime stack complete (C1–C7)",
                    "track": "runtime",
                    "hub_phase": "C",
                    "jump": "sr-you-are-here",
                    "status": "done",
                },
            }
        return {
            "label": "PHASE D COMPLETE — flip ENFORCE gate when ready",
            "naming_note": "D1–D16 shipped. Model dispatch shadow → enforce via hub/maintainer only.",
            "primary": {
                "step": "ENFORCE",
                "title": "Model dispatch ENFORCE mode",
                "track": "strategic",
                "hub_phase": "D",
                "jump": "packet-readiness-panel",
            },
            "parallel": {
                "step": CURRENT_RUNTIME_STEP,
                "title": "Runtime stack complete (C1–C7)",
                "track": "runtime",
                "hub_phase": "C",
                "jump": "sr-you-are-here",
                "status": "done",
            },
        }
    if RUNTIME_STACK_COMPLETE:
        return {
            "label": f"DO THIS STEP NOW: {CURRENT_STRATEGIC_STEP}",
            "naming_note": "Phase C complete (C1–C7). Strategic focus = Pre-LLM world model.",
            "primary": {
                "step": CURRENT_STRATEGIC_STEP,
                "title": STEP_CATALOG[CURRENT_STRATEGIC_STEP]["title"],
                "track": "strategic",
                "hub_phase": "D",
                "jump": "sr-map-9",
            },
            "parallel": {
                "step": CURRENT_RUNTIME_STEP,
                "title": "Runtime stack complete (C1–C7)",
                "track": "runtime",
                "hub_phase": "C",
                "jump": "sr-you-are-here",
                "status": "done",
            },
        }
    return {
        "label": f"DO THIS STEP NOW: {CURRENT_RUNTIME_STEP}",
        "naming_note": "Step ID matches phase letter — C4 is Phase C, D1 is Phase D.",
        "primary": {
            "step": CURRENT_RUNTIME_STEP,
            "title": STEP_CATALOG[CURRENT_RUNTIME_STEP]["title"],
            "track": "runtime",
            "hub_phase": "C",
            "jump": "sr-you-are-here",
        },
        "parallel": {
            "step": CURRENT_STRATEGIC_STEP,
            "title": STEP_CATALOG[CURRENT_STRATEGIC_STEP]["title"],
            "track": "strategic",
            "hub_phase": "D",
            "jump": "sr-map-9",
        },
    }


def _build_ui_contract(phases: list[dict[str, Any]]) -> dict[str, Any]:
    phase_d_ids = _phase_d_step_ids(phases)
    span = f"{phase_d_ids[0]} → {phase_d_ids[-1]}" if phase_d_ids else ""
    return {
        "ssot_module": "scripts/system_roadmap.py",
        "build_script": "scripts/build-sina-command-panel.py",
        "audit_script": "scripts/audit_hub_source_alignment.py",
        "procedure_doc": HUB_UI_PROCEDURE_DOC,
        "map_doc": MAP_DOC,
        "law_doc": LAW_DOC,
        "master_doc": MASTER_DOC,
        "payload_version": PAYLOAD_VERSION,
        "phase_order": list(PHASE_ORDER),
        "current_strategic_step": CURRENT_STRATEGIC_STEP,
        "current_runtime_step": CURRENT_RUNTIME_STEP,
        "runtime_stack_complete": RUNTIME_STACK_COMPLETE,
        "phase_d": {
            "step_count": len(phase_d_ids),
            "step_ids": phase_d_ids,
            "build_order_span": span,
        },
        "strategic_build_step_count": _strategic_build_step_count(),
        "step_id_law": "FINAL v5.2 — step prefix = phase letter; governance entry SINA_GOVERNANCE_ENTRY_LOCKED_v1.md",
        "step_id_migration_doc": "brain-os/wtm/WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md",
        "do_now": _build_do_now(),
        "render_rules": [
            "Founder UI renders system_roadmap payload only — no duplicate step catalogs in app.js",
            "Step counts and build-order spans come from ui_contract or live payload fields",
            "Locked markdown docs mirror code SSOT; audit fails build on drift",
            "Upgrade path: edit system_roadmap.py → MAP vN+1 → archive vN → rebuild hub",
        ],
    }


def _build_ship_ready() -> dict[str, Any]:
    out = copy.deepcopy(SHIP_READY)
    mode = _live_gate_mode()
    out["gate_mode"] = mode
    if _gate_is_enforce():
        nxt = []
        if not _artifact_exists("user_signals_v1.json"):
            nxt.append("l0_user_signals")
        if not _artifact_exists("eval_packet_v1_report.json"):
            nxt.append("eval_packet_vs_raw_llm")
        nxt.append("l8_embedding_index")
        out["current_step"] = nxt[0] if nxt else "L8"
        out["checklist_next"] = nxt or ["l8_embedding_index"]
    else:
        out["checklist_next"] = ["enforce_gate_flip", "l0_user_signals"]
    return out


def system_roadmap_payload() -> dict:
    phases = _phases_def()
    journey, live = _build_journey(phases)
    phase_d_steps = [j for j in journey if j.get("phase_id") == "D"]
    for ph in phases:
        if ph.get("id") == "D":
            ph["status"] = _phase_d_column_status(phase_d_steps)
    ui_contract = _build_ui_contract(phases)

    return {
        "ok": True,
        "schema": "world-target-model-session-v1",
        "updated_at": _now(),
        "version": PAYLOAD_VERSION,
        "ui_contract": ui_contract,
        "session_scope": SESSION_SCOPE,
        "law_doc": LAW_DOC,
        "ui_doc": UI_DOC,
        "master_doc": MASTER_DOC,
        "map_doc": MAP_DOC,
        "authority_doc": AUTHORITY_DOC,
        "authorities": SYSTEM_AUTHORITIES,
        "wtm_locked_docs": WTM_LOCKED_DOCS,
        "not_wtm_roadmaps": NOT_WTM_ROADMAPS,
        "world_target_map": _build_world_target_map(),
        "hub_url": "http://127.0.0.1:13020/?tab=system-roadmap",
        "diagram_url": "http://127.0.0.1:13020/?tab=system-roadmap&view=diagram",
        "phase_order": list(PHASE_ORDER),
        "upgrade": {
            "title": "World Target Model",
            "session_date": SESSION_SCOPE["date"],
            "trigger": SESSION_SCOPE["trigger"],
            "what_we_built": "Spine A1–A4 → Intelligence B1–B6 → Runtime C1–C3",
            "core_gap": "Learning after action ✅ · Understanding before action ❌",
            "chronology": UPGRADE_CHRONOLOGY,
        },
        "misconceptions": MISCONCEPTIONS,
        "session_built": SESSION_BUILT,
        "live": live,
        "journey": journey,
        "current_vs_target": CURRENT_VS_TARGET,
        "current_system_built": CURRENT_SYSTEM_BUILT,
        "layer_blueprint": _build_layer_blueprint(),
        "llm_packet_schema": _build_llm_packet_schema(),
        "packet_readiness": _build_packet_readiness(),
        "eval_packet": _build_eval_packet(),
        "eval_packet_v1b": _build_eval_packet_v1b(),
        "dispatch_policy": _build_dispatch_policy(),
        "graph_executor": _build_graph_executor(),
        "user_workspace_signals": _build_user_workspace_signals(),
        "gate_receipts": _build_gate_receipts(),
        "event_bus": _build_event_bus(),
        "strategic_synthesis": _build_strategic_synthesis(),
        "session_lineage": SESSION_LINEAGE,
        "implementation_hardening": _build_implementation_hardening(),
        "ship_ready": _build_ship_ready(),
        "roadmap_attachments": [
            {
                "id": "claude-analyst-pre-llm-gate-v1",
                "path": CLAUDE_ANALYST_ATTACHMENT,
                "title": "Claude AI · pre-LLM gate hardening (trigger)",
                "critic_class": "EXTERNAL_CRITIC",
                "layer": "A",
                "status": "attached",
                "convinced": True,
                "parent_steps": ["D5", "D15"],
                "substeps_added": ["D15.1", "D15.2"],
                "summary": "Gate modes OFF/SHADOW/ENFORCE · model_dispatch choke · 90-day hardened order",
            },
            {
                "id": "gpt-claude-wtm-synthesis-v1",
                "path": "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md",
                "title": "GPT + Claude WTM synthesis (LOCKED)",
                "critic_class": "SYNTHESIS",
                "layer": "D",
                "status": "locked",
                "convinced": True,
                "parent_steps": ["D16", "Eval-1", "L0"],
                "substeps_added": [],
                "summary": "Saved GPT/Claude analysis, agent insights, live results, pendings — compare only",
            },
            {
                "id": "strategic-next-steps-v2",
                "path": "STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md",
                "title": "Strategic next steps — big picture (LOCKED v2)",
                "critic_class": "FOUNDER_SYNTHESIS",
                "layer": "D",
                "status": "locked",
                "convinced": True,
                "parent_steps": ["STRATEGIC-SLICE", "Eval-1b"],
                "substeps_added": [],
                "summary": "Goals, pendings, phase plan 0–5, lessons — hub /api/strategic-synthesis-v1",
            },
            {
                "id": "cursor-agent-post-claude-synthesis-v1",
                "path": CURSOR_AGENT_SYNTHESIS,
                "title": "Cursor agent · post-Claude synthesis",
                "critic_class": "AGENT_SYNTHESIS",
                "layer": "B",
                "status": "attached",
                "convinced": True,
                "parent_steps": ["D5", "D15"],
                "substeps_added": [],
                "summary": "Research · lessons · knowledge library · D5 ship · hub · shadow gate — do not drop",
            },
            {
                "id": "golden-pre-llm-gate-research-v1",
                "path": GOLDEN_RESEARCH_REPORT,
                "title": "Golden pre-LLM gate · best-of-worlds research",
                "critic_class": "RESEARCH_SYNTHESIS",
                "layer": "B",
                "status": "attached",
                "convinced": True,
                "parent_steps": ["D5", "D9", "D10", "D15"],
                "substeps_added": [],
                "summary": "Industry refs · 7 golden suggestions · replay envelope · top 5 ideas · today vs target",
            },
            {
                "id": "agent-lessons-pre-llm-v1",
                "path": AGENT_LESSONS_PRE_LLM,
                "title": "Agent lessons · pre-LLM gate & threads",
                "critic_class": "AGENT_LESSONS",
                "layer": "B",
                "status": "active",
                "convinced": True,
                "parent_steps": ["D5", "D15"],
                "substeps_added": [],
                "summary": "Durable lessons + active threads · auto-updated on research turns",
            },
            {
                "id": "blueprint-market-100-plans-v1",
                "path": "archive/attachments/commercial_goal_specialist/sina_os/BLUEPRINT_MARKET_100_PLANS_RESEARCH_REPORT_v1.md",
                "title": "Blueprint × market · 100 plans (Jun 2026)",
                "critic_class": "RESEARCH_SYNTHESIS",
                "layer": "B",
                "status": "attached",
                "convinced": True,
                "parent_steps": ["STRATEGIC-SLICE", "W1", "W2", "W3"],
                "substeps_added": [],
                "summary": "Live market research · PLAN-001..100 · SSOT v3.1 aligned · essay in commercial-governance field",
            },
        ],
        "strategic_build_phases": STRATEGIC_BUILD_PHASES,
        "truth": {
            "current_flow": CURRENT_VS_TARGET["current_flow"],
            "target_flow": CURRENT_VS_TARGET["target_flow"],
            "critical": "The model is NOT the brain. The system before the model is the real intelligence.",
            "model_role": "Model = reasoning executor on a pre-built world model",
        },
        "phases": phases,
        "next_steps": [
            {
                "track": "Strategic slice",
                "step": "STRATEGIC-SLICE",
                "title": "Sustain Eval-1/L0/L1/ENFORCE + lane attests",
                "priority": 1,
                "goal": "Slice green; commercial P0 parallel",
            },
            {
                "track": "Runtime",
                "step": "PHASE-2B",
                "title": "Founder spine Action + graph executor",
                "priority": 2,
                "goal": "Close loop via eval proof bridge — dispatch_ready stays false",
            },
            {
                "track": "Engineering queue",
                "step": "L8-HYBRID",
                "title": "Embedding index + hybrid D9",
                "priority": 3,
                "goal": "Retrieval beyond D5 token overlap",
            },
        ],
    }


def main() -> int:
    import argparse
    import json

    p = argparse.ArgumentParser(description="World Target Model roadmap payload SSOT")
    p.add_argument("--json", action="store_true", help="Emit full system_roadmap_payload JSON")
    args = p.parse_args()
    payload = system_roadmap_payload()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        pd = (payload.get("ui_contract") or {}).get("phase_d") or {}
        print(json.dumps({"version": payload.get("version"), "phase_d": pd}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

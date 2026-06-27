#!/usr/bin/env python3
"""Meta-reasoning policy stack — hub payload for L0–L12 decision governance."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
LAW_DOC = "brain-os/law/META_REASONING_POLICY_STACK_LOCKED_v1.md"
TAB_ID = "decision-governance"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _layers() -> list[dict[str, Any]]:
    return [
        {
            "layer": "L0",
            "id": "source_authority",
            "title": "Source authority (SSOT law)",
            "purpose": "Decides what is truth source",
            "effect": "If it's not in SSOT, it is not a directive.",
            "canonical": [
                "SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md",
                "SINA_OS_SSOT_LOCKED.md",
                "scripts/system_roadmap.py",
            ],
        },
        {
            "layer": "L1",
            "id": "input_classification",
            "title": "Input classification",
            "purpose": "How incoming data is treated before interpretation",
            "effect": "No raw execution from external text.",
            "canonical": [
                "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md",
                "AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md",
            ],
        },
        {
            "layer": "L2",
            "id": "step_order",
            "title": "Step order governance",
            "purpose": "Controls execution sequence",
            "effect": "Order is structural, not negotiable.",
            "canonical": [
                "WORLD_TARGET_MODEL_MAP_LOCKED_v5.md",
                "WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md",
            ],
        },
        {
            "layer": "L3",
            "id": "build_authority",
            "title": "Build authority",
            "purpose": "What actually gets implemented",
            "effect": "Only one WTM step is real at a time per track.",
            "canonical": ["scripts/system_roadmap.py", "AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md"],
        },
        {
            "layer": "L4",
            "id": "critic_isolation",
            "title": "Critic isolation",
            "purpose": "Prevents external model steering",
            "effect": "Critic = lens, not controller.",
            "canonical": ["CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md"],
        },
        {
            "layer": "L5",
            "id": "architecture_stability",
            "title": "Architecture stability",
            "purpose": "Prevents redesign drift",
            "effect": "System evolves vertically, not structurally.",
            "canonical": [
                "WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md",
                "WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md",
            ],
        },
        {
            "layer": "L6",
            "id": "memory_authority",
            "title": "Memory authority",
            "purpose": "Governs truth storage layers",
            "effect": "Memory ≠ truth unless designated B-layer.",
            "canonical": ["WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md §4"],
        },
        {
            "layer": "L7",
            "id": "graph_separation",
            "title": "Graph separation",
            "purpose": "Prevents semantic graph confusion",
            "effect": "Graphs exist in different dimensions.",
            "canonical": ["WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md §2"],
        },
        {
            "layer": "L8",
            "id": "planning_authority",
            "title": "Planning authority",
            "purpose": "Who controls planning truth",
            "effect": "Planning split by time — D10 wins pre-exec.",
            "canonical": ["WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md §5"],
        },
        {
            "layer": "L9",
            "id": "pipeline_validation",
            "title": "Pipeline validation",
            "purpose": "Correctness before state change",
            "effect": "Nothing moves without validation gate.",
            "canonical": [
                "brain-os/law/HUB_SOURCE_UI_ALIGNMENT_PROCEDURE_LOCKED_v1.md",
                "brain-os/law/GOVERNANCE_DRIFT_ENGINE_LOCKED_v1.md",
            ],
        },
        {
            "layer": "L10",
            "id": "handoff_contract",
            "title": "Handoff contract (C ↔ D)",
            "purpose": "Runtime → pre-LLM interface",
            "effect": "Bridge passes references, not intelligence.",
            "canonical": ["SINA_RUNTIME_STACK_LOCKED_v1.md", "WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md"],
        },
        {
            "layer": "L11",
            "id": "version_immutability",
            "title": "Version & immutability",
            "purpose": "Prevents silent drift",
            "effect": "No invisible evolution.",
            "canonical": [
                "SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md",
                "SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md",
            ],
        },
        {
            "layer": "L12",
            "id": "agent_automation_safety",
            "title": "Agent & automation safety (foundation capstone)",
            "purpose": "Foundational understanding — agents/automation never get silent hands",
            "effect": "Learn gates first; then lock in incident laws — not a WTM layer.",
            "canonical": [
                "SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md",
                "brain-os/law/SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md",
                "AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md",
            ],
        },
    ]


def _layer_lessons() -> list[dict[str, str]]:
    return [
        {"layer": "L0", "lesson": "Truth in SSOT + machine step state — hub/chat are mirrors."},
        {"layer": "L1", "lesson": "Label every input before acting (ASF_ORDER, EXTERNAL_CRITIC, …)."},
        {"layer": "L2", "lesson": "Step order frozen A→B→C→D — no critic reorder."},
        {"layer": "L3", "lesson": "Build only CURRENT_*_STEP — one real step per track."},
        {"layer": "L4", "lesson": "External models compare — they do not steer roadmap."},
        {"layer": "L5", "lesson": "Evolve vertically inside a step — never collapse layers."},
        {"layer": "L6", "lesson": "B-layer = historical truth; D reads — memory ≠ authority."},
        {"layer": "L7", "lesson": "Tool ≠ semantic ≠ recovery graph — never merge stores."},
        {"layer": "L8", "lesson": "Planning split: B4 bias · C6 runtime · D10 pre-exec SSOT."},
        {"layer": "L9", "lesson": "Done = validators PASS — evidence, not optimism."},
        {"layer": "L10", "lesson": "C5 bridge passes handles only — no smuggled intelligence."},
        {"layer": "L11", "lesson": "Law change = version bump + archive — no silent drift."},
        {"layer": "L12", "lesson": "Agents & automation: no silent paste/merge/dispatch — foundation capstone, not WTM."},
    ]


def _application_guide() -> dict[str, Any]:
    return {
        "version": "1.2",
        "section": "META_REASONING_POLICY_STACK_LOCKED_v1.md §9",
        "foundation_not_wtm": True,
        "zero_overlap_rule": "Governance Ln and WTM Ln share labels only — zero mapping, zero mirror.",
        "learning_chain": "Foundation L0–L12 → discover → lock *_LOCKED_vN.md (SSOT) → enforce in hub",
        "do_not_confuse": {
            "governance_l0_l12": "FOUNDATION — how agents & automation are controlled (this tab only)",
            "product_l0_l16": "PRODUCT — what to build (World Target Model tab — unrelated namespace)",
        },
        "layer_lessons": _layer_lessons(),
        "founder_daily_loop": [
            "Decision governance → read foundation L0–L12 (not WTM)",
            "Today + Order Guardian → operational do-now (separate track)",
            "External paste → INPUT CLASS: EXTERNAL_CRITIC first line",
            "After ship claim → governance drift + validate-*",
            "Worth keeping → draft → lock SSOT vN+1 (L11)",
        ],
        "agent_session_loop": [
            "Governance entry §0b → foundation stack (not WTM tab)",
            "Classify incoming message (L1)",
            "Find applicable LOCKED law (L0) — not chat precedent",
            "EXTERNAL_CRITIC / research → compare only (L4)",
            "Agent skill + repo boundary (L5)",
            "Validators before done (L9)",
            "No silent agent/automation side-effects (L12)",
            "Record resolutions → agent-governance-events.jsonl",
            "Repeatable lesson → propose SSOT lock",
        ],
        "scenarios": [
            {
                "situation": "ChatGPT sends new step order",
                "apply": "L1 + L4 — classify critic; map to WTM",
                "wrong": "Change CURRENT_*_STEP from chat",
            },
            {
                "situation": "Hub tab count ≠ law",
                "apply": "L9 — audit_essentials_nav + rebuild",
                "wrong": "Edit law to match broken hub",
            },
            {
                "situation": "Governance L12 confused with WTM L12",
                "apply": "§9.0 — unrelated labels; read foundation only here",
                "wrong": "Merge or map layer tables across tabs",
            },
            {
                "situation": "Auto Runtime-paste into Cursor",
                "apply": "L12 — founder opt-in only",
                "wrong": "Auto-inject prompt",
            },
            {
                "situation": "Architect report informational lag",
                "apply": "L1 SYSTEM_STATE — inform only",
                "wrong": "Treat as DRIFT / false D-REG-1",
            },
            {
                "situation": "Agent claims fixed without proof",
                "apply": "L9 — re-run audits; show PASS/FAIL",
                "wrong": "Accept without validators",
            },
        ],
        "how_system_learns": [
            "Foundation L0–L12 — how to think before locking rules",
            "Discovery — Council, research pipeline, incidents",
            "Lock — *_LOCKED_vN.md becomes SSOT (L11)",
            "Enforce — validators, drift, agent skills (L9)",
            "Record — jsonl, scoreboard, governance events",
        ],
        "learning_rule": "Foundation teaches; SSOT decides; WTM is a separate product tab — never merge namespaces.",
    }


def _enforcement_map() -> list[dict[str, str]]:
    return [
        {"layer": "L0", "enforcement": "audit_hub_source_alignment.py · build-sina-command-panel.py"},
        {"layer": "L1", "enforcement": "CHATGPT_EXTERNAL_CRITIC_LAW · agent reply template"},
        {"layer": "L2", "enforcement": "system_roadmap.py STEP_CATALOG · audit step count"},
        {"layer": "L3", "enforcement": "CURRENT_*_STEP · hub WTM do_now"},
        {"layer": "L4", "enforcement": "Critic law · TO-003 report-only (open)"},
        {"layer": "L5–L8", "enforcement": "WORLD_TARGET_MODEL_AUTHORITY_LAW · SYSTEM_AUTHORITIES"},
        {"layer": "L9", "enforcement": "validate-*-v1.sh · governance_drift_engine.py"},
        {"layer": "L10", "enforcement": "runtime/context_fabric/ · C5 bridge"},
        {"layer": "L11", "enforcement": "archive/superseded/ · authority index versions"},
        {"layer": "L12", "enforcement": "Auto-paste incident · execution spine · dispatch_policy Layer-1"},
        {"layer": "Dispatch", "enforcement": "DISPATCH_POLICY_LOCKED_v1.md · validate-dispatch-policy-classes-v1"},
        {"layer": "Record", "enforcement": "~/.sina/agent-governance-events.jsonl"},
    ]


def _dispatch_policy_crosscheck() -> dict[str, Any]:
    """Governance L1 input_classes are orthogonal to dispatch Layer-1 classes (sa-0610)."""
    try:
        from runtime.dispatch_policy.policy_engine import (  # noqa: WPS433
            LAW_LAYER1_CLASSES,
            dispatch_policy_payload,
        )

        dp = dispatch_policy_payload()
        align = dp.get("alignment") or {}
        layer1 = sorted(LAW_LAYER1_CLASSES)
        return {
            "ok": bool(align.get("law_classes_ok") and align.get("mapping_ok")),
            "layer1_classes": layer1,
            "law_doc": dp.get("doc_path") or "brain-os/law/DISPATCH_POLICY_LOCKED_v1.md",
            "alignment": align,
            "orthogonality_note": (
                "META_REASONING input_classes (ASF_ORDER…EXTERNAL_CRITIC) classify ingress; "
                "dispatch classes (observe/suggest/auto_low_risk) gate auto-execution — no ID overlap"
            ),
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def meta_reasoning_payload(*, hub: dict | None = None) -> dict[str, Any]:
    sr = (hub or {}).get("system_roadmap") or {}
    auth = sr.get("authorities") or (sr.get("world_target_map") or {}).get("authorities") or {}
    law_path = SOURCE_A / LAW_DOC
    return {
        "ok": True,
        "schema": "meta_reasoning_policy_v1",
        "built_at": _now(),
        "tab_id": TAB_ID,
        "law_doc": LAW_DOC,
        "law_path": str(law_path),
        "law_exists": law_path.is_file(),
        "one_liner": "Foundation teaches; SSOT decides; hub projects. Governance L0–L12 ≠ WTM L0–L16.",
        "governance_entry": "SINA_GOVERNANCE_ENTRY_LOCKED_v1.md §0b",
        "authority_index_row": "META_REASONING",
        "flow": [
            "SSOT (truth)",
            "Input classification",
            "Authority filters",
            "Graph / memory / planning separation",
            "Runtime validation",
            "Execution (gated)",
        ],
        "triple_loop": [
            {"loop": "BUILD", "layers": ["L3"], "note": "Implement current step only"},
            {"loop": "VERIFY", "layers": ["L9"], "note": "Validators + audits"},
            {"loop": "GOVERN", "layers": ["L0", "L1", "L4", "L11", "L12"], "note": "Authority + safety + record"},
        ],
        "layers": _layers(),
        "layer_count": len(_layers()),
        "enforcement_map": _enforcement_map(),
        "authority_hierarchy": auth.get("authority_hierarchy") or [],
        "meta_reasoning_stack": auth.get("meta_reasoning_stack") or [],
        "linked_tabs": [
            {"tab": "decision-governance", "title": "Decision governance", "role": "primary"},
            {"tab": "system-roadmap", "title": "World Target Model", "role": "step truth"},
            {"tab": "council-room", "title": "Council Room", "role": "fleet governance"},
            {"tab": "essentials", "title": "Essentials", "role": "read chain"},
            {"tab": "doc-library", "title": "Doc library", "role": "all laws"},
        ],
        "application_guide": _application_guide(),
        "input_classes": [
            {"class": "ASF_ORDER", "rank": 0, "authority": "explicit founder imperative"},
            {"class": "LOCKED_SOURCE", "rank": 1, "authority": "*_LOCKED_vN.md at root"},
            {"class": "MACHINE_SSOT", "rank": 2, "authority": "system_roadmap.py · validators"},
            {"class": "SMART_JUDGMENT", "rank": 3, "authority": "beneficial line — harden only"},
            {"class": "BLUEPRINT", "rank": 4, "authority": "inform only"},
            {"class": "ATTACHMENT", "rank": 5, "authority": "staging until convince"},
            {"class": "EXTERNAL_CRITIC", "rank": 6, "authority": "compare only — never steer"},
        ],
        "dispatch_policy_crosscheck": _dispatch_policy_crosscheck(),
    }


def handle_action(body: dict, hub: dict | None = None) -> dict:
    action = (body.get("action") or "get").strip().lower()
    if action in ("get", "list", ""):
        return meta_reasoning_payload(hub=hub)
    return {"ok": False, "error": f"unknown action: {action}"}

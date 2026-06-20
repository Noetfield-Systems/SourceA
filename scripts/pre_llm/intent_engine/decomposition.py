"""Goal decomposition tree — pre-execution plan skeleton (not D10 SSOT)."""
from __future__ import annotations

from typing import Any

_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "fix": [
        {"id": "locate_failure", "title": "Locate failure surface", "kind": "diagnose"},
        {"id": "assess_impact", "title": "Assess dependency impact (D3)", "kind": "graph"},
        {"id": "apply_patch", "title": "Apply minimal fix", "kind": "execute"},
        {"id": "validate_fix", "title": "Run targeted validator", "kind": "validate"},
    ],
    "build": [
        {"id": "clarify_requirements", "title": "Clarify acceptance + gate", "kind": "intent"},
        {"id": "map_insertion", "title": "Map code insertion points (D1/D2)", "kind": "graph"},
        {"id": "implement", "title": "Implement module + API", "kind": "execute"},
        {"id": "validate_ship", "title": "Validator green + hub wire", "kind": "validate"},
    ],
    "refactor": [
        {"id": "map_deps", "title": "Map module/file deps (D3)", "kind": "graph"},
        {"id": "plan_moves", "title": "Plan safe move order", "kind": "plan"},
        {"id": "apply_refactor", "title": "Apply structural changes", "kind": "execute"},
        {"id": "regression_check", "title": "Regression validators", "kind": "validate"},
    ],
    "debug": [
        {"id": "reproduce", "title": "Reproduce / capture signal", "kind": "diagnose"},
        {"id": "trace_graph", "title": "Trace call/impact graph (D3)", "kind": "graph"},
        {"id": "hypothesize", "title": "Rank hypotheses (D9 pending)", "kind": "reason"},
        {"id": "confirm", "title": "Confirm with validator or test", "kind": "validate"},
    ],
    "audit": [
        {"id": "inventory", "title": "Inventory artifacts + APIs", "kind": "observe"},
        {"id": "compare_law", "title": "Compare against locked law docs", "kind": "governance"},
        {"id": "report_gaps", "title": "Report gaps + blockers", "kind": "report"},
    ],
    "explain": [
        {"id": "gather_context", "title": "Gather code + dependency context", "kind": "retrieve"},
        {"id": "structure_answer", "title": "Structure explanation tree", "kind": "plan"},
        {"id": "cite_sources", "title": "Cite paths + symbols", "kind": "provenance"},
    ],
    "validate": [
        {"id": "select_validator", "title": "Select validate-*.sh gate", "kind": "intent"},
        {"id": "preflight", "title": "Preflight substrate (D1–D3)", "kind": "graph"},
        {"id": "run_gate", "title": "Run validator + capture receipt", "kind": "execute"},
    ],
    "ship": [
        {"id": "preflight_gates", "title": "All gates green", "kind": "validate"},
        {"id": "hub_refresh", "title": "Rebuild hub + restart if needed", "kind": "execute"},
        {"id": "record_provenance", "title": "Record provenance in governance", "kind": "governance"},
    ],
    "explore": [
        {"id": "formulate_query", "title": "Formulate retrieval query (D7 pending)", "kind": "intent"},
        {"id": "scan_index", "title": "Scan code index (D1)", "kind": "retrieve"},
        {"id": "summarize_findings", "title": "Summarize findings", "kind": "report"},
    ],
    "other": [
        {"id": "clarify_intent", "title": "Clarify primary goal (D4)", "kind": "intent"},
        {"id": "gather_context", "title": "Gather minimal context", "kind": "retrieve"},
        {"id": "decide_path", "title": "Re-classify after clarification", "kind": "plan"},
    ],
}


def build_decomposition_tree(*, goal_class: str, text: str) -> list[dict[str, Any]]:
    steps = _TEMPLATES.get(goal_class) or _TEMPLATES["other"]
    tree: list[dict[str, Any]] = []
    for i, step in enumerate(steps):
        tree.append(
            {
                **step,
                "order": i + 1,
                "status": "pending",
                "source_text_hint": (text or "")[:120] if i == 0 else "",
                "children": [],
            }
        )
    return tree


def missing_context_hints(*, goal_class: str, ambiguity: dict[str, Any], text: str) -> list[str]:
    hints: list[str] = []
    codes = {f.get("code") for f in ambiguity.get("ambiguity_flags") or []}
    if "missing_scope" in codes or "vague_target" in codes:
        hints.append("Specify target file, module path, or WTM step (e.g. D4, scripts/pre_llm/…)")
    if "too_short" in codes:
        hints.append("Expand goal with desired outcome and acceptance gate (validator name)")
    if goal_class in ("fix", "debug") and "error" not in (text or "").lower():
        hints.append("Include error message, failing validator, or observable symptom")
    if goal_class == "build" and not any(c.isdigit() for c in (text or "")):
        hints.append("Name the module, API route, or artifact to create")
    if ambiguity.get("needs_clarification"):
        hints.append("Disambiguate primary goal before retrieval/planning (D5/D10)")
    return hints

"""Task-specific repo grounding for Eval-1b live arm."""
from __future__ import annotations

import re
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[2]
SCRIPTS = SOURCE_A / "scripts"

RETRIEVE_DISPATCH_PATHS: tuple[str, ...] = (
    "scripts/runtime/orchestrator/orchestrator_engine.py",
    "scripts/runtime/multi_step_planner/planner_engine.py",
)

FACTORY_RUNRECEIPT_PATHS: tuple[str, ...] = (
    "scripts/runreceipt/pack_v1.py",
    "product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md",
)
FACTORY_RUNRECEIPT_SCHEMA_DOC = "product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md"

L8_EMBEDDING_PROVIDER_PY = "scripts/pre_llm/vector_retrieval/embedding_provider.py"
L8_QUERY_ENGINE_PY = "scripts/pre_llm/vector_retrieval/query_engine.py"
L8_HYBRID_PATHS: tuple[str, ...] = (L8_EMBEDDING_PROVIDER_PY, L8_QUERY_ENGINE_PY)

BUGFIX_GATE_PATHS: tuple[str, ...] = (
    "scripts/model_dispatch.py",
    "scripts/gate_receipts_hub.py",
    "scripts/gate_receipt_lib.py",
)

GOVERNANCE_RULES_PATHS: tuple[str, ...] = (
    "scripts/agent_rules_in_charge.py",
    "scripts/agent_rules_loop_orchestrator.py",
)

TASK_PATHS: dict[str, list[str]] = {
    "bugfix-gate": [
        "scripts/model_dispatch.py",
        "scripts/gate_receipts_hub.py",
        "scripts/gate_receipt_lib.py",
        "scripts/agent_loop.py",
        "ENFORCE_BYPASS_MAP_LOCKED_v1.md",
    ],
    "plan-eval-1b": [
        "scripts/eval_packet_v1b/runner.py",
        "scripts/eval_packet_v1/runner.py",
        "scripts/eval_packet_v1b/scorer.py",
    ],
    "retrieve-dispatch": [
        "scripts/runtime/orchestrator/orchestrator_engine.py",
        "scripts/runtime/multi_step_planner/planner_engine.py",
    ],
    "governance-rules": [
        "scripts/agent_rules_in_charge.py",
        "scripts/agent_rules_loop_orchestrator.py",
    ],
    "factory-runreceipt": [
        "scripts/runreceipt/pack_v1.py",
        "product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md",
    ],
    "event-bus": [
        "scripts/runtime/event_bus/bus_v1.py",
    ],
    "l8-hybrid": [
        "scripts/pre_llm/vector_retrieval/embedding_provider.py",
        "scripts/pre_llm/vector_retrieval/query_engine.py",
    ],
}

TASK_NEEDLES: dict[str, list[str]] = {
    "bugfix-gate": [
        "gate_decision",
        "gate_eligible_false",
        "gate_eligible",
        "enforce",
        "model_dispatch",
        "gate_receipts",
        "gate_receipt_lib",
        "loop_gate_block",
        "prepare_packet",
        "dispatch_chat",
    ],
    "plan-eval-1b": [
        "eval_packet_v1b",
        "run_eval",
        "live_pilot",
        "scaffold",
        "runner.py",
    ],
    "retrieve-dispatch": [
        "dispatch_ready",
        "orchestrator",
        "planner_engine",
        "spine_sequence",
        "founder_confirm",
    ],
    "factory-runreceipt": [
        "run.jsonl",
        "summary.json",
        "receipt",
        "runreceipt",
        "evidence",
    ],
    "l8-hybrid": [
        "embedding",
        "hybrid_score",
        "embed_text",
        "vector_retrieval",
        "hybrid",
    ],
    "governance-rules": [
        "rules_in_charge",
        "agent_rules",
        "loop_orchestrator",
        "session",
    ],
}


def _snippet(path: Path, *, needles: list[str], max_chars: int = 900) -> str:
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    low = text.lower()
    best_idx = -1
    for n in needles:
        nlow = n.lower()
        idx = low.find(nlow)
        if idx >= 0:
            best_idx = idx
            break
    if best_idx < 0:
        best_idx = 0
    start = max(0, best_idx - 200)
    chunk = text[start : start + max_chars]
    return chunk.strip()


def build_task_grounding(*, task_id: str, prompt: str, keywords: list[str]) -> dict:
    rel_paths = list(TASK_PATHS.get(task_id) or [])
    needles = list(TASK_NEEDLES.get(task_id) or []) + list(keywords)
    needles += re.findall(r"[a-z_]{4,}", prompt.lower())
    needles = list(dict.fromkeys(n for n in needles if n))
    snippets: list[dict] = []
    for rel in rel_paths[:6]:
        full = SOURCE_A / rel
        snip = _snippet(full, needles=needles)
        if snip:
            snippets.append({"path": rel, "snippet": snip})
    return {
        "task_id": task_id,
        "expected_paths": rel_paths,
        "snippets": snippets,
    }


def cross_check_bugfix_gate_grounding() -> list[str]:
    """Machine proof bugfix-gate cites model_dispatch gate_decision + gate_receipts (sa-0153)."""
    errors: list[str] = []
    prompt = "Fix model_dispatch when gate_eligible is false in enforce mode"
    keywords = ["gate_eligible", "enforce", "model_dispatch", "block"]
    g = build_task_grounding(task_id="bugfix-gate", prompt=prompt, keywords=keywords)
    paths = list(g.get("expected_paths") or [])
    for rel in BUGFIX_GATE_PATHS:
        if rel not in paths:
            errors.append(f"missing expected path {rel}")
    snips = {s["path"]: s["snippet"] for s in (g.get("snippets") or [])}
    for rel in ("scripts/model_dispatch.py", "scripts/gate_receipts_hub.py"):
        if rel not in snips:
            errors.append(f"missing snippet for {rel}")
            continue
    md = (
        snips.get("scripts/model_dispatch.py", "")
        + snips.get("scripts/gate_receipts_hub.py", "")
    ).lower()
    if md:
        if "gate_eligible" not in md:
            errors.append("model_dispatch/gate_receipts snippet must mention gate_eligible")
        if "enforce" not in md:
            errors.append("snippet must mention enforce")
    dispatch_md = snips.get("scripts/model_dispatch.py", "").lower()
    if dispatch_md and "gate_decision" not in dispatch_md and "gate_eligible_false" not in dispatch_md:
        errors.append("model_dispatch snippet must mention gate_decision or gate_eligible_false")
    return errors


def cross_check_retrieve_dispatch_grounding() -> list[str]:
    """Machine proof retrieve-dispatch cites orchestrator + planner_engine (sa-0137)."""
    errors: list[str] = []
    prompt = "Where is dispatch_ready set false in the runtime orchestrator?"
    keywords = ["dispatch_ready", "orchestrator", "false", "runtime"]
    g = build_task_grounding(task_id="retrieve-dispatch", prompt=prompt, keywords=keywords)
    paths = list(g.get("expected_paths") or [])
    for rel in RETRIEVE_DISPATCH_PATHS:
        if rel not in paths:
            errors.append(f"missing expected path {rel}")
    snips = {s["path"]: s["snippet"] for s in (g.get("snippets") or [])}
    for rel in RETRIEVE_DISPATCH_PATHS:
        if rel not in snips:
            errors.append(f"missing snippet for {rel}")
            continue
        if "dispatch_ready" not in snips[rel].lower():
            errors.append(f"{rel} snippet must mention dispatch_ready")
    return errors


def cross_check_factory_runreceipt_grounding() -> list[str]:
    """Machine proof factory-runreceipt cites RUNRECEIPT schema doc + pack_v1 (sa-0138)."""
    errors: list[str] = []
    prompt = "Define RunReceipt artifacts run.jsonl summary.json HTML pack for wire lane"
    keywords = ["run.jsonl", "summary", "receipt", "wire", "PASS"]
    g = build_task_grounding(task_id="factory-runreceipt", prompt=prompt, keywords=keywords)
    paths = list(g.get("expected_paths") or [])
    for rel in FACTORY_RUNRECEIPT_PATHS:
        if rel not in paths:
            errors.append(f"missing expected path {rel}")
    snips = {s["path"]: s["snippet"] for s in (g.get("snippets") or [])}
    for rel in FACTORY_RUNRECEIPT_PATHS:
        if rel not in snips:
            errors.append(f"missing snippet for {rel}")
    schema_md = snips.get(FACTORY_RUNRECEIPT_SCHEMA_DOC, "").lower()
    if schema_md and "run.jsonl" not in schema_md:
        errors.append("RUNRECEIPT schema doc snippet must mention run.jsonl")
    if schema_md and "summary.json" not in schema_md:
        errors.append("RUNRECEIPT schema doc snippet must mention summary.json")
    pack_md = snips.get("scripts/runreceipt/pack_v1.py", "").lower()
    if pack_md and "run.jsonl" not in pack_md:
        errors.append("pack_v1 snippet must mention run.jsonl")
    return errors


def cross_check_l8_hybrid_grounding() -> list[str]:
    """Machine proof l8-hybrid cites embedding_provider.py + query_engine (sa-0139)."""
    errors: list[str] = []
    prompt = "How does L8 hybrid embedding retrieval extend D5 token index?"
    keywords = ["embedding", "vector", "hybrid", "retrieval"]
    g = build_task_grounding(task_id="l8-hybrid", prompt=prompt, keywords=keywords)
    paths = list(g.get("expected_paths") or [])
    for rel in L8_HYBRID_PATHS:
        if rel not in paths:
            errors.append(f"missing expected path {rel}")
    snips = {s["path"]: s["snippet"] for s in (g.get("snippets") or [])}
    if L8_EMBEDDING_PROVIDER_PY not in snips:
        errors.append(f"missing snippet for {L8_EMBEDDING_PROVIDER_PY}")
    else:
        embed_md = snips[L8_EMBEDDING_PROVIDER_PY].lower()
        if "embedding" not in embed_md:
            errors.append("embedding_provider snippet must mention embedding")
        if "hybrid" not in embed_md and "embed_text" not in embed_md:
            errors.append("embedding_provider snippet must mention hybrid or embed_text")
    if L8_QUERY_ENGINE_PY not in snips:
        errors.append(f"missing snippet for {L8_QUERY_ENGINE_PY}")
    else:
        qe_md = snips[L8_QUERY_ENGINE_PY].lower()
        if "hybrid_score" not in qe_md and "hybrid" not in qe_md:
            errors.append("query_engine snippet must mention hybrid_score or hybrid")
    return errors


def cross_check_governance_rules_grounding() -> list[str]:
    """Machine proof governance-rules cites agent_rules in_charge + loop_orchestrator (sa-0623)."""
    errors: list[str] = []
    prompt = "How does rules-in-charge loop load agent_rules scripts at session start?"
    keywords = ["rules_in_charge", "agent_rules", "session", "orchestrator"]
    g = build_task_grounding(task_id="governance-rules", prompt=prompt, keywords=keywords)
    paths = list(g.get("expected_paths") or [])
    for rel in GOVERNANCE_RULES_PATHS:
        if rel not in paths:
            errors.append(f"missing expected path {rel}")
    snips = {s["path"]: s["snippet"] for s in (g.get("snippets") or [])}
    for rel in GOVERNANCE_RULES_PATHS:
        if rel not in snips:
            errors.append(f"missing snippet for {rel}")
            continue
        md = snips[rel].lower()
        if "rules" not in md and "agent_rules" not in md:
            errors.append(f"{rel} snippet must mention rules or agent_rules")
    return errors


def format_grounding_for_llm(grounding: dict) -> str:
    lines = ["## eval_task_grounding (SSOT — cite these exact paths)"]
    for p in grounding.get("expected_paths") or []:
        lines.append(f"- {p}")
    for item in grounding.get("snippets") or []:
        lines.append(f"\n### {item['path']}\n```\n{item['snippet']}\n```")
    return "\n".join(lines)[:12000]

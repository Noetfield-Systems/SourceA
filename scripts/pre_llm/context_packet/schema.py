"""llm_context_packet_v1.json — field contract + validation (design-first)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "llm-context-packet-v1"
PACKET_VERSION = "1.0"
PACKET_SSOT_PATH = Path.home() / ".sina" / "llm_context_packet_v1.json"
LAW_DOC = "LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md"

# Which WTM step owns each top-level packet section
FIELD_PRODUCERS: dict[str, list[str]] = {
    "intent": ["D4"],
    "workspace": ["L1", "hub"],
    "code": ["D1", "D2"],
    "dependencies": ["D3"],
    "retrieval": ["D5", "D6", "D7"],
    "reasoning": ["D8"],
    "ranking": ["D9"],
    "plan": ["D10"],
    "tools": ["D11"],
    "validation": ["D12"],
    "diff": ["D13"],
    "compression": ["D14"],
    "memory": ["D6", "D16"],
    "constraints": ["governance"],
    "compressed_context": ["D14"],
    "provenance": ["D15"],
}

# Steps physically logged today (auto-updated as phases ship)
SHIPPED_PRODUCERS: set[str] = {
    "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15", "D16",
}

GATE_REQUIRED_SECTIONS = (
    "intent",
    "code",
    "dependencies",
    "ranking",
    "plan",
    "compression",
    "compressed_context",
    "constraints",
    "provenance",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def empty_packet_template(*, task_id: str = "packet-design-stub", repo_root: str = "") -> dict:
    """Canonical empty shape — all modules build toward this."""
    return {
        "schema": SCHEMA,
        "packet_version": PACKET_VERSION,
        "generated_at": _now(),
        "task_id": task_id,
        "repo_root": repo_root,
        "readiness": {
            "score": 0.0,
            "required_fields_ok": False,
            "producer_steps": sorted(SHIPPED_PRODUCERS),
            "missing_for_gate": list(GATE_REQUIRED_SECTIONS),
        },
        "intent": {
            "goal_class": None,
            "ambiguity_flags": [],
            "decomposition_tree": [],
            "producer": "D4",
        },
        "workspace": {"active_files": [], "session_focus": None, "producer": "L1"},
        "code": {
            "files": [],
            "symbols": [],
            "fusion_ref": None,
            "producer": "D1,D2",
        },
        "dependencies": {
            "module_edges_sample": [],
            "impact_ready": False,
            "producer": "D3",
        },
        "retrieval": {"chunks": [], "queries": [], "producer": "D5,D7"},
        "reasoning": {"paths": [], "producer": "D8"},
        "ranking": {"ranked_evidence": [], "producer": "D9"},
        "plan": {"graph": {"nodes": [], "edges": []}, "producer": "D10"},
        "tools": {"selection": [], "producer": "D11"},
        "validation": {"checks": [], "producer": "D12"},
        "diff": {"changes": [], "producer": "D13"},
        "compression": {
            "budget": {"token_limit": 0, "tokens_used": 0},
            "producer": "D14",
        },
        "memory": {"slots": [], "producer": "D6,D16"},
        "constraints": {"policy_refs": [], "safety": [], "producer": "governance"},
        "compressed_context": {"narrative": "", "producer": "D14"},
        "provenance": {
            "producer_steps": [],
            "artifacts": {},
            "law_doc": LAW_DOC,
        },
    }


def _section_populated(packet: dict, section: str) -> bool:
    val = packet.get(section)
    if val is None:
        return False
    if section == "intent":
        return bool(val.get("goal_class"))
    if section == "code":
        return bool(val.get("files") or val.get("symbols"))
    if section == "dependencies":
        return bool(val.get("impact_ready"))
    if section == "ranking":
        return bool(val.get("ranked_evidence"))
    if section == "plan":
        g = val.get("graph") or {}
        return bool(g.get("nodes"))
    if section == "compression":
        b = val.get("budget") or {}
        return int(b.get("token_limit") or 0) > 0
    if section == "compressed_context":
        return bool((val.get("narrative") or "").strip())
    if section == "constraints":
        return bool(val.get("policy_refs") or val.get("safety"))
    if section == "provenance":
        return bool(val.get("producer_steps"))
    return bool(val)


def validate_packet(packet: dict, *, strict_gate: bool = False) -> dict:
    errors: list[str] = []
    if packet.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if not packet.get("task_id"):
        errors.append("task_id required")

    missing_gate = [s for s in GATE_REQUIRED_SECTIONS if not _section_populated(packet, s)]
    populated = [s for s in GATE_REQUIRED_SECTIONS if _section_populated(packet, s)]
    score = round(len(populated) / max(len(GATE_REQUIRED_SECTIONS), 1), 3)

    if strict_gate and missing_gate:
        for s in missing_gate:
            errors.append(f"gate: missing or empty section '{s}'")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "readiness_score": score,
        "gate_eligible": len(missing_gate) == 0,
        "missing_for_gate": missing_gate,
        "populated_sections": populated,
        "field_producers": FIELD_PRODUCERS,
        "shipped_producers": sorted(SHIPPED_PRODUCERS),
    }


def hydrate_from_disk_substrate(packet: dict) -> dict:
    """Hydrate packet from D1–D16 disk SSOT; stays not gate-eligible until constraints populated."""
    out = dict(packet)
    try:
        from pre_llm.code_intelligence.store import load_canonical as load_d1  # noqa: WPS433
        from pre_llm.dependency_graph.store import load_canonical as load_d3  # noqa: WPS433
        from pre_llm.graph_fusion.store import load_canonical as load_d2  # noqa: WPS433

        d1 = load_d1()
        d2 = load_d2()
        d3 = load_d3()
        if d1:
            out.setdefault("code", {})
            out["code"]["files"] = [f.get("path") for f in (d1.get("files") or [])[:40]]
            out["code"]["symbols"] = list((d1.get("symbols") or {}).keys())[:40]
            out["code"]["fusion_ref"] = d2.get("generated_at") if d2 else None
            out["repo_root"] = out.get("repo_root") or d1.get("repo_root")
        if d3:
            out.setdefault("dependencies", {})
            out["dependencies"]["impact_ready"] = bool(d3.get("dependency_ready"))
            out["dependencies"]["module_edges_sample"] = (d3.get("module_graph") or [])[:12]
        from pre_llm.intent_engine.store import load_canonical as load_d4  # noqa: WPS433

        d4 = load_d4()
        if d4 and d4.get("packet_intent"):
            out["intent"] = dict(d4["packet_intent"])
        try:
            from pre_llm.vector_retrieval.store import load_canonical as load_d5  # noqa: WPS433

            d5 = load_d5()
            if d5 and d5.get("retrieval_ready") and (d5.get("chunks") or []):
                out.setdefault("retrieval", {})
                out["retrieval"]["chunks"] = [
                    {
                        "chunk_id": c.get("chunk_id"),
                        "path": c.get("path"),
                        "kind": c.get("kind"),
                    }
                    for c in (d5.get("chunks") or [])[:12]
                ]
                out["retrieval"]["queries"] = []
                out["retrieval"]["producer"] = "D5"
        except Exception as exc:
            out.setdefault("provenance", {})["d5_hydrate_error"] = str(exc)
        try:
            from pre_llm.memory_git_bridge.store import load_canonical as load_d6  # noqa: WPS433

            d6 = load_d6()
            if d6 and d6.get("bridge_ready") and (d6.get("slots") or []):
                out.setdefault("memory", {})
                out["memory"]["slots"] = [
                    {
                        "slot_id": s.get("slot_id"),
                        "kind": s.get("kind"),
                        "task_id": s.get("task_id"),
                        "timestamp": s.get("timestamp"),
                        "summary": s.get("summary"),
                        "path": s.get("path"),
                    }
                    for s in (d6.get("slots") or [])[:12]
                ]
                out["memory"]["producer"] = "D6"
                feed = [
                    {
                        "chunk_id": s.get("slot_id"),
                        "path": s.get("path"),
                        "kind": s.get("kind"),
                    }
                    for s in (d6.get("slots") or [])[:6]
                ]
                if feed:
                    out.setdefault("retrieval", {})
                    existing = out["retrieval"].get("chunks") or []
                    out["retrieval"]["chunks"] = existing + feed
                    out["retrieval"]["producer"] = "D5,D6"
        except Exception as exc:
            out.setdefault("provenance", {})["d6_hydrate_error"] = str(exc)
        try:
            from pre_llm.query_expansion.store import load_canonical as load_d7  # noqa: WPS433

            d7 = load_d7()
            if d7 and d7.get("expansion_ready") and (d7.get("queries") or []):
                out.setdefault("retrieval", {})
                out["retrieval"]["queries"] = [
                    {
                        "id": q.get("id"),
                        "text": q.get("text"),
                        "mode": q.get("mode"),
                        "source": q.get("source"),
                    }
                    for q in (d7.get("queries") or [])[:12]
                ]
                out["retrieval"]["retrieval_plan"] = d7.get("retrieval_plan")
                producers = out["retrieval"].get("producer") or "D5"
                if "D7" not in producers:
                    out["retrieval"]["producer"] = f"{producers},D7" if producers else "D7"
        except Exception as exc:
            out.setdefault("provenance", {})["d7_hydrate_error"] = str(exc)
        try:
            from pre_llm.graph_reasoning.store import load_canonical as load_d8  # noqa: WPS433

            d8 = load_d8()
            if d8 and d8.get("reasoning_ready") and (d8.get("paths") or []):
                out.setdefault("reasoning", {})
                out["reasoning"]["paths"] = [
                    {
                        "path_id": p.get("path_id"),
                        "kind": p.get("kind"),
                        "seed": p.get("seed"),
                        "seed_type": p.get("seed_type"),
                        "node_count": p.get("node_count"),
                        "summary": p.get("summary"),
                    }
                    for p in (d8.get("paths") or [])[:12]
                ]
                out["reasoning"]["producer"] = "D8"
        except Exception as exc:
            out.setdefault("provenance", {})["d8_hydrate_error"] = str(exc)
        try:
            from pre_llm.context_ranking.store import load_canonical as load_d9  # noqa: WPS433

            d9 = load_d9()
            if d9 and d9.get("ranking_ready") and (d9.get("ranked_evidence") or []):
                out.setdefault("ranking", {})
                out["ranking"]["ranked_evidence"] = [
                    {
                        "rank": r.get("rank"),
                        "evidence_id": r.get("evidence_id"),
                        "kind": r.get("kind"),
                        "source_step": r.get("source_step"),
                        "path": r.get("path"),
                        "score": r.get("score"),
                        "summary": (r.get("summary") or "")[:200],
                    }
                    for r in (d9.get("ranked_evidence") or [])[:16]
                ]
                out["ranking"]["goal_class"] = d9.get("goal_class")
                out["ranking"]["producer"] = "D9"
        except Exception as exc:
            out.setdefault("provenance", {})["d9_hydrate_error"] = str(exc)
        try:
            from pre_llm.planning_engine.store import load_canonical as load_d10  # noqa: WPS433

            d10 = load_d10()
            if d10 and d10.get("plan_ready") and (d10.get("graph") or {}).get("nodes"):
                g = d10["graph"]
                out.setdefault("plan", {})
                out["plan"]["graph"] = {
                    "nodes": [
                        {
                            "id": n.get("id"),
                            "title": n.get("title"),
                            "kind": n.get("kind"),
                            "order": n.get("order"),
                            "status": n.get("status"),
                        }
                        for n in (g.get("nodes") or [])[:16]
                    ],
                    "edges": [
                        {
                            "from": e.get("from"),
                            "to": e.get("to"),
                            "kind": e.get("kind"),
                        }
                        for e in (g.get("edges") or [])[:24]
                    ],
                }
                out["plan"]["goal_class"] = d10.get("goal_class")
                out["plan"]["producer"] = "D10"
        except Exception as exc:
            out.setdefault("provenance", {})["d10_hydrate_error"] = str(exc)
        try:
            from pre_llm.tool_router.store import load_canonical as load_d11  # noqa: WPS433

            d11 = load_d11()
            if d11 and d11.get("router_ready") and (d11.get("selection") or []):
                out.setdefault("tools", {})
                out["tools"]["selection"] = [
                    {
                        "plan_node_id": s.get("plan_node_id"),
                        "capability_id": s.get("capability_id"),
                        "tool_id": s.get("tool_id"),
                        "permission": s.get("permission"),
                        "cost_estimate": s.get("cost_estimate"),
                        "allowed": s.get("allowed"),
                        "policy_gate": s.get("policy_gate"),
                    }
                    for s in (d11.get("selection") or [])[:20]
                ]
                out["tools"]["total_cost_estimate"] = d11.get("total_cost_estimate")
                out["tools"]["producer"] = "D11"
        except Exception as exc:
            out.setdefault("provenance", {})["d11_hydrate_error"] = str(exc)
        try:
            from pre_llm.validation_layer.store import load_canonical as load_d12  # noqa: WPS433

            d12 = load_d12()
            if d12 and d12.get("validation_ready") and (d12.get("checks") or []):
                out.setdefault("validation", {})
                out["validation"]["checks"] = [
                    {
                        "id": c.get("id"),
                        "category": c.get("category"),
                        "status": c.get("status"),
                        "severity": c.get("severity"),
                        "detail": c.get("detail"),
                    }
                    for c in (d12.get("checks") or [])[:24]
                ]
                out["validation"]["dry_run"] = d12.get("dry_run")
                out["validation"]["producer"] = "D12"
        except Exception as exc:
            out.setdefault("provenance", {})["d12_hydrate_error"] = str(exc)
        try:
            from pre_llm.diff_intelligence.store import load_canonical as load_d13  # noqa: WPS433

            d13 = load_d13()
            if d13 and d13.get("diff_ready") and (d13.get("changes") or []):
                out.setdefault("diff", {})
                out["diff"]["changes"] = [
                    {
                        "change_id": c.get("change_id"),
                        "path": c.get("path"),
                        "kind": c.get("kind"),
                        "lines_added": c.get("lines_added"),
                        "lines_removed": c.get("lines_removed"),
                        "scope": c.get("scope"),
                        "in_ranked_focus": c.get("in_ranked_focus"),
                        "impact": c.get("impact"),
                    }
                    for c in (d13.get("changes") or [])[:24]
                ]
                out["diff"]["impact_map"] = d13.get("impact_map") or {}
                out["diff"]["git_scope"] = d13.get("git_scope")
                out["diff"]["producer"] = "D13"
        except Exception as exc:
            out.setdefault("provenance", {})["d13_hydrate_error"] = str(exc)
        try:
            from pre_llm.context_compression.store import load_canonical as load_d14  # noqa: WPS433

            d14 = load_d14()
            if d14 and d14.get("compression_ready"):
                out.setdefault("compression", {})
                out["compression"]["budget"] = d14.get("budget") or {}
                out["compression"]["layers"] = [
                    {
                        "layer": layer.get("layer"),
                        "tokens": layer.get("tokens"),
                        "items_in": layer.get("items_in"),
                        "items_out": layer.get("items_out"),
                    }
                    for layer in (d14.get("layers") or [])[:12]
                ]
                out["compression"]["packed_evidence"] = (d14.get("packed_evidence") or [])[:16]
                out["compression"]["producer"] = "D14"
                out.setdefault("compressed_context", {})
                out["compressed_context"]["narrative"] = d14.get("narrative") or ""
                out["compressed_context"]["sections"] = [
                    layer.get("layer") for layer in (d14.get("layers") or []) if layer.get("layer")
                ]
                out["compressed_context"]["producer"] = "D14"
        except Exception as exc:
            out.setdefault("provenance", {})["d14_hydrate_error"] = str(exc)
        steps = set(out.get("provenance", {}).get("producer_steps") or [])
        steps.update(SHIPPED_PRODUCERS)
        out.setdefault("provenance", {})["producer_steps"] = sorted(steps)
        out["readiness"] = {
            **(out.get("readiness") or {}),
            "producer_steps": sorted(SHIPPED_PRODUCERS),
            "score": validate_packet(out)["readiness_score"],
            "required_fields_ok": False,
        }
    except Exception as exc:
        out.setdefault("provenance", {})["hydrate_error"] = str(exc)
    return out


def schema_contract_payload() -> dict:
    """Hub/API — packet contract for WTM and module authors."""
    stub = empty_packet_template()
    hydrated = hydrate_from_disk_substrate(stub)
    check = validate_packet(hydrated)
    return {
        "ok": True,
        "schema": SCHEMA,
        "packet_version": PACKET_VERSION,
        "law_doc": LAW_DOC,
        "ssot_path": str(PACKET_SSOT_PATH),
        "field_producers": FIELD_PRODUCERS,
        "shipped_producers": sorted(SHIPPED_PRODUCERS),
        "gate_required_sections": list(GATE_REQUIRED_SECTIONS),
        "pre_llm_steps_shipped": f"{len(SHIPPED_PRODUCERS)}/16",
        "template": stub,
        "hydrated_stub": hydrated,
        "validation": check,
    }

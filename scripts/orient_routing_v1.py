#!/usr/bin/env python3
"""SourceA orientation routing — receipt cascade · role routing · node id mapping.

SSOT: data/sourcea_orient_routing_v1.json
Report: ~/.sina/orient-routing-report-v1.json
Law: AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
SSOT_PATH = DATA / "sourcea_orient_routing_v1.json"
REPORT_PATH = SINA / "orient-routing-report-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _expand(path: str) -> Path:
    return Path(path.replace("~", str(Path.home())))


def load_ssot() -> dict[str, Any]:
    if not SSOT_PATH.is_file():
        return {}
    return json.loads(SSOT_PATH.read_text(encoding="utf-8"))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def validate_orient_chain() -> dict[str, Any]:
    ssot = load_ssot()
    errors: list[str] = []
    steps: list[dict[str, Any]] = []
    for row in ssot.get("orient_chain") or []:
        rel = str(row.get("path") or "")
        if rel.startswith("~/"):
            p = _expand(rel)
        else:
            p = ROOT / rel
        ok = p.is_file()
        if not ok:
            errors.append(f"ORIENT_CHAIN missing {rel}")
        steps.append({"id": row.get("id"), "path": rel, "ok": ok})
    return {"ok": len(errors) == 0, "errors": errors, "steps": steps, "count": len(steps)}


def node_for_session_step(step_id: str) -> str:
    ssot = load_ssot()
    mapping = ssot.get("session_gate_step_nodes") or {}
    return str(mapping.get(step_id) or "session_gate_v1")


def node_for_validator(script_name: str) -> str:
    ssot = load_ssot()
    mapping = ssot.get("validator_check_nodes") or {}
    base = script_name.replace(".sh", "").replace(".py", "")
    for key, nid in mapping.items():
        if key in script_name or script_name in key:
            return str(nid)
    return str(mapping.get(base) or "validate_w10_vocab")


def role_routing(role: str) -> dict[str, Any]:
    ssot = load_ssot()
    routes = ssot.get("role_routing") or {}
    return dict(routes.get(role) or routes.get("any") or {})


def build_receipt_cascade() -> dict[str, Any]:
    ssot = load_ssot()
    failures: list[dict[str, Any]] = []
    seen: set[str] = set()

    def push(entry: dict[str, Any]) -> None:
        key = f"{entry.get('node_id')}:{entry.get('check_id')}"
        if key in seen:
            return
        seen.add(key)
        failures.append(entry)

    gate = _read_json(SINA / "agent_session_gate_receipt_v1.json")
    if gate.get("ok") is not True:
        for step in gate.get("steps") or []:
            if step.get("ok") is False:
                sid = str(step.get("step") or "unknown")
                push(
                    {
                        "source": "session_gate",
                        "check_id": sid,
                        "node_id": node_for_session_step(sid),
                        "severity": "error",
                        "message": f"session gate step FAIL: {sid}",
                        "fix": "python3 scripts/agent_session_gate_run_v1.py --role worker --json",
                    }
                )
        if not failures:
            push(
                {
                    "source": "session_gate",
                    "check_id": "overall",
                    "node_id": "session_gate_v1",
                    "severity": "error",
                    "message": "session gate ok=false",
                    "fix": "python3 scripts/agent_session_gate_run_v1.py --role worker --json",
                }
            )

    graph = _read_json(SINA / "pipeline-node-graph-receipt-v1.json")
    for tier in graph.get("tiers") or []:
        if tier.get("ok") is False:
            for node in tier.get("nodes") or []:
                if node.get("required") and not node.get("ok") and not node.get("skipped"):
                    nid = str(node.get("id") or "pipeline_node_graph_runner_v1")
                    push(
                        {
                            "source": "graph_run",
                            "check_id": nid,
                            "node_id": nid,
                            "severity": "warn",
                            "message": node.get("tail") or f"graph node FAIL: {nid}",
                            "fix": f"python3 scripts/pipeline_node_graph_runner_v1.py --tier {tier.get('tier')} --json",
                        }
                    )

    crit = _read_json(SINA / "find-bugs" / "last-run.json")
    cc = int(crit.get("critical_count") or 0)
    if cc > 0:
        push(
            {
                "source": "critical_bugs",
                "check_id": "critical_count",
                "node_id": "validate_w10_vocab",
                "severity": "error",
                "message": f"critical_count={cc}",
                "fix": "python3 scripts/find_critical_bugs.py",
            }
        )

    live = _read_json(SINA / "agent-live-surfaces-v1.json")
    if not live.get("factory_now_line"):
        push(
            {
                "source": "live_surfaces",
                "check_id": "factory_now_line",
                "node_id": "disk_live_wire",
                "severity": "warn",
                "message": "missing factory_now_line",
                "fix": "python3 scripts/disk_live_wire_sync_v1.py --json",
            }
        )

    _cascade_pipeline_receipts(push)

    nodes_affected = sorted({str(f.get("node_id")) for f in failures if f.get("node_id")})
    return {
        "ok": len(failures) == 0,
        "failures": failures,
        "nodes_affected": nodes_affected,
        "at": _now(),
        "ssot": str(SSOT_PATH.relative_to(ROOT)),
    }


def format_cascade_brief(cascade: dict[str, Any]) -> str:
    if not cascade.get("failures"):
        return "all wires green"
    parts = []
    for f in (cascade.get("failures") or [])[:6]:
        parts.append(f"FAIL {f.get('node_id')} ← {f.get('source')}.{f.get('check_id')}")
    return " · ".join(parts)


def _cascade_pipeline_receipts(push) -> None:
    ssot = load_ssot()
    for src in ssot.get("receipt_cascade_sources") or []:
        sid = str(src.get("id") or "")
        if sid not in ("orientation", "hospital", "maze"):
            continue
        rel = str(src.get("path") or "")
        path = _expand(rel) if rel.startswith("~") else ROOT / rel
        if src.get("only_if_exists") and not path.is_file():
            continue
        rec = _read_json(path)
        if not rec:
            continue
        if rec.get("ok") is False:
            node_id = str(src.get("node_id") or sid)
            push(
                {
                    "source": sid,
                    "check_id": "pipeline_receipt",
                    "node_id": node_id,
                    "severity": "warn" if sid == "orientation" else "error",
                    "message": rec.get("discharge") or rec.get("founder_next") or f"{sid} ok=false",
                    "fix": f"python3 scripts/agent_three_pipelines_router_v1.py {sid} --json",
                }
            )


def pipeline_nodes_brief() -> dict[str, Any]:
    ssot = load_ssot()
    rows: list[dict[str, Any]] = []
    for key, meta in (ssot.get("pipeline_nodes") or {}).items():
        if not isinstance(meta, dict):
            continue
        receipt_rel = str(meta.get("receipt") or "")
        if receipt_rel.startswith("~"):
            receipt_path = _expand(receipt_rel)
        elif receipt_rel:
            receipt_path = ROOT / receipt_rel
        else:
            receipt_path = Path()
        rec = _read_json(receipt_path) if receipt_path.is_file() else {}
        rows.append(
            {
                "pipeline": key,
                "node_id": meta.get("node_id"),
                "tier": meta.get("tier"),
                "founder_word_only": meta.get("founder_word_only"),
                "receipt_exists": receipt_path.is_file(),
                "receipt_ok": rec.get("ok") if rec else None,
            }
        )
    return {"pipelines": rows, "count": len(rows)}


def mesh_brief() -> dict[str, Any]:
    cat = _read_json(DATA / "sourcea_node_mesh_catalog_v1.json")
    graph = _read_json(DATA / "sourcea_pipeline_node_graph_v1.json")
    ssot = load_ssot()
    return {
        "active_nodes": len(cat.get("active_nodes") or []),
        "logical_nodes": len(cat.get("logical_nodes") or []),
        "parallel_groups": len(graph.get("parallel_groups") or cat.get("parallel_groups") or []),
        "graph_tiers": len(graph.get("tiers") or []),
        "edges": len(graph.get("edges") or []),
        "pipeline_nodes": list((ssot.get("pipeline_nodes") or {}).keys()),
        "synestm": cat.get("synestm") or graph.get("synestm"),
    }


def build_orient_report(*, role: str = "any") -> dict[str, Any]:
    chain = validate_orient_chain()
    cascade = build_receipt_cascade()
    live = _read_json(SINA / "agent-live-surfaces-v1.json")
    route = role_routing(role)
    report = {
        "schema": "orient-routing-report-v1",
        "ok": chain.get("ok"),
        "cascade_ok": cascade.get("ok"),
        "at": _now(),
        "role": role,
        "factory_now_line": live.get("factory_now_line") or "",
        "sascip_line": live.get("sascip_line") or live.get("stranger_agent_monitor", {}).get("one_line", ""),
        "orient_chain": chain,
        "receipt_cascade": cascade,
        "cascade_line": format_cascade_brief(cascade),
        "role_routing": route,
        "node_mesh_brief": mesh_brief(),
        "pipeline_nodes_brief": pipeline_nodes_brief(),
        "founder_word_routing": load_ssot().get("founder_word_routing") or {},
        "daily_ladder": load_ssot().get("daily_routing_ladder") or [],
        "hints": _build_hints(cascade, route),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def _build_hints(cascade: dict[str, Any], route: dict[str, Any]) -> list[str]:
    hints: list[str] = []
    if cascade.get("ok"):
        hints.append(f"next: {route.get('next_tap') or 'RUN INBOX'}")
    else:
        for f in (cascade.get("failures") or [])[:3]:
            hints.append(f"{f.get('node_id')}: {f.get('fix')}")
    hints.append("session start = session gate only · orientation/hospital/maze = founder word")
    return hints


def validate_orient_routing() -> dict[str, Any]:
    errors: list[str] = []
    ssot = load_ssot()
    if ssot.get("schema") != "sourcea-orient-routing-v1":
        errors.append("missing or bad sourcea_orient_routing_v1.json")
    chain = validate_orient_chain()
    errors.extend(chain.get("errors") or [])
    if not (ssot.get("orient_chain") or []):
        errors.append("orient_chain empty")
    if not (ssot.get("session_gate_step_nodes") or {}):
        errors.append("session_gate_step_nodes empty")
    if not (ssot.get("role_routing") or {}):
        errors.append("role_routing empty")
    if not (ssot.get("pipeline_nodes") or {}):
        errors.append("pipeline_nodes empty")
    if not (ssot.get("graph_tiers") or {}):
        errors.append("graph_tiers empty")
    graph = _read_json(DATA / "sourcea_pipeline_node_graph_v1.json")
    lat_ids = {
        n["id"]
        for t in graph.get("tiers") or []
        if t.get("id") == "T_lat_orient"
        for n in t.get("nodes") or []
    }
    orient_node = (ssot.get("pipeline_nodes") or {}).get("orient_routing", {}).get("node_id")
    if lat_ids and orient_node and orient_node not in lat_ids:
        errors.append("orient_routing node not in T_lat_orient graph tier")
    doc = ROOT / "docs/SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md"
    if not doc.is_file():
        errors.append("missing SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md")
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "orient_steps": len(ssot.get("orient_chain") or []),
        "validator_mappings": len(ssot.get("validator_check_nodes") or {}),
    }

"""Run D12 validation checks — substrates, graph safety, dry-run."""
from __future__ import annotations

import py_compile
from pathlib import Path
from typing import Any

from pre_llm.code_intelligence.store import CODE_INTEL_SSOT_PATH, load_canonical as load_d1
from pre_llm.context_packet.schema import hydrate_from_disk_substrate, validate_packet
from pre_llm.dependency_graph.store import DEP_GRAPH_SSOT_PATH, load_canonical as load_d3
from pre_llm.graph_reasoning.store import REASONING_SSOT_PATH, load_canonical as load_d8
from pre_llm.intent_engine.store import INTENT_SSOT_PATH, load_canonical as load_d4
from pre_llm.context_ranking.store import RANKING_SSOT_PATH, load_canonical as load_d9
from pre_llm.memory_git_bridge.store import BRIDGE_SSOT_PATH, load_canonical as load_d6
from pre_llm.planning_engine.store import PLANNING_SSOT_PATH, load_canonical as load_d10
from pre_llm.query_expansion.store import EXPANSION_SSOT_PATH, load_canonical as load_d7
from pre_llm.tool_router.store import ROUTER_SSOT_PATH, load_canonical as load_d11
from pre_llm.vector_retrieval.store import VECTOR_SSOT_PATH, load_canonical as load_d5

SOURCE_A = Path(__file__).resolve().parents[3]

_SUBSTRATE_CHECKS: list[tuple[str, Path, str, str]] = [
    ("d1_code_intelligence", CODE_INTEL_SSOT_PATH, "D1", "query_layer_ready"),
    ("d3_dependency_graph", DEP_GRAPH_SSOT_PATH, "D3", "dependency_ready"),
    ("d4_intent_engine", INTENT_SSOT_PATH, "D4", "intent_ready"),
    ("d5_vector_retrieval", VECTOR_SSOT_PATH, "D5", "retrieval_ready"),
    ("d6_memory_bridge", BRIDGE_SSOT_PATH, "D6", "bridge_ready"),
    ("d7_query_expansion", EXPANSION_SSOT_PATH, "D7", "expansion_ready"),
    ("d8_graph_reasoning", REASONING_SSOT_PATH, "D8", "reasoning_ready"),
    ("d9_context_ranking", RANKING_SSOT_PATH, "D9", "ranking_ready"),
    ("d10_planning_engine", PLANNING_SSOT_PATH, "D10", "plan_ready"),
    ("d11_tool_router", ROUTER_SSOT_PATH, "D11", "router_ready"),
]


def _check_status(*, ok: bool, severity: str = "required") -> str:
    if ok:
        return "pass"
    return "fail" if severity == "required" else "warn"


def _substrate_checks() -> list[dict[str, Any]]:
    loaders = {
        "D1": load_d1,
        "D3": load_d3,
        "D4": load_d4,
        "D5": load_d5,
        "D6": load_d6,
        "D7": load_d7,
        "D8": load_d8,
        "D9": load_d9,
        "D10": load_d10,
        "D11": load_d11,
    }
    checks: list[dict[str, Any]] = []
    for check_id, path, step, flag in _SUBSTRATE_CHECKS:
        exists = path.is_file()
        data = loaders[step]() if exists else {}
        ready = bool(data.get(flag)) if data else False
        checks.append(
            {
                "id": check_id,
                "category": "substrate",
                "step": step,
                "status": _check_status(ok=exists and ready),
                "severity": "required" if step in ("D1", "D3", "D4", "D10", "D11") else "advisory",
                "detail": f"{path.name} exists={exists} {flag}={ready}",
            }
        )
    return checks


def _graph_safety_checks(d3: dict[str, Any], d10: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    impact_ok = bool(d3.get("dependency_ready"))
    stats = d3.get("graph_stats") or {}
    checks.append(
        {
            "id": "graph_dependency_ready",
            "category": "graph_safety",
            "status": _check_status(ok=impact_ok),
            "severity": "required",
            "detail": f"module_edges={stats.get('module_edges', 0)} file_edges={stats.get('file_edges', 0)}",
        }
    )

    graph = d10.get("graph") or {}
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    plan_ok = len(nodes) >= 3 and len(edges) >= 2
    checks.append(
        {
            "id": "plan_graph_integrity",
            "category": "graph_safety",
            "status": _check_status(ok=plan_ok),
            "severity": "required",
            "detail": f"nodes={len(nodes)} edges={len(edges)}",
        }
    )

    node_ids = {n.get("id") for n in nodes}
    dangling = [e for e in edges if e.get("from") not in node_ids or e.get("to") not in node_ids]
    checks.append(
        {
            "id": "plan_edge_integrity",
            "category": "graph_safety",
            "status": _check_status(ok=len(dangling) == 0),
            "severity": "required",
            "detail": f"dangling_edges={len(dangling)}",
        }
    )
    return checks


def _policy_checks(d11: dict[str, Any]) -> list[dict[str, Any]]:
    selection = d11.get("selection") or []
    blocked = [s for s in selection if not s.get("allowed")]
    execute_blocked = [s for s in blocked if s.get("permission") == "execute"]
    checks: list[dict[str, Any]] = [
        {
            "id": "tool_policy_review",
            "category": "policy",
            "status": "pass" if selection else "warn",
            "severity": "advisory",
            "detail": f"selection={len(selection)} blocked={len(blocked)}",
        },
        {
            "id": "execute_blocked_pre_gate",
            "category": "policy",
            "status": "pass" if execute_blocked else "warn",
            "severity": "required",
            "detail": f"execute_blocked={len(execute_blocked)} (expected pre-D15)",
        },
    ]
    return checks


def _compile_sim_checks(d9: dict[str, Any], repo_root: Path) -> list[dict[str, Any]]:
    paths: list[str] = []
    for r in (d9.get("ranked_evidence") or [])[:6]:
        p = r.get("path") or ""
        if p.endswith(".py") and not p.startswith("script/"):
            paths.append(p)

    compiled = 0
    failed = 0
    for rel in paths[:4]:
        full = repo_root / rel if not Path(rel).is_absolute() else Path(rel)
        if not full.is_file():
            failed += 1
            continue
        try:
            py_compile.compile(str(full), doraise=True)
            compiled += 1
        except py_compile.PyCompileError:
            failed += 1

    ok = failed == 0 and (compiled > 0 or len(paths) == 0)
    return [
        {
            "id": "compile_sim_top_evidence",
            "category": "dry_run",
            "status": _check_status(ok=ok, severity="advisory"),
            "severity": "advisory",
            "detail": f"compiled={compiled} failed={failed} sampled={min(len(paths), 4)}",
        }
    ]


def _packet_dry_run(*, task_id: str, repo_root: str) -> list[dict[str, Any]]:
    from pre_llm.context_packet.schema import empty_packet_template  # noqa: WPS433

    packet = hydrate_from_disk_substrate(
        empty_packet_template(task_id=task_id, repo_root=repo_root)
    )
    result = validate_packet(packet)
    return [
        {
            "id": "packet_schema_dry_run",
            "category": "dry_run",
            "status": "pass" if result.get("ok") else "warn",
            "severity": "advisory",
            "detail": (
                f"readiness={result.get('readiness_score')} "
                f"gate_eligible={result.get('gate_eligible')} "
                f"missing={result.get('missing_for_gate')}"
            ),
            "readiness_score": result.get("readiness_score"),
            "gate_eligible": result.get("gate_eligible"),
        }
    ]


def run_all_checks(
    *,
    task_id: str,
    repo_root: Path,
    d3: dict[str, Any],
    d9: dict[str, Any],
    d10: dict[str, Any],
    d11: dict[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    checks.extend(_substrate_checks())
    checks.extend(_graph_safety_checks(d3, d10))
    checks.extend(_policy_checks(d11))
    checks.extend(_compile_sim_checks(d9, repo_root))
    checks.extend(_packet_dry_run(task_id=task_id, repo_root=str(repo_root)))

    required = [c for c in checks if c.get("severity") == "required"]
    required_pass = sum(1 for c in required if c.get("status") == "pass")
    fail_count = sum(1 for c in checks if c.get("status") == "fail")
    warn_count = sum(1 for c in checks if c.get("status") == "warn")

    validation_ready = fail_count == 0 and required_pass == len(required)

    return {
        "checks": checks,
        "check_count": len(checks),
        "required_pass": required_pass,
        "required_total": len(required),
        "fail_count": fail_count,
        "warn_count": warn_count,
        "validation_ready": validation_ready,
        "dry_run": True,
    }

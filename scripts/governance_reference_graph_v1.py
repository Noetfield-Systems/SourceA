#!/usr/bin/env python3
"""G2 — reference graph: law → skill → validator → projection (machine-built)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from governance_paths_v1 import AUTHORITY_INDEX

SINA = Path.home() / ".sina"
GRAPH_PATH = SINA / "governance-reference-graph-v1.json"
INDEX = AUTHORITY_INDEX
CURSOR_MAP = ROOT / "SOURCEA_CURSOR_RULES_AND_SKILLS_MAP_LOCKED_v2.md"

DEFAULT_PROJECTIONS = ["hub", "monitor", "catalog"]
LAW_EXTRA: dict[str, dict] = {
    "GOV_EVENT_SPINE": {
        "skills": ["sina-conscious-recovery"],
        "rules": ["sina-governance-entry.mdc"],
        "validators": [
            "validate-governance-event-spine-v1.sh",
            "validate-governance-replay-v1.sh",
            "validate-governance-projection-g3-v1.sh",
            "validate-governance-self-heal-g7-v1.sh",
        ],
        "scripts": [
            "governance_event_spine_v1.py",
            "governance_reference_graph_v1.py",
            "governance_replay_worker_v1.py",
            "governance_projection_g3_v1.py",
            "governance_self_heal_daemon_v1.py",
        ],
        "projections": ["catalog", "truth_bundle"],
        "materializer": "governance_reference_graph_v1.py --build",
    },
    "LIVE_DECISION_FORM": {
        "skills": ["sina-conscious-recovery"],
        "rules": ["complex-situation-fork.mdc"],
        "validators": ["validate-live-founder-decision-form-v1.sh"],
        "scripts": ["live_founder_decision_form_v1.py"],
        "projections": ["live_form", "catalog"],
        "materializer": "live_founder_decision_form_v1.py --write-receipt",
    },
    "LIVE_GOV_BP": {
        "skills": ["truth-projection"],
        "validators": ["validate-governance-propagation-live-v1.sh"],
        "scripts": ["governance_propagation_cascade_v1.py"],
        "projections": ["hub", "monitor", "truth_bundle"],
        "materializer": "governance_propagation_cascade_v1.py",
    },
    "LOST_LINK_ETHICS": {
        "skills": ["sina-conscious-recovery"],
        "rules": ["lost-link-recovery-reward.mdc"],
        "validators": ["validate-integrity-batch-2-v1.sh"],
        "projections": ["catalog"],
        "materializer": "sync-cursor-agent-skills.sh",
    },
    "MASTER_CATALOG": {
        "skills": ["sina-conscious-recovery"],
        "validators": ["validate-authority-index-coverage-v1.sh"],
        "scripts": ["ecosystem_master_catalog_v1.py"],
        "projections": ["catalog", "hub"],
        "materializer": "ecosystem_master_catalog_v1.py",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_index_rows() -> list[dict]:
    if not INDEX.is_file():
        return []
    rows: list[dict] = []
    for line in INDEX.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("| `"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6 or parts[1] in ("ID", "----"):
            continue
        rid = parts[1].strip("` ")
        doc = parts[2].strip("` ")
        machine = parts[6].strip("` ") if len(parts) > 6 else ""
        if not rid or rid == "ID":
            continue
        node: dict = {
            "id": rid,
            "doc": doc,
            "skills": [],
            "rules": [],
            "validators": [],
            "scripts": [],
            "projections": list(DEFAULT_PROJECTIONS),
            "materializer": "align_command_data_ui_v1.py",
        }
        if machine and machine not in ("—", "-", ""):
            m = machine.replace("`", "")
            if ".sh" in m:
                node["validators"].append(m)
            elif ".py" in m:
                node["scripts"].append(m)
            elif m.endswith(".mdc"):
                node["rules"].append(m)
            else:
                node["scripts"].append(m)
        extra = LAW_EXTRA.get(rid, {})
        for k in ("skills", "rules", "validators", "scripts", "projections", "materializer"):
            if k in extra:
                if k == "materializer":
                    node[k] = extra[k]
                else:
                    node[k] = list(dict.fromkeys(node.get(k, []) + extra[k]))
        rows.append(node)
    return rows


def _global_skills_rules() -> dict:
    skills: list[str] = []
    rules: list[str] = []
    if CURSOR_MAP.is_file():
        text = CURSOR_MAP.read_text(encoding="utf-8", errors="replace")
        skills = sorted(set(re.findall(r"`(@?sina-[\w-]+)`", text) + re.findall(r"`(truth-projection)`", text)))
        rules = sorted(set(re.findall(r"`([\w.-]+\.mdc)`", text)))
    return {"skills": skills, "rules": rules}


def _knowledge_edges(nodes: list[dict]) -> list[dict]:
    """LAW → governs → SKILL → executed_by → AGENT → produces → ARTIFACT → projected_to → HUB."""
    edges: list[dict] = []
    for node in nodes:
        law = node.get("id") or ""
        doc = node.get("doc") or ""
        for skill in node.get("skills") or []:
            edges.append({"from": law, "from_kind": "law", "rel": "governs", "to": skill, "to_kind": "skill"})
            edges.append(
                {
                    "from": skill,
                    "from_kind": "skill",
                    "rel": "executed_by",
                    "to": "sourcea_worker",
                    "to_kind": "agent",
                }
            )
        artifact = doc or law
        edges.append(
            {"from": "sourcea_worker", "from_kind": "agent", "rel": "produces", "to": artifact, "to_kind": "artifact"}
        )
        for proj in node.get("projections") or []:
            edges.append(
                {
                    "from": artifact,
                    "from_kind": "artifact",
                    "rel": "projected_to",
                    "to": proj,
                    "to_kind": "projection",
                }
            )
    return edges


def build_graph() -> dict:
    nodes = _parse_index_rows()
    glob = _global_skills_rules()
    edges = _knowledge_edges(nodes)
    graph = {
        "schema": "governance-reference-graph-v1.1",
        "built_at": _now(),
        "law_path": "SOURCEA_GOVERNANCE_EVENT_SPINE_SCHEMA_LOCKED_v1.md",
        "golden_rule": "brain-os/law/GOVERNANCE_RUNTIME_GOLDEN_RULE_LOCKED_v1.md",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "global": glob,
        "nodes": nodes,
        "knowledge_edges": edges,
        "edges_kind": "law→governs→skill→executed_by→agent→produces→artifact→projected_to→hub|monitor|catalog",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    GRAPH_PATH.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "path": str(GRAPH_PATH), "node_count": len(nodes)}


def impact_scan(*, object_id: str) -> dict:
    if not GRAPH_PATH.is_file():
        build_graph()
    data = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    node = next((n for n in data.get("nodes", []) if n.get("id") == object_id), None)
    if not node:
        return {"ok": False, "error": "object not in graph", "object_id": object_id}
    affected_objects = [object_id]
    for skill in node.get("skills") or []:
        affected_objects.append(f"skill:{skill}")
    for v in node.get("validators") or []:
        affected_objects.append(f"validator:{v}")
    for p in node.get("projections") or []:
        affected_objects.append(f"projection:{p}")
    return {
        "ok": True,
        "object_id": object_id,
        "affected": {
            "skills": node.get("skills", []),
            "rules": node.get("rules", []),
            "validators": node.get("validators", []),
            "scripts": node.get("scripts", []),
            "projections": node.get("projections", []),
            "materializer": node.get("materializer"),
            "objects": list(dict.fromkeys(affected_objects)),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--impact", metavar="ROW_ID")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.impact:
        print(json.dumps(impact_scan(object_id=args.impact), indent=2))
        return 0

    if args.build or not GRAPH_PATH.is_file():
        print(json.dumps(build_graph(), indent=2))
        return 0

    print(GRAPH_PATH.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

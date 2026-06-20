#!/usr/bin/env python3
"""Compile FBE node graph from CREED FACTORY_MESH + CHURCH + Trust Motor patterns.

Graph SSOT output: data/fbe_node_graph_v1.json
Receipt: ~/.sina/fbe-compile-receipt-v1.json
Law: docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
BUNDLE_PATH = DATA / "fbe_factory_builder_bundle_v1.json"
GRAPH_PATH = DATA / "fbe_node_graph_v1.json"
PIPELINES_PATH = DATA / "fbe_pipelines_v1.json"
RECEIPT_PATH = SINA / "fbe-compile-receipt-v1.json"
CHARTER = "docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md"

CREED_MESH = Path.home() / "Desktop/YA5/PLUS ONE/CREED/.cursor/governance/FACTORY_MESH.json"
CHURCH_GRAPH = Path.home() / "Desktop/YA5/PLUS ONE/CHURCH/.cursor/governance/NODE_GRAPH.json"

STUB_CMD = ["python3", "scripts/fbe/stub_node_v1.py"]
PY = sys.executable


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _hash_file(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _fbe_id(line: str, source_id: str) -> str:
    sid = source_id.replace("/", "_")
    if line == "refinery":
        return f"fbe_refinery_{sid}"
    if line == "assembly":
        return f"fbe_assembly_{sid}"
    if line == "motor":
        return f"fbe_motor_{sid}" if not sid.startswith("fbe_motor_") else sid
    if line == "meta":
        return sid if sid.startswith("fbe_") else f"fbe_{sid}"
    return f"fbe_{line}_{sid}"


def _stub_cmd(node_id: str, line: str) -> list[str]:
    return [*STUB_CMD, "--node", node_id, "--line", line, "--json"]


def _motor_nodes() -> list[dict]:
    """18 Trust Motor nodes — LOCKED doc §6."""
    defs = [
        ("session_gate_v1", "Session gate delegate", ["python3", "scripts/agent_session_gate_run_v1.py", "--role", "any", "--json"], "~/.sina/agent-session-gate-receipt-v1.json", True, "INTERNAL"),
        ("sascip_v1", "SASCIP live wire", ["python3", "scripts/stranger_agent_safety_live_wire_v1.py", "--role", "any", "--tier", "session", "--agent", "cursor", "--json"], "~/.sina/stranger-agent-safety-live-wire-v1.json", True, "INTERNAL"),
        ("zero_drift_v1", "Zero-drift wire", ["python3", "scripts/governance_zero_drift_live_wire_v1.py", "--role", "any", "--tier", "session", "--json"], "~/.sina/governance-zero-drift-live-wire-v1.json", True, "INTERNAL"),
        ("disk_live_wire_v1", "Disk live wire sync", ["python3", "scripts/disk_live_wire_sync_v1.py", "--json"], "~/.sina/disk-live-wire-receipt-v1.json", True, "INTERNAL"),
        ("vocabulary_v1", "Vocabulary gate", ["python3", "scripts/vocabulary_guard_v1.py", "--json"], "~/.sina/vocabulary-guard-v1.json", True, "INTERNAL"),
        ("pre_write_v1", "Pre-write guard", ["python3", "scripts/pre_write_guard_v1.py", "check", "--agent", "cursor", "--path", "data/fbe_node_graph_v1.json", "--json"], "receipts/pre-write-v1.json", True, "INTERNAL"),
        ("work_order_sign_v1", "Sign work order", ["python3", "scripts/fbe_sign_work_order_v1.py", "--json"], "receipts/work-order-signed-v1.json", True, "INTERNAL"),
        ("tenant_isolation_v1", "Tenant isolation", ["python3", "scripts/fbe_check_tenant_isolation_v1.py", "--json"], "receipts/tenant-isolation-v1.json", True, "INTERNAL"),
        ("conduct_v1", "Pre-ship conduct", ["python3", "scripts/fbe_motor_conduct_v1.py", "--json"], "receipts/motor-conduct-v1.json", True, "INTERNAL"),
        ("event_spine_v1", "Event spine emit", ["python3", "scripts/fbe_event_spine_emit_v1.py", "--json"], "~/.sina/fbe-events-v1.jsonl", False, "INTERNAL"),
        ("registry_sync_v1", "Motor registry sync", ["python3", "scripts/fbe_motor_registry_sync_v1.py", "--json"], "~/.sina/fbe-motor-registry-v1.json", True, "INTERNAL"),
        ("receipt_federate_v1", "Receipt federation", ["python3", "scripts/fbe_receipt_federate_v1.py", "--json"], "receipts/federated-run-v1.json", True, "INTERNAL"),
        ("critic_v1", "Motor conduct critic", ["python3", "scripts/fbe_motor_critic_v1.py", "--json"], "receipts/motor-critic-v1.json", False, "INTERNAL"),
        ("verify_v1", "Motor plant prove", ["python3", "scripts/fbe_verify_motor_v1.py", "--json"], "receipts/motor-verify-v1.json", True, "INTERNAL"),
        ("hub_projection_v1", "Hub FBE projection", ["python3", "scripts/fbe_hub_projection_v1.py", "--json"], None, False, "HUB_API"),
        ("mac_health_v1", "Mac health probe", ["python3", "scripts/mac_health_live_v1.py", "--json"], None, False, "INTERNAL"),
        ("graph_delegate_v1", "Graph runner delegate", ["python3", "scripts/fbe_motor_delegate_v1.py", "--fbe-prove", "--json"], "~/.sina/fbe-motor-delegate-receipt-v1.json", False, "INTERNAL"),
        ("factory_control_v1", "Factory control", ["python3", "scripts/factory_control_v1.py", "status", "--json"], None, False, "INTERNAL"),
    ]
    nodes = []
    for sid, label, cmd, receipt, required, plane in defs:
        nid = _fbe_id("motor", sid)
        row: dict[str, Any] = {
            "id": nid,
            "label": label,
            "line": "motor",
            "source_id": sid,
            "layer": "GOV" if sid in ("tenant_isolation_v1", "pre_write_v1", "work_order_sign_v1") else "L1",
            "kind": "gate" if "gate" in label.lower() or sid.endswith("_v1") and sid in ("sascip_v1", "vocabulary_v1", "pre_write_v1", "tenant_isolation_v1", "conduct_v1", "verify_v1") else "wire",
            "cmd": cmd,
            "required": required,
            "plane": plane,
            "status": "active",
        }
        if receipt:
            row["receipt"] = receipt
        nodes.append(row)
    return nodes


REFINERY_PROVE_WRAPPERS: dict[str, str] = {
    "creed-orient-v1": "scripts/fbe/refinery/fbe_refinery_orient_v1.py",
    "creed-session-v1": "scripts/fbe/refinery/fbe_refinery_session_v1.py",
    "factory-definition-v1": "scripts/fbe/refinery/fbe_refinery_definition_v1.py",
    "factory-mirror-v1": "scripts/fbe/refinery/fbe_refinery_mirror_v1.py",
    "factory-route-audit-v1": "scripts/fbe/refinery/fbe_refinery_route_audit_v1.py",
    "factory-clone-parity-v1": "scripts/fbe/refinery/fbe_refinery_clone_parity_v1.py",
    "factory-verify-v1": "scripts/fbe/refinery/fbe_refinery_verify_job_v1.py",
}

ASSEMBLY_PROVE_WRAPPERS: dict[str, str] = {
    "church-orient-v1": "scripts/fbe/assembly/fbe_assembly_orient_v1.py",
    "church-architect-v1": "scripts/fbe/assembly/fbe_assembly_architect_v1.py",
    "church-boundary-v1": "scripts/fbe/assembly/fbe_assembly_boundary_v1.py",
    "church-rules-v1": "scripts/fbe/assembly/fbe_assembly_rules_v1.py",
    "church-definition-v1": "scripts/fbe/assembly/fbe_assembly_definition_v1.py",
    "church-neutrality-v1": "scripts/fbe/assembly/fbe_assembly_neutrality_v1.py",
    "church-isolation-v1": "scripts/fbe/assembly/fbe_assembly_isolation_v1.py",
    "church-policy-v1": "scripts/fbe/assembly/fbe_assembly_policy_v1.py",
    "church-dealer-letter-v1": "scripts/fbe/assembly/fbe_assembly_dealer_letter_v1.py",
    "church-intake-v1": "scripts/fbe/assembly/fbe_assembly_intake_v1.py",
    "church-market-fidelity-v1": "scripts/fbe/assembly/fbe_assembly_market_fidelity_v1.py",
    "church-verify-v1": "scripts/fbe/assembly/fbe_assembly_verify_v1.py",
    "church-scaffold-v1": "scripts/fbe/assembly/fbe_assembly_scaffold_v1.py",
    "church-merge-v1": "scripts/fbe/assembly/fbe_assembly_merge_v1.py",
    "church-brand-unity-v1": "scripts/fbe/assembly/fbe_assembly_brand_unity_v1.py",
    "church-narrative-v1": "scripts/fbe/assembly/fbe_assembly_narrative_v1.py",
    "church-forbidden-v1": "scripts/fbe/assembly/fbe_assembly_forbidden_v1.py",
    "church-demo-v1": "scripts/fbe/assembly/fbe_assembly_demo_v1.py",
    "church-gtm-v1": "scripts/fbe/assembly/fbe_assembly_gtm_v1.py",
    "church-deploy-v1": "scripts/fbe/assembly/fbe_assembly_deploy_v1.py",
    "church-domain-v1": "scripts/fbe/assembly/fbe_assembly_domain_v1.py",
    "church-live-smoke-v1": "scripts/fbe/assembly/fbe_assembly_live_smoke_v1.py",
}


def _refinery_cmd(source_id: str, node_id: str) -> list[str]:
    wrapper = REFINERY_PROVE_WRAPPERS.get(source_id)
    if wrapper:
        return ["python3", wrapper, "--bay", "sample-bay", "--json"]
    return _stub_cmd(node_id, "refinery")


def _assembly_cmd(source_id: str, node_id: str, *, planned: bool) -> list[str]:
    if planned:
        return _stub_cmd(node_id, "assembly")
    wrapper = ASSEMBLY_PROVE_WRAPPERS.get(source_id)
    if wrapper:
        return ["python3", wrapper, "--bay", "sample-bay", "--json"]
    return _stub_cmd(node_id, "assembly")


def _refinery_from_creed(mesh: dict) -> tuple[list[dict], list[dict]]:
    nodes_out: list[dict] = []
    id_map: dict[str, str] = {}
    for n in mesh.get("nodes") or []:
        src = str(n.get("id") or "")
        nid = _fbe_id("refinery", src)
        id_map[src] = nid
        status = str(n.get("status") or "active")
        deprecated = status == "deprecated"
        cmd = _refinery_cmd(src, nid)
        row: dict[str, Any] = {
            "id": nid,
            "label": str(n.get("kind") or src) + " · " + src,
            "line": "refinery",
            "source_id": src,
            "layer": str(n.get("layer") or "L1"),
            "kind": str(n.get("kind") or "machine"),
            "cmd": cmd,
            "required": not deprecated,
            "plane": "RUNTIME_CLOUD",
            "status": status,
        }
        if deprecated:
            row["redirect"] = n.get("note") or "locale-prove stack"
            row["required"] = False
        nodes_out.append(row)

    edges_out = []
    for e in mesh.get("edges") or []:
        fr = id_map.get(str(e.get("from") or ""))
        to = id_map.get(str(e.get("to") or ""))
        if fr and to:
            edges_out.append({"from": fr, "to": to, "kind": str(e.get("kind") or "wire")})
    return nodes_out, edges_out


def _assembly_from_church(church: dict) -> list[dict]:
    nodes_out: list[dict] = []
    for n in church.get("nodes") or []:
        src = str(n.get("id") or "")
        nid = _fbe_id("assembly", src)
        status = str(n.get("status") or "wired")
        planned = status == "planned"
        row: dict[str, Any] = {
            "id": nid,
            "label": src,
            "line": "assembly",
            "source_id": src,
            "layer": str(n.get("layer") or "L1"),
            "kind": "gate" if "check:" in str(n.get("npm") or "") or "verify:" in str(n.get("npm") or "") else "wire",
            "cmd": _assembly_cmd(src, nid, planned=planned),
            "required": not planned,
            "plane": "RUNTIME_CLOUD",
            "status": status,
        }
        nodes_out.append(row)
    return nodes_out


def _meta_nodes() -> list[dict]:
    return [
        {
            "id": "fbe_compiler_v1",
            "label": "FBE template compiler",
            "line": "meta",
            "cmd": ["python3", "scripts/fbe_compile_node_graph_v1.py", "--json"],
            "required": True,
            "plane": "INTERNAL",
            "status": "active",
        },
        {
            "id": "fbe_spawn_v1",
            "label": "FBE factory spawn",
            "line": "meta",
            "cmd": ["python3", "scripts/fbe_spawn_factory_v1.py", "--json"],
            "receipt": "~/.sina/fbe-factory-registry-v1.json",
            "required": True,
            "plane": "INTERNAL",
            "status": "active",
        },
        {
            "id": "fbe_run_job_v1",
            "label": "FBE full job orchestrator",
            "line": "meta",
            "cmd": ["python3", "scripts/fbe_run_job_v1.py", "--json"],
            "receipt": "~/.sina/fbe-run-job-receipt-v1.json",
            "required": False,
            "plane": "RUNTIME_CLOUD",
            "status": "active",
        },
        {
            "id": "fbe_hub_projection_v1",
            "label": "FBE hub projection",
            "line": "meta",
            "cmd": ["python3", "scripts/fbe_hub_projection_v1.py", "--json"],
            "required": False,
            "plane": "HUB_API",
            "status": "active",
        },
    ]


def _assign_tiers(
    meta: list[dict],
    motor: list[dict],
    refinery: list[dict],
    assembly: list[dict],
) -> list[dict]:
    motor_by = {n["id"]: n for n in motor}
    refinery_by = {n["id"]: n for n in refinery}
    assembly_by = {n["id"]: n for n in assembly}

    def pick(mapping: dict, ids: list[str]) -> list[dict]:
        return [mapping[i] for i in ids if i in mapping]

    tiers = [
        {"id": "F0_meta", "parallel": False, "budget_sec": 30, "nodes": meta},
        {
            "id": "T0_motor_safety",
            "parallel": True,
            "budget_sec": 30,
            "nodes": pick(motor_by, [
                "fbe_motor_sascip_v1",
                "fbe_motor_tenant_isolation_v1",
                "fbe_motor_pre_write_v1",
                "fbe_motor_session_gate_v1",
            ]),
        },
        {
            "id": "T1_motor_truth",
            "parallel": True,
            "budget_sec": 60,
            "nodes": pick(motor_by, [
                "fbe_motor_zero_drift_v1",
                "fbe_motor_vocabulary_v1",
                "fbe_motor_disk_live_wire_v1",
                "fbe_motor_registry_sync_v1",
            ]),
        },
        {
            "id": "T2_refinery_prove",
            "parallel": True,
            "budget_sec": 120,
            "nodes": pick(refinery_by, [
                "fbe_refinery_factory-route-audit-v1",
                "fbe_refinery_factory-clone-parity-v1",
                "fbe_refinery_factory-verify-v1",
            ]),
        },
        {
            "id": "T3_refinery_brand",
            "parallel": False,
            "budget_sec": 180,
            "nodes": pick(refinery_by, [
                "fbe_refinery_factory-brand-visual-prove-v1",
                "fbe_refinery_factory-product-delivery-v1",
            ]),
        },
        {
            "id": "T4_assembly_market",
            "parallel": True,
            "budget_sec": 90,
            "nodes": [n for n in assembly if n.get("status") == "wired"],
        },
        {
            "id": "T5_federate",
            "parallel": False,
            "budget_sec": 30,
            "nodes": pick(motor_by, [
                "fbe_motor_receipt_federate_v1",
                "fbe_motor_verify_v1",
                "fbe_motor_conduct_v1",
            ]),
        },
    ]
    # Remaining motor/refinery/assembly nodes in catch-all tiers
    assigned = {n["id"] for t in tiers for n in t["nodes"]}
    remaining_motor = [n for n in motor if n["id"] not in assigned]
    remaining_refinery = [n for n in refinery if n["id"] not in assigned]
    remaining_assembly = [n for n in assembly if n["id"] not in assigned and n.get("status") == "planned"]

    if remaining_motor:
        tiers.append({"id": "T1_motor_extra", "parallel": True, "budget_sec": 60, "nodes": remaining_motor})
    if remaining_refinery:
        tiers.append({"id": "T2_refinery_extra", "parallel": True, "budget_sec": 120, "nodes": remaining_refinery})
    if remaining_assembly:
        tiers.append({"id": "T4_assembly_planned", "parallel": False, "budget_sec": 90, "nodes": remaining_assembly})

    return tiers


def _build_pipelines(bundle: dict) -> dict:
    pipeline_defs = bundle.get("pipelines") or {}
    rows = []
    for group, ids in pipeline_defs.items():
        for pid in ids:
            rows.append({
                "id": pid,
                "group": group,
                "tier": "F0" if group == "bundle" else group[0].upper() + "0",
                "label": pid.replace("-", " ").title(),
            })
    return {
        "schema": "fbe-pipelines-v1",
        "version": "1.0.0",
        "saved_at": _now(),
        "pipelines": rows,
        "shipGate": {
            "graph": "validate-fbe-node-graph-v1.sh PASS",
            "bundle": "validate-fbe-factory-builder-bundle-v1.sh PASS",
            "motor": "fbe_motor_session_gate_v1 structural PASS",
        },
    }


def compile_graph(*, write: bool = False) -> dict:
    bundle = _read_json(BUNDLE_PATH)
    mesh = _read_json(CREED_MESH)
    church = _read_json(CHURCH_GRAPH)

    errors: list[str] = []
    if mesh.get("schema") != "creed-factory-mesh-v2":
        errors.append(f"missing CREED mesh: {CREED_MESH}")
    if church.get("schema") != "church-node-graph-v2":
        errors.append(f"missing CHURCH graph: {CHURCH_GRAPH}")
    if int(mesh.get("nodeCount") or 0) != 36:
        errors.append(f"CREED nodeCount expected 36 got {mesh.get('nodeCount')}")

    refinery, creed_edges = _refinery_from_creed(mesh)
    assembly = _assembly_from_church(church)
    motor = _motor_nodes()
    meta = _meta_nodes()

    line_nodes = refinery + assembly + motor
    line_count = len(line_nodes)
    graph_total = line_count + len(meta)

    cross_edges = [
        {"from": "fbe_compiler_v1", "to": "fbe_motor_session_gate_v1", "kind": "trigger"},
        {"from": "fbe_motor_session_gate_v1", "to": "fbe_refinery_creed-orient-v1", "kind": "gate"},
        {"from": "fbe_refinery_creed-session-v1", "to": "fbe_assembly_church-intake-v1", "kind": "gate"},
        {"from": "fbe_assembly_church-verify-v1", "to": "fbe_motor_receipt_federate_v1", "kind": "wire"},
        {"from": "fbe_spawn_v1", "to": "fbe_compiler_v1", "kind": "orchestrate"},
        {"from": "fbe_run_job_v1", "to": "fbe_spawn_v1", "kind": "orchestrate"},
        {"from": "fbe_hub_projection_v1", "to": "fbe_motor_registry_sync_v1", "kind": "surface"},
    ]

    tiers = _assign_tiers(meta, motor, refinery, assembly)
    parallel_groups = [
        {"id": "F0_meta_fanout", "tier": "F0_meta", "parallel": False, "nodes": [n["id"] for n in meta]},
        {"id": "T0_motor_safety_fanout", "tier": "T0_motor_safety", "parallel": True, "nodes": [n["id"] for t in tiers if t["id"] == "T0_motor_safety" for n in t["nodes"]]},
        {"id": "T1_motor_truth_fanout", "tier": "T1_motor_truth", "parallel": True, "nodes": [n["id"] for t in tiers if t["id"] == "T1_motor_truth" for n in t["nodes"]]},
        {"id": "T2_refinery_prove_fanout", "tier": "T2_refinery_prove", "parallel": True, "nodes": [n["id"] for t in tiers if t["id"] == "T2_refinery_prove" for n in t["nodes"]]},
        {"id": "T4_assembly_market_fanout", "tier": "T4_assembly_market", "parallel": True, "nodes": [n["id"] for t in tiers if t["id"] == "T4_assembly_market" for n in t["nodes"]]},
        {"id": "T5_federate_fanout", "tier": "T5_federate", "parallel": False, "nodes": [n["id"] for t in tiers if t["id"] == "T5_federate" for n in t["nodes"]]},
    ]

    graph = {
        "schema": "fbe-node-graph-v1",
        "version": "1.0.0",
        "saved_at": _now(),
        "charter": CHARTER,
        "bundle": "data/fbe_factory_builder_bundle_v1.json",
        "epic": "E12",
        "line_node_count": 76,
        "graph_total_nodes": graph_total,
        "counts": {
            "refinery": len(refinery),
            "assembly": len(assembly),
            "motor": len(motor),
            "meta": len(meta),
        },
        "sources": {
            "creed_mesh": str(CREED_MESH),
            "church_graph": str(CHURCH_GRAPH),
            "creed_mesh_hash": _hash_file(CREED_MESH),
            "church_graph_hash": _hash_file(CHURCH_GRAPH),
        },
        "receipt": "~/.sina/fbe-pipeline-node-graph-receipt-v1.json",
        "parallel_groups": parallel_groups,
        "edges": creed_edges + cross_edges,
        "tiers": tiers,
    }

    ok = not errors and line_count == 76
    receipt = {
        "schema": "fbe-compile-receipt-v1",
        "ok": ok,
        "at": _now(),
        "line_node_count": line_count,
        "graph_total_nodes": graph_total,
        "expected_line_nodes": 76,
        "counts": graph["counts"],
        "errors": errors,
        "sources": graph["sources"],
        "graph_path": str(GRAPH_PATH.relative_to(ROOT)),
    }

    if write and ok:
        DATA.mkdir(parents=True, exist_ok=True)
        GRAPH_PATH.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
        pipelines = _build_pipelines(bundle)
        PIPELINES_PATH.write_text(json.dumps(pipelines, indent=2) + "\n", encoding="utf-8")
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    return {"ok": ok, "graph": graph, "receipt": receipt}


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile FBE node graph from live campus patterns")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = compile_graph(write=args.write)
    if args.json:
        print(json.dumps(row.get("receipt") if args.write else row, indent=2))
    else:
        r = row.get("receipt") or row
        print(f"ok={r.get('ok')} line_nodes={r.get('line_node_count', r.get('counts'))}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

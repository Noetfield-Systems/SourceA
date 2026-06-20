#!/usr/bin/env python3
"""P1 Orientation (Atlas) — mandatory gate + tree + WHY for every new arrival. Read-only.

Law: AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md (v2)
Trigger: orientation · Tier 1 · SHORT
Receipt: ~/.sina/agent-orientation-receipt-v1.json
Reading pack: ~/.sina/agent-orientation-reading-pack-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "agent-orientation-receipt-v1.json"
SCHEMA = "agent-orientation-receipt-v2"

sys.path.insert(0, str(SCRIPTS))
from agent_three_pipelines_lib_v1 import (  # noqa: E402
    GATE_TREE,
    LAW,
    ORIENTATION_READS,
    load_orientation_reads,
    TIERS,
    build_reading_pack,
    file_station,
    now_iso,
)


def _run_json(cmd: list[str], *, timeout: int = 90) -> dict:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT), timeout=timeout)
        i = out.find("{")
        return json.loads(out[i:]) if i >= 0 else {"raw": out[-500:]}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}


def run_orientation(*, role: str = "any") -> dict:
    meta = TIERS["orientation"]
    stations: list[dict] = []

    for sid, name, rel in load_orientation_reads():
        st = file_station(sid, name, rel)
        st["kind"] = "read"
        stations.append(st)

    pack = build_reading_pack(role=role)
    stations.append(
        {
            "id": "O12",
            "name": "reading_pack_written",
            "ok": (SINA / "agent-orientation-reading-pack-v1.json").is_file(),
            "paths_in_pack": len(pack.get("reads") or []),
        }
    )

    catalog = _run_json([sys.executable, str(SCRIPTS / "ecosystem_master_catalog_v1.py"), "--json"])
    stations.append(
        {
            "id": "O13",
            "name": "ecosystem_catalog",
            "kind": "probe",
            "ok": bool(catalog.get("ok", True)),
            "machines": catalog.get("machine_count") or catalog.get("machines_count"),
        }
    )

    bundle = _run_json([sys.executable, str(SCRIPTS / "agent_truth_bundle_v1.py"), "--json"])
    stations.append(
        {
            "id": "O14",
            "name": "truth_bundle",
            "kind": "probe",
            "ok": bundle.get("schema") == "agent-truth-bundle-v1",
            "mode": bundle.get("mode"),
        }
    )

    pipe = _run_json([sys.executable, str(SCRIPTS / "agentic_layer_pipeline_v2.py"), "--json", "--tier", "fast"], timeout=120)
    stations.append(
        {
            "id": "O18",
            "name": "agentic_pipeline_map",
            "kind": "probe",
            "node_id": "agentic_layer_fast",
            "ok": pipe.get("schema") == "agentic-layer-pipeline-v2",
            "health": (pipe.get("health") or {}).get("status"),
        }
    )

    orient = _run_json([sys.executable, str(SCRIPTS / "agent_orient_v1.py"), "--role", role, "--json"], timeout=60)
    stations.append(
        {
            "id": "O19",
            "name": "orient_routing_cascade",
            "kind": "probe",
            "node_id": "orient_routing_v1",
            "ok": orient.get("schema") == "orient-routing-report-v1" or orient.get("ok") is not None,
            "cascade_ok": orient.get("cascade_ok"),
            "cascade_line": orient.get("cascade_line") or (orient.get("receipt_cascade") or {}).get("ok"),
            "report": str(SINA / "orient-routing-report-v1.json"),
        }
    )

    graph = _run_json(
        [sys.executable, str(SCRIPTS / "pipeline_node_graph_runner_v1.py"), "--tier", "T_lat_orient", "--dry-run", "--json"],
        timeout=30,
    )
    stations.append(
        {
            "id": "O20",
            "name": "node_graph_lat_dry_run",
            "kind": "probe",
            "node_id": "pipeline_node_graph_runner_v1",
            "ok": graph.get("schema") == "pipeline-node-graph-receipt-v1" and bool(graph.get("tiers")),
            "tier": "T_lat_orient",
        }
    )

    read_ok = all(s.get("ok") for s in stations if s.get("kind") == "read")
    ok = read_ok and all(s.get("ok") for s in stations)

    row = {
        "schema": SCHEMA,
        "ok": ok,
        "at": now_iso(),
        **meta,
        "role_hint": role,
        "execution_authority": False,
        "orientation_complete": ok,
        "gate_tree": GATE_TREE,
        "stations": stations,
        "reading_pack": str(SINA / "agent-orientation-reading-pack-v1.json"),
        "agent_must": [
            "Read gate_tree · pick ONE branch",
            "Read reading_pack paths in order",
            "Bookmark H1 · never legacy for daily",
            "No worker-submit · no hub rebuild · no law edits",
        ],
        "founder_next": "Say role (worker/brain/…) or send to hospital if returning agent",
        "law": LAW,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="P1 Orientation Atlas — Tier 1 mandatory")
    ap.add_argument("--role", default="any")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_orientation(role=args.role)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ORIENTATION tier=1 ok={row['ok']} stations={len(row['stations'])} pack={row['reading_pack']}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

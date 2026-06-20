#!/usr/bin/env python3
"""Full ecosystem connected gate — worker + nerve + node graph + agentic + orient."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "sourcea-ecosystem-connected-receipt-v1.json"
GRAPH_RECEIPT = SINA / "pipeline-node-graph-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _age_hours(path: Path) -> float | None:
    row = _read(path)
    at = str(row.get("at") or "")
    if not at:
        return None
    try:
        ts = datetime.strptime(at.replace("Z", ""), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - ts).total_seconds() / 3600
    except ValueError:
        return None


def _shell_ok(script: str) -> bool:
    p = subprocess.run(["bash", script], cwd=ROOT, capture_output=True, text=True)
    return p.returncode == 0


def assess_ecosystem_connected(*, write_receipt: bool = True) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from validate_sourcea_worker_connected_v1 import assess_connected  # noqa: WPS433
    from agent_nerve_system_v1 import run_nerve_pulse  # noqa: WPS433
    from investigator_judge_unified_receipt_v1 import build_unified_receipt  # noqa: WPS433

    worker = assess_connected(hub_check=True, write_receipt=False)
    nerve = run_nerve_pulse(write=True, refresh_loops=False)
    graph = _read(GRAPH_RECEIPT)
    graph_age = _age_hours(GRAPH_RECEIPT)
    graph_fresh = graph_age is not None and graph_age <= 24
    graph_ok = bool(graph.get("ok")) or bool(graph.get("degraded"))
    agentic_ok = _shell_ok("scripts/validate-agentic-layer-wire-v1.sh")
    brain_l2_ok = _shell_ok("scripts/validate-brain-l2-wire-v1.sh")
    orient_ok = _shell_ok("scripts/validate-orient-routing-v1.sh")
    oegcc_wired = _shell_ok("scripts/validate-outbound-email-controller-loop-v1.sh")
    ij = build_unified_receipt(write=True)

    checks = {
        "worker_connected": bool(worker.get("ok")),
        "nerve_system": bool(nerve.get("ok")),
        "nerve_worker_gate": bool((nerve.get("ship_gates") or {}).get("worker_connected")),
        "node_graph_fresh": graph_fresh,
        "node_graph_ok": graph_ok,
        "agentic_layer_wire": agentic_ok,
        "brain_l2_wire": brain_l2_ok,
        "orient_routing": orient_ok,
        "investigator_judge": bool(ij.get("ok")),
        "oegcc_loop_wired": oegcc_wired,
    }
    ok = all(checks.values())
    row = {
        "schema": "sourcea-ecosystem-connected-receipt-v1",
        "at": _now(),
        "ok": ok,
        "ecosystem_connected": ok,
        "checks": checks,
        "worker_connected_line": worker.get("line"),
        "nerve_system_line": nerve.get("nerve_system_line"),
        "outbound_progress_line": worker.get("outbound_progress_line"),
        "execution_honesty_line": worker.get("execution_honesty_line"),
        "graph_receipt_at": graph.get("at"),
        "graph_degraded": graph.get("degraded"),
        "investigator_judge_line": ij.get("unified_line"),
        "command": "bash scripts/validate-sourcea-ecosystem-connected-v1.sh",
        "line": "ecosystem-connected · PASS" if ok else "ecosystem-connected · BLOCK",
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA ecosystem connected gate")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = assess_ecosystem_connected(write_receipt=True)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Sync worker-dual-40 w1-01..w1-20 from machine proofs (eval SA block).

TRACE: AUTO-TRACE-WORKER1-SA-BLOCK-SYNC-v1.0 · agent Auto
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os/plan-registry/worker-dual-40/REGISTRY.json"

PROOFS: dict[str, list[str]] = {
    "w1-01": ["bash", str(ROOT / "scripts/validate-eval-report-capture-v1.sh")],
    "w1-02": [
        "python3",
        "-c",
        "from pathlib import Path; t=Path('scripts/find_critical_bugs.py').read_text(); "
        "assert 'validate-governance-fleet-v1.sh' in t",
    ],
    "w1-03": ["bash", str(ROOT / "scripts/validate-dispatch-policy-alignment-v1.sh")],
    "w1-04": ["bash", str(ROOT / "scripts/validate-graph-executor-pos-dispatch-v1.sh")],
    "w1-05": ["bash", str(ROOT / "scripts/validate-eval-packet-v1b-live.sh")],
    "w1-06": ["bash", str(ROOT / "scripts/validate-eval-packet-v1b-scorer-plan-paths-v1.sh")],
    "w1-07": ["bash", str(ROOT / "scripts/validate-eval-packet-v1b-retrieve-dispatch-grounding-v1.sh")],
    "w1-08": ["bash", str(ROOT / "scripts/validate-eval-packet-v1b-factory-runreceipt-grounding-v1.sh")],
    "w1-09": ["bash", str(ROOT / "scripts/validate-eval-packet-v1b-l8-hybrid-grounding-v1.sh")],
    "w1-10": ["bash", str(ROOT / "scripts/validate-eval-packet-v1b-scaffold-after-live-v1.sh")],
    "w1-11": ["bash", str(ROOT / "scripts/validate-council-strategic-brief-eval-v1.sh")],
    "w1-12": ["bash", str(ROOT / "scripts/validate-eval-packet-v1b-strict-build-chain-v1.sh")],
    "w1-13": ["bash", str(ROOT / "scripts/validate-no-asf-eval-authority-v1.sh")],
    "w1-14": ["bash", str(ROOT / "scripts/validate-command-data-eval-win-pct-v1.sh")],
    "w1-15": ["bash", str(ROOT / "scripts/validate-council-strategic-brief-eval-v1.sh")],
    "w1-16": ["python3", str(ROOT / "scripts/audit_hub_source_alignment.py")],
    "w1-17": ["bash", str(ROOT / "scripts/validate-dispatch-classifier-task-ids-v1.sh")],
    "w1-18": ["bash", str(ROOT / "scripts/validate-gate-receipts-v1.sh")],
    "w1-19": ["bash", str(ROOT / "scripts/validate-governance-drift-v1.sh")],
    "w1-20": [
        "python3",
        "-c",
        "from pathlib import Path; pri=Path('brain-os/plan-registry/SOURCEA-PRIORITY.md').read_text(); "
        "assert 'sa-0150' in pri, 'sa-0150 PRIORITY row missing'",
    ],
}


def _proved(cmd: list[str]) -> bool:
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, timeout=180)
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def main() -> int:
    data = json.loads(REG.read_text(encoding="utf-8"))
    updated: list[str] = []
    for plan in data.get("plans") or []:
        wid = plan.get("id") or ""
        if wid not in PROOFS or plan.get("status") == "done":
            continue
        if _proved(PROOFS[wid]):
            plan["status"] = "done"
            updated.append(wid)
    REG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"OK: sync_worker_1_sa_block_status_v1 updated={updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

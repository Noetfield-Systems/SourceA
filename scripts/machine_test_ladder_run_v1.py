#!/usr/bin/env python3
"""Tiered machine test ladder — run validators by cadence · write disk receipt.

Law: SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md
Receipt: ~/.sina/machine-test-ladder-receipt-v1.json

Usage:
  python3 scripts/machine_test_ladder_run_v1.py --tier daily --json
  python3 scripts/machine_test_ladder_run_v1.py --tier weekly --role worker --json
"""
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
RECEIPT = SINA / "machine-test-ladder-receipt-v1.json"
SCHEMA = "machine-test-ladder-receipt-v1"
LAW = "SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_step(step_id: str, cmd: list[str], *, timeout: int = 300) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout or "") + (proc.stderr or "")
        j = {}
        if "{" in out:
            try:
                j = json.loads(out[out.find("{") :])
            except json.JSONDecodeError:
                j = {}
        return {
            "id": step_id,
            "ok": proc.returncode == 0,
            "exit": proc.returncode,
            "json": j if j else None,
            "tail": out.strip()[-320:],
        }
    except subprocess.TimeoutExpired:
        return {"id": step_id, "ok": False, "exit": -1, "tail": "timeout"}


def _tier_steps(tier: str, *, role: str) -> list[tuple[str, list[str], int]]:
    py = sys.executable
    bash = "bash"
    daily = [
        ("D1_super_fast_hub", [bash, str(SCRIPTS / "validate-super-fast-hub-v1.sh")], 120),
        ("D2_two_hub", [bash, str(SCRIPTS / "validate-two-hub-v1.sh")], 180),
        ("D3_governance_fast", [py, str(SCRIPTS / "governance_center_run_v1.py"), "--tier", "fast", "--json"], 300),
        ("D4_agentic_pipeline_fast", [py, str(SCRIPTS / "agentic_layer_pipeline_v2.py"), "--json", "--tier", "fast"], 180),
        ("D5_session_gate", [py, str(SCRIPTS / "agent_session_gate_run_v1.py"), "--role", role, "--json"], 240),
        ("D6_three_pipelines_smoke", [bash, str(SCRIPTS / "validate-agent-three-pipelines-v1.sh")], 120),
    ]
    three_day = daily + [
        ("3D1_hub_copy_founder", [bash, str(SCRIPTS / "validate-founder-docs-no-terminal-v1.sh")], 60),
        ("3D2_no_autorun", [bash, str(SCRIPTS / "validate-hub-p0-no-autorun-v1.sh")], 60),
        ("3D3_agentic_wire", [bash, str(SCRIPTS / "validate-agentic-layer-wire-v1.sh")], 120),
        ("3D4_worker_inbox", [bash, str(SCRIPTS / "validate-worker-inbox-delivery-v1.sh")], 120),
        ("3D5_scoreboard_sync", [bash, str(SCRIPTS / "validate-fleet-snapshot-scoreboard-v1.sh")], 120),
        ("3D6_machine_pipelines_smoke", [bash, str(SCRIPTS / "validate-machine-three-pipelines-v1.sh")], 120),
    ]
    weekly = three_day + [
        ("W1_governance_full", [py, str(SCRIPTS / "governance_center_run_v1.py"), "--tier", "full", "--json"], 600),
        ("W2_anti_staleness_bundle", [bash, str(SCRIPTS / "validate-anti-staleness-bundle-v1.sh")], 900),
        ("W3_find_critical_bugs", [py, str(SCRIPTS / "find_critical_bugs.py")], 600),
        ("W4_broker_receipt", [bash, str(SCRIPTS / "validate-broker-receipt-cycle-v1.sh")], 120),
    ]
    monthly = weekly + [
        ("M1_hub_alignment", [py, str(SCRIPTS / "audit_hub_source_alignment.py")], 300),
        ("M2_ecosystem_catalog", [py, str(SCRIPTS / "ecosystem_master_catalog_v1.py"), "--json"], 120),
    ]
    mapping = {"daily": daily, "3day": three_day, "weekly": weekly, "monthly": monthly}
    return mapping[tier]


def run_ladder(*, tier: str, role: str = "worker") -> dict:
    steps_spec = _tier_steps(tier, role=role)
    steps = [_run_step(sid, cmd, timeout=to) for sid, cmd, to in steps_spec]

    crit = 0
    crit_path = SINA / "find-bugs" / "last-run.json"
    if crit_path.is_file():
        try:
            crit = int(json.loads(crit_path.read_text()).get("critical_count") or 0)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    ok = all(s.get("ok") for s in steps)
    ship_talk_ok = crit == 0 if tier in ("weekly", "monthly") else True

    row = {
        "schema": SCHEMA,
        "ok": ok and ship_talk_ok,
        "at": _now(),
        "tier": tier,
        "role": role,
        "steps": steps,
        "steps_passed": sum(1 for s in steps if s.get("ok")),
        "steps_total": len(steps),
        "critical_count": crit,
        "ship_talk_blocked": not ship_talk_ok,
        "law": LAW,
        "baseline_paths": [
            str(SINA / "agentic-layer-pipeline-v2.json"),
            str(SINA / "governance-center-receipt-v1.json"),
            str(SINA / "two-hub-heal-receipt-v1.json"),
            str(crit_path),
            str(SINA / "h2-pending-registry-v1.json"),
        ],
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Machine test ladder by cadence")
    ap.add_argument("--tier", required=True, choices=["daily", "3day", "weekly", "monthly"])
    ap.add_argument("--role", default="worker")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_ladder(tier=args.tier, role=args.role)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"LADDER tier={args.tier} ok={row['ok']} {row['steps_passed']}/{row['steps_total']} critical={row['critical_count']}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

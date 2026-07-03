#!/usr/bin/env python3
"""Worker execution gate — session + cost tier + mission routing (LP-WORKER-EXEC)."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RECEIPT = ROOT / "receipts" / "proof" / "worker-execution-gate-latest-v1.json"
MISSION_REG = ROOT / "data" / "mission-registry-v1.json"
COST_QUEUE = ROOT / "data" / "worker-cost-tier-queue-v1.json"
PY = sys.executable


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_receipt(doc: dict[str, Any]) -> None:
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _run(cmd: list[str]) -> tuple[int, str]:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT))
        return 0, out
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output or ""


def route_cost_tier(*, task: str) -> dict[str, Any]:
    row = _read(COST_QUEUE)
    task_l = (task or "").lower()
    tier = "T2"
    reason = "default Worker tier"
    for item in row.get("reclassified_open_queue") or []:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").lower()
        if title and any(tok in task_l for tok in title.split()[:3] if len(tok) > 3):
            tier = str(item.get("cost_tier") or tier)
            reason = f"matched queue item {item.get('id')}"
            break
    if any(k in task_l for k in ("grep", "sweep", "registry", "validate", "lint", "sync")):
        tier = "T0"
        reason = "T0 keyword match"
    elif any(k in task_l for k in ("copilot", "hygiene", "kaizen")):
        tier = "T1"
        reason = "T1 keyword match"
    elif any(k in task_l for k in ("merge", "integrat", "main")):
        tier = "T3"
        reason = "T3 integrator keyword"
    return {"tier": tier, "reason": reason}


def resolve_mission(*, mission_id: str, task: str) -> dict[str, Any]:
    reg = _read(MISSION_REG)
    missions = reg.get("missions") or []
    if mission_id:
        hit = next((m for m in missions if m.get("mission_id") == mission_id), None)
        if hit:
            return {"ok": True, "mission_id": mission_id, "lane_id": hit.get("lane_id"), "name": hit.get("name")}
        return {"ok": False, "error": f"unknown mission_id {mission_id}"}
    task_l = (task or "").lower()
    keywords = {
        "M1": ("verify", "external", "buyer", "l4"),
        "M2": ("forge", "motor", "cron", "factory"),
        "M3": ("determinism", "trigger", "truth", "drift"),
        "M4": ("kaizen", "build", "w-lba", "improve"),
        "M5": ("signal", "recipe", "client"),
    }
    for mid, kws in keywords.items():
        if any(k in task_l for k in kws):
            hit = next((m for m in missions if m.get("mission_id") == mid), {})
            return {"ok": True, "mission_id": mid, "lane_id": hit.get("lane_id"), "name": hit.get("name")}
    return {"ok": False, "error": "no mission match — pass --mission-id M1|M2|M3|M4|M5"}


def run_gate(*, role: str = "worker", task: str = "", mission_id: str = "", skip_adversarial: bool = False, skip_session: bool = False) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    ok = True

    if not skip_session:
        code, out = _run([PY, str(SCRIPTS / "agent_session_gate_run_v1.py"), "--role", role, "--json"])
        session_ok = code == 0
        steps.append({"step": "session_gate", "ok": session_ok, "exit": code})
        if not session_ok:
            ok = False
    else:
        steps.append({"step": "session_gate", "ok": True, "skipped": True})

    tier = route_cost_tier(task=task)
    steps.append({"step": "cost_tier", "ok": True, **tier})

    mission = resolve_mission(mission_id=mission_id, task=task)
    steps.append({"step": "mission_routing", **mission})
    if not mission.get("ok"):
        ok = False

    if ok and not skip_adversarial and (SCRIPTS / "adversarial_critique_gate_v1.sh").is_file():
        code, out = _run(["bash", str(SCRIPTS / "adversarial_critique_gate_v1.sh")])
        adv_ok = code == 0
        steps.append({"step": "adversarial_critique", "ok": adv_ok, "exit": code})
        if not adv_ok:
            ok = False

    op_key = hashlib.sha256(f"{task}:{mission_id}:{_now()}".encode()).hexdigest()[:40]
    doc = {
        "schema": "worker-execution-gate-v1",
        "version": "1.0.0",
        "at": _now(),
        "ok": ok,
        "role": role,
        "task": task[:200],
        "mission_id": mission.get("mission_id") if mission.get("ok") else mission_id,
        "cost_tier": tier.get("tier"),
        "op_key": op_key,
        "steps": steps,
        "report_line": (
            f"worker_gate PASS · mission={mission.get('mission_id')} tier={tier.get('tier')}"
            if ok
            else f"worker_gate FAIL · {steps[-1].get('error') or steps[-1].get('step')}"
        ),
    }
    _write_receipt(doc)
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--role", default="worker")
    ap.add_argument("--task", default="")
    ap.add_argument("--mission-id", default="")
    ap.add_argument("--skip-adversarial", action="store_true")
    ap.add_argument("--skip-session", action="store_true", help="machine-cycle bootstrap without full session gate")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_gate(
        role=args.role,
        task=args.task,
        mission_id=args.mission_id,
        skip_adversarial=args.skip_adversarial,
        skip_session=args.skip_session,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

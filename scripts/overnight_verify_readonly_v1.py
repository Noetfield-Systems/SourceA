#!/usr/bin/env python3
"""Founder-gated overnight verify — read-only CHECK (max 5 turns). HUB-P0-3."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path.home() / ".sina" / "overnight-verify-report-v1.json"
MAX_TURNS = 5


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _turn_honest() -> dict:
    import importlib.util

    mod_path = ROOT / "scripts" / "program-1000-honest-status-v1.py"
    spec = importlib.util.spec_from_file_location("program_1000_honest_status_v1", mod_path)
    if not spec or not spec.loader:
        row = _read_json(Path.home() / ".sina" / "PROGRAM_1000_HONEST_STATUS.json")
    else:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        row = mod.build_status()
    kill = "RED" if (row.get("unproven_done") or row.get("drift")) else "GREEN"
    return {
        "turn": 1,
        "check": "honest_progress",
        "ok": kill == "GREEN",
        "kill": kill,
        "verified_done": row.get("honest_done"),
        "unproven_done": row.get("unproven_done"),
        "drift": row.get("drift"),
        "detail": row.get("law"),
    }


def _turn_freeze() -> dict:
    fn = _read_json(Path.home() / ".sina" / "factory-now-v1.json")
    frozen = bool(fn.get("frozen") or fn.get("freeze_on") or fn.get("kill_flag"))
    kill = "RED" if frozen else "GREEN"
    return {
        "turn": 2,
        "check": "factory_freeze",
        "ok": True,
        "kill": kill if frozen else "GREEN",
        "frozen": frozen,
        "mode": fn.get("mode"),
        "copy": "Semi-auto · founder-gated" if frozen else "Factory not blocking",
    }


def _turn_queue() -> dict:
    t = _read_json(Path.home() / ".sina" / "run-inbox-disk-truth-v1.json")
    q = t.get("queue") or {}
    return {
        "turn": 3,
        "check": "queue_truth",
        "ok": bool(q.get("sa_id")),
        "sa_id": q.get("sa_id"),
        "queue_role": q.get("queue_role"),
        "pending": bool(t.get("pending")),
    }


def _turn_hub() -> dict:
    import urllib.request

    ok_hub = ok_worker = False
    try:
        with urllib.request.urlopen("http://127.0.0.1:13020/health", timeout=3) as r:
            ok_hub = r.status == 200
    except Exception:
        pass
    try:
        with urllib.request.urlopen("http://127.0.0.1:13030/health", timeout=3) as r:
            ok_worker = r.status == 200
    except Exception:
        pass
    return {
        "turn": 4,
        "check": "hub_worker_health",
        "ok": ok_hub and ok_worker,
        "hub_13020": ok_hub,
        "worker_13030": ok_worker,
    }


def _turn_ecosystem() -> dict:
    script = ROOT / "scripts" / "validate-ecosystem-safety-v1.sh"
    if not script.is_file():
        return {"turn": 5, "check": "ecosystem_safety", "ok": False, "error": "validator missing"}
    try:
        proc = subprocess.run(
            ["bash", str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )
        return {
            "turn": 5,
            "check": "ecosystem_safety",
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "tail": (proc.stdout or proc.stderr or "")[-500:],
        }
    except subprocess.TimeoutExpired:
        return {"turn": 5, "check": "ecosystem_safety", "ok": False, "error": "timeout"}


def run_verify() -> dict:
    turns = [_turn_honest(), _turn_freeze(), _turn_queue(), _turn_hub(), _turn_ecosystem()]
    turns = turns[:MAX_TURNS]
    kills = [t.get("kill") for t in turns if t.get("kill") == "RED"]
    overall_kill = "RED" if kills or any(not t.get("ok") for t in turns[:2]) else "GREEN"
    summary = (
        "Semi-auto · founder-gated — fix unproven/drift before overnight"
        if overall_kill == "RED"
        else "Read-only overnight check PASS — receipt-bound progress only"
    )
    return {
        "schema": "overnight-verify-readonly-v1",
        "at": _now(),
        "turns": len(turns),
        "max_turns": MAX_TURNS,
        "kill": overall_kill,
        "summary": summary,
        "checks": turns,
        "writes": False,
        "model": "disk-check-only",
    }


def main() -> int:
    report = run_verify()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report.get("kill") == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())

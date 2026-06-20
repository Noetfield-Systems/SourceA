#!/usr/bin/env python3
"""Run every Goal 1 enforcement step in order — Brain must paste this output.

Founder prompt: see os/chat-handoffs/BRAIN_ENFORCEMENT_AUDIT_PROMPT_LOCKED_v1.md
Law: GOAL1_LOOP_ACTIVATION_CHAIN · ONE_SA_PER_TURN_MECHANICAL · INCIDENT-003
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int = 60) -> dict:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        body = (proc.stdout or "").strip()
        row: dict = {"exit_code": proc.returncode, "stdout": body[:4000], "stderr": (proc.stderr or "")[:800]}
        if body:
            try:
                row["json"] = json.loads(body.split("\n")[-1] if body.startswith("{") else body)
            except json.JSONDecodeError:
                for line in body.splitlines():
                    if line.strip().startswith("{"):
                        try:
                            row["json"] = json.loads(line)
                            break
                        except json.JSONDecodeError:
                            pass
        row["ok"] = proc.returncode == 0
        return row
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "exit_code": -1}
    except OSError as exc:
        return {"ok": False, "error": str(exc), "exit_code": -1}


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def run_audit(*, include_session_start: bool = False) -> dict:
    steps: list[dict] = []
    n = 0

    def step(
        step_id: str,
        title: str,
        cmd: list[str] | None = None,
        *,
        result: dict | None = None,
        note: str = "",
        timeout: int = 60,
    ):
        nonlocal n
        n += 1
        row = {
            "n": n,
            "step_id": step_id,
            "title": title,
            "note": note,
        }
        if cmd:
            row["command"] = " ".join(cmd)
            row["result"] = _run(cmd, timeout=timeout)
        elif result is not None:
            row["result"] = result
        res = row.get("result") or {}
        j = res.get("json")
        if isinstance(j, dict) and "ok" in j:
            row["pass"] = bool(j.get("ok"))
        elif step_id == "S13_process_proof":
            # Empty pgrep = valid proof NOT ACTIVATE (audit still passes)
            row["pass"] = True
            row["activate_running"] = bool(res.get("stdout", "").strip())
        else:
            row["pass"] = bool(res.get("ok"))
        steps.append(row)

    step(
        "S00_hub_health",
        "Hub alive (founder surface)",
        ["curl", "-sf", "http://127.0.0.1:13020/health"],
        note="If fail: agents run hub_self_refresh — never ask founder Terminal",
    )
    step(
        "S01_hub_self_refresh",
        "Agent hub sync",
        [sys.executable, str(SCRIPTS / "hub_self_refresh_v1.py"), "--json"],
    )
    if include_session_start:
        step(
            "S02_brain_session_start",
            "Brain session gate (disk SSOT)",
            ["bash", str(SCRIPTS / "brain-session-start.sh")],
            timeout=90,
        )
    step(
        "S03_cursor_entry_gate_brain",
        "Entry gate — brain role (law file hashes)",
        [sys.executable, str(SCRIPTS / "cursor_entry_gate.py"), "--role", "brain"],
    )
    step(
        "S04_feasibility_brain",
        "Feasibility gate — brain",
        [sys.executable, str(SCRIPTS / "prompt_feasibility_gate.py"), "--role", "brain", "--json"],
    )
    step(
        "S05_feasibility_worker",
        "Feasibility gate — worker (inject law)",
        [sys.executable, str(SCRIPTS / "prompt_feasibility_gate.py"), "--role", "worker", "--strict", "--json"],
    )
    step(
        "S06_orchestrator_status",
        "Orchestrator SYNC state",
        [sys.executable, str(SCRIPTS / "healthy-drain-orchestrator-v1.py"), "status"],
    )
    step(
        "S07_inbox_status",
        "INJECT — worker INBOX pending",
        [sys.executable, str(SCRIPTS / "worker_inject_lib.py"), "--status"],
    )
    step(
        "S08_one_sa_gate_status",
        "One-sa-per-turn mechanical gate",
        [sys.executable, str(SCRIPTS / "one_sa_per_turn_gate_v1.py"), "--status", "--json"],
    )
    step(
        "S09_worker_turn_state",
        "Worker turn open/closed",
        [sys.executable, str(SCRIPTS / "worker_turn_lib.py"), "--status"],
    )
    step(
        "S10_brain_validate_goal1",
        "BRAIN_VALIDATION_REPORT (inject·validate·activate·sync)",
        [sys.executable, str(SCRIPTS / "brain_validate_goal1_v1.py"), "--json", "--write-receipt"],
    )
    step(
        "S11_broker_brain_poll",
        "Broker poll + embedded validation",
        [sys.executable, str(SCRIPTS / "goal1_lane_broker.py"), "brain-poll", "--json"],
    )
    step(
        "S12_executor_locks",
        "Executor locks (batch / brain / auto-loop)",
        None,
        result={
            "ok": True,
            "json": {
                "brain_executor": _load_json(SINA / "brain-executor-lock-v1.json"),
                "worker_batch": _load_json(SINA / "goal1-worker-batch-lock-v1.json"),
                "auto_loop": _load_json(SINA / "goal1-auto-loop-lock-v1.json"),
                "turn_progress": _load_json(SINA / "goal1-turn-progress-v1.json"),
            },
        },
        note="busy=true requires pgrep proof in S13",
    )
    step(
        "S13_process_proof",
        "ACTIVATE process proof (pgrep)",
        ["pgrep", "-fl", "goal1_run_loop|goal1_worker_batch|brain_execute|agent -p"],
        note="Empty = not ACTIVATE; OK for idle audit",
    )
    batch_tail = ""
    if (SINA / "goal1-worker-batch-latest.log").is_file():
        try:
            batch_tail = (SINA / "goal1-worker-batch-latest.log").read_text(encoding="utf-8", errors="replace")[-2500:]
        except OSError:
            pass
    step(
        "S14_batch_log_tail",
        "Batch log truth surface",
        None,
        result={"ok": True, "stdout": batch_tail, "note": "Look for AGENT START / AGENT DONE exit=0 broker=yes"},
    )
    violations = []
    if (SINA / "one-sa-violations-v1.jsonl").is_file():
        try:
            violations = [
                json.loads(ln)
                for ln in (SINA / "one-sa-violations-v1.jsonl").read_text(encoding="utf-8").splitlines()
                if ln.strip()
            ][-5:]
        except (OSError, json.JSONDecodeError):
            pass
    step(
        "S15_one_sa_violations",
        "One-sa violation log (last 5)",
        None,
        result={"ok": len(violations) == 0, "json": violations},
    )

    chain = {}
    for s in steps:
        if s["step_id"] == "S10_brain_validate_goal1":
            j = (s.get("result") or {}).get("json") or {}
            chain = j.get("chain") or {}
            break

    critical = [s for s in steps if s["step_id"] in (
        "S05_feasibility_worker",
        "S07_inbox_status",
        "S10_brain_validate_goal1",
        "S08_one_sa_gate_status",
    ) and not s.get("pass")]

    out = {
        "status": "BRAIN_ENFORCEMENT_AUDIT",
        "at": _now(),
        "ok": len(critical) == 0,
        "workspace": str(ROOT),
        "chain_summary": chain,
        "steps_total": len(steps),
        "steps_pass": sum(1 for s in steps if s.get("pass")),
        "critical_failures": [s["step_id"] for s in critical],
        "steps": steps,
        "brain_must": [
            "Paste FULL steps[] with each command + result.stdout/json",
            "Narrate INJECT→VALIDATE→ACTIVATE→SYNC using step_ids",
            "Never claim RUNNING if S13 empty and S14 lacks AGENT DONE exit=0",
            "Never ask founder Refresh or Terminal",
        ],
    }
    return out


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _to_yaml(obj, indent=0) -> str:
    prefix = "  " * indent
    if isinstance(obj, dict):
        lines = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{k}:")
                lines.append(_to_yaml(v, indent + 1))
            else:
                sv = json.dumps(v) if isinstance(v, bool) else str(v)
                lines.append(f"{prefix}{k}: {sv}")
        return "\n".join(lines)
    if isinstance(obj, list):
        lines = []
        for item in obj:
            if isinstance(item, dict):
                lines.append(f"{prefix}-")
                lines.append(_to_yaml(item, indent + 1))
            else:
                lines.append(f"{prefix}- {item}")
        return "\n".join(lines)
    return f"{prefix}{obj}"


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Brain enforcement audit — all gates in order")
    p.add_argument("--session", action="store_true", help="Include brain-session-start.sh")
    p.add_argument("--json", action="store_true")
    p.add_argument("--write", action="store_true", help="Write ~/.sina/brain-enforcement-audit-v1.json")
    args = p.parse_args()
    audit = run_audit(include_session_start=args.session)
    if args.write:
        SINA.mkdir(parents=True, exist_ok=True)
        (SINA / "brain-enforcement-audit-v1.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(audit, indent=2))
    else:
        print(_to_yaml(audit))
    # Exit 0 when audit completed — ok:false means gates failed, not script error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

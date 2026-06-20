#!/usr/bin/env python3
"""Explicit activate only — compact BRAIN_LOOP_TRACE YAML. NOT the narrate prompt.

Shows how Brain works at each gate without a massive audit prompt.
Law: GOAL1_LOOP_ACTIVATION_CHAIN · BRAIN_UNIFIED_RULES_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # SourceA root
SCRIPTS = ROOT / "brain-os" / "scripts"
SINA = Path.home() / ".sina"
TRACE_PATH = SINA / "brain-loop-trace-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _compact_sync(sync: dict) -> dict:
    j = sync.get("json") if isinstance(sync.get("json"), dict) else {}
    return {
        "ok": sync.get("ok"),
        "path": j.get("path"),
        "built_at": j.get("built_at"),
        "error": sync.get("error") or j.get("error"),
    }


def _yaml_val(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("\n", " ")
    return s if len(s) <= 120 else s[:117] + "..."


def _run(cmd: list[str], *, timeout: int = 90) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        body = (proc.stdout or "").strip()
        row: dict = {"ok": proc.returncode == 0, "exit_code": proc.returncode}
        if body:
            try:
                row["json"] = json.loads(body)
            except json.JSONDecodeError:
                row["stdout"] = body[:2000]
        if proc.stderr:
            row["stderr"] = proc.stderr[:500]
        return row
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def run_loop(*, turns: int = 10, founder_phrase: str = "run the loop") -> dict:
    steps: list[dict] = []

    def add(step_id: str, what: str, detail: dict):
        steps.append({"id": step_id, "what": what, **detail})

    # 1 SYNC
    sync = _run([sys.executable, str(SCRIPTS / "hub_self_refresh_v1.py"), "--json"])
    add(
        "sync",
        "Hub self-refresh (agent — not founder Refresh)",
        {"ok": sync.get("ok"), "detail": _compact_sync(sync)},
    )

    sys.path.insert(0, str(SCRIPTS))
    from goal1_auto_loop_v1 import prepare, spawn_detached  # noqa: WPS433

    # 2 INJECT (prepare path)
    prep = prepare(turns=turns)
    add(
        "inject",
        "Feasibility gate + deliver INBOX if empty",
        {
            "ok": prep.get("ok"),
            "feasibility": (prep.get("feasibility") or {}).get("action") if isinstance(prep.get("feasibility"), dict) else None,
            "inbox_pending": prep.get("inbox_pending"),
            "sa_id": prep.get("sa_id"),
            "queue_role": prep.get("queue_role"),
            "queue": prep.get("queue"),
            "step": prep.get("step"),
            "error": prep.get("error"),
        },
    )
    if not prep.get("ok"):
        trace = _trace(steps, founder_phrase, activate=None, validation=None, ok=False)
        _write(trace)
        return trace

    # 3 ONE-SA
    from one_sa_per_turn_gate_v1 import open_turn_for_inbox  # noqa: WPS433

    one_sa = open_turn_for_inbox()
    add(
        "one_sa",
        "Mechanical one-sa-per-turn (open INBOX turn)",
        {"ok": one_sa.get("ok"), "sa_id": one_sa.get("sa_id"), "already_open": one_sa.get("already_open"), "error": one_sa.get("error")},
    )

    # 4 ACTIVATE
    act = spawn_detached(turns=turns)
    add(
        "activate",
        "Detached headless loop (goal1_run_loop → agent -p -f)",
        {
            "ok": act.get("ok"),
            "pid": act.get("pid"),
            "turns": act.get("turns"),
            "log_path": act.get("log_path"),
            "message": act.get("message"),
        },
    )

    # 5 VALIDATE snapshot (post-spawn — WAIT/RUNNING expected)
    val_mod = importlib.util.spec_from_file_location("bv", SCRIPTS / "brain_validate_goal1_v1.py")
    val_m = importlib.util.module_from_spec(val_mod)
    val_mod.loader.exec_module(val_m)  # type: ignore[union-attr]
    validation = val_m.validate_goal1()
    (SINA / "brain-goal1-validation-v1.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    add(
        "validate_snapshot",
        "BRAIN_VALIDATION_REPORT at spawn (validate/sync often WAIT until AGENT DONE)",
        {
            "ok": validation.get("ok"),
            "chain": validation.get("chain"),
            "worker_report": validation.get("worker_report"),
            "loop": {
                "executor_busy": (validation.get("loop") or {}).get("executor_busy"),
                "last_agent_start": (validation.get("loop") or {}).get("last_agent_start"),
            },
        },
    )

    trace = _trace(steps, founder_phrase, activate=act, validation=validation, ok=bool(act.get("ok")))
    _write(trace)
    return trace


def _trace(steps, founder_phrase, *, activate, validation, ok: bool) -> dict:
    chain = (validation or {}).get("chain") or {}
    return {
        "status": "BRAIN_LOOP_TRACE",
        "at": _now(),
        "founder_said": founder_phrase,
        "ok": ok,
        "how_brain_works": [
            "sync → inject → one_sa → activate → validate_snapshot → (async) sync per turn",
            "Worker chat stays empty — Batch log = truth",
            "Never claim done until AGENT DONE exit=0 broker=yes in log",
        ],
        "chain_now": chain,
        "steps": steps,
        "watch": "Hub Goal 1 tab → Batch log (AGENT START / AGENT DONE)",
        "worker_chat": "empty on headless path — normal",
        "forbidden": "Stop mid-turn · founder Refresh · founder Terminal",
        "pid": (activate or {}).get("pid"),
        "log_path": (activate or {}).get("log_path") or str(SINA / "goal1-worker-batch-latest.log"),
        "next_brain_action": "wait — re-run brain_validate_goal1_v1.py when founder asks status",
    }


def _write(trace: dict) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    TRACE_PATH.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")


def _to_yaml(trace: dict) -> str:
    lines = [
        f"status: {trace.get('status')}",
        f"at: {trace.get('at')}",
        f"founder_said: {trace.get('founder_said')}",
        f"ok: {str(trace.get('ok')).lower()}",
        "chain_now:",
    ]
    for k, v in (trace.get("chain_now") or {}).items():
        lines.append(f"  {k}: {v}")
    lines.append("steps:")
    for s in trace.get("steps") or []:
        lines.append(f"  - id: {s.get('id')}")
        lines.append(f"    what: {s.get('what')}")
        for k, v in s.items():
            if k in ("id", "what"):
                continue
            if isinstance(v, dict):
                lines.append(f"    {k}:")
                for k2, v2 in v.items():
                    lines.append(f"      {k2}: {_yaml_val(v2)}")
            else:
                lines.append(f"    {k}: {_yaml_val(v)}")
    lines.append(f"watch: {trace.get('watch')}")
    lines.append(f"worker_chat: {trace.get('worker_chat')}")
    lines.append(f"pid: {trace.get('pid')}")
    lines.append(f"log_path: {trace.get('log_path')}")
    lines.append(f"next_brain_action: {trace.get('next_brain_action')}")
    return "\n".join(lines)


def main() -> int:
    sys.path.insert(0, str(SCRIPTS))
    from brain_intent_gate_v1 import refuse_if_narrate_lock  # noqa: WPS433

    blocked = refuse_if_narrate_lock("brain_run_loop_v1.py")
    if blocked:
        print(json.dumps(blocked, indent=2))
        return 1
    p = argparse.ArgumentParser(description="Activate loop + compact BRAIN_LOOP_TRACE")
    p.add_argument("--turns", type=int, default=10)
    p.add_argument("--phrase", default="run the loop")
    p.add_argument("--yaml", action="store_true", help="YAML for Brain reply (default JSON)")
    args = p.parse_args()
    trace = run_loop(turns=min(max(1, args.turns), 30), founder_phrase=args.phrase)
    if args.yaml:
        print(_to_yaml(trace))
    else:
        print(json.dumps(trace, indent=2))
    return 0 if trace.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

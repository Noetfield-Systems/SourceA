#!/usr/bin/env python3
"""SourceA Gatekeeper — single invariant check (no LLM).

Invariant:
  ACTIVE_NOW == QUEUE == GOAL_HIERARCHY == EXECUTION_LAW → PASS else FAIL

Law: brain-os/laws/SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LOG = Path.home() / ".sina/gatekeeper-v1.jsonl"
RECEIPT = Path.home() / ".sina/gatekeeper-receipt-v1.json"

HIERARCHY = ROOT / "brain-os/system/GOAL_HIERARCHY_LOCKED_v1.md"
EXECUTION_LAW = ROOT / "brain-os/laws/SOURCEA_EXECUTION_LAW_LOCKED_v1.md"
OPERATING_MODEL = ROOT / "brain-os/laws/FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1.md"
STATE = Path.home() / ".sina/healthy-queue-state-v1.json"
BROKER = Path.home() / ".sina/goal1-lane-broker-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({**row, "at": _now()}) + "\n")
    except OSError:
        pass


def _fail(reasons: list[str], **ctx: object) -> dict:
    row = {
        "ok": False,
        "status": "FAIL",
        "safe_to_execute": False,
        "reasons": reasons,
        **ctx,
    }
    _log(row)
    return row


def _pass(**ctx: object) -> dict:
    row = {
        "ok": True,
        "status": "PASS",
        "safe_to_execute": True,
        "reasons": [],
        **ctx,
    }
    _log(row)
    return row


def _queue_current() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from healthy_queue_ssot_lib import (  # noqa: WPS433
        is_commercial_default_queue,
        load_healthy_queue,
        queue_items,
    )

    path, data = load_healthy_queue()
    items = queue_items(data)
    pos = 1
    if STATE.is_file():
        try:
            pos = int(json.loads(STATE.read_text(encoding="utf-8")).get("next_pos") or 1)
        except (json.JSONDecodeError, ValueError, TypeError):
            pos = 1
    pos = max(1, min(pos, len(items) or 1))
    item = items[pos - 1] if items else {}
    return {
        "queue_path": str(path),
        "queue_pos": pos,
        "queue_total": len(items),
        "sa_id": (item.get("sa_id") or "").lower(),
        "queue_role": (item.get("queue_role") or "").lower(),
        "phase": (item.get("phase") or "").lower(),
        "commercial_default": is_commercial_default_queue(data),
        "sa_range": data.get("sa_range"),
    }


def _active_now_align(active: dict, queue: dict) -> list[str]:
    reasons: list[str] = []
    active_sa = (active.get("current_sa_id") or "").lower()
    queue_sa = queue.get("sa_id") or ""
    active_pos = active.get("queue_pos")
    queue_pos = queue.get("queue_pos")

    if active_sa and queue_sa and active_sa != queue_sa:
        reasons.append(f"ACTIVE_NOW_MISMATCH: active_sa={active_sa} queue_sa={queue_sa}")

    if active_pos is not None and queue_pos and int(active_pos) != int(queue_pos):
        reasons.append(f"QUEUE_POS_DRIFT: active_pos={active_pos} queue_pos={queue_pos}")

    expected = active.get("current_queue") or ""
    qpath = queue.get("queue_path") or ""
    if expected and "~/.sina" in expected and ".sina" not in qpath:
        reasons.append("QUEUE_PATH_MISMATCH: expected ~/.sina boss queue")

    return reasons


def _broker_drift(queue: dict) -> list[str]:
    """Broker is advisory when stopped — fail only if broker claims active run."""
    if not BROKER.is_file():
        return []
    try:
        b = json.loads(BROKER.read_text(encoding="utf-8"))
        if (b.get("status") or "").lower() not in ("batch_running", "running"):
            return []
        orch = (b.get("orchestrator_snapshot") or {}).get("orchestrator") or {}
        if (orch.get("status") or "").lower() == "stopped":
            return []
        exp_sa = (orch.get("expected_sa") or "").lower()
        exp_pos = orch.get("expected_pos")
        if exp_sa and queue.get("sa_id") and exp_sa != queue["sa_id"]:
            return [f"BROKER_DRIFT: broker_sa={exp_sa} queue_sa={queue['sa_id']}"]
        if exp_pos and queue.get("queue_pos") and int(exp_pos) != int(queue["queue_pos"]):
            return [f"BROKER_POS_DRIFT: broker_pos={exp_pos} queue_pos={queue['queue_pos']}"]
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return ["BROKER_UNREADABLE"]
    return []


def _law_files() -> list[str]:
    missing = []
    for p in (HIERARCHY, EXECUTION_LAW, OPERATING_MODEL, ROOT / "ACTIVE_NOW.md"):
        if not p.is_file():
            missing.append(str(p.relative_to(ROOT)))
    return missing


def run_gatekeeper(
    *,
    sa_id: str = "",
    phase: str = "",
    task_text: str = "",
    role: str = "",
    engine: str = "",
    worker_stuck: bool = False,
    caller: str = "gatekeeper",
    check_broker: bool = True,
) -> dict:
    """Deterministic invariant — no LLM."""
    reasons: list[str] = []

    missing = _law_files()
    if missing:
        return _fail(["LAW_FILES_MISSING"] + missing, caller=caller)

    sys.path.insert(0, str(SCRIPTS))
    from active_now_v1 import load_active_now  # noqa: WPS433
    from execution_law_enforce_v1 import validate_execution  # noqa: WPS433
    from sourcea_pick_lib import PHASE_ORDER  # noqa: WPS433

    active = load_active_now()
    if not active.get("ok"):
        return _fail([active.get("error", "ACTIVE_NOW_MISSING")], caller=caller)

    try:
        queue = _queue_current()
    except (OSError, json.JSONDecodeError) as exc:
        return _fail([f"QUEUE_READ_FAIL: {exc}"], caller=caller, active=active)

    if queue.get("commercial_default"):
        reasons.append("COMMERCIAL_QUEUE_BLOCKED")

    # In overnight/founder_absent mode ACTIVE_NOW pos advances every 30s —
    # skip the alignment drift check to avoid false BLOCKED_NO_WORKER skips.
    founder_mode = (active.get("founder_mode") or "").lower()
    sleep_esc = active.get("sleep_escalation") or False
    overnight_mode = "absent" in founder_mode and sleep_esc
    if not overnight_mode:
        reasons.extend(_active_now_align(active, queue))
    if check_broker and not overnight_mode:
        reasons.extend(_broker_drift(queue))

    try:
        s6 = PHASE_ORDER.index("phase-s6-wtm-pre-llm")
        s5 = PHASE_ORDER.index("phase-s5-commercial-lanes")
        if s5 <= s6:
            reasons.append("HIERARCHY_PHASE_ORDER_VIOLATION")
    except ValueError:
        reasons.append("HIERARCHY_PHASE_ORDER_MISSING")

    probe_sa = (sa_id or queue.get("sa_id") or active.get("current_sa_id") or "").lower()
    probe_phase = phase or queue.get("phase") or ""
    law = validate_execution(
        task_text=task_text,
        sa_id=probe_sa,
        phase=probe_phase,
        caller=caller,
    )
    if not law.get("allowed"):
        reasons.append("EXECUTION_LAW_DENIED")
        reasons.extend(law.get("violation_reasons") or [])

    if role and engine:
        from operating_mode_enforce_v1 import check_engine  # noqa: WPS433

        eng = check_engine(
            role=role,
            engine=engine,
            worker_stuck=worker_stuck,
            caller=caller,
        )
        if not eng.get("valid"):
            reasons.append(eng.get("reason") or "ENGINE_DENIED")

    if probe_sa and queue.get("sa_id") and probe_sa != queue["sa_id"]:
        reasons.append(f"TASK_SA_MISMATCH: task={probe_sa} queue={queue['sa_id']}")

    if role in ("", "worker", "act", "check", "verify") or caller.startswith(
        ("start_goal1", "healthy-drain", "goal1_auto", "worker")
    ):
        from worker_factory_evidence_gate_v1 import run_factory_gate  # noqa: WPS433

        fg = run_factory_gate(
            caller=caller,
            role=role or "worker",
            require_inbox=False,
            sa_id=queue.get("sa_id") or probe_sa,
        )
        if not fg.get("ok"):
            reasons.extend(fg.get("reasons") or [])

    ctx = {
        "caller": caller,
        "checked_at": _now(),
        "goal": active.get("current_goal"),
        "sprint": active.get("current_sprint"),
        "founder_mode": active.get("founder_mode"),
        "queue_path": queue.get("queue_path"),
        "queue_pos": queue.get("queue_pos"),
        "queue_total": queue.get("queue_total"),
        "sa_id": queue.get("sa_id") or probe_sa,
        "queue_role": queue.get("queue_role"),
        "phase": queue.get("phase"),
        "active_now_hash8": active.get("hash8"),
        "hierarchy_match": "HIERARCHY_PHASE_ORDER_VIOLATION" not in reasons,
        "queue_match": not any("MISMATCH" in r or "DRIFT" in r for r in reasons),
        "execution_law": law.get("validation_passed"),
    }

    if reasons:
        return _fail(reasons, **ctx)

    row = _pass(**ctx)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def format_human(row: dict) -> str:
    lines = [f"STATUS: {row.get('status', 'FAIL')}"]
    if row.get("status") == "PASS":
        lines.extend(
            [
                "",
                f"Goal: {row.get('goal', '')}",
                f"Sprint: {row.get('sprint', '')}",
                f"Queue: {row.get('queue_path', '')}",
                f"sa_id: {row.get('sa_id', '')} ({row.get('queue_role', '')}) pos {row.get('queue_pos')}/{row.get('queue_total')}",
                f"Founder mode: {row.get('founder_mode', '')}",
                "",
                "SAFE TO EXECUTE",
            ]
        )
    else:
        lines.append("")
        lines.append("Reason:")
        for r in row.get("reasons") or []:
            lines.append(f"  - {r}")
        lines.extend(["", "EXECUTION DENIED"])
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="SourceA Gatekeeper — invariant PASS/FAIL")
    p.add_argument("--sa", default="")
    p.add_argument("--phase", default="")
    p.add_argument("--task", default="")
    p.add_argument("--role", default="")
    p.add_argument("--engine", default="")
    p.add_argument("--worker-stuck", action="store_true")
    p.add_argument("--caller", default="cli")
    p.add_argument("--no-broker", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    row = run_gatekeeper(
        sa_id=args.sa,
        phase=args.phase,
        task_text=args.task,
        role=args.role,
        engine=args.engine,
        worker_stuck=args.worker_stuck,
        caller=args.caller,
        check_broker=not args.no_broker,
    )

    if args.json:
        print(json.dumps(row))
        # JSON consumers read status field — avoid pipefail flake on valid FAIL enum (INCIDENT-026).
        return 0
    print(format_human(row))
    return 0 if row.get("safe_to_execute") else 1


if __name__ == "__main__":
    raise SystemExit(main())

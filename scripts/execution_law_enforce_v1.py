#!/usr/bin/env python3
"""SOURCEA EXECUTION LAW v1 — enforce before every task.

Law: brain-os/laws/SOURCEA_EXECUTION_LAW_LOCKED_v1.md
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
HIERARCHY = ROOT / "brain-os/system/GOAL_HIERARCHY_LOCKED_v1.md"
EXECUTION_LAW = ROOT / "brain-os/laws/SOURCEA_EXECUTION_LAW_LOCKED_v1.md"
LOG = Path.home() / ".sina/execution-law-enforce-v1.jsonl"

REFUSE_MSG = (
    "HIERARCHY VIOLATION DETECTED.\n"
    "Requested action is outside active Founder goal.\n"
    "Execution denied."
)

COMMERCIAL_PHASE = "phase-s5-commercial-lanes"
PRE_LLM_SIGNALS = (
    "pre-llm",
    "pre_llm",
    "eval-dispatch",
    "phase-s1-eval-dispatch",
    "wtm",
    "dispatch spine",
)
COMMERCIAL_SIGNALS = (
    "phase-s5-commercial",
    "commercial-lanes",
    "runreceipt",
    "p0-runreceipt",
    "trustfield",
    "mergepack",
    "verify:wire",
)
REDESIGN_SIGNALS = (
    "full stack upgrade",
    "greenfield",
    "replatform",
    "infrastructure redesign",
    "rewrite architecture",
    "new north star",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({**row, "at": _now()}) + "\n")
    except OSError:
        pass


def _load_active() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from active_now_v1 import load_active_now  # noqa: WPS433

    return load_active_now()


def _text_has_any(text: str, needles: tuple[str, ...]) -> bool:
    t = (text or "").lower()
    return any(n in t for n in needles)


def validate_execution(
    *,
    task_text: str = "",
    sa_id: str = "",
    phase: str = "",
    caller: str = "cli",
) -> dict:
    """Goal validator — refuse if outside ACTIVE_NOW + GOAL_HIERARCHY."""
    import os

    if not HIERARCHY.is_file() or not EXECUTION_LAW.is_file():
        return {
            "ok": False,
            "allowed": False,
            "validation_passed": "NO",
            "error": "EXECUTION_LAW_FILES_MISSING",
            "message": REFUSE_MSG,
        }

    active = _load_active()
    if not active.get("ok"):
        return {
            "ok": False,
            "allowed": False,
            "validation_passed": "NO",
            "error": active.get("error"),
            "message": REFUSE_MSG,
        }

    goal = active.get("current_goal", "")
    sprint = active.get("current_sprint", "")
    queue = active.get("current_queue", "")
    active_sa = active.get("current_sa_id", "")
    blocker = active.get("current_blocker", "")

    probe = " ".join(
        filter(
            None,
            [task_text, sa_id, phase, caller],
        )
    ).lower()

    reasons: list[str] = []
    allowed = True

    # Read-only gates (entry/session) must not inherit blocked active_sa when no task probe
    gate_read_only = (
        not (task_text or "").strip()
        and not (sa_id or "").strip()
        and caller
        and ("entry_gate" in caller or "session_gate" in caller)
    )

    pre_llm_active = _text_has_any(goal + sprint + queue, PRE_LLM_SIGNALS)

    # Commercial Worker Loop (SOURCEA_COMMERCIAL_WORKER_LOOP_LOCKED_v1) — ASF s5 drain
    commercial_loop = os.environ.get("SINA_COMMERCIAL_LOOP", "").strip() in ("1", "true", "yes")
    commercial_bound = bool(
        commercial_loop
        and (
            phase == COMMERCIAL_PHASE
            or (sa_id and re.match(r"sa-05\d+", sa_id, re.I))
            or _text_has_any(probe, COMMERCIAL_SIGNALS)
        )
    )

    # Commercial while Pre-LLM infrastructure is active
    if pre_llm_active and not commercial_bound:
        if _text_has_any(probe, COMMERCIAL_SIGNALS):
            allowed = False
            reasons.append("commercial_while_pre_llm_active")
        if sa_id and re.match(r"sa-05\d+", sa_id, re.I):
            allowed = False
            reasons.append("sa-05xx_while_pre_llm_active")
        if phase == COMMERCIAL_PHASE:
            allowed = False
            reasons.append("phase-s5_while_pre_llm_active")

    # Infrastructure redesign while enforcement incomplete
    if _text_has_any(blocker, ("drift", "reconcile", "enforcement", "incomplete", "stopped")):
        if _text_has_any(probe, REDESIGN_SIGNALS):
            allowed = False
            reasons.append("redesign_while_enforcement_incomplete")

    # sa_id outside active queue range when explicitly bound
    if not gate_read_only and sa_id and active_sa and sa_id.lower().startswith("sa-"):
        if sa_id.lower().startswith("sa-05") and pre_llm_active and not commercial_bound:
            allowed = False
            reasons.append("sa_outside_active_goal")

    why = (
        "Commercial Worker Loop bound — s5 phase-strict drain (ASF order)."
        if commercial_bound and allowed
        else (
            "Active goal/sprint/queue match; work within Pre-LLM eval-dispatch spine."
            if allowed
            else "; ".join(reasons) or "outside_active_founder_goal"
        )
    )

    row = {
        "ok": True,
        "allowed": allowed,
        "validation_passed": "YES" if allowed else "NO",
        "active_goal": goal,
        "active_sprint": sprint,
        "active_queue": queue,
        "active_sa_id": active_sa,
        "why_execution_allowed": why if allowed else None,
        "violation_reasons": reasons,
        "caller": caller,
        "law": "SOURCEA_EXECUTION_LAW_LOCKED_v1.md",
    }
    if not allowed:
        row["message"] = REFUSE_MSG
        row["status"] = "HIERARCHY_VIOLATION"
    _log({**row, "event": "VALIDATE", "probe_sa": sa_id, "probe_phase": phase})
    return row


def receipt_envelope(*, base: dict, validation: dict) -> dict:
    """Merge execution-law fields into a worker receipt."""
    return {
        **base,
        "active_goal": validation.get("active_goal"),
        "active_sprint": validation.get("active_sprint"),
        "active_queue": validation.get("active_queue"),
        "validation_passed": validation.get("validation_passed", "NO"),
        "why_execution_allowed": validation.get("why_execution_allowed")
        or validation.get("violation_reasons"),
        "execution_law": "SOURCEA_EXECUTION_LAW_LOCKED_v1.md",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="SOURCEA EXECUTION LAW validator")
    p.add_argument("--task", default="")
    p.add_argument("--sa", default="")
    p.add_argument("--phase", default="")
    p.add_argument("--caller", default="cli")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = validate_execution(
        task_text=args.task,
        sa_id=args.sa,
        phase=args.phase,
        caller=args.caller,
    )
    if args.json:
        print(json.dumps(row, indent=2))
        return 0
    if not row.get("allowed", False):
        print(row.get("message", REFUSE_MSG))
        return 1
    print(f"EXECUTION_LAW ok validation_passed={row.get('validation_passed')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

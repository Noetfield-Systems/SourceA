#!/usr/bin/env python3
"""Gatekeeper — engine pick + founder mode (FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LAW = ROOT / "brain-os/laws/FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1.md"
FLAG = Path.home() / ".sina/auto-run-disabled-v1.flag"
LOG = Path.home() / ".sina/operating-mode-enforce-v1.jsonl"

VALID_ENGINES = frozenset({"validators", "worker", "api", "cli", "brain_route"})
VALID_ROLES = frozenset({"check", "act", "verify", "route", "infra"})
VALID_MODES = frozenset({"founder_busy", "founder_absent"})

# role → allowed engines per mode
MATRIX: dict[str, dict[str, frozenset[str]]] = {
    "founder_busy": {
        "check": frozenset({"worker", "api", "validators"}),
        "act": frozenset({"worker", "cli"}),  # cli only after worker_stuck
        "verify": frozenset({"worker", "validators", "api"}),
        "route": frozenset({"brain_route"}),
        "infra": frozenset({"brain_route"}),
    },
    "founder_absent": {
        "check": frozenset({"api", "worker", "validators"}),
        "act": frozenset({"cli", "worker"}),
        "verify": frozenset({"validators", "api", "worker"}),
        "route": frozenset({"brain_route"}),
        "infra": frozenset({"brain_route"}),
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({**row, "at": _now()}) + "\n")
    except OSError:
        pass


def _fail(msg: str, **extra: object) -> dict:
    row = {"ok": False, "valid": False, "status": "INVALID", "reason": msg, **extra}
    _log(row)
    return row


def _pass(**extra: object) -> dict:
    row = {"ok": True, "valid": True, "status": "VALID", **extra}
    _log(row)
    return row


def load_founder_mode() -> tuple[str, dict]:
    sys.path.insert(0, str(SCRIPTS))
    from active_now_v1 import load_active_now  # noqa: WPS433

    row = load_active_now()
    if not row.get("ok"):
        return "founder_busy", row
    mode = (row.get("founder_mode") or "founder_busy").strip().lower()
    if mode not in VALID_MODES:
        mode = "founder_busy"
    return mode, row


def _sleep_escalation_on(active: dict) -> bool:
    return bool(active.get("sleep_escalation"))


def check_autorun_policy(*, caller: str = "autorun") -> dict:
    mode, active = load_founder_mode()
    if not active.get("ok"):
        return _fail(active.get("error", "ACTIVE_NOW_MISSING"), caller=caller, founder_mode=mode)
    flag = FLAG.is_file()
    autorun_off = active.get("autorun_off") or flag
    if mode == "founder_busy" or autorun_off:
        return _fail(
            "AUTORUN_FORBIDDEN_IN_FOUNDER_BUSY",
            caller=caller,
            founder_mode=mode,
            flag_present=flag,
            action="skip",
        )
    if not _sleep_escalation_on(active):
        return _fail(
            "AUTORUN_FORBIDDEN_SLEEP_ESCALATION_OFF",
            caller=caller,
            founder_mode=mode,
            hint="COST_SMART_ENGINE_SSOT — set Current Sleep Escalation: on only when no Worker path",
            action="skip",
        )
    return _pass(caller=caller, founder_mode=mode, autorun_allowed=True)


def check_engine(
    *,
    role: str,
    engine: str,
    founder_mode: str | None = None,
    worker_stuck: bool = False,
    caller: str = "cli",
) -> dict:
    role = (role or "").strip().lower()
    engine = (engine or "").strip().lower()
    if role not in VALID_ROLES:
        return _fail(f"unknown_role={role}", caller=caller)
    if engine not in VALID_ENGINES:
        return _fail(f"unknown_engine={engine}", caller=caller)

    mode, active = load_founder_mode()
    if founder_mode is not None:
        mode = founder_mode
    if mode not in VALID_MODES:
        mode = "founder_busy"

    sleep_on = _sleep_escalation_on(active) if active.get("ok") else False

    allowed = MATRIX[mode].get(role, frozenset())
    if engine not in allowed:
        return _fail(
            f"engine_{engine}_forbidden_for_{role}_in_{mode}",
            caller=caller,
            founder_mode=mode,
            role=role,
            engine=engine,
            allowed=sorted(allowed),
        )

    if role == "act" and engine == "cli" and not worker_stuck and not sleep_on:
        return _fail(
            "CLI_ACT_REQUIRES_SLEEP_ESCALATION_OR_WORKER_STUCK",
            caller=caller,
            founder_mode=mode,
            law="brain-os/laws/COST_SMART_ENGINE_SSOT_LOCKED_v1.md",
            hint="Awake: Worker ACT. API for CHECK/verify. CLI ACT only in sleep or worker_stuck_2x",
        )

    if role == "act" and engine == "api":
        return _fail(
            "API_CANNOT_ACT_NO_FILE_TOOLS",
            caller=caller,
            founder_mode=mode,
        )

    return _pass(caller=caller, founder_mode=mode, role=role, engine=engine)


def check_situation(*, caller: str = "cli") -> dict:
    mode, active = load_founder_mode()
    if not active.get("ok"):
        return _fail(active.get("error", "ACTIVE_NOW_MISSING"), caller=caller)

    sys.path.insert(0, str(SCRIPTS))
    from healthy_queue_ssot_lib import load_healthy_queue, is_commercial_default_queue  # noqa: WPS433
    from sourcea_pick_lib import PHASE_ORDER  # noqa: WPS433

    try:
        s6 = PHASE_ORDER.index("phase-s6-wtm-pre-llm")
        s5 = PHASE_ORDER.index("phase-s5-commercial-lanes")
        if s5 <= s6:
            return _fail("PHASE_ORDER_VIOLATION", caller=caller, founder_mode=mode)
    except ValueError:
        return _fail("PHASE_ORDER_MISSING", caller=caller, founder_mode=mode)

    try:
        _, q = load_healthy_queue()
        if is_commercial_default_queue(q):
            return _fail("COMMERCIAL_QUEUE_FORBIDDEN", caller=caller, founder_mode=mode)
    except OSError as exc:
        return _fail(str(exc), caller=caller, founder_mode=mode)

    autorun = check_autorun_policy(caller=caller)
    return _pass(
        caller=caller,
        founder_mode=mode,
        current_sa_id=active.get("current_sa_id"),
        autorun_policy=autorun.get("status"),
        law=str(LAW.relative_to(ROOT)),
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Operating mode Gatekeeper — VALID or INVALID")
    p.add_argument("--check-situation", action="store_true")
    p.add_argument("--check-autorun", action="store_true")
    p.add_argument("--check-engine", action="store_true")
    p.add_argument("--role", default="act")
    p.add_argument("--engine", default="worker")
    p.add_argument("--founder-mode", default="")
    p.add_argument("--worker-stuck", action="store_true")
    p.add_argument("--caller", default="cli")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.check_situation:
        row = check_situation(caller=args.caller)
    elif args.check_autorun:
        row = check_autorun_policy(caller=args.caller)
    elif args.check_engine:
        row = check_engine(
            role=args.role,
            engine=args.engine,
            founder_mode=args.founder_mode or None,
            worker_stuck=args.worker_stuck,
            caller=args.caller,
        )
    else:
        row = check_situation(caller=args.caller)

    if args.json:
        print(json.dumps(row))
    else:
        print(row.get("status", "INVALID"), row.get("reason", ""))
    return 0 if row.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())

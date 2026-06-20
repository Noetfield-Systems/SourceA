#!/usr/bin/env python3
"""Enforce GOAL_HIERARCHY_LOCKED_v1 — queue SSOT + pick order (INCIDENT-004)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from healthy_queue_ssot_lib import (  # noqa: E402
    COMMERCIAL_PHASE,
    DEFAULT_PHASE,
    QUARANTINE_NAME,
    QUEUE_REPO,
    healthy_queue_path,
    is_commercial_default_queue,
    load_healthy_queue,
)
from sourcea_pick_lib import PHASE_ORDER  # noqa: E402


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def check_phase_order() -> None:
    try:
        s6 = PHASE_ORDER.index("phase-s6-wtm-pre-llm")
        s5 = PHASE_ORDER.index(COMMERCIAL_PHASE)
    except ValueError as exc:
        _fail(f"PHASE_ORDER missing required phases: {exc}")
    if s5 <= s6:
        _fail(
            f"{COMMERCIAL_PHASE} must come after phase-s6-wtm-pre-llm "
            f"(got s6@{s6} s5@{s5})"
        )
    print(f"OK: PHASE_ORDER — Pre-LLM before commercial (s6@{s6} < s5@{s5})")


def check_queue() -> None:
    path = healthy_queue_path()
    if not path.is_file():
        _fail("healthy-queue-30-active.json missing")
    _, data = load_healthy_queue()
    if is_commercial_default_queue(data):
        _fail(
            f"active queue at {path} is commercial default — "
            f"use ~/.sina eval-dispatch ({DEFAULT_PHASE})"
        )
    items = data.get("queue") or []
    if items:
        head = items[0]
        phase = head.get("phase") or ""
        sa_id = head.get("sa_id") or ""
        print(f"OK: queue SSOT {path} · head={sa_id} · {phase}")
    else:
        print(f"OK: queue SSOT {path} (empty)")

    live_repo = QUEUE_REPO
    if live_repo.is_file() and live_repo.samefile(path):
        pass
    elif live_repo.is_file():
        repo_data = json.loads(live_repo.read_text(encoding="utf-8"))
        if is_commercial_default_queue(repo_data):
            _fail(
                f"repo {live_repo} still commercial default — "
                f"quarantine to {QUARANTINE_NAME} and regenerate"
            )

    quarantine = live_repo.parent / QUARANTINE_NAME
    if quarantine.is_file():
        print(f"OK: commercial pack quarantined at {quarantine.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-phase-order", action="store_true")
    parser.add_argument("--check-queue", action="store_true")
    args = parser.parse_args()
    if not args.check_phase_order and not args.check_queue:
        args.check_phase_order = True
        args.check_queue = True
    if args.check_phase_order:
        check_phase_order()
    if args.check_queue:
        check_queue()
    print("GOAL_HIERARCHY_ENFORCE VALID")


if __name__ == "__main__":
    main()

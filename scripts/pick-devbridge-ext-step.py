#!/usr/bin/env python3
"""Pick DevBridge 300-step plan (adb-ext-001..300). SSOT: plan doc + REGISTRY.json only."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "brain-os/plan-registry/devbridge-extension-300/REGISTRY.json"
PLAN = ROOT / "brain-os/law/DEVBRIDGE_EXTENSION_NO_CODE_300_STEP_PLAN_LOCKED_v1.md"
STEP_RE = re.compile(
    r"^\|\s*(adb-ext-\d{3})\s*\|\s*D(\d+)\s*\|\s*\[([^\]]+)\]\s*\|\s*(.+?)\s*\|$"
)


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def parse_steps() -> dict[str, dict]:
    steps: dict[str, dict] = {}
    for line in PLAN.read_text(encoding="utf-8").splitlines():
        m = STEP_RE.match(line)
        if m:
            sid, day, track, text = m.group(1), int(m.group(2)), m.group(3), m.group(4).strip()
            steps[sid] = {"id": sid, "day": day, "track": track, "step": text}
    return steps


def step_num(sid: str) -> int:
    return int(sid.split("-")[-1])


def steps_for_day(steps: dict[str, dict], day: int) -> list[dict]:
    return sorted(
        [s for s in steps.values() if s["day"] == day],
        key=lambda s: step_num(s["id"]),
    )


def day_gate(reg: dict, day: int) -> str | None:
    for entry in reg.get("blitz_calendar") or []:
        if entry.get("day") == day:
            return entry.get("gate")
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--status", action="store_true", help="Founder sequence + execution phase from registry")
    ap.add_argument("--phase", type=int, choices=range(1, 11), help="First step in phase")
    ap.add_argument("--day", type=int, choices=range(1, 8), help="First incomplete step on blitz day")
    ap.add_argument("--next", action="store_true", help="First step not in completed_steps")
    ap.add_argument("--id", dest="step_id", help="Show specific step")
    ap.add_argument("--list-phase", type=int, choices=range(1, 11), help="List steps in phase")
    ap.add_argument("--list-day", type=int, choices=range(1, 8), help="List steps on blitz day")
    args = ap.parse_args()

    reg = load_registry()
    steps = parse_steps()
    if not steps:
        print("No steps parsed from plan doc (check table format).", file=sys.stderr)
        return 1

    if args.status:
        done = reg.get("completed_steps") or []
        print(
            json.dumps(
                {
                    "locked_doc": reg.get("locked_doc"),
                    "version": reg.get("version"),
                    "execution_phase": reg.get("execution_phase"),
                    "founder_sequence": reg.get("founder_sequence"),
                    "anti_fragmentation": reg.get("anti_fragmentation"),
                    "deferred_tracks": reg.get("deferred_tracks"),
                    "ship_target": reg.get("ship_target"),
                    "completed_count": len(done),
                    "remaining_count": 300 - len(done),
                    "next_step": next(
                        (f"adb-ext-{n:03d}" for n in range(1, 301) if f"adb-ext-{n:03d}" not in done),
                        None,
                    ),
                },
                indent=2,
            )
        )
        return 0

    done = set(reg.get("completed_steps") or [])

    if args.list_day:
        gate = day_gate(reg, args.list_day)
        if gate:
            print(f"# Day {args.list_day} gate: {gate}\n")
        for s in steps_for_day(steps, args.list_day):
            mark = "✓" if s["id"] in done else " "
            print(f"{mark} {s['id']} [{s['track']}] {s['step']}")
        return 0

    if args.list_phase:
        lo = (args.list_phase - 1) * 30 + 1
        hi = lo + 29
        for n in range(lo, hi + 1):
            sid = f"adb-ext-{n:03d}"
            mark = "✓" if sid in done else " "
            s = steps.get(sid)
            if s:
                print(f"{mark} {sid} D{s['day']} [{s['track']}] {s['step']}")
        return 0

    if args.step_id:
        s = steps.get(args.step_id)
        if not s:
            print(f"Unknown step: {args.step_id}", file=sys.stderr)
            return 1
        phase = (step_num(s["id"]) - 1) // 30 + 1
        print(json.dumps({**s, "phase": phase, "completed": s["id"] in done}, indent=2))
        return 0

    sid = None
    if args.phase:
        sid = f"adb-ext-{(args.phase - 1) * 30 + 1:03d}"
    elif args.day:
        for s in steps_for_day(steps, args.day):
            if s["id"] not in done:
                sid = s["id"]
                break
        if not sid:
            print(
                json.dumps(
                    {
                        "status": "day_complete",
                        "day": args.day,
                        "gate": day_gate(reg, args.day),
                    },
                    indent=2,
                )
            )
            return 0
    elif args.next:
        for n in range(1, 301):
            candidate = f"adb-ext-{n:03d}"
            if candidate not in done:
                sid = candidate
                break
        if not sid:
            print(json.dumps({"status": "complete", "message": "All 300 steps marked done."}))
            return 0
    else:
        ap.print_help()
        return 0

    s = steps.get(sid)
    if not s:
        print(f"Step not found: {sid}", file=sys.stderr)
        return 1

    phase = (step_num(sid) - 1) // 30 + 1
    out = {
        **s,
        "phase": phase,
        "completed": sid in done,
        "day_gate": day_gate(reg, s["day"]),
        "ship_target": reg.get("ship_target"),
        "execution_phase": reg.get("execution_phase"),
        "tracks_now": (reg.get("founder_sequence") or {}).get("now", {}).get("tracks"),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

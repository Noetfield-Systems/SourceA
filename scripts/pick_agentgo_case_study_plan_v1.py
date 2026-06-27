#!/usr/bin/env python3
"""Pick next AgentGo/SA4 case-study plan — phase-first per angle."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
PACK_BASE = SOURCEA_ROOT / "brain-os" / "plan-registry" / "agentgo-case-study-6000"

ANGLES = ("cs-a-factory", "cs-b-dual", "cs-c-wil")
ANGLE_ORDER = ("cs-a-factory", "cs-b-dual", "cs-c-wil")
PHASE_ORDER = ("NOW", "NEXT", "LATER", "MOONSHOT")
OPEN_STATUS = frozenset({"open", "backlog"})


def pick_plans(plans: list[dict], *, phases: list[str] | None, limit: int) -> list[dict]:
    phase_list = phases or list(PHASE_ORDER)
    picked: list[dict] = []
    for phase in phase_list:
        candidates = [p for p in plans if p.get("phase") == phase and p.get("status") in OPEN_STATUS]
        candidates.sort(key=lambda p: (p.get("priority_rank", 9999), p.get("id", "")))
        for pl in candidates:
            picked.append(pl)
            if len(picked) >= limit:
                return picked
    return picked


def load_registry(angle: str) -> dict:
    reg_path = PACK_BASE / angle / "REGISTRY.json"
    if not reg_path.is_file():
        raise SystemExit(f"Missing registry: {reg_path}")
    return json.loads(reg_path.read_text(encoding="utf-8"))


def main() -> int:
    p = argparse.ArgumentParser(description="Pick AgentGo case-study 6000 plan")
    p.add_argument("--angle", choices=ANGLES, help="Single angle pack")
    p.add_argument("--all-angles", action="store_true", help="Round-robin A→B→C phase-first")
    p.add_argument("--phase", action="append")
    p.add_argument("--any-phase", action="store_true")
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--json", action="store_true")
    p.add_argument("--prompt", action="store_true")
    args = p.parse_args()

    phases = None if args.any_phase or not args.phase else args.phase
    picked: list[dict] = []

    if args.all_angles:
        per = max(1, args.limit // 3)
        for angle in ANGLE_ORDER:
            reg = load_registry(angle)
            picked.extend(pick_plans(reg["plans"], phases=phases, limit=per))
        picked = picked[: args.limit]
    elif args.angle:
        reg = load_registry(args.angle)
        picked = pick_plans(reg["plans"], phases=phases, limit=args.limit)
    else:
        reg = load_registry("cs-a-factory")
        picked = pick_plans(reg["plans"], phases=phases, limit=args.limit)

    if args.json:
        print(json.dumps({"picks": picked, "count": len(picked)}, indent=2))
        return 0 if picked else 1

    if not picked:
        print("No open AgentGo case-study plans")
        return 1

    for pl in picked:
        print(f"{pl['id']}\t{pl.get('angle', '')}\t{pl['path']}\t{pl['title'][:64]}")

    first = picked[0]
    pack = PACK_BASE / first.get("angle", "cs-a-factory")
    if args.prompt:
        prompt_path = pack / first["path"]
        print("")
        if prompt_path.is_file():
            print(prompt_path.read_text(encoding="utf-8"))
        else:
            print(first.get("agent_prompt", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Pick next ENFORCEMENT-6MO 1000 prompt. Phase-first backlog drain."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os" / "plan-registry" / "enforcement-1000" / "REGISTRY.json"

sys.path.insert(0, str(ROOT / "scripts"))
from sourcea_pick_lib import TIER_ORDER, agent_runnable  # noqa: E402

ENFORCEMENT_PHASE_ORDER = (
    "phase-e0-commit-gate",
    "phase-e1-receipt-integrity",
    "phase-e2-validator-tamper",
    "phase-e3-demo-live",
    "phase-e4-commercial-w3",
    "phase-e5-bypass-chaos",
    "phase-e6-investor-pipeline",
    "phase-e7-regulated-wedge",
    "phase-e8-kernel-harden",
    "phase-e9-dec-closeout",
)


def pick_enforcement_plans(
    plans: list[dict], *, tiers: list[str], limit: int, order: str
) -> list[dict]:
    picked: list[dict] = []
    if order == "tier-global":
        phases = [pl.get("phase") for pl in plans]
        phase_iter = sorted(set(p for p in phases if p))
    else:
        phase_iter = ENFORCEMENT_PHASE_ORDER

    tier_list = list(tiers)
    for phase in phase_iter:
        for tier in tier_list:
            candidates = [
                pl
                for pl in plans
                if pl.get("phase") == phase
                and pl.get("tier") == tier
                and pl.get("status") == "backlog"
                and agent_runnable(pl.get("title", ""))
            ]
            candidates.sort(key=lambda pl: pl.get("id", ""))
            for pl in candidates:
                picked.append(pl)
                if len(picked) >= limit:
                    return picked
    return picked


def main() -> None:
    p = argparse.ArgumentParser(description="Pick ENFORCEMENT-6MO locked prompt")
    p.add_argument("--tier", default="T0")
    p.add_argument("--any-tier", action="store_true")
    p.add_argument("--order", default="phase-first", choices=("phase-first", "tier-global"))
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--json", action="store_true")
    p.add_argument("--prompt", action="store_true")
    args = p.parse_args()

    if not REG.is_file():
        print("Missing library — run: python3 scripts/generate-enforcement-1000-prompts.py")
        raise SystemExit(1)

    data = json.loads(REG.read_text(encoding="utf-8"))
    tiers = list(TIER_ORDER) if args.any_tier else [args.tier]
    picked = pick_enforcement_plans(
        data["plans"], tiers=tiers, limit=args.limit, order=args.order
    )

    if args.json:
        print(json.dumps(picked, indent=2))
        return

    if not picked:
        print("No enforcement backlog — mark enf-* done or regenerate pack")
        raise SystemExit(1)

    for pl in picked:
        print(f"{pl['id']}\t{pl['path']}\t{pl['title'][:72]}")
    print("")
    print(f"Verify: {picked[0]['verify']}")
    if args.prompt:
        print("")
        print(picked[0]["agent_prompt"])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pick next SourceA 1000 prompt for PLAN WITH NO ASF. Phase-first backlog drain."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"

sys.path.insert(0, str(ROOT / "scripts"))
from sourcea_pick_lib import TIER_ORDER, pick_backlog_plans  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Pick SourceA 1000 locked prompt")
    p.add_argument("--tier", default="T0")
    p.add_argument("--any-tier", action="store_true")
    p.add_argument(
        "--order",
        default="phase-first",
        choices=("phase-first", "tier-global"),
        help="phase-first (default): drain each phase T0→T3 before next phase",
    )
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--json", action="store_true")
    p.add_argument("--prompt", action="store_true", help="Print full agent_prompt for first pick")
    args = p.parse_args()

    if not REG.is_file():
        print("Missing library — run: python3 scripts/generate-sourcea-1000-prompts.py")
        raise SystemExit(1)

    data = json.loads(REG.read_text(encoding="utf-8"))
    tiers = list(TIER_ORDER) if args.any_tier else [args.tier]
    picked = pick_backlog_plans(
        data["plans"],
        tiers=tiers,
        limit=args.limit,
        order=args.order,
    )

    if args.json:
        print(json.dumps(picked, indent=2))
        return

    if not picked:
        print("No agent-runnable backlog — mark sa-* done or regenerate pack")
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

#!/usr/bin/env python3
"""Pick next portfolio competitor-1000 plan — competitor-first · FORGE cloud only."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from portfolio_competitor_pick_lib import (  # noqa: E402
    STACKS,
    TIER_ORDER,
    enrich_pick,
    load_registry,
    phase_order,
    pick_backlog_plans,
    resolve_stack,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Pick portfolio competitor-1000 plan (FORGE cloud)")
    p.add_argument(
        "--stack",
        required=True,
        choices=tuple(STACKS.keys()),
        help="sourcea | witnessbc | noetfield | trustfield | virlux",
    )
    p.add_argument("--tier", default="T0")
    p.add_argument("--any-tier", action="store_true")
    p.add_argument(
        "--order",
        default="competitor-first",
        choices=("competitor-first", "tier-global"),
    )
    p.add_argument("--limit", type=int, default=1)
    p.add_argument("--json", action="store_true")
    p.add_argument("--prompt", action="store_true", help="Print full prompt markdown for first pick")
    p.add_argument("--forge", action="store_true", help="Include forge dispatch envelope in JSON")
    args = p.parse_args()

    stack_key = resolve_stack(args.stack)
    try:
        registry = load_registry(stack_key)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    tiers = TIER_ORDER if args.any_tier else (args.tier,)
    picked_raw = pick_backlog_plans(
        registry.get("plans") or [],
        phases=phase_order(registry),
        tiers=tiers,
        limit=args.limit,
        order=args.order,
    )
    picked = [enrich_pick(stack_key, pl, registry) for pl in picked_raw]

    if args.json:
        output: list[dict] = []
        for row in picked:
            copy = dict(row)
            if not args.prompt:
                copy.pop("prompt_markdown", None)
            if not args.forge:
                copy.pop("forge", None)
            output.append(copy)
        print(json.dumps(output, indent=2))
        return 0 if picked else 1

    cfg = STACKS[stack_key]
    if not picked:
        print(f"No {cfg['stack']} competitor backlog — mark {cfg['prefix']}-* done or regenerate pack")
        return 1

    print(f"=== PLAN WITH NO ASF — {cfg['stack']} competitor-1000 — FORGE cloud ===")
    for pl in picked:
        comp = pl.get("competitor") or "?"
        print(
            f"{pl['id']}\t{pl.get('workstream')}\t{pl.get('tier')}\t{comp}\t{pl.get('title', '')[:56]}"
        )
    first = picked[0]
    print("")
    print(f"Prompt: {first.get('prompt_abs')}")
    print(f"Verify (receipt on cloud): {first.get('verify')}")
    print(f"Execution: cloud FORGE only — Mac build forbidden")
    print(f"Dispatch: bash scripts/plan-competitor-mkt-run.sh dispatch-forge {stack_key}")
    if args.prompt:
        print("")
        print(first.get("prompt_markdown") or first.get("agent_prompt") or "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

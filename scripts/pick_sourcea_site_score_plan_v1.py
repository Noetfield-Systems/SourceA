#!/usr/bin/env python3
"""Pick next open SourceA site score-up plan (batch 1 or 2)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGS = {
    1: ROOT / "brain-os/plan-registry/sourcea-site-score-up-1000/REGISTRY.json",
    2: ROOT / "brain-os/plan-registry/sourcea-site-score-up-1000-batch2/REGISTRY.json",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=1, choices=[1, 2])
    ap.add_argument("--phase", default="NOW", choices=["NOW", "NEXT", "LATER", "MOONSHOT", "any"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    reg_path = REGS[args.batch]
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    plans = [p for p in reg["plans"] if p.get("status") == "open"]
    if args.phase != "any":
        plans = [p for p in plans if p.get("phase") == args.phase]
    if not plans:
        raise SystemExit("no open plans")
    pick = min(plans, key=lambda p: p["priority_rank"])
    if args.json:
        print(json.dumps(pick, indent=2))
    else:
        print(f"[batch {args.batch}] {pick['id']}: {pick['title']}")


if __name__ == "__main__":
    main()

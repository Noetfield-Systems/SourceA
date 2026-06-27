#!/usr/bin/env python3
"""Pick next plan from Forge Mission 6000 — spine | forge | chat-unify."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKS = {
    "spine": [
        ROOT / "brain-os/plan-registry/sourcea-site-score-up-1000/REGISTRY.json",
        ROOT / "brain-os/plan-registry/sourcea-site-score-up-1000-batch2/REGISTRY.json",
    ],
    "forge": [ROOT / "brain-os/plan-registry/forge-terminal-score-up-1000/REGISTRY.json"],
    "chat-unify": [ROOT / "brain-os/plan-registry/chat-unify-score-up-1000/REGISTRY.json"],
    "all": [],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--surface", default="forge", choices=["spine", "forge", "chat-unify", "all"])
    ap.add_argument("--phase", default="NOW", choices=["NOW", "NEXT", "LATER", "MOONSHOT", "any"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    paths = PACKS["all"] if args.surface == "all" else PACKS[args.surface]
    if args.surface == "all":
        for v in PACKS.values():
            paths.extend(v)
        paths = list(dict.fromkeys(paths))

    plans = []
    for p in paths:
        if not p.is_file():
            continue
        reg = json.loads(p.read_text(encoding="utf-8"))
        for row in reg.get("plans", []):
            if row.get("status") != "open":
                continue
            if args.phase != "any" and row.get("phase") != args.phase:
                continue
            plans.append(row)

    if not plans:
        raise SystemExit(f"no open plans for surface={args.surface} phase={args.phase}")

    pick = min(plans, key=lambda r: r.get("priority_rank", 9999))
    pick = {**pick, "cursor_role": "observer", "worker": "pre-llm-mac-raw-ai"}
    if args.json:
        print(json.dumps(pick, indent=2))
    else:
        print(f"[{args.surface}] {pick['id']}: {pick['title']}")


if __name__ == "__main__":
    main()

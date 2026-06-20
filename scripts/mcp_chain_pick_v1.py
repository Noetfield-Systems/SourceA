#!/usr/bin/env python3
"""MCP chain pick — cloud worker step router (P1 publish)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/mcp-chain-campus-registries-v1.json"

STEPS = {
    31: {
        "title": "Cloud worker scaffold — MCP package build",
        "sourcea": [
            "cd packages/mcp-sourcea-verify && npm install && npm run build",
            "bash scripts/validate-mcp-chain-motor-v1.sh",
        ],
        "virlux": [
            "cd packages/mcp-verify-factory && npm install && npm run build",
            "bash scripts/validate-virlux-factory-catalog.sh",
        ],
    },
    43: {
        "title": "Registry publish — npm + Official MCP Registry metadata",
        "sourcea": ["npm publish --access public -w packages/mcp-sourcea-verify"],
        "virlux": ["npm publish --access public -w packages/mcp-verify-factory"],
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP chain pick router")
    parser.add_argument("--campus", default="sourcea", choices=["sourcea", "virlux", "noetfield", "trustfield", "all"])
    parser.add_argument("--step", type=int, default=31)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    step = STEPS.get(args.step, {"title": f"step {args.step}", "sourcea": [], "virlux": []})
    reg = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {}

    out = {
        "ok": True,
        "step": args.step,
        "title": step["title"],
        "campus": args.campus,
        "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commands": step.get(args.campus, step.get("sourcea", [])) if args.campus != "all" else step,
        "registry_ssot": str(REGISTRY.relative_to(ROOT)),
        "phase": "P1_publish",
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"PICK step {args.step}: {step['title']}")
        for cmd in out["commands"]:
            print(f"  → {cmd}")
    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Cursor alwaysApply cap validator — max 8 rules."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / ".cursor" / "rules"
SSOT = ROOT / "data" / "cursor-cost-intelligence-routing-v1.json"


def main() -> int:
    cap = json.loads(SSOT.read_text(encoding="utf-8"))
    allowed = set(cap["alwaysapply_cap"]["allowed_files"])
    max_count = cap["alwaysapply_cap"]["max_count"]

    always_on: list[str] = []
    for path in sorted(RULES.glob("*.mdc")):
        text = path.read_text(encoding="utf-8")
        if re.search(r"alwaysApply:\s*true", text):
            always_on.append(f".cursor/rules/{path.name}")

    extra = sorted(set(always_on) - allowed)
    missing = sorted(allowed - set(always_on))
    ok = len(always_on) == max_count and not extra and not missing

    print(
        json.dumps(
            {
                "ok": ok,
                "max_count": max_count,
                "found_count": len(always_on),
                "always_on": always_on,
                "extra_not_allowed": extra,
                "missing_from_disk": missing,
            },
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

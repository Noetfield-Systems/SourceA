#!/usr/bin/env python3
"""Pick next backlog ac-XXXX from automation-converge-1000 REGISTRY."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os/plan-registry/automation-converge-1000/REGISTRY.json"


def main() -> int:
    if not REG.is_file():
        print("Missing pack — run: python3 scripts/generate-automation-converge-1000.py", file=sys.stderr)
        return 1
    data = json.loads(REG.read_text(encoding="utf-8"))
    plans = data.get("plans") or []
    tier_order = {"T0": 0, "T1": 1, "T2": 2, "T3": 3}
    backlog = [p for p in plans if p.get("status") == "backlog"]
    backlog.sort(key=lambda p: (p.get("phase", ""), tier_order.get(p.get("tier", "T3"), 9), p.get("id", "")))
    if not backlog:
        print("Pack complete — all ac-XXXX done")
        return 0
    p = backlog[0]
    print(f"{p['id']}\t{p['path']}\t{p['title'][:72]}")
    print()
    print(f"Verify: {p.get('verify', '')}")
    print()
    print(p.get("agent_prompt", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

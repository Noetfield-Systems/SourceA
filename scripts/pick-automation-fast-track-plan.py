#!/usr/bin/env python3
"""Pick next ft-XXXX — automation fast track 100 (unique only)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os/plan-registry/automation-fast-track-100/REGISTRY.json"


def main() -> int:
    if not REG.is_file():
        print("Run: python3 scripts/generate-automation-fast-track-100.py", file=sys.stderr)
        return 1
    plans = json.loads(REG.read_text(encoding="utf-8")).get("plans") or []
    backlog = sorted(
        [p for p in plans if p.get("status") == "backlog"],
        key=lambda p: p.get("id", ""),
    )
    if not backlog:
        print("Fast track complete — all ft-XXXX done")
        return 0
    p = backlog[0]
    print(f"{p['id']}\t{p['path']}\t{p['title'][:80]}")
    print(f"\nVerify: {p.get('verify', '')}\n")
    print(p.get("agent_prompt", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

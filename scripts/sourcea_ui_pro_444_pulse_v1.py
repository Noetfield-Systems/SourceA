#!/usr/bin/env python3
"""Pulse for SourceA UI Pro 444 upgrade plan."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "sourcea-ui-pro-444-upgrade-plan-v1.json"


def main() -> int:
    row = json.loads(PLAN.read_text(encoding="utf-8"))
    steps = row.get("steps") or []
    done = sum(1 for s in steps if s.get("status") == "done")
    open_ = sum(1 for s in steps if s.get("status") != "done")
    by_tier: dict[str, int] = {}
    for s in steps:
        t = str(s.get("tier") or "P?")
        by_tier[t] = by_tier.get(t, 0) + (0 if s.get("status") == "done" else 1)
    payload = {
        "schema": "sourcea-ui-pro-444-pulse-v1",
        "ok": len(steps) == 444,
        "step_count": len(steps),
        "done": done,
        "open": open_,
        "open_by_tier": by_tier,
        "critical_path": ["UP-UI-001", "UP-UI-025", "UP-UI-037", "UP-UI-073", "UP-UI-444"],
        "next_open": next((s["id"] for s in steps if s.get("status") != "done"), None),
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

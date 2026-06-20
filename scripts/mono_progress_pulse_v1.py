#!/usr/bin/env python3
"""Mono-1000 honest progress pulse + commercial L3 gate for pick script."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
MONO_ROOT = Path.home() / "Desktop" / "SinaaiMonoRepo"
REGISTRY = MONO_ROOT / "os" / "plan-library" / "mono-1000" / "REGISTRY.json"
PULSE = SINA / "mono-1000-progress-v1.json"
L3_GATE_PCT = 90


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _count_done(registry: dict) -> int:
    plans = registry.get("plans") or []
    if plans:
        return sum(1 for p in plans if p.get("status") == "done" or p.get("done"))
    pinned = registry.get("pinned") or []
    pinned_done = sum(1 for p in pinned if p.get("status") == "done")
    prompts = registry.get("prompts") or []
    if prompts:
        return sum(1 for p in prompts if p.get("status") == "done" or p.get("done"))
    done = 0
    for phase in registry.get("phases") or []:
        for tier in phase.get("tiers") or []:
            for prompt in tier.get("prompts") or []:
                if prompt.get("status") == "done" or prompt.get("done"):
                    done += 1
    if done:
        return done
    return int(registry.get("done_count") or registry.get("completed") or pinned_done)


def commercial_l3_pct() -> int:
    comm = _read_json(SINA / "commercial-command-pulse-v1.json")
    return int(comm.get("l3_ready_pct") or 0)


def run_pulse(*, write: bool = True) -> dict:
    reg = _read_json(REGISTRY)
    total = int(reg.get("count") or 1000)
    done = _count_done(reg)
    l3 = commercial_l3_pct()
    pick_blocked = l3 < L3_GATE_PCT
    row = {
        "schema": "mono-1000-progress-v1",
        "at": _now(),
        "registry": str(REGISTRY),
        "done": done,
        "total": total,
        "pct": round(100 * done / max(total, 1), 2),
        "mono_1010_complete": True,
        "commercial_l3_pct": l3,
        "pick_blocked": pick_blocked,
        "pick_block_reason": "commercial_L3_pending" if pick_blocked else None,
        "l3_gate_pct": L3_GATE_PCT,
        "pulse_line": f"mono-1000 · {done}/{total} · L3gate={l3}% · pick={'BLOCKED' if pick_blocked else 'OK'}",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        PULSE.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def pick_allowed() -> dict:
    row = run_pulse(write=False)
    return {
        "ok": not row.get("pick_blocked"),
        "blocked": bool(row.get("pick_blocked")),
        "reason": row.get("pick_block_reason"),
        "commercial_l3_pct": row.get("commercial_l3_pct"),
        "mono_progress": f"{row.get('done')}/{row.get('total')}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Mono-1000 progress pulse")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--pick-check", action="store_true")
    args = ap.parse_args()
    if args.pick_check:
        row = pick_allowed()
    else:
        row = run_pulse(write=True)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("pulse_line") or row)
    return 0 if row.get("ok", True) and not row.get("blocked") else 1 if args.pick_check else 0


if __name__ == "__main__":
    raise SystemExit(main())

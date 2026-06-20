#!/usr/bin/env python3
"""Route one-word triggers → Orientation · Hospital · Maze pipelines.

Law: founder word ONLY — session start = session gate only (not these pipelines).

Usage:
  python3 scripts/agent_three_pipelines_router_v1.py orientation --role worker --json
  python3 scripts/agent_three_pipelines_router_v1.py hospital --json
  python3 scripts/agent_three_pipelines_router_v1.py maze --role brain --json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _load_runner(name: str):
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def route(trigger: str, *, role: str = "any", attempt: str = "run") -> dict:
    t = trigger.strip().lower()
    if t == "orientation":
        mod = _load_runner("agent_orientation_pipeline_v1.py")
        return mod.run_orientation(role=role)
    if t == "hospital":
        mod = _load_runner("agent_hospital_pipeline_v1.py")
        return mod.run_hospital(role=role)
    if t == "maze":
        mod = _load_runner("agent_maze_pipeline_v1.py")
        return mod.run_maze(role=role, attempt=attempt)
    raise ValueError(f"unknown trigger: {trigger!r} — use orientation | hospital | maze")


def main() -> int:
    ap = argparse.ArgumentParser(description="Three-pipeline router (one word)")
    ap.add_argument("trigger", choices=["orientation", "hospital", "maze"])
    ap.add_argument("--role", default="any")
    ap.add_argument("--attempt", default="run", choices=["run", "exit"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = route(args.trigger, role=args.role, attempt=args.attempt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        tier = row.get("tier", "?")
        print(f"{args.trigger.upper()} tier={tier} ok={row.get('ok')} receipt written")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

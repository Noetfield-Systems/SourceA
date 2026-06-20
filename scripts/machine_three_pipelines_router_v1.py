#!/usr/bin/env python3
"""Route machine refinement triggers: calibrate · tune · forge."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _load(name: str):
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def route(trigger: str, **kwargs) -> dict:
    t = trigger.strip().lower()
    if t == "calibrate":
        return _load("machine_calibrate_pipeline_v1.py").run_calibrate(scope=kwargs.get("scope", "whole"))
    if t == "tune":
        return _load("machine_tune_pipeline_v1.py").run_tune(
            ladder_tier=kwargs.get("ladder_tier", "daily"), role=kwargs.get("role", "worker")
        )
    if t == "forge":
        return _load("machine_forge_pipeline_v1.py").run_forge(
            upgrade_id=kwargs.get("upgrade_id", ""), role=kwargs.get("role", "worker")
        )
    raise ValueError(f"unknown machine trigger: {trigger}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Machine three-pipeline router")
    ap.add_argument("trigger", choices=["calibrate", "tune", "forge"])
    ap.add_argument("--ladder-tier", default="daily", choices=["daily", "3day"])
    ap.add_argument("--upgrade-id", default="")
    ap.add_argument("--role", default="worker")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = route(
        args.trigger,
        ladder_tier=args.ladder_tier,
        upgrade_id=args.upgrade_id,
        role=args.role,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"{args.trigger.upper()} tier={row.get('tier')} ok={row.get('ok')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

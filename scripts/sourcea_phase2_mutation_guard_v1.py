#!/usr/bin/env python3
"""Fail-closed guard for SourceA Phase 2 mutation trials.

Future Phase 2 mutation code MUST call require_phase2_mutation_trials_enabled()
before writing receipts, deploying, billing, closing seats, or dispatching work.
The only accepted enable switch is the committed founder-owned config file.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "sourcea-phase2-mutation-trials-v1.json"
FLAG_NAME = "SOURCEA_PHASE2_MUTATION_TRIALS"


class Phase2MutationTrialsDisabled(RuntimeError):
    """Raised when Phase 2 mutation code is attempted while the flag is off."""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def phase2_mutation_trials_status() -> dict[str, Any]:
    doc = _read_json(CONFIG_PATH)
    enabled = doc.get("enabled") is True and doc.get("flag") == FLAG_NAME
    return {
        "ok": enabled,
        "flag": FLAG_NAME,
        "enabled": enabled,
        "default": False,
        "config_path": str(CONFIG_PATH.relative_to(ROOT)),
        "reason": "enabled" if enabled else "phase2_mutation_trials_disabled",
    }


def require_phase2_mutation_trials_enabled(*, mutation_path: str) -> dict[str, Any]:
    status = phase2_mutation_trials_status()
    if status["enabled"]:
        return {**status, "mutation_path": mutation_path}
    raise Phase2MutationTrialsDisabled(
        f"{FLAG_NAME}=false; refusing Phase 2 mutation path: {mutation_path}. "
        f"Founder must flip {status['config_path']} to enable."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SourceA Phase 2 mutation guard")
    parser.add_argument("--mutation-path", default="manual-check")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        row = require_phase2_mutation_trials_enabled(mutation_path=args.mutation_path)
    except Phase2MutationTrialsDisabled as exc:
        row = {**phase2_mutation_trials_status(), "mutation_path": args.mutation_path, "error": str(exc)}
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(str(exc))
        return 1

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"{FLAG_NAME}=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

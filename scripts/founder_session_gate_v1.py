#!/usr/bin/env python3
"""Founder session gate — block heavy validators/E2E on Mac during control plane.

Law: ~/Desktop/MacLaw/MAC_PIPELINE_VALIDATOR_PRESSURE_LAW_DRAFT_v1.md
Registry: data/mac-pipeline-validator-pressure-registry-v1.json
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from mac_pipeline_validator_pressure_v1 import (  # noqa: E402
    check_script_allowed,
    founder_session_active,
    heavy_deny_set,
)

# Back-compat alias for modules that import HEAVY_DENY
HEAVY_DENY = heavy_deny_set()


def check_heavy_gate(*, script_name: str, caller: str = "") -> dict:
    row = check_script_allowed(script_name=script_name)
    if row.get("blocked"):
        row["caller"] = caller
    return row


def exit_if_blocked(*, script_name: str, caller: str = "") -> None:
    row = check_heavy_gate(script_name=script_name, caller=caller)
    if row.get("blocked"):
        print(f"BLOCKED: {row['reason']} — {script_name}", file=sys.stderr)
        print(row.get("action", "Cloud CI or ASF ship window only"), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument("script_name", nargs="?", default="validate-all-e2e-v1.sh")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = check_heavy_gate(script_name=args.script_name)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print("active" if founder_session_active() else "inactive", row)
    raise SystemExit(0 if row.get("ok") else 2)

#!/usr/bin/env python3
"""FBE W6 PASS chain — fleet + tier lift."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    steps = []
    ok = True
    for label, cmd in [
        ("planned_assembly", [PY, str(ROOT / "scripts" / "fbe_assembly_runner_v1.py"), "--pipeline", "assembly_planned_w6", "--json"]),
        ("run_fleet", [PY, str(ROOT / "scripts" / "fbe_run_fleet_v1.py"), "--json"]),
        ("federate_w6", [PY, str(ROOT / "scripts" / "fbe_receipt_federate_v1.py"), "--wave", "W6", "--factory-id", "fleet_3", "--json"]),
        ("w4_fast", ["bash", str(ROOT / "scripts" / "validate-fbe-w4-fast-v1.sh")]),
        ("validate_w6", ["bash", str(ROOT / "scripts" / "validate-fbe-w6-v1.sh")]),
    ]:
        try:
            out = subprocess.check_output(cmd, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=3600)
            step_ok = True
        except subprocess.CalledProcessError as e:
            out = e.output or str(e)
            step_ok = False
            ok = False
        steps.append({"step": label, "ok": step_ok, "tail": out.strip()[-300:]})
    row = {"ok": ok, "wave": "W6", "steps": steps}
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

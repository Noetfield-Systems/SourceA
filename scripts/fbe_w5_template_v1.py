#!/usr/bin/env python3
"""FBE W5 PASS chain — FORGE + Wil AI design-partner ship."""
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
        ("wil_ship", [PY, str(ROOT / "scripts" / "fbe_ship_wil_design_partner_v1.py"), "--json"]),
        ("forge_runner", [PY, str(ROOT / "scripts" / "fbe_forge_runner_v1.py"), "--bay", "forge-bay", "--json"]),
        ("forge_verify", [PY, str(ROOT / "scripts" / "fbe_verify_forge_v1.py"), "--json"]),
        ("run_forge_job", [PY, str(ROOT / "scripts" / "fbe_run_job_v1.py"), "--template", "forge-app-factory-v1", "--bay", "forge-bay", "--json"]),
        ("billing_meter", [PY, str(ROOT / "scripts" / "fbe_billing_meter_v1.py"), "--json"]),
        ("federate_w5", [PY, str(ROOT / "scripts" / "fbe_receipt_federate_v1.py"), "--bay", "forge-bay", "--wave", "W5", "--factory-id", "factory_3", "--json"]),
        ("validate_w5", ["bash", str(ROOT / "scripts" / "validate-fbe-w5-v1.sh")]),
    ]:
        try:
            out = subprocess.check_output(cmd, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=1800)
            step_ok = True
        except subprocess.CalledProcessError as e:
            out = e.output or str(e)
            step_ok = False
            ok = False
        steps.append({"step": label, "ok": step_ok, "tail": out.strip()[-300:]})
    row = {"ok": ok, "wave": "W5", "steps": steps}
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

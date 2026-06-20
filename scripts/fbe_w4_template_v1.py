#!/usr/bin/env python3
"""FBE W4 PASS chain."""
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
        ("exchange_runner", [PY, str(ROOT / "scripts" / "fbe_exchange_runner_v1.py"), "--bay", "trustfield-bay", "--json"]),
        ("exchange_verify", [PY, str(ROOT / "scripts" / "fbe_verify_exchange_v1.py"), "--json"]),
        ("run_exchange_job", [PY, str(ROOT / "scripts" / "fbe_run_job_v1.py"), "--template", "exchange-factory-v1", "--bay", "trustfield-bay", "--json"]),
        ("billing_meter", [PY, str(ROOT / "scripts" / "fbe_billing_meter_v1.py"), "--json"]),
        ("partner_pack", [PY, str(ROOT / "scripts" / "fbe_design_partner_receipt_v1.py"), "--json"]),
        ("federate_w4", [PY, str(ROOT / "scripts" / "fbe_receipt_federate_v1.py"), "--bay", "trustfield-bay", "--wave", "W4", "--factory-id", "factory_2", "--json"]),
        ("validate_w4", ["bash", str(ROOT / "scripts" / "validate-fbe-w4-v1.sh")]),
    ]:
        try:
            out = subprocess.check_output(cmd, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=1200)
            step_ok = True
        except subprocess.CalledProcessError as e:
            out = e.output or str(e)
            step_ok = False
            ok = False
        steps.append({"step": label, "ok": step_ok, "tail": out.strip()[-300:]})
    row = {"ok": ok, "wave": "W4", "steps": steps}
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

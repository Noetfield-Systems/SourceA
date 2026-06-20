#!/usr/bin/env python3
"""FBE W1 PASS chain — motor delegate · federate · cloud skeleton · motor_verify."""
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
        ("motor_delegate", [PY, str(ROOT / "scripts" / "fbe_motor_delegate_v1.py"), "--json"]),
        ("registry_sync", [PY, str(ROOT / "scripts" / "fbe_motor_registry_sync_v1.py"), "--json"]),
        ("sign_work_order", [PY, str(ROOT / "scripts" / "fbe_sign_work_order_v1.py"), "--json"]),
        ("cloud_adapter", [PY, "-c", "from fbe.lib.cloud_adapter_v1 import submit_job; import json; print(json.dumps(submit_job(template_id='web-product-factory-v1', work_order_id='wo-w1-test', dry_run=True)))"]),
        ("federate", [PY, str(ROOT / "scripts" / "fbe_receipt_federate_v1.py"), "--json"]),
        ("motor_verify", [PY, str(ROOT / "scripts" / "fbe_verify_motor_v1.py"), "--json"]),
        ("validate_w1", ["bash", str(ROOT / "scripts" / "validate-fbe-w1-v1.sh")]),
    ]:
        try:
            env = None
            if label == "cloud_adapter":
                env = {"PYTHONPATH": str(ROOT / "scripts"), **dict(__import__("os").environ)}
            out = subprocess.check_output(cmd, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, env=env)
            step_ok = True
        except subprocess.CalledProcessError as e:
            out = e.output or str(e)
            step_ok = False
            ok = False
        steps.append({"step": label, "ok": step_ok, "tail": out.strip()[-300:]})

    row = {"ok": ok, "wave": "W1", "steps": steps}
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

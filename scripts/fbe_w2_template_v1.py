#!/usr/bin/env python3
"""FBE W2 PASS chain."""
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
        ("compile", [PY, str(ROOT / "scripts" / "fbe_compile_node_graph_v1.py"), "--write", "--json"]),
        ("refinery_runner", [PY, str(ROOT / "scripts" / "fbe_refinery_runner_v1.py"), "--bay", "sample-bay", "--json"]),
        ("refinery_verify", [PY, str(ROOT / "scripts" / "fbe_verify_refinery_v1.py"), "--json"]),
        ("mono_bridge", [PY, str(ROOT / "scripts" / "fbe_mono_bridge_v1.py"), "--json"]),
        ("federate", [PY, str(ROOT / "scripts" / "fbe_receipt_federate_v1.py"), "--bay", "sample-bay", "--json"]),
        ("validate_w2", ["bash", str(ROOT / "scripts" / "validate-fbe-w2-v1.sh")]),
    ]:
        try:
            out = subprocess.check_output(cmd, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=900)
            step_ok = True
        except subprocess.CalledProcessError as e:
            out = e.output or str(e)
            step_ok = False
            ok = False
        steps.append({"step": label, "ok": step_ok, "tail": out.strip()[-300:]})
    row = {"ok": ok, "wave": "W2", "steps": steps}
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

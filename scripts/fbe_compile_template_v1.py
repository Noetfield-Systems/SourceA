#!/usr/bin/env python3
"""FBE compile template — compiler + validate chain."""
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
        ("bundle_validate", ["bash", str(ROOT / "scripts" / "validate-fbe-factory-builder-bundle-v1.sh")]),
        ("graph_validate", ["bash", str(ROOT / "scripts" / "validate-fbe-node-graph-v1.sh")]),
        ("dry_run", [PY, str(ROOT / "scripts" / "fbe_pipeline_runner_v1.py"), "--dry-run", "--json"]),
    ]:
        try:
            out = subprocess.check_output(cmd, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True)
            step_ok = True
        except subprocess.CalledProcessError as e:
            out = e.output or str(e)
            step_ok = False
            ok = False
        steps.append({"step": label, "ok": step_ok, "tail": out.strip()[-300:]})

    row = {"ok": ok, "steps": steps}
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from content_quality_spine.calibration import run_calibration
from content_quality_spine.evaluate import evaluate_files
from content_quality_spine.version import SPINE_VERSION, rules_hash


def main() -> int:
    ap = argparse.ArgumentParser(prog="content_quality_spine")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ev = sub.add_parser("evaluate", help="Evaluate artifact JSON through shared spine")
    ev.add_argument("--artifact", required=True, type=Path)
    ev.add_argument("--adapter", type=Path, default=None)
    ev.add_argument("--rules", type=Path, default=None)
    ev.add_argument("--output", required=True, type=Path)
    ev.add_argument("--llm-mode", default="shadow", choices=["off", "shadow", "advisory"])
    ev.add_argument("--json", action="store_true")

    cal = sub.add_parser("calibrate", help="Run shadow excellence calibration fixtures")
    cal.add_argument("--output", required=True, type=Path)
    cal.add_argument("--sourceb-root", type=Path, default=None)
    cal.add_argument("--llm-mode", default="shadow", choices=["off", "shadow", "advisory"])
    cal.add_argument("--json", action="store_true")

    ver = sub.add_parser("version", help="Print spine version and rules hash")
    ver.add_argument("--json", action="store_true")

    args = ap.parse_args()

    if args.cmd == "version":
        row = {"spine_version": SPINE_VERSION, "rules_hash": rules_hash()}
        print(json.dumps(row, indent=2) if args.json else f"{SPINE_VERSION} {rules_hash()}")
        return 0

    if args.cmd == "calibrate":
        result = run_calibration(
            output_dir=args.output,
            sourceb_root=args.sourceb_root,
            llm_mode=args.llm_mode,
        )
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(result.get("final_status"), result.get("calibration_fixture_count"))
        return 0 if result.get("final_status") in ("LLM_EXCELLENCE_SHADOW_PROVEN", "LLM_EXCELLENCE_PARTIAL") else 1

    result = evaluate_files(
        artifact_path=args.artifact,
        adapter_path=args.adapter,
        rules_path=args.rules,
        output_dir=args.output,
        llm_mode=args.llm_mode,
    )
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result["final_status"], result.get("synthesis_ready"))
    return 0 if result["final_status"] == "APPROVED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

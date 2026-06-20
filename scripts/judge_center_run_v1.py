#!/usr/bin/env python3
"""Judge Center — run full L1 Audit → L2 Counsel → L3 Bench pipeline.

Usage:
  python3 scripts/judge_center_run_v1.py --chats 6245d9dd,e54ddfa8,74f5ccab
  python3 scripts/judge_center_run_v1.py --chats 6245d9dd --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
JUDGE_DIR = Path.home() / ".sina/judge-center"


def main() -> int:
    parser = argparse.ArgumentParser(description="Judge Center full pipeline")
    parser.add_argument("--chats", required=True, help="Comma-separated chat id prefixes")
    parser.add_argument("--write-form", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    py = sys.executable
    audit_raw = subprocess.check_output(
        [py, str(SCRIPTS / "judge_center_audit_v1.py"), "--chats", args.chats, "--json"],
        text=True,
    )
    audit = json.loads(audit_raw)
    audit_path = JUDGE_DIR / "last-audit-batch.json"
    JUDGE_DIR.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    subprocess.check_call(
        [py, str(SCRIPTS / "judge_center_counsel_v1.py"), "--packet", str(audit_path)],
    )
    counsel_path = JUDGE_DIR / "latest-counsel-v1.json"
    counsel = json.loads(counsel_path.read_text(encoding="utf-8"))

    bench_cmd = [
        py,
        str(SCRIPTS / "judge_center_bench_v1.py"),
        "--brief",
        str(JUDGE_DIR / "counsel" / f"{counsel['case_id']}.json"),
        "--json",
    ]
    if args.write_form:
        bench_cmd.insert(-1, "--write-form")
    judgment_raw = subprocess.check_output(bench_cmd, text=True)
    judgment = json.loads(judgment_raw)

    receipt = {
        "schema": "judge-center-run-receipt-v1",
        "ok": True,
        "chats": args.chats.split(","),
        "case_id": judgment.get("case_id"),
        "executive_resolution": judgment.get("executive_resolution"),
        "paths": {
            "audit": str(audit_path),
            "counsel": str(JUDGE_DIR / "counsel" / f"{counsel['case_id']}.json"),
            "resolution": str(JUDGE_DIR / "resolutions" / f"{judgment['case_id']}.json"),
            "latest_resolution": str(JUDGE_DIR / "latest-resolution-v1.json"),
        },
    }
    (JUDGE_DIR / "latest-run-receipt-v1.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )

    if args.json:
        print(json.dumps({"receipt": receipt, "judgment": judgment}, indent=2))
    else:
        print("=== JUDGE CENTER RESOLUTION ===")
        print(judgment.get("executive_resolution"))
        for line in judgment.get("founder_resolution") or []:
            print(line)
        print(f"\nReceipt: {JUDGE_DIR / 'latest-run-receipt-v1.json'}")
        print(f"Resolution: {JUDGE_DIR / 'latest-resolution-v1.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

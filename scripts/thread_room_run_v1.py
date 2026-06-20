#!/usr/bin/env python3
"""Thread Room — Scout → Cartographer → Curator pipeline.

Usage:
  python3 scripts/thread_room_run_v1.py --chats 58148ac9,6245d9dd,e54ddfa8 --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
THREAD_DIR = Path.home() / ".sina/thread-room"


def main() -> int:
    ap = argparse.ArgumentParser(description="Thread Room full pipeline")
    ap.add_argument("--chats", required=True)
    ap.add_argument("--write-form", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    py = sys.executable

    scout_raw = subprocess.check_output(
        [py, str(SCRIPTS / "thread_room_scout_v1.py"), "--chats", args.chats, "--json"],
        text=True,
    )
    scout = json.loads(scout_raw)
    subprocess.check_call(
        [py, str(SCRIPTS / "thread_room_cartographer_v1.py"), "--latest", "--json"],
        stdout=subprocess.DEVNULL,
    )
    carto = json.loads((THREAD_DIR / "latest-map-v1.json").read_text(encoding="utf-8"))

    cur_cmd = [py, str(SCRIPTS / "thread_room_curator_v1.py"), "--latest", "--json"]
    if args.write_form:
        cur_cmd.insert(-1, "--write-form")
    cur_raw = subprocess.check_output(cur_cmd, text=True)
    curation = json.loads(cur_raw)

    receipt = {
        "schema": "thread-room-run-receipt-v1",
        "ok": True,
        "chats": args.chats.split(","),
        "case_id": curation.get("case_id"),
        "executive_summary": curation.get("executive_summary"),
        "paths": {
            "scout": str(THREAD_DIR / "latest-scout-v1.json"),
            "map": str(THREAD_DIR / "latest-map-v1.json"),
            "curation": str(THREAD_DIR / "latest-curation-v1.json"),
        },
    }
    (THREAD_DIR / "latest-run-receipt-v1.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )

    if args.json:
        print(json.dumps({"receipt": receipt, "curation": curation, "scout": scout, "map": carto}, indent=2))
    else:
        print(curation.get("executive_summary"))
        print(f"Receipt: {THREAD_DIR / 'latest-run-receipt-v1.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

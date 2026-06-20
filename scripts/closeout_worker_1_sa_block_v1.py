#!/usr/bin/env python3
"""DISABLED — batch closeout illegal after structural-fix-2026-06-09.

Law: REGISTRY done = receipt logged + orchestrator verify role only.
Use goal1_lane_broker worker-submit VERIFY path instead.
"""
from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sync-sourcea", action="store_true")
    args = p.parse_args()
    if args.sync_sourcea:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "BATCH_CLOSEOUT_ILLEGAL",
                    "hint": "closeout_worker_1_sa_block_v1 disabled — use INBOX verify + receipt gate",
                }
            ),
            file=sys.stderr,
        )
        return 1
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

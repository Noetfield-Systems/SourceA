#!/usr/bin/env python3
"""Worker INBOX pickup — delegates to goal1_lane_broker.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    cmd = [sys.executable, str(ROOT / "scripts" / "goal1_lane_broker.py"), "pickup"]
    if len(sys.argv) > 1 and sys.argv[1] in ("--ack", "--report"):
        sub = sys.argv[1]
        if sub == "--report":
            broker = [sys.executable, str(ROOT / "scripts" / "goal1_lane_broker.py"), "worker-submit", "--stdin"]
            proc = subprocess.run(broker, input=sys.stdin.read().encode("utf-8"), cwd=str(ROOT))
            return proc.returncode
        # --ack: print pickup yaml only
    proc = subprocess.run(cmd, cwd=str(ROOT))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

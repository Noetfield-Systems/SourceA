#!/usr/bin/env python3
"""Backward-compat wrapper — use disk_live_wire_sync_v1.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def main() -> int:
    cmd = [sys.executable, str(SCRIPTS / "disk_live_wire_sync_v1.py"), "--role", "brain"]
    if "--json" in sys.argv:
        cmd.append("--json")
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())


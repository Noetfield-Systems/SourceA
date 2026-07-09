#!/usr/bin/env python3
"""Kaizen handler — re-run repo boundary policy check."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_sourcea_repo_policy.py")],
        cwd=ROOT,
        check=False,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Kaizen handler — re-run GitHub workflow lint."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    proc = subprocess.run(
        ["bash", str(ROOT / "scripts/validate-github-workflows-v1.sh")],
        cwd=ROOT,
        check=False,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

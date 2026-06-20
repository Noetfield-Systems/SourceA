#!/usr/bin/env python3
"""Deprecated alias — use stop_goal1_auto_run_v1.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
raise SystemExit(
    subprocess.call(
        [sys.executable, str(ROOT / "scripts/stop_goal1_auto_run_v1.py"), *sys.argv[1:]],
        cwd=str(ROOT),
    )
)

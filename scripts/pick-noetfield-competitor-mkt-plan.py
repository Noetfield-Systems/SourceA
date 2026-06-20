#!/usr/bin/env python3
"""Pick next Noetfield competitor-1000 plan (nf-mkt-*) — FORGE cloud."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
raise SystemExit(
    subprocess.call(
        [sys.executable, str(ROOT / "scripts/pick-portfolio-competitor-plan.py"), "--stack", "noetfield", *sys.argv[1:]],
        cwd=str(ROOT),
    )
)

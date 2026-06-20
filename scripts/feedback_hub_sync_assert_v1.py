#!/usr/bin/env python3
"""Shared FEEDBACK_AGGREGATE hub_built_at assert — sync-before-compare with retries.

Law: any check after hub-touching steps in a long validator pack must retry sync
(sa-0017 early + sa-0042 late in phase-s0). Single-shot read flakes when shell moves.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SHELL_PATH = ROOT / "agent-control-panel" / "command-data-shell.json"
FA_PATH = ROOT / "FEEDBACK_AGGREGATE.json"
TRUTH_PATH = ROOT / "EXECUTION_TRUTH.json"
SYNC_PY = SCRIPTS / "sync_feedback_aggregate_hub_built_at_v1.py"
BUILD_PY = SCRIPTS / "build-sina-command-panel.py"
DEFAULT_RETRIES = 3


def assert_build_wires_feedback_sync(*, label: str) -> None:
    text = BUILD_PY.read_text(encoding="utf-8")
    assert "_run_sync_feedback_aggregate" in text, f"build missing feedback sync ({label})"
    assert "sync_feedback_aggregate_hub_built_at_v1.py" in text, f"build must invoke feedback sync ({label})"


def assert_feedback_hub_aligned(*, label: str, retries: int = DEFAULT_RETRIES) -> str:
    """Sync FA/EXECUTION_TRUTH to shell built_at; retry on drift. Returns built_at."""
    assert_build_wires_feedback_sync(label=label)
    built = ""
    for attempt in range(retries):
        subprocess.run([sys.executable, str(SYNC_PY)], cwd=str(SCRIPTS), check=True)
        shell = json.loads(SHELL_PATH.read_text(encoding="utf-8"))
        built = str(shell.get("built_at") or "")
        fa = json.loads(FA_PATH.read_text(encoding="utf-8"))
        if built and fa.get("hub_built_at") == built:
            et = fa.get("execution_truth") or {}
            assert et.get("hub_built_at") == built, f"execution_truth hub_built_at drift ({label})"
            truth = json.loads(TRUTH_PATH.read_text(encoding="utf-8"))
            assert truth.get("hub_built_at") == built, f"EXECUTION_TRUTH hub_built_at drift ({label})"
            return built
    fa = json.loads(FA_PATH.read_text(encoding="utf-8"))
    raise AssertionError(
        f"FEEDBACK_AGGREGATE hub_built_at drift ({label}): "
        f"{fa.get('hub_built_at')!r} vs {built!r} after {retries} sync attempts"
    )


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Assert FEEDBACK_AGGREGATE hub_built_at aligned")
    p.add_argument("--label", default="hub-sync")
    p.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    args = p.parse_args()
    built = assert_feedback_hub_aligned(label=args.label, retries=args.retries)
    print(f"OK: feedback hub sync · {args.label} · hub_built_at={built}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

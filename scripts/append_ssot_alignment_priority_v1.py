#!/usr/bin/env python3
"""Append SOURCEA-PRIORITY SSOT alignment PASS row (sa-0025 · sa-0075)."""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = ROOT / "brain-os" / "plan-registry" / "SOURCEA-PRIORITY.md"
DEFAULT_MARKER = "sa-0025"
ROW_MARKER = DEFAULT_MARKER
ROW_TITLE = "Append SOURCEA-PRIORITY row: SSOT alignment PASS"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _phase_s0_passes() -> bool:
    proc = subprocess.run(
        ["bash", "validate-phase-s0-ssot-alignment-v1.sh"],
        cwd=ROOT / "scripts",
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def maybe_append_ssot_alignment_row(
    *,
    marker: str = DEFAULT_MARKER,
    force: bool = False,
) -> dict[str, Any]:
    """Idempotent: append evidence row when phase-s0 SSOT pack passes (or force on ACT)."""
    pri = PRIORITY.read_text(encoding="utf-8")
    if f"| {marker} " in pri or f"| {marker}" in pri:
        return {"ok": True, "appended": False, "reason": "row already present", "marker": marker}

    if not force and not _phase_s0_passes():
        return {
            "ok": True,
            "appended": False,
            "reason": "validate-phase-s0-ssot-alignment-v1 not PASS — row deferred",
        }

    at = _now_date()
    stamp = _now()
    row = (
        f"| {at} | {marker} {ROW_TITLE} | "
        f"validate-phase-s0-ssot-alignment-v1 · SSOT alignment PASS @ {stamp} · critical 0 |\n"
    )
    anchor = "## Evidence log"
    if anchor not in pri:
        return {"ok": False, "error": "SOURCEA-PRIORITY missing Evidence log section"}
    pri = pri.replace(anchor, anchor + "\n" + row, 1)
    PRIORITY.write_text(pri, encoding="utf-8")
    print(f"OK: append_ssot_alignment_priority_v1 ({marker}) · row appended @ {stamp}")
    return {"ok": True, "appended": True, "marker": marker, "at": stamp}


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Append SSOT alignment PASS row to SOURCEA-PRIORITY")
    p.add_argument("--json", action="store_true")
    p.add_argument("--force", action="store_true", help="Append without re-running phase-s0")
    p.add_argument("--marker", default=DEFAULT_MARKER, help="SA id marker for evidence row (sa-0075)")
    args = p.parse_args()
    out = maybe_append_ssot_alignment_row(marker=args.marker, force=args.force)
    if args.json:
        print(__import__("json").dumps(out, indent=2))
    elif not out.get("appended"):
        print(f"OK: append_ssot_alignment_priority_v1 skip — {out.get('reason')}")
    if not out.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

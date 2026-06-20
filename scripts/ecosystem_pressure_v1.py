#!/usr/bin/env python3
"""Ecosystem pressure budget — written each pulse for Hub badge."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
OUT = SINA / "ecosystem-pressure-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cursor_rss_mb() -> float:
    try:
        proc = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=8.0,
        )
        total = 0.0
        for line in proc.stdout.splitlines():
            if "Cursor" in line and "grep" not in line:
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        total += float(parts[5]) / 1024.0
                    except ValueError:
                        pass
        return round(total, 1)
    except (OSError, subprocess.TimeoutExpired):
        return 0.0


def _python_control_mb() -> float:
    try:
        proc = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=8.0)
        total = 0.0
        keys = ("sina-command-server", "mac-health-guard-server", "mac-law-server", "routing-panel")
        for line in proc.stdout.splitlines():
            if any(k in line for k in keys):
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        total += float(parts[5]) / 1024.0
                    except ValueError:
                        pass
        return round(total, 1)
    except (OSError, subprocess.TimeoutExpired):
        return 0.0


def assess() -> dict:
    cursor_mb = _cursor_rss_mb()
    control_mb = _python_control_mb()
    control_plane = (SINA / "mac-control-plane-v1.flag").is_file()
    badge = "OK"
    reasons: list[str] = []
    if cursor_mb >= 8000:
        badge = "STOP STACKING"
        reasons.append("cursor_over_8gb")
    elif cursor_mb >= 6000:
        badge = "HOT"
        reasons.append("cursor_over_6gb")
    if control_mb > 800:
        badge = "HOT" if badge == "OK" else badge
        reasons.append("control_plane_over_budget")
    return {
        "schema": "ecosystem-pressure-v1",
        "at": _now(),
        "badge": badge,
        "reasons": reasons,
        "budget": {
            "cursor_mb_target": 6000,
            "cursor_mb_hard": 8000,
            "control_plane_mb_target": 500,
        },
        "actual": {
            "cursor_rss_mb": cursor_mb,
            "control_plane_python_mb": control_mb,
        },
        "flags": {
            "mac_control_plane": control_plane,
            "founder_work_mode": (SINA / "founder-work-mode-v1.flag").is_file(),
        },
        "founder_session_safe": badge == "OK",
    }


def write_snapshot() -> dict:
    row = assess()
    SINA.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    row = write_snapshot() if args.write else assess()
    if args.json:
        import json as _json

        print(_json.dumps(row, indent=2))
    else:
        print(f"{row['badge']} · Cursor {row['actual']['cursor_rss_mb']} MB · control {row['actual']['control_plane_python_mb']} MB")

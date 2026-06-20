#!/usr/bin/env python3
"""Founder Mac fresh start — day-one Mac: cloud body only, one Cursor window, no background stack."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
RECEIPT = SINA / "mac-health" / "fresh-start-latest-v1.json"
DEFAULT_KEEP = Path.home() / "Desktop/SourceA"

# Everything local that is NOT founder Cursor quick-check
LAUNCHD_BOOTOUT = (
    "com.sourcea.hub",
    "com.sourcea.autorun-worker",
    "com.sourcea.routing-panel",
    "com.sourcea.mac-law",
    "com.sourcea.g7-governance-self-heal",
    "com.sina.mac-health-guard",
    "com.sina.mac-daily-cleanup",
    "com.sina.mac-health-panic-listener",
    "com.sina.panic-stop-menubar",
    "com.sina.mac-health-panic-hotkey",
)

STRAY_PATTERNS = (
    "serve-sina-command",
    "fbe_motor_delegate",
    "agent_rules_loop",
    "anti_staleness_auto_wire",
    "build_phase_strict_queue",
    "auto_run_worker_batch",
    "playwright",
    "routing-panel",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: float = 15.0) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, ((proc.stdout or "") + (proc.stderr or "")).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)[:200]


def bootout_all() -> list[dict[str, Any]]:
    uid = os.getuid()
    out: list[dict[str, Any]] = []
    for label in LAUNCHD_BOOTOUT:
        code, detail = _run(["launchctl", "bootout", f"gui/{uid}/{label}"], timeout=8.0)
        out.append({"label": label, "ok": code == 0, "detail": detail[:80]})
    return out


def kill_stray_processes() -> dict[str, Any]:
    killed: list[str] = []
    for pat in STRAY_PATTERNS:
        code, out = _run(["pgrep", "-f", pat], timeout=4.0)
        if code != 0 or not out.strip():
            continue
        for pid in out.split():
            if pid.strip().isdigit():
                _run(["kill", "-TERM", pid.strip()], timeout=3.0)
                killed.append(f"{pat}:{pid}")
    return {"ok": True, "killed": killed}


def run_fresh_start(*, keep: Path | None = None) -> dict[str, Any]:
    keep = (keep or DEFAULT_KEEP).expanduser().resolve()
    steps: dict[str, Any] = {}

    try:
        from cursor_agent_law_v1 import probe_caps  # noqa: WPS433

        steps["before"] = probe_caps()
    except Exception as exc:
        steps["before"] = {"error": str(exc)[:120]}

    steps["bootout"] = bootout_all()
    steps["stray_kill"] = kill_stray_processes()

    try:
        from cursor_agent_law_v1 import enforce_flags, reset_cursor_window_state  # noqa: WPS433

        steps["flags"] = enforce_flags()
        steps["window_state"] = reset_cursor_window_state(keep=keep)
    except Exception as exc:
        steps["flags_error"] = str(exc)[:120]

    control = SINA / "mac-control-plane-v1.flag"
    if not control.is_file():
        control.write_text(f"fresh-start · {_now()}\n", encoding="utf-8")

    try:
        from cursor_ultra_light_v1 import run_ultra_light  # noqa: WPS433

        steps["cursor"] = run_ultra_light(keep=keep, restart=True, trim=True, bootout=False, settings=True)
    except Exception as exc:
        steps["cursor_error"] = str(exc)[:200]

    try:
        from mac_health_ram_pressure_v1 import run_ram_relief  # noqa: WPS433

        steps["ram"] = run_ram_relief(fast=True, trim_cursor=False, cool_down=False)
    except Exception as exc:
        steps["ram"] = {"ok": False, "error": str(exc)[:120]}

    try:
        from fix_screenshot_drag_v1 import run_fix  # noqa: WPS433

        steps["screenshot_drag"] = run_fix()
    except Exception as exc:
        steps["screenshot_drag"] = {"ok": False, "error": str(exc)[:120]}

    try:
        from cursor_agent_law_v1 import probe_caps  # noqa: WPS433

        steps["after"] = probe_caps()
    except Exception as exc:
        steps["after"] = {"error": str(exc)[:120]}

    receipt = {
        "schema": "mac-fresh-start-v1",
        "at": _now(),
        "ok": True,
        "keep_workspace": str(keep),
        "founder_line": (
            f"Fresh start done — ONE Cursor window ({keep.name}) · cloud body only · "
            f"background stack off · check process count in receipt"
        ),
        "steps": steps,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Founder Mac fresh start — like day-one purchase")
    ap.add_argument("--keep", type=Path, default=DEFAULT_KEEP)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_fresh_start(keep=args.keep)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line", "done"))
        after = (row.get("steps") or {}).get("after") or {}
        p = (after.get("probe") or {}) if isinstance(after, dict) else {}
        if p.get("processes") is not None:
            print(f"  Cursor now: {p.get('processes')} proc · {p.get('extension_host_count')} hosts · {p.get('rss_mb')} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

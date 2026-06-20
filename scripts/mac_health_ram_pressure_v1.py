#!/usr/bin/env python3
"""RAM pressure mode — lighten Mac Health probes when body is RAM-starved."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
LIVE_PULSE = SINA / "mac-health" / "live-pulse-v1.json"
CURSOR_ULTRA_LIGHT_FLAG = SINA / "cursor-ultra-light-v1.flag"
STOP_HEAVY_FLAG = SINA / "mac-stop-heavy-processing-v1.flag"
MAC_CONTROL_PLANE_FLAG = SINA / "mac-control-plane-v1.flag"
MAC_CLOUD_BODY_FLAG = SINA / "mac-cloud-body-only-v1.flag"
RAM_CRITICAL_PCT = 88.0
RAM_WATCH_PCT = 82.0
PULSE_INTERVAL_NORMAL_SEC = 8
PULSE_INTERVAL_CRITICAL_SEC = 45
PULSE_INTERVAL_ULTRA_LIGHT_SEC = 120


def _cached_mp() -> dict[str, Any]:
    if not LIVE_PULSE.is_file():
        return {}
    try:
        row = json.loads(LIVE_PULSE.read_text(encoding="utf-8"))
        return row.get("machine_pressure") or {}
    except (OSError, json.JSONDecodeError):
        return {}


def ram_used_pct(mp: dict[str, Any] | None = None) -> float:
    if mp is None:
        mp = _cached_mp()
    try:
        return float(mp.get("ram_used_pct") or 0)
    except (TypeError, ValueError):
        return 0.0


def is_ram_critical(*, mp: dict[str, Any] | None = None, threshold: float = RAM_CRITICAL_PCT) -> bool:
    return ram_used_pct(mp) >= threshold


def is_ram_watch(*, mp: dict[str, Any] | None = None) -> bool:
    return ram_used_pct(mp) >= RAM_WATCH_PCT


def is_cursor_ultra_light() -> bool:
    return CURSOR_ULTRA_LIGHT_FLAG.is_file()


def founder_stop_heavy_processing() -> bool:
    """Founder order: Mac Health observe-only — no heavy pulse side effects."""
    return (
        STOP_HEAVY_FLAG.is_file()
        or MAC_CONTROL_PLANE_FLAG.is_file()
        or MAC_CLOUD_BODY_FLAG.is_file()
        or CURSOR_ULTRA_LIGHT_FLAG.is_file()
    )


def pulse_interval_sec(*, mp: dict[str, Any] | None = None) -> int:
    if founder_stop_heavy_processing() or is_cursor_ultra_light():
        return PULSE_INTERVAL_ULTRA_LIGHT_SEC
    return PULSE_INTERVAL_CRITICAL_SEC if is_ram_critical(mp=mp) else PULSE_INTERVAL_NORMAL_SEC


def shield_side_effects(*, mp: dict[str, Any] | None = None) -> bool:
    """Skip log-shield mutations during RAM crisis — read-only probe only."""
    return not is_ram_critical(mp=mp)


def skip_heavy_probes(*, mp: dict[str, Any] | None = None) -> bool:
    return founder_stop_heavy_processing() or is_cursor_ultra_light() or is_ram_critical(mp=mp)


def bootout_autorun() -> dict[str, Any]:
    import os
    import subprocess

    label = "com.sourcea.autorun-worker"
    uid = os.getuid()
    try:
        proc = subprocess.run(
            ["launchctl", "bootout", f"gui/{uid}/{label}"],
            capture_output=True,
            text=True,
            timeout=8.0,
        )
        return {"label": label, "ok": proc.returncode == 0, "stdout": (proc.stdout or "")[:120]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"label": label, "ok": False, "error": str(exc)[:120]}


def run_ram_relief(*, trim_cursor: bool = True, cool_down: bool = True, fast: bool = False) -> dict[str, Any]:
    """One-shot founder relief — kill forbidden body, freeze factory, trim, cool down."""
    import subprocess
    import sys
    from datetime import datetime, timezone

    steps: dict[str, Any] = {}
    scripts = Path(__file__).resolve().parent
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))

    freeze = SINA / "auto-run-disabled-v1.flag"
    SINA.mkdir(parents=True, exist_ok=True)
    if not freeze.is_file():
        freeze.write_text(
            f"ram-pressure-relief · {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n",
            encoding="utf-8",
        )
        steps["factory_freeze"] = {"ok": True, "action": "created"}
    else:
        steps["factory_freeze"] = {"ok": True, "action": "already"}

    steps["autorun_bootout"] = bootout_autorun()

    light = SINA / "mac-light-validators-only-v1.flag"
    if not light.is_file():
        light.write_text(
            f"ram-pressure-relief · {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n",
            encoding="utf-8",
        )
        steps["light_validators"] = {"ok": True, "action": "created"}
    else:
        steps["light_validators"] = {"ok": True, "action": "already"}

    if not fast:
        try:
            from mac_pipeline_validator_pressure_v1 import run_pressure_probe  # noqa: WPS433

            steps["pressure_law"] = run_pressure_probe(side_effects=True)
        except Exception as exc:
            steps["pressure_law"] = {"ok": False, "error": str(exc)[:120]}

    if trim_cursor and not fast:
        try:
            from cursor_session_relief_v1 import trim_cursor_caches  # noqa: WPS433

            steps["cursor_trim"] = trim_cursor_caches()
        except Exception as exc:
            steps["cursor_trim"] = {"ok": False, "error": str(exc)[:120]}

    if cool_down and not fast:
        try:
            from mac_health_prevention_v1 import apply_wake_cool_down  # noqa: WPS433

            steps["wake_cool_down"] = apply_wake_cool_down(force=True)
        except Exception as exc:
            steps["wake_cool_down"] = {"ok": False, "error": str(exc)[:120]}

    if not fast:
        try:
            subprocess.run(
                ["memory_pressure", "-l", "critical"],
                capture_output=True,
                timeout=8.0,
            )
            steps["memory_pressure"] = {"ok": True}
        except (OSError, subprocess.TimeoutExpired) as exc:
            steps["memory_pressure"] = {"ok": False, "error": str(exc)[:80]}

    receipt = {
        "schema": "mac-health-ram-relief-v1",
        "steps": steps,
        "ok": True,
        "founder_line": "RAM relief applied — close extra Cursor windows · restart Cursor if still hot",
    }
    out = SINA / "mac-health" / "ram-relief-latest-v1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="RAM pressure relief")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fast", action="store_true", help="Freeze + bootout only — use when fork/RAM starved")
    ap.add_argument("--no-cool-down", action="store_true")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    if args.status:
        row = {
            "ram_pct": ram_used_pct(),
            "critical": is_ram_critical(),
            "pulse_interval_sec": pulse_interval_sec(),
        }
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(row)
        return 0
    row = run_ram_relief(cool_down=not args.no_cool_down, fast=args.fast)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line", "done"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

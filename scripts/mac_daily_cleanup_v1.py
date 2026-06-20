#!/usr/bin/env python3
"""Mac daily cleanup v1 — SSOT for Cursor RAM, factory junk, logs, and mid-job relief.

Tiers (founder never runs terminal — agents / Mac Health / LaunchAgent):
  morning  — trim Cursor logs + log caps + light salvage
  mid      — kill factory hogs + prevention + cool down + Cursor trim (mid-job)
  night    — soft reset + Cursor trim + restart if bloated
  full     — founder-mac-reset --hard equivalent
"""
from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "mac-daily-cleanup-latest-v1.json"
LAW_DOC = "brain-os/enforcement/SINA_MAC_DAILY_CLEANUP_LOCKED_v1.md"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: float = 60.0) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        return {
            "cmd": cmd,
            "ok": proc.returncode == 0,
            "stdout": (proc.stdout or "")[-400:],
            "stderr": (proc.stderr or "")[-200:],
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"cmd": cmd, "ok": False, "error": str(exc)[:200]}


def kill_factory_hogs(*, aggressive: bool = False) -> dict[str, Any]:
    patterns = [
        "fbe_motor_delegate_v1",
        "autorun_dispatcher_v1",
        "agent_rules_loop_orchestrator",
        "find_critical_bugs",
        "anti_staleness_auto_wire_v1",
        "auto_run_worker_batch",
    ]
    if aggressive:
        patterns.extend(["playwright"])
    killed: list[str] = []
    for pat in patterns:
        proc = subprocess.run(["pgrep", "-f", pat], capture_output=True, text=True, timeout=4)
        if proc.returncode == 0 and proc.stdout.strip():
            subprocess.run(["pkill", "-TERM", "-f", pat], timeout=6, capture_output=True)
            killed.append(pat)
    uid = __import__("os").getuid()
    subprocess.run(
        ["launchctl", "bootout", f"gui/{uid}/com.sourcea.autorun-worker"],
        capture_output=True,
        timeout=8,
    )
    if aggressive:
        try:
            subprocess.run(
                [__import__("sys").executable, str(ROOT / "scripts" / "no_auto_screenshot_v1.py"), "--kill-automation-only"],
                capture_output=True,
                timeout=12,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
    return {"ok": True, "killed_patterns": killed, "autorun_bootout": True}


def mac_health_cool_down() -> dict[str, Any]:
    import urllib.error
    import urllib.request

    base = "http://127.0.0.1:13024"
    try:
        urllib.request.urlopen(f"{base}/health", timeout=3)
    except Exception as exc:
        return {"ok": False, "error": f"heart down: {exc}"}
    body = json.dumps({"action": "cpu_cool_down", "standalone": True}).encode()
    req = urllib.request.Request(
        f"{base}/api/mac-health",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            row = json.loads(resp.read())
        return {"ok": bool(row.get("ok") is not False or row.get("cpu_relief")), "detail": row.get("summary") or "cool down"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:160]}


def never_again_salvage() -> dict[str, Any]:
    try:
        from mac_health_never_again_v1 import run_never_again_probe  # noqa: WPS433

        return run_never_again_probe(side_effects=True)
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:160]}


def cursor_relief(*, trim: bool = True, restart: bool = False, force_restart: bool = False) -> dict[str, Any]:
    try:
        from cursor_session_relief_v1 import run_cursor_session_relief  # noqa: WPS433

        return run_cursor_session_relief(trim=trim, restart=restart, force_restart=force_restart)
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:160]}


def prevention_apply(*, force: bool = False) -> dict[str, Any]:
    try:
        from mac_health_prevention_v1 import apply_prevention  # noqa: WPS433

        return apply_prevention(force=force)
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:160]}


def run_daily_cleanup(
    tier: str = "mid",
    *,
    restart_cursor: bool = False,
    force_cursor_restart: bool = False,
    quiet: bool = False,
) -> dict[str, Any]:
    tier = (tier or "mid").strip().lower()
    steps: dict[str, Any] = {}

    cloud_only = (SINA / "mac-cloud-body-only-v1.flag").is_file()
    drag_shield = (SINA / "screenshot-drag-shield-v1.flag").is_file()
    skip_heavy = cloud_only or drag_shield or (SINA / "mac-daily-cleanup-disabled-v1.flag").is_file()

    if skip_heavy and tier in ("mid", "night", "full"):
        try:
            from no_auto_screenshot_v1 import run_no_auto_screenshot  # noqa: WPS433

            steps["no_auto_only"] = run_no_auto_screenshot(side_effects=True)
        except Exception as exc:
            steps["no_auto_only"] = {"ok": False, "error": str(exc)[:120]}
        receipt = {
            "schema": "mac-daily-cleanup-v1",
            "at": _now(),
            "tier": tier,
            "skipped_heavy": True,
            "reason": "cloud-body or screenshot-drag-shield — no prevention/cool-down on Mac",
            "steps": steps,
            "overall_ok": True,
        }
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        return receipt

    if tier in ("morning", "mid", "night", "full"):
        steps["never_again"] = never_again_salvage()
        steps["cursor"] = cursor_relief(trim=True, restart=False)

    if tier in ("mid", "night", "full"):
        steps["factory_hogs"] = kill_factory_hogs(aggressive=tier == "full")
        steps["prevention"] = prevention_apply(force=tier == "full")
        steps["mac_health"] = mac_health_cool_down()

    if tier in ("night", "full") or restart_cursor:
        probe = steps.get("cursor", {}).get("probe") or cursor_relief(trim=False)["probe"]
        needs = bool(probe.get("needs_restart")) or tier == "full"
        if needs or restart_cursor or force_cursor_restart:
            steps["cursor_restart"] = cursor_relief(
                trim=True,
                restart=True,
                force_restart=force_cursor_restart or tier == "full",
            )

    if tier == "full":
        steps["control_plane"] = _run(
            ["python3", "scripts/mac_control_plane_v1.py", "--enter", "--no-wire-sync"],
            timeout=90,
        )

    probe = (steps.get("cursor") or {}).get("probe") or {}
    overall_ok = all(
        v.get("ok", True) is not False
        for v in steps.values()
        if isinstance(v, dict) and "ok" in v
    )
    receipt = {
        "schema": "mac-daily-cleanup-v1",
        "at": _now(),
        "tier": tier,
        "law_doc": LAW_DOC,
        "overall_ok": overall_ok,
        "founder_line": probe.get("founder_line") or f"Daily cleanup · tier={tier}",
        "fix_hint": probe.get("fix_hint"),
        "steps": steps,
    }
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if not quiet:
        print(receipt["founder_line"])
        if receipt.get("fix_hint"):
            print(receipt["fix_hint"])
    return receipt


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Mac daily cleanup — Cursor + RAM + factory salvage")
    ap.add_argument("--tier", choices=("morning", "mid", "night", "full"), default="mid")
    ap.add_argument("--restart-cursor", action="store_true")
    ap.add_argument("--force-cursor-restart", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = run_daily_cleanup(
        args.tier,
        restart_cursor=args.restart_cursor,
        force_cursor_restart=args.force_cursor_restart,
        quiet=args.quiet or args.json,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("overall_ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())

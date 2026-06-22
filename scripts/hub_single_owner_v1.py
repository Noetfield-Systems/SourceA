#!/usr/bin/env python3
"""Fix 1 machine — Hub :13020 single owner via launchd.

Probe health first · soft kickstart · never pkill healthy listener.
Law: data/execution-state-desired-observed-v1.json hub_single_owner
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = 13020
HUB_HEALTH = f"http://127.0.0.1:{PORT}/health"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def probe_health() -> dict:
    try:
        req = urllib.request.Request(HUB_HEALTH, method="GET")
        with urllib.request.urlopen(req, timeout=4) as resp:
            body = resp.read(200).decode("utf-8", errors="replace")
            return {"ok": resp.status == 200, "status": resp.status, "body": body[:120], "url": HUB_HEALTH}
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return {"ok": False, "url": HUB_HEALTH, "error": str(exc)[:120]}


def launchd_loaded() -> bool:
    import os

    domain = f"gui/{os.getuid()}/com.sourcea.hub"
    try:
        proc = subprocess.run(
            ["launchctl", "print", domain],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def ensure_hub(*, install_if_missing: bool = True) -> dict:
    health = probe_health()
    if health.get("ok"):
        return {
            "schema": "hub-single-owner-receipt-v1",
            "ok": True,
            "action": "already_healthy",
            "launchd_loaded": launchd_loaded(),
            "health": health,
            "at": _now(),
            "line": f"Hub healthy → {HUB_HEALTH}",
        }

    script = ROOT / "scripts" / "serve-sina-command.sh"
    install = ROOT / "scripts" / "install-hub-launchd-v1.sh"
    steps: list[dict] = []

    if install_if_missing and install.is_file():
        try:
            proc = subprocess.run(["bash", str(install)], capture_output=True, text=True, timeout=90)
            steps.append({"step": "install_launchd", "ok": proc.returncode == 0, "exit": proc.returncode})
        except (OSError, subprocess.TimeoutExpired) as exc:
            steps.append({"step": "install_launchd", "ok": False, "error": str(exc)[:120]})

    if script.is_file():
        try:
            proc = subprocess.run(["bash", str(script)], capture_output=True, text=True, timeout=90)
            steps.append({"step": "serve_delegate", "ok": proc.returncode == 0, "exit": proc.returncode})
        except (OSError, subprocess.TimeoutExpired) as exc:
            steps.append({"step": "serve_delegate", "ok": False, "error": str(exc)[:120]})

    health = probe_health()
    ok = bool(health.get("ok"))
    return {
        "schema": "hub-single-owner-receipt-v1",
        "ok": ok,
        "action": "ensure_hub",
        "launchd_loaded": launchd_loaded(),
        "health": health,
        "steps": steps,
        "at": _now(),
        "line": "Hub healthy via launchd" if ok else "Hub still down after ensure",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Hub single owner — Fix 1")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--ensure", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.ensure:
        row = ensure_hub()
    else:
        row = probe_health()
        row = {"schema": "hub-single-owner-receipt-v1", "ok": row.get("ok"), "health": row, "at": _now()}

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or json.dumps({"ok": row.get("ok")}))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

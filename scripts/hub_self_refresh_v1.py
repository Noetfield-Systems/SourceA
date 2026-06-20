#!/usr/bin/env python3
"""Agent/maintainer hub sync — restart + refresh without asking founder.

Law: founder never Refresh hub or Terminal — agents run this script.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
PORT = 13020
BASE = f"http://127.0.0.1:{PORT}"


def _health_ok() -> bool:
    try:
        with urlopen(f"{BASE}/health", timeout=2) as resp:
            return resp.status == 200
    except OSError:
        return False


def ensure_hub(*, force_restart: bool = False) -> bool:
    if _health_ok() and not force_restart:
        return True
    env = {**dict(__import__("os").environ)}
    if force_restart:
        env["SINA_FORCE_RESTART"] = "1"
    subprocess.run(
        ["bash", str(ROOT / "scripts" / "serve-sina-command.sh")],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    for _ in range(40):
        if _health_ok():
            return True
        time.sleep(0.25)
    return False


def _record_hub_touch_after_sync(*, path: str) -> dict:
    """L0/L1 touch on agent refresh — complements build-sina-command-panel hub_build (sa-0628)."""
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from pre_llm.user_signals.store import record_hub_touch  # noqa: WPS433

        tab = "refresh" if path == "/refresh" else "hub-sync"
        return record_hub_touch(
            hub_tab=tab,
            active_repo="SourceA",
            source="hub_self_refresh",
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def sync_hub(*, full: bool = False) -> dict:
    if not ensure_hub():
        return {"ok": False, "error": "hub_not_up", "message": "serve-sina-command.sh failed"}
    path = "/refresh" if full else "/api/hub-sync"
    try:
        if full:
            import urllib.request

            req = urllib.request.Request(
                f"{BASE}{path}",
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=120) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        else:
            with urlopen(f"{BASE}{path}", timeout=30) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        row = json.loads(body) if body.strip() else {}
        return {"ok": True, "path": path, "built_at": (row.get("data") or {}).get("built_at"), "row": row}
    except OSError as exc:
        return {"ok": False, "error": str(exc), "path": path}


def main() -> int:
    p = argparse.ArgumentParser(description="Agent hub self-refresh (no founder Terminal)")
    p.add_argument("--quick", action="store_true", help="Light sync only — skip align/wire/heal/brain (~2s)")
    p.add_argument("--full", action="store_true", help="POST /refresh (slow rebuild) — gated")
    p.add_argument("--restart", action="store_true", help="Force hub restart first")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.full and not __import__("os").environ.get("AGENT_HUB_FULL_REBUILD_OK"):
        msg = (
            "BLOCKED: --full rebuild requires AGENT_HUB_FULL_REBUILD_OK=1 "
            "(M2/Maintainer legacy UI sa only). Law: AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md. "
            "Use: python3 hub_self_refresh_v1.py --json"
        )
        if args.json:
            print(json.dumps({"ok": False, "error": msg, "blocked": "no_hub_rebuild_stuck"}))
        else:
            print(msg, file=sys.stderr)
        return 2
    if args.restart:
        ensure_hub(force_restart=True)
    result = sync_hub(full=args.full)
    if result.get("ok") and not args.quick:
        result["user_signals"] = _record_hub_touch_after_sync(path=str(result.get("path") or ""))
        align = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "align_command_data_ui_v1.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )
        result["align_ui"] = {
            "ok": align.returncode == 0,
            "stdout": (align.stdout or "").strip()[-200:],
            "stderr": (align.stderr or "").strip()[-200:],
        }
        wire = subprocess.run(
            ["bash", str(ROOT / "scripts" / "validate-ui-wiring-v1.sh")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        result["ui_wiring"] = {
            "ok": wire.returncode == 0,
            "stdout": (wire.stdout or "").strip()[-200:],
        }
        as01 = subprocess.run(
            ["bash", str(ROOT / "scripts" / "validate-hub-p0-no-autorun-v1.sh")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=90,
        )
        result["anti_staleness_as01"] = {
            "ok": as01.returncode == 0,
            "stdout": (as01.stdout or as01.stderr or "").strip()[-200:],
        }
        heal = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "heal_command_data_shell_v1.py"), "--force"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        result["shell_heal"] = {
            "ok": heal.returncode == 0,
            "stdout": (heal.stdout or "").strip()[-200:],
        }
        sync_fb = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "sync_feedback_aggregate_hub_built_at_v1.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        result["feedback_sync"] = {
            "ok": sync_fb.returncode == 0,
            "stdout": (sync_fb.stdout or "").strip()[-200:],
        }
        brain_sync = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "brain_sync_lib_v1.py"), "--mode", "light"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        result["brain_sync"] = {
            "ok": brain_sync.returncode == 0,
            "stdout": (brain_sync.stdout or "").strip()[-200:],
        }
    if args.json or True:
        print(json.dumps(result, indent=2))
    align_ok = (result.get("align_ui") or {}).get("ok", True)
    wire_ok = (result.get("ui_wiring") or {}).get("ok", True)
    as01_ok = (result.get("anti_staleness_as01") or {}).get("ok", True)
    heal_ok = (result.get("shell_heal") or {}).get("ok", True)
    sync_ok = (result.get("feedback_sync") or {}).get("ok", True)
    return 0 if result.get("ok") and align_ok and wire_ok and as01_ok and heal_ok and sync_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

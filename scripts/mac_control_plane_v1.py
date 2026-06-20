#!/usr/bin/env python3
"""Mac control plane v1 — Mac observes · cloud/API workers execute.

Law: ~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md
SSOT: data/founder-execution-model-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"

FLAG = SINA / "mac-control-plane-v1.flag"
CONFIG = SINA / "config" / "mac-control-plane-v1.json"
FOUNDER_WORK = SINA / "founder-work-mode-v1.flag"
QUIET_FLAG = SINA / "mac-health-quiet-v1.flag"
CLI_FLAG = SINA / "cli-disabled-v1.flag"
API_FLAG = SINA / "api-disabled-v1.flag"
AUTORUN_FLAG = SINA / "auto-run-disabled-v1.flag"
FILM_FREEZE = SINA / "commercial-film-render-frozen-v1.flag"
FACTORY_NOW = SINA / "factory-now-v1.json"
VISUAL_PROOF = SINA / "config" / "visual_proof.json"
RECEIPT = SINA / "mac-health" / "mac-control-plane-receipt-v1.json"
SSOT = ROOT / "data" / "founder-execution-model-v1.json"

PANIC_LABELS = (
    "com.sina.mac-health-panic-hotkey",
    "com.sina.panic-stop-menubar",
    "com.sina.mac-health-panic-listener",
)

# Control panel INBOX deliver — not local factory motor spawn (requires bounded resume).
_INBOX_DELIVER_CALLERS = frozenset(
    {
        "healthy_drain_orchestrator",
        "healthy-drain:deliver",
        "plans_unified_queue_assign",
        "goal1_lane_broker",
        "loop_specialist_tick",
        "worker_healthy_pack_autodrain",
        "worker_healthy_pack_loop",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _scripts_path() -> None:
    p = str(SCRIPTS)
    if p not in sys.path:
        sys.path.insert(0, p)


def is_active() -> bool:
    return FLAG.is_file()


def load_config() -> dict[str, Any]:
    if not CONFIG.is_file():
        return {}
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def spawn_blocked_on_mac(*, caller: str = "") -> dict[str, Any]:
    """Return blocked row when local factory spawn must not run on Mac body."""
    if not is_active():
        return {"ok": True, "blocked": False, "caller": caller}
    c = (caller or "").strip()
    if c in _INBOX_DELIVER_CALLERS or c.startswith("healthy-drain"):
        _scripts_path()
        try:
            from factory_control_v1 import load_resume_token  # noqa: WPS433

            if load_resume_token():
                return {
                    "ok": True,
                    "blocked": False,
                    "caller": caller,
                    "mac_control_plane": True,
                    "resume_inbox_deliver": True,
                }
        except Exception:
            pass
    return {
        "ok": False,
        "blocked": True,
        "reason": "mac_control_plane",
        "action": "Enqueue on cloud/API worker — Mac control panel only",
        "caller": caller,
        "execution_plane": "cloud_api_worker",
        "control_plane": "mac_hub",
    }


def _bootout(label: str) -> dict[str, Any]:
    uid = os.getuid()
    try:
        proc = subprocess.run(
            ["launchctl", "print", f"gui/{uid}/{label}"],
            capture_output=True,
            text=True,
            timeout=4.0,
        )
        loaded = proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        loaded = False
    action = "none"
    if loaded:
        try:
            subprocess.run(
                ["launchctl", "bootout", f"gui/{uid}/{label}"],
                capture_output=True,
                timeout=8.0,
            )
            action = "bootout"
        except (OSError, subprocess.TimeoutExpired):
            action = "bootout_fail"
    return {"label": label, "was_loaded": loaded, "action": action}


def _freeze_factory_local() -> dict[str, Any]:
    _scripts_path()
    from factory_control_v1 import MODE_PATH, _atomic_write, rebuild_factory_now  # noqa: WPS433

    row = {
        "schema": "factory-mode-v1",
        "mode": "FREEZE",
        "since": _now(),
        "set_by": "mac_control_plane",
        "reason": "Mac control plane — cloud/API executes",
    }
    _atomic_write(MODE_PATH, row)
    rebuild_factory_now(caller="mac_control_plane", force=True)
    return {"mode": "FREEZE", "path": str(MODE_PATH)}


def _disable_visual_proof() -> dict[str, Any]:
    if VISUAL_PROOF.is_file():
        try:
            data = json.loads(VISUAL_PROOF.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
    else:
        data = {}
    vp = data.get("visual_proof") if isinstance(data.get("visual_proof"), dict) else data
    if not isinstance(vp, dict):
        vp = {}
    vp["enabled"] = False
    data["visual_proof"] = vp
    VISUAL_PROOF.parent.mkdir(parents=True, exist_ok=True)
    VISUAL_PROOF.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"path": str(VISUAL_PROOF), "enabled": False}


def _wire_sync() -> dict[str, Any]:
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "founder_execution_model_v1.py"), "--wire-sync", "--json"],
            capture_output=True,
            text=True,
            timeout=180.0,
            cwd=str(ROOT),
        )
        if proc.stdout.strip():
            return json.loads(proc.stdout)
        return {"ok": False, "stderr": (proc.stderr or "")[:400]}
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _kill_capture_automation_lawful() -> None:
    """Mac Law — never blanket-kill native screencapture (founder drag thumbnail sacred)."""
    try:
        subprocess.run(
            [sys.executable, str(SCRIPTS / "no_auto_screenshot_v1.py"), "--kill-automation-only"],
            capture_output=True,
            timeout=4.0,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


def enter(*, wire_sync: bool = True) -> dict[str, Any]:
    """Activate Mac control plane — quiet Mac, factory frozen, cloud APIs on."""
    SINA.mkdir(parents=True, exist_ok=True)
    ts = _now()

    # Paid AI unblocked — do NOT use api-disabled kill switch (autorun pause flag stays per Mac Health)
    ship_window = SINA / "asf-ship-window-v1.flag"
    for path in (
        API_FLAG,
        SINA / "agent-cancel-v1.flag",
        SINA / "mac-health-emergency-active-v1.flag",
        ship_window,
    ):
        if path.is_file():
            path.unlink()

    light_only = SINA / "mac-light-validators-only-v1.flag"
    light_only.write_text(
        f"mac-light-validators-only-v1 · {ts} · heavy gates forbidden on Mac body\n",
        encoding="utf-8",
    )

    line = f"mac-control-plane-v1 · {ts} · Mac observes · cloud/API executes"
    FLAG.write_text(line + "\n", encoding="utf-8")
    FOUNDER_WORK.write_text(
        f"founder-work-mode-v1 · {ts} · control plane — factory off · zero noise · AI unblocked\n",
        encoding="utf-8",
    )
    QUIET_FLAG.write_text(f"mac-health-quiet-v1 · {ts} · mac control plane\n", encoding="utf-8")
    CLI_FLAG.write_text(f"cli-disabled-v1 · {ts} · local CLI drain forbidden on Mac body\n", encoding="utf-8")
    FILM_FREEZE.write_text(f"commercial-film-render-frozen-v1 · {ts} · control plane\n", encoding="utf-8")

    cfg = {
        "schema": "mac-control-plane-v1",
        "saved_at": ts,
        "execution_plane": "cloud_api_worker",
        "control_plane": "mac_hub",
        "mac_role": "control_plane_only",
        "cloud_role": "execution_plane_headless",
        "ssot": str(SSOT),
        "hub": "http://127.0.0.1:13020/",
        "routing_panel": "http://127.0.0.1:8780/",
        "mac_law": "http://127.0.0.1:8781/",
        "local_factory": "frozen",
        "local_cli": "disabled",
        "cloud_api": "enabled",
    }
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    factory_row = _freeze_factory_local()
    visual = _disable_visual_proof()

    launch_rows = [_bootout("com.sourcea.autorun-worker")]
    launch_rows.extend(_bootout(lbl) for lbl in PANIC_LABELS)

    _kill_capture_automation_lawful()
    try:
        subprocess.run(["pkill", "-9", "afplay"], capture_output=True, timeout=4.0)
    except (OSError, subprocess.TimeoutExpired):
        pass

    uid = os.getuid()
    try:
        subprocess.run(
            ["launchctl", "kickstart", "-k", f"gui/{uid}/com.sourcea.hub"],
            capture_output=True,
            timeout=8.0,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass

    wire = _wire_sync() if wire_sync else {"skipped": True}

    hub = "down"
    try:
        proc = subprocess.run(
            ["curl", "-sf", "-m", "3", "http://127.0.0.1:13020/health"],
            capture_output=True,
            text=True,
            timeout=5.0,
        )
        hub = (proc.stdout or "down")[:120]
    except (OSError, subprocess.TimeoutExpired):
        pass

    receipt = {
        "schema": "mac-control-plane-receipt-v1",
        "at": ts,
        "ok": True,
        "hub": hub,
        "factory": factory_row,
        "visual_proof": visual,
        "launch": launch_rows,
        "wire_sync": wire,
        "note": "Use /Applications/Cursor.app — cloud workers execute · Mac manages only",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def assess() -> dict[str, Any]:
    issues: list[str] = []
    if not FLAG.is_file():
        issues.append("mac-control-plane-v1.flag missing")
    if not FOUNDER_WORK.is_file():
        issues.append("founder-work-mode-v1.flag missing")
    if not CLI_FLAG.is_file():
        issues.append("cli-disabled-v1.flag missing — local CLI must stay off")
    if API_FLAG.is_file():
        issues.append("api-disabled-v1.flag present — cloud APIs blocked")

    _scripts_path()
    resume = None
    try:
        from factory_control_v1 import current_mode, load_resume_token  # noqa: WPS433

        resume = load_resume_token()
        mode = current_mode()
        if resume:
            if mode not in ("SINGLE_SA", "FREEZE", "AUDIT"):
                issues.append(f"factory mode {mode} — expected SINGLE_SA during bounded resume")
        elif mode == "SINGLE_SA":
            now_row: dict = {}
            if FACTORY_NOW.is_file():
                try:
                    now_row = json.loads(FACTORY_NOW.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    now_row = {}
            bounded_drain = (
                AUTORUN_FLAG.is_file()
                and not bool(now_row.get("stop_receipt_open"))
                and int(now_row.get("valid_yes") or 0) >= 1000
                and str(now_row.get("mode") or mode) == "SINGLE_SA"
            )
            if not bounded_drain:
                issues.append(
                    f"factory mode {mode} — expected FREEZE or AUDIT (or bounded SINGLE_SA with autorun paused + Goal1 honest)"
                )
        elif mode not in ("FREEZE", "AUDIT"):
            issues.append(f"factory mode {mode} — expected FREEZE or AUDIT")
    except Exception as exc:
        issues.append(f"factory_mode_check: {exc}")

    if not resume and not AUTORUN_FLAG.is_file():
        issues.append("auto-run-disabled-v1.flag missing — keep autorun paused during focus (Mac Health)")

    cfg = load_config()
    if cfg.get("execution_plane") != "cloud_api_worker":
        issues.append("config execution_plane not cloud_api_worker")

    return {
        "ok": not issues,
        "issues": issues,
        "active": is_active(),
        "resume_token": bool(resume),
        "config": cfg,
        "receipt": str(RECEIPT) if RECEIPT.is_file() else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Mac control plane — cloud executes · Mac manages")
    ap.add_argument("--enter", action="store_true", help="Activate control plane on this Mac")
    ap.add_argument("--assess", action="store_true", help="Assess control plane state")
    ap.add_argument("--spawn-check", metavar="CALLER", help="Check if local spawn blocked")
    ap.add_argument("--no-wire-sync", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.enter:
        row = enter(wire_sync=not args.no_wire_sync)
    elif args.spawn_check:
        row = spawn_blocked_on_mac(caller=args.spawn_check)
    elif args.assess:
        row = assess()
    else:
        row = assess()
        if not row.get("ok"):
            row = {"assess": row, "hint": "run --enter to activate"}

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        if args.enter:
            print("MAC CONTROL PLANE ON")
            print(f"  · Hub: {row.get('hub', '?')}")
            print("  · Local factory FREEZE · autorun booted out")
            print("  · CLI disabled on Mac · cloud APIs enabled")
            print("  · Open http://127.0.0.1:13020/ and http://127.0.0.1:8780/")
        else:
            print(json.dumps(row, indent=2))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())

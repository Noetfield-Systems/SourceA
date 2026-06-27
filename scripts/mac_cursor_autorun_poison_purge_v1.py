#!/usr/bin/env python3
"""Purge Mac Cursor AUTO-RUN poison — cloud Auto Runtime only (ASF 2026-06-24)."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "mac-cursor-autorun-poison-purge-receipt-v1.json"

DELETE_REL = [
    "scripts/goal1_auto_run_v1.py",
    "scripts/goal1_unified_autorun_v1.py",
    "scripts/goal1_auto_run_deliver_v1.py",
    "scripts/autorun_dispatcher_v1.py",
    "scripts/auto_run_worker_batch_v1.py",
    "scripts/autorun_worker_guard_v1.sh",
    "scripts/com.sourcea.autorun-worker.plist",
    "scripts/install-autorun.sh",
    "scripts/install-autorun-launchd-v1.sh",
    "scripts/stop_goal1_auto_run_v1.py",
    "scripts/stop_goal1_loop_v1.py",
    "scripts/auto_start_worker_batch_on_hub_v1.sh",
    "scripts/validate-goal1-auto-run-v1.sh",
    "scripts/validate-goal1-auto-run-activation-chain-v1.sh",
    "scripts/validate-goal1-unified-autorun-v1.sh",
    "scripts/validate-goal1-auto-loop-v1.sh",
    "scripts/validate-goal1-loop-activation-chain-v1.sh",
    "scripts/validate-auto-run-fully-automatic-v1.sh",
    "scripts/validate-auto-run-window-preflight-v1.sh",
    "scripts/start-overnight-3engine-v1.sh",
    "launch/com.sourcea.autorun-worker.plist",
    "brain-os/laws/AUTO_RUN_FULLY_AUTOMATIC_LOCKED_v1.md",
    "brain-os/laws/AUTO_RUN_WINDOW_PREFLIGHT_LOCKED_v1.md",
    "brain-os/contract/TODAY_AUTORUN_50_PLAN_LOCKED_v1.md",
]

DELETE_SINA = [
    "auto-run-disabled-v1.flag",
    "goal1-auto-run-lock-v1.json",
    "goal1-auto-loop-lock-v1.json",
    "auto-run-worker-batch-v1.json",
    "goal1-unified-autorun-v1.json",
    "goal1-worker-batch-lock-v1.json",
    "goal1-worker-batch-latest.log",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _unload_launchd() -> dict:
    label = "com.sourcea.autorun-worker"
    for cmd in (
        ["launchctl", "bootout", f"gui/{Path.home().stat().st_uid}", str(ROOT / "launch/com.sourcea.autorun-worker.plist")],
        ["launchctl", "unload", str(ROOT / "launch/com.sourcea.autorun-worker.plist")],
        ["launchctl", "remove", label],
    ):
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        except Exception:
            pass
    return {"label": label, "attempted": True}


def _pkill() -> None:
    for pat in ("autorun_dispatcher_v1", "goal1_auto_run_v1", "goal1_unified_autorun"):
        subprocess.run(["pkill", "-f", pat], capture_output=True, text=True)


def main() -> int:
    deleted: list[str] = []
    missing: list[str] = []
    for rel in DELETE_REL:
        p = ROOT / rel
        if p.is_file():
            p.unlink()
            deleted.append(rel)
        elif p.exists():
            missing.append(f"{rel} (not a file)")
        else:
            missing.append(rel)

    for name in DELETE_SINA:
        p = SINA / name
        if p.is_file():
            p.unlink()
            deleted.append(f"~/.sina/{name}")

    launchd = _unload_launchd()
    _pkill()

    row = {
        "ok": True,
        "schema": "mac-cursor-autorun-poison-purge-v1",
        "at": _now(),
        "authority": "ASF anti-poison 2026-06-24",
        "law": "brain-os/law/enforcement/SOURCEA_MAC_CURSOR_AUTORUN_POISON_PURGED_LOCKED_v1.md",
        "motor_replacement": "cloud Auto Runtime only — data/cloud-auto-runtime-v1.json",
        "deleted_count": len(deleted),
        "deleted": deleted,
        "missing": missing,
        "launchd": launchd,
        "forbidden_forever": [
            "Mac Cursor AUTO-RUN",
            "goal1_unified_autorun",
            "autorun_dispatcher",
            "com.sourcea.autorun-worker",
        ],
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if "--json" in sys.argv:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK purged {len(deleted)} paths · receipt {RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

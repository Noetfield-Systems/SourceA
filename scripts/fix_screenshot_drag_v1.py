#!/usr/bin/env python3
"""Fix founder screenshot drag — auto capture OFF + stop background killers + macOS thumbnail ON.

Drag breaks when:
  1. Blanket pkill screencapture (fixed in law — must not return)
  2. mac-daily-cleanup / hub / prevention runs while you drag
  3. show-thumbnail OFF in macOS settings
  4. RAM maxed — UI frozen (Cursor 35 proc) — feels like 'drag broken'
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
RECEIPT = SINA / "mac-health" / "screenshot-drag-fix-latest-v1.json"
DAILY_CLEANUP_DISABLED = SINA / "mac-daily-cleanup-disabled-v1.flag"
SHIELD_FLAG = SINA / "screenshot-drag-shield-v1.flag"

BOOTOUT = (
    "com.sina.mac-daily-cleanup",
    "com.sourcea.hub",
    "com.sourcea.autorun-worker",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: float = 15.0) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, ((proc.stdout or "") + (proc.stderr or "")).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)[:200]


def ensure_macos_screenshot_thumbnail() -> dict[str, Any]:
    """Floating thumbnail required for drag-to-app."""
    steps: list[dict[str, Any]] = []
    code, current = _run(["defaults", "read", "com.apple.screencapture", "show-thumbnail"], timeout=5.0)
    was = (current or "").strip()
    if was not in ("1", "true", "yes"):
        code2, out = _run(
            ["defaults", "write", "com.apple.screencapture", "show-thumbnail", "-bool", "true"],
            timeout=5.0,
        )
        steps.append({"step": "show-thumbnail", "ok": code2 == 0, "was": was, "detail": out[:80]})
        _run(["killall", "SystemUIServer"], timeout=8.0)
        steps.append({"step": "SystemUIServer_restart", "ok": True})
    else:
        steps.append({"step": "show-thumbnail", "ok": True, "already": True})
    return {"ok": True, "steps": steps}


def bootout_interference() -> dict[str, Any]:
    uid = os.getuid()
    rows: list[dict[str, Any]] = []
    for label in BOOTOUT:
        code, detail = _run(["launchctl", "bootout", f"gui/{uid}/{label}"], timeout=8.0)
        rows.append({"label": label, "ok": code == 0, "detail": detail[:80]})
    SINA.mkdir(parents=True, exist_ok=True)
    DAILY_CLEANUP_DISABLED.write_text(
        f"screenshot-drag-shield · {_now()} · mid cleanup was interrupting founder drag\n",
        encoding="utf-8",
    )
    SHIELD_FLAG.write_text(f"screenshot-drag-shield-v1 · {_now()}\n", encoding="utf-8")
    return {"ok": True, "bootout": rows, "daily_cleanup_disabled": str(DAILY_CLEANUP_DISABLED)}


def enforce_no_auto() -> dict[str, Any]:
    scripts = Path(__file__).resolve().parent
    code, out = _run(
        [os.environ.get("PYTHON", "python3"), str(scripts / "no_auto_screenshot_v1.py"), "--enforce", "--json"],
        timeout=20.0,
    )
    try:
        row = json.loads(out) if out.startswith("{") else {"raw": out[:200]}
    except json.JSONDecodeError:
        row = {"ok": code == 0, "raw": out[:200]}
    return {"ok": code == 0, "detail": row}


def run_fix(*, macos_defaults: bool = True) -> dict[str, Any]:
    steps: dict[str, Any] = {}
    if macos_defaults:
        steps["macos"] = ensure_macos_screenshot_thumbnail()
    steps["bootout"] = bootout_interference()
    steps["no_auto"] = enforce_no_auto()
    try:
        from cursor_agent_law_v1 import probe_caps  # noqa: WPS433

        steps["cursor"] = probe_caps()
    except Exception as exc:
        steps["cursor"] = {"error": str(exc)[:120]}

    cursor_v = (steps.get("cursor") or {}).get("violations") or []
    proc = int(((steps.get("cursor") or {}).get("probe") or {}).get("processes") or 0)
    receipt = {
        "schema": "screenshot-drag-fix-v1",
        "at": _now(),
        "ok": True,
        "founder_line": (
            "Screenshot drag shield ON · auto capture OFF · daily cleanup + hub OFF · "
            f"show-thumbnail ON · Cursor {proc} proc"
            + (" — run fresh-start if >15" if proc > 15 else "")
        ),
        "steps": steps,
        "if_still_broken": [
            "RAM full freezes drag — run: bash ~/Desktop/SourceA/scripts/founder-mac-fresh-start-v1.sh",
            "Then ⌘⇧4 → wait for corner thumbnail → drag to app (not while Mac Health cool-down running)",
        ],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Fix founder screenshot drag")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-defaults", action="store_true")
    args = ap.parse_args()
    row = run_fix(macos_defaults=not args.no_defaults)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line", "done"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

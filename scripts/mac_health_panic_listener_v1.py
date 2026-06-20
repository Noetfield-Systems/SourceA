#!/usr/bin/env python3
"""PANIC hotkey listener — python3.12 (Accessibility entry).

Shortcuts (GlobalHotKeys — reliable combo detection):
  ⌃⌥⌘S  — Control+Option+Command+S
  ⌃⌘P   — Control+Command+P  (easier backup — no Option)
  F19    — if your keyboard has it
File:    touch ~/.sina/PANIC.now
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
LOG = SINA / "mac-health-panic-hotkey.log"
PANIC_FILE = SINA / "PANIC.now"
BASSO = "/System/Library/Sounds/Basso.aiff"
SOURCE_A = Path(os.environ.get("SINA_SOURCEA", Path.home() / "Desktop/SourceA"))
SCRIPT = SOURCE_A / "scripts" / "mac_health_emergency_stop_v1.py"
DEBOUNCE_SEC = 2.0
_last = 0.0


def _log(msg: str) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} [py312] {msg}\n"
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line)


def _alert() -> None:
    """Instant feedback on PANIC hotkey — fully silent unless notifications enabled."""
    try:
        from mac_health_settings_v1 import notifications_enabled, load_settings  # noqa: WPS433

        if not notifications_enabled():
            return
        sounds_on = bool((load_settings().get("notifications") or {}).get("sounds_enabled", False))
    except Exception:
        return
    if sounds_on and Path(BASSO).is_file():
        subprocess.Popen(
            ["afplay", BASSO],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.Popen(
            [
                "/usr/bin/osascript",
                "-e",
                'display notification "Factory frozen — killing agents…" with title "⛔ Mac Health PANIC" sound name "Basso"',
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.Popen(
            [
                "/usr/bin/osascript",
                "-e",
                'display notification "Factory frozen — killing agents…" with title "⛔ Mac Health PANIC"',
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _fire(trigger: str) -> None:
    global _last
    now = time.monotonic()
    if now - _last < DEBOUNCE_SEC:
        _log(f"debounced {trigger}")
        return
    _last = now
    if not SCRIPT.is_file():
        _log(f"FAIL missing {SCRIPT}")
        return
    _log(f"PANIC trigger={trigger}")
    _alert()
    env = {**os.environ, "PYTHONPATH": str(SOURCE_A / "scripts"), "SINA_SOURCEA": str(SOURCE_A)}
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--trigger", trigger, "--fast", "--json"],
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        line = "Agents stopped."
        try:
            row = json.loads(proc.stdout or "{}")
            line = row.get("founder_line") or row.get("summary") or line
        except json.JSONDecodeError:
            if proc.stdout:
                line = proc.stdout.strip()[-300:]
        safe = line.replace('"', "'")[:400]
        try:
            from mac_health_settings_v1 import notifications_enabled  # noqa: WPS433

            if notifications_enabled():
                subprocess.run(
                    [
                        "/usr/bin/osascript",
                        "-e",
                        f'display alert "⛔ STOPPED" message "{safe}" buttons {{"OK"}} default button "OK"',
                    ],
                    timeout=15,
                )
        except Exception:
            pass
        _log(f"done {line[:120]}")
    except (OSError, subprocess.TimeoutExpired) as exc:
        _log(f"FAIL run {exc}")


def _check_file() -> None:
    if PANIC_FILE.is_file():
        try:
            PANIC_FILE.unlink()
        except OSError:
            pass
        _fire("panic-file")


def main() -> int:
    try:
        from pynput import keyboard  # type: ignore
    except ImportError:
        _log("FAIL pynput not installed")
        return 1

    _log(f"listener start pid={os.getpid()} python={sys.executable}")

    # GlobalHotKeys = proper combo detection (manual modifier set was flaky)
    hotkey_map = {
        "<ctrl>+<alt>+<cmd>+s": lambda: _fire("hotkey-ctrl-alt-cmd-s"),
        "<ctrl>+<cmd>+p": lambda: _fire("hotkey-ctrl-cmd-p"),
        "<f19>": lambda: _fire("hotkey-f19"),
    }
    hotkeys = keyboard.GlobalHotKeys(hotkey_map)
    hotkeys.start()
    _log(
        "OK GlobalHotKeys armed — ⌃⌥⌘S · ⌃⌘P (easier) · F19 · touch ~/.sina/PANIC.now"
    )

    try:
        while hotkeys.is_alive():
            _check_file()
            time.sleep(0.35)
    except KeyboardInterrupt:
        pass
    finally:
        hotkeys.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

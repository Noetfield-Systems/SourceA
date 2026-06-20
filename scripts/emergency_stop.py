#!/usr/bin/env python3
"""Full emergency stop — hub, inject, remote_ops, M8 UI paste. Callable from app or shell."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
KILL_SCRIPT = SOURCE_A / "scripts/kill-sina-command.sh"
TERMINAL_CMD = "~/Desktop/SourceA/scripts/emergency-stop.sh"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_emergency_stop(*, from_hub: bool = False) -> dict:
    """
    Stop all Sina Command automation. Safe to call from hub API (schedules self-exit separately).
    """
    steps: list[str] = []
    ok = True
    err = ""

    if KILL_SCRIPT.is_file():
        try:
            proc = subprocess.run(
                ["bash", str(KILL_SCRIPT)],
                cwd=SOURCE_A,
                capture_output=True,
                text=True,
                timeout=90,
            )
            out = ((proc.stdout or "") + (proc.stderr or "")).strip()
            if proc.returncode != 0:
                ok = False
                err = f"kill script exit {proc.returncode}"
            if out:
                steps.extend(line.strip() for line in out.splitlines() if line.strip())
        except subprocess.TimeoutExpired:
            ok = False
            err = "kill script timed out"
        except OSError as e:
            ok = False
            err = str(e)
    else:
        ok = False
        err = f"missing {KILL_SCRIPT}"

    # Belt-and-suspenders if script partial
    try:
        from auto_prompt_guard import disable_auto_feed_everywhere, ensure_kill_on  # noqa: WPS433
        from intelligence_circle import disable_live_agent_automation  # noqa: WPS433

        ensure_kill_on()
        disable_auto_feed_everywhere()
        disable_live_agent_automation()
        steps.append("auto-paste kill switch ON")
    except Exception as e:
        steps.append(f"guard warn: {e}")

    return {
        "ok": ok,
        "stopped_at": _now(),
        "from_hub": from_hub,
        "terminal_command": TERMINAL_CMD,
        "script": str(KILL_SCRIPT),
        "steps": steps[-12:],
        "message": (
            "Emergency stop complete — hub (:13020) and rebuild worker (:13030) off, auto-paste blocked."
            if ok
            else f"Emergency stop partial — {err}. Run in Terminal: {TERMINAL_CMD}"
        ),
        "error": err or None,
    }

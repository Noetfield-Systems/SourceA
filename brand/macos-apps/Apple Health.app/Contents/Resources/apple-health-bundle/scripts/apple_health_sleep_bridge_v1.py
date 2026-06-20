#!/usr/bin/env python3
"""Apple Health → SourceA sleep governance bridge. Event-driven — no timer."""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

def _source_a_root() -> Path:
    import os

    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[1]


ROOT = _source_a_root()
ACTIVE = ROOT / "ACTIVE_NOW.md"
SCRIPTS = ROOT / "scripts"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def evaluate() -> dict:
    sys_path = SCRIPTS
    import sys

    sys.path.insert(0, str(sys_path))
    from apple_health_mini import load_sleep_signal  # noqa: WPS433
    from active_now_v1 import load_active_now  # noqa: WPS433

    sig = load_sleep_signal()
    active = load_active_now()
    state = (sig.get("state") or "awake").lower()
    asleep = state in ("asleep", "in_bed", "sleeping")
    fm = (active.get("founder_mode") or "founder_busy").lower()
    sleep_on = bool(active.get("sleep_escalation"))

    recommend = "stay"
    if asleep and fm == "founder_busy" and not sleep_on:
        recommend = "arm_sleep"
    elif not asleep and fm == "founder_absent" and sleep_on:
        recommend = "wake"

    return {
        "ok": True,
        "health_state": state,
        "health_asleep": asleep,
        "founder_mode": fm,
        "sleep_escalation": sleep_on,
        "recommend": recommend,
        "signal_at": sig.get("updated_at"),
        "auto_arm": (Path.home() / ".sina/apple-health/auto-arm-sleep-v1.flag").is_file(),
    }


def apply_sleep_from_health() -> dict:
    """Arm sleep when Health says asleep (only if auto-arm flag on or caller is manual)."""
    proc = subprocess.run(
        ["bash", str(SCRIPTS / "arm-sleep-mode-v1.sh")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "ok": proc.returncode == 0,
        "trigger": "apple_health_sleep_start",
        "stdout": (proc.stdout or "")[-500:],
    }


def apply_wake_from_health() -> dict:
    """Founder awake — stop overnight, return to founder_busy."""
    for name in ("stop-sidecar-engines-watch-v1.sh", "stop-sleep-mac-caretaker-watch-v1.sh"):
        sp = SCRIPTS / name
        if sp.is_file():
            subprocess.run(["bash", str(sp)], cwd=str(ROOT), timeout=30)
    overnight_pid = Path.home() / ".sina/overnight-3engine-v1.pid"
    if overnight_pid.is_file():
        try:
            import os

            os.kill(int(overnight_pid.read_text().strip()), 15)
        except OSError:
            pass
        overnight_pid.unlink(missing_ok=True)
    Path.home().joinpath(".sina/auto-run-disabled-v1.flag").touch()
    if ACTIVE.is_file():
        text = ACTIVE.read_text(encoding="utf-8")
        text = re.sub(r"\*\*Current Founder Mode:\*\*.*", "**Current Founder Mode:** `founder_busy`", text)
        text = re.sub(r"\*\*Current Sleep Escalation:\*\*.*", "**Current Sleep Escalation:** `off`", text)
        text = re.sub(
            r"\*\*Current Sprint:\*\*.*",
            "**Current Sprint:** Awake — Apple Health wake signal",
            text,
        )
        ACTIVE.write_text(text, encoding="utf-8")
    return {"ok": True, "trigger": "apple_health_sleep_end", "founder_mode": "founder_busy"}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = evaluate()
    print(json.dumps(row, indent=2) if args.json else json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

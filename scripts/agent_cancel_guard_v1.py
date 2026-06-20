#!/usr/bin/env python3
"""Agent cancel guard — honor mac-health panic stop flag (UPGR-091)."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

CANCEL_FLAG = Path.home() / ".sina" / "agent-cancel-v1.flag"
DEFAULT_MAX_AGE_SEC = 86400.0


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def agent_cancel_active(*, max_age_sec: float = DEFAULT_MAX_AGE_SEC) -> bool:
    if not CANCEL_FLAG.is_file():
        return False
    if max_age_sec <= 0:
        return True
    try:
        age = time.time() - CANCEL_FLAG.stat().st_mtime
        return age <= max_age_sec
    except OSError:
        return False


def agent_cancel_skip(*, caller: str = "unknown") -> dict:
    """Standard skip row when panic stop cancelled in-flight work."""
    line = ""
    if CANCEL_FLAG.is_file():
        try:
            line = CANCEL_FLAG.read_text(encoding="utf-8").splitlines()[0][:200]
        except OSError:
            line = ""
    return {
        "ok": False,
        "action": "skip",
        "reason": "AGENT_CANCEL",
        "caller": caller,
        "cancel_flag": str(CANCEL_FLAG),
        "cancel_line": line,
        "at": _now(),
    }


def write_cancel_receipt(*, caller: str, path: Path | None = None) -> Path:
    out = path or (Path.home() / ".sina" / "agent-cancel-receipt-v1.json")
    row = agent_cancel_skip(caller=caller)
    row["schema"] = "agent-cancel-receipt-v1"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Check agent-cancel flag")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = {
        "active": agent_cancel_active(),
        "flag": str(CANCEL_FLAG),
        "exists": CANCEL_FLAG.is_file(),
    }
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print("active" if row["active"] else "clear")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Open Google App Passwords for hello@trustfield.ca — MSB wave live send."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SECRETS = Path.home() / ".sina" / "secrets.env"
KEY = "GOOGLE_WORKSPACE_APP_PASSWORD"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _has_key() -> bool:
    if not SECRETS.is_file():
        return False
    for ln in SECRETS.read_text(encoding="utf-8").splitlines():
        if ln.startswith(f"{KEY}="):
            v = ln.split("=", 1)[1].strip()
            return bool(v) and v not in ("", "REPLACE_ME")
    return False


def main() -> int:
    if _has_key():
        print(json.dumps({"ok": True, "at": _now(), "message": f"{KEY} already set in secrets.env"}))
        return 0
    subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "Google Chrome" to open location "https://myaccount.google.com/apppasswords"',
        ],
        check=False,
    )
    print(
        json.dumps(
            {
                "ok": False,
                "at": _now(),
                "action": f"Add to {SECRETS}: GOOGLE_WORKSPACE_APP_PASSWORD=<16-char app password>",
                "account": "hello@trustfield.ca (Google Workspace)",
                "then": "cd ~/Desktop/TrustField\\ Technologies && ./scripts/agentic_msb_wave_send.sh 15",
            },
            indent=2,
        )
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

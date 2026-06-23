#!/usr/bin/env python3
"""Open witness.bc Stripe API key page; poll env for WITNESSBC_STRIPE_SECRET_KEY then sync links."""
from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ENV = Path.home() / ".sina/witnessbc-stripe-links-v1.env"
SYNC = Path(__file__).resolve().parent / "sync_witnessbc_stripe_payment_links_v1.py"
ACCT = "acct_1SLh0sF7zpKqepMk"
KEY_URL = f"https://dashboard.stripe.com/{ACCT}/apikeys/create"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _has_secret() -> bool:
    if not ENV.is_file():
        return False
    for ln in ENV.read_text(encoding="utf-8").splitlines():
        if ln.startswith("WITNESSBC_STRIPE_SECRET_KEY="):
            v = ln.split("=", 1)[1].strip()
            return v.startswith(("sk_", "rk_"))
    return False


def main() -> int:
    subprocess.run(["open", KEY_URL], check=False)
    deadline = time.time() + 120
    while time.time() < deadline:
        if _has_secret():
            proc = subprocess.run(
                ["python3", str(SYNC), "--create", "--pull", "--deploy", "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            print(proc.stdout or proc.stderr)
            return proc.returncode
        time.sleep(2)
    print(json.dumps({"ok": False, "at": _now(), "error": "timeout waiting for WITNESSBC_STRIPE_SECRET_KEY"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

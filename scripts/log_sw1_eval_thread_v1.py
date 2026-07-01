#!/usr/bin/env python3
"""Log SW1 design-partner eval thread receipt."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
RECEIPT = SINA / "sw1-eval-thread-receipt-v1.json"
REPO_URL = "https://github.com/kazemnezhadsina144-dot/sourcea-boot"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_receipt(*, thread_url: str = "", contact: str = "", notes: str = "") -> dict:
    row = {
        "schema": "sw1-eval-thread-receipt-v1",
        "at": _now(),
        "status": "eval_thread_logged",
        "repo_url": REPO_URL,
        "thread_url": thread_url or None,
        "contact": contact or None,
        "notes": notes or "Design-partner eval thread — README 5-min path + validate-sourcea-boot-v1.sh",
        "readme_quickstart": True,
        "ci_validator": "scripts/validate-sourcea-boot-v1.sh",
        "sw1_ready": bool(thread_url or contact),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    p = argparse.ArgumentParser(description="SW1 eval thread receipt")
    p.add_argument("--thread-url", default="")
    p.add_argument("--contact", default="")
    p.add_argument("--notes", default="")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = write_receipt(thread_url=args.thread_url, contact=args.contact, notes=args.notes)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: SW1 eval receipt · sw1_ready={row.get('sw1_ready')} · {RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

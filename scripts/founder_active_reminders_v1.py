#!/usr/bin/env python3
"""Founder active reminders — disk SSOT for standing orders (not chat-only).

Reads/writes: ~/.sina/founder-active-reminders-v1.json
Wired: daily duty card inject · session gate · H2 registry pointer
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REMINDER_PATH = Path.home() / ".sina" / "founder-active-reminders-v1.json"
H2_REGISTRY = Path.home() / ".sina" / "h2-pending-registry-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_reminders() -> dict:
    if not REMINDER_PATH.is_file():
        return {}
    try:
        return json.loads(REMINDER_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def inject_slice(rem: dict | None = None) -> dict:
    r = rem or load_reminders()
    if not r:
        return {}
    return {
        "path": str(REMINDER_PATH),
        "title": r.get("title"),
        "one_line": r.get("one_line"),
        "fix_order_top3": [x.get("action") for x in (r.get("fix_order") or [])[:3]],
        "open_count": (r.get("honest_counts") or {}).get("pending_open"),
        "plan_doc": r.get("plan_doc"),
    }


def sync_h2_pointer() -> None:
    """Attach reminder pointer to H2 registry for Brain/H2 surfaces."""
    if not H2_REGISTRY.is_file():
        return
    try:
        reg = json.loads(H2_REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    reg["founder_active_reminder"] = inject_slice()
    reg["founder_active_reminder"]["synced_at"] = _now()
    H2_REGISTRY.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Founder active reminders")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--inject", action="store_true")
    ap.add_argument("--sync-h2", action="store_true", help="Write pointer into h2-pending-registry")
    args = ap.parse_args()

    if args.sync_h2:
        sync_h2_pointer()

    if args.inject:
        out = inject_slice()
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if out else 1

    rem = load_reminders()
    if args.json:
        print(json.dumps(rem, indent=2, ensure_ascii=False))
    else:
        print(rem.get("one_line") or "no reminders")
    return 0 if rem else 1


if __name__ == "__main__":
    raise SystemExit(main())

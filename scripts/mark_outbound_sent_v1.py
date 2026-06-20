#!/usr/bin/env python3
"""Mark AB1/NW1 outbound receipt as sent (founder tap after Mail Send)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
LANES = {
    "ab1": SINA / "ab1-outbound-send-receipt-v1.json",
    "nw1": SINA / "nw1-outbound-send-receipt-v1.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def mark_sent(lane: str, *, screenshot: str = "") -> dict:
    path = LANES.get(lane)
    if not path or not path.is_file():
        raise SystemExit(f"FAIL: missing receipt for {lane}: {path}")
    row = json.loads(path.read_text(encoding="utf-8"))
    row[f"{lane}_status"] = "sent"
    row["sent_at"] = _now()
    row["send_mode"] = "founder_confirmed_send"
    if screenshot:
        row["screenshot_path"] = screenshot
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    watch: dict = {}
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from commercial_agents_wire_v1 import row_id_for_lane, run_commercial_action  # noqa: WPS433

        rid = row_id_for_lane(lane)
        if rid:
            watch = run_commercial_action("reply_stage", row_id=rid)
    except Exception as exc:
        watch = {"ok": False, "error": str(exc)}

    return {"receipt": row, "reply_watch": watch}


def main() -> int:
    p = argparse.ArgumentParser(description="Mark outbound send receipt as sent")
    p.add_argument("--lane", required=True, choices=sorted(LANES))
    p.add_argument("--screenshot", default="")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = mark_sent(args.lane, screenshot=args.screenshot)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: {args.lane.upper()} marked sent · {LANES[args.lane]}")
        rw = (row.get("reply_watch") or {})
        if rw.get("ok"):
            print(f"Reply watch armed · row={rw.get('row_id')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

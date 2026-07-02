#!/usr/bin/env python3
"""Kaizen queue — one machine_safe item per Forge Run cycle (W-LBA-005)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "data" / "autorun-kaizen-backlog-v1.json"
RECEIPT_DIR = ROOT / "receipts" / "cloud" / "kaizen"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pick_next(*, mark_done: str | None = None) -> dict[str, Any]:
    row = json.loads(BACKLOG.read_text(encoding="utf-8"))
    items = row.get("items") if isinstance(row.get("items"), list) else []
    if mark_done:
        for item in items:
            if isinstance(item, dict) and item.get("id") == mark_done:
                item["status"] = "done"
                item["done_at"] = _now()
        BACKLOG.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    candidates = [
        i
        for i in items
        if isinstance(i, dict)
        and i.get("class") == "machine_safe"
        and i.get("status") in ("pending", "in_progress")
    ]
    candidates.sort(key=lambda x: int(x.get("roi_rank") or 999))
    chosen = candidates[0] if candidates else None
    out = {
        "schema": "autorun-kaizen-pick-v1",
        "at": _now(),
        "ok": chosen is not None,
        "picked": chosen,
        "report_line": (
            f"kaizen_pick · {chosen.get('id')} · {chosen.get('title')[:60]}"
            if chosen
            else "kaizen_pick · IDLE_NO_WORK · no machine_safe items"
        ),
    }
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    (RECEIPT_DIR / "kaizen-pick-latest-v1.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8"
    )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pick", action="store_true")
    ap.add_argument("--mark-done", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = pick_next(mark_done=args.mark_done or None)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 0


if __name__ == "__main__":
    raise SystemExit(main())

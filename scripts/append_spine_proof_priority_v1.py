#!/usr/bin/env python3
"""Append SOURCEA-PRIORITY spine proof row when spine.bridge event exists (sa-0425)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = ROOT / "brain-os" / "plan-registry" / "SOURCEA-PRIORITY.md"
ROW_MARKER = "sa-0425 spine.bridge event proof"


def _now_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _latest_bridge_event() -> dict[str, Any] | None:
    from runtime.event_bus.bus_v1 import tail  # noqa: WPS433

    rows = tail(topic="spine.bridge", n=50)
    for row in reversed(rows):
        if row.get("topic") != "spine.bridge":
            continue
        payload = row.get("payload") or {}
        if row.get("source") == "founder_action" and payload.get("ok") is True:
            return row
    return None


def maybe_append_spine_proof_row() -> dict[str, Any]:
    """Idempotent: append evidence row only when founder spine.bridge event exists."""
    event = _latest_bridge_event()
    if not event:
        return {"ok": True, "appended": False, "reason": "no founder spine.bridge event"}

    pri = PRIORITY.read_text(encoding="utf-8")
    if ROW_MARKER in pri:
        return {"ok": True, "appended": False, "reason": "row already present", "marker": ROW_MARKER}

    payload = event.get("payload") or {}
    action_id = payload.get("action_id") or "unknown"
    at = (event.get("at") or "")[:10] or _now_date()
    row = (
        f"| {at} | {ROW_MARKER} | {action_id} ok · founder_action · "
        f"event_bus spine.bridge · critical 0 |\n"
    )
    anchor = "## Evidence log"
    if anchor not in pri:
        return {"ok": False, "error": "SOURCEA-PRIORITY missing Evidence log section"}
    pri = pri.replace(anchor, anchor + "\n" + row, 1)
    PRIORITY.write_text(pri, encoding="utf-8")
    print(f"OK: append_spine_proof_priority_v1 (sa-0425) · {action_id} · row appended")
    return {
        "ok": True,
        "appended": True,
        "action_id": action_id,
        "marker": ROW_MARKER,
        "event_at": event.get("at"),
    }


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Append spine.bridge proof row to SOURCEA-PRIORITY")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    out = maybe_append_spine_proof_row()
    if args.json:
        print(json.dumps(out, indent=2))
    elif not out.get("appended"):
        print(f"OK: append_spine_proof_priority_v1 skip — {out.get('reason')}")


if __name__ == "__main__":
    main()

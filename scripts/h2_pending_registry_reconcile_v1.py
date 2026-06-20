#!/usr/bin/env python3
"""Reconcile H2 pending registry — close shipped rows · trim sync spam · honest counts."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
H2_REGISTRY = SINA / "h2-pending-registry-v1.json"
SCRIPTS = Path(__file__).resolve().parents[1]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def reconcile_registry(*, write: bool = True) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from h2_pending_count_lib_v1 import count_h2_pending  # noqa: WPS433

    if not H2_REGISTRY.is_file():
        return {"ok": False, "error": "missing registry"}

    reg = json.loads(H2_REGISTRY.read_text(encoding="utf-8"))
    before = count_h2_pending(reg)

    # Trim sync_notes spam (keep last 5 unique)
    notes = reg.get("sync_notes") or []
    if isinstance(notes, list) and len(notes) > 5:
        seen: list[str] = []
        for n in reversed(notes):
            s = str(n)
            if s not in seen:
                seen.append(s)
            if len(seen) >= 5:
                break
        reg["sync_notes"] = list(reversed(seen))

    # Split maintainer_ship: open vs scheduled_cadence vs closed_receipts
    maintainer = list(reg.get("maintainer_ship") or [])
    open_rows: list[dict] = []
    scheduled: list[dict] = []
    closed: list[dict] = reg.get("maintainer_ship_closed") or []

    for row in maintainer:
        rid = str(row.get("id") or "")
        status = str(row.get("status") or "").lower()
        if status in ("shipped", "wired") or row.get("shipped_at"):
            closed.append({**row, "closed_at": row.get("shipped_at") or _now(), "closed_reason": status or "shipped"})
        elif rid.startswith("UP-") or rid == "LEGACY-HERO":
            scheduled.append(row)
        else:
            open_rows.append(row)

    # Canonical UP-01..UP-06 live in scheduled_cadence only (not pending_total)
    from machine_three_pipelines_lib_v1 import UPGRADE_BOARD  # noqa: WPS433

    by_sched_id = {str(r.get("id")): r for r in scheduled if isinstance(r, dict)}
    for spec in UPGRADE_BOARD:
        rid = str(spec.get("id") or "")
        if not rid.startswith("UP-"):
            continue
        if rid not in by_sched_id:
            scheduled.append(
                {
                    "id": rid,
                    "title": spec.get("goal") or rid,
                    "cadence": spec.get("cadence") or "scheduled",
                    "status": "scheduled",
                    "win": spec.get("win") or "",
                    "form_pick": spec.get("form_pick") or "No",
                }
            )
            by_sched_id[rid] = scheduled[-1]

    # UP-* must never inflate open pending buckets
    deferred = list(reg.get("deferred") or [])
    next_phase = list(reg.get("next_phase") or [])
    reg["deferred"] = [
        r for r in deferred if not str(r.get("id") or "").startswith("UP-")
    ]
    reg["next_phase"] = [
        r for r in next_phase if not str(r.get("id") or "").startswith("UP-")
    ]

    reg["maintainer_ship"] = open_rows
    reg["scheduled_cadence"] = scheduled
    reg["maintainer_ship_closed"] = closed
    reg["updated_at"] = _now()
    reg["updated_by"] = "h2_pending_registry_reconcile_v1.py"
    reg["reconcile_at"] = reg["updated_at"]

    after = count_h2_pending(reg)
    if write:
        H2_REGISTRY.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "schema": "h2-pending-registry-reconcile-v1",
        "at": reg["updated_at"],
        "before_pending_total": before["pending_total"],
        "after_pending_total": after["pending_total"],
        "scheduled_total": after["scheduled_total"],
        "closed_moved": len(closed) - len(reg.get("maintainer_ship_closed") or []) + len(
            [r for r in closed if r not in (reg.get("maintainer_ship_closed") or [])]
        ),
        "breakdown": after,
        "path": str(H2_REGISTRY),
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Reconcile H2 pending registry")
    p.add_argument("--json", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    row = reconcile_registry(write=not args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"H2-RECONCILE: {row.get('before_pending_total')} → {row.get('after_pending_total')} "
            f"scheduled={row.get('scheduled_total')}"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

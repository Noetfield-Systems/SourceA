#!/usr/bin/env python3
"""Forge v0.2 batch drain — rank + implement pending top-20 until clear or max_cycles."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DRAIN_LOG_REL = "receipts/forge_v0.2/drain_log.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_drain_log(row: dict[str, Any], *, root: Path) -> None:
    path = root / DRAIN_LOG_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, separators=(",", ":")) + "\n")


def run_forge_v02_drain(
    *,
    max_cycles: int = 20,
    target: str = "top_20",
    root: Path | None = None,
    write_output: bool = True,
    sleep_s: float = 2.0,
) -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from forge_v02_github_v1 import run_forge_v02_from_github  # noqa: WPS433
    from forge_v02_implement_v1 import (  # noqa: WPS433
        already_implemented_ids,
        is_real_shippable_plan,
        run_forge_v02_implement,
    )
    from forge_v02_status_v1 import _top_20_ids, build_forge_v02_status, write_implement_index  # noqa: WPS433

    base = root or ROOT
    cycles: list[dict[str, Any]] = []
    consecutive_fail = 0
    limit = max(0, int(max_cycles))

    if limit == 0:
        status = build_forge_v02_status(root=base)
        return {
            "schema": "forge-v02-drain-v1",
            "at": _now(),
            "architecture": "A",
            "ok": True,
            "max_cycles": 0,
            "target": target,
            "cycles_run": 0,
            "cycles": [],
            "status": status,
            "telemetry_line": status.get("telemetry_line"),
            "for_founder": {"show_this": status.get("telemetry_line")},
        }

    forge_result = run_forge_v02_from_github(write_output=write_output, root=base)
    snapshot_top = (
        _top_20_ids(root=base)
        if target == "top_20"
        else [str(r.get("id") or "") for r in (forge_result.get("top_20") or []) if r.get("id")]
    )

    for cycle in range(1, limit + 1):
        done = already_implemented_ids(root=base)
        pending = [pid for pid in snapshot_top if pid not in done and is_real_shippable_plan(pid, root=base)]
        if not pending:
            break
        pid = pending[0]
        try:
            impl = run_forge_v02_implement(pid, root=base, write_output=write_output)
        except Exception as exc:
            impl = {"plan_id": pid, "ok": False, "status": "FAIL", "error": str(exc), "implement_mode": "fail"}
        cycle_row = {
            "cycle": cycle,
            "at": _now(),
            "plan_id": pid,
            "status": impl.get("status"),
            "implement_mode": impl.get("implement_mode"),
            "telemetry_line": impl.get("telemetry_line"),
        }
        cycles.append(cycle_row)
        if write_output:
            _append_drain_log(cycle_row, root=base)
        if impl.get("status") == "PASS":
            consecutive_fail = 0
        else:
            consecutive_fail += 1
            if consecutive_fail >= 2:
                break
        if sleep_s > 0 and cycle < limit and pending[1:]:
            time.sleep(sleep_s)

    if write_output:
        run_forge_v02_from_github(write_output=write_output, root=base)
        write_implement_index(root=base)
    status = build_forge_v02_status(root=base)
    shippable_snapshot = [pid for pid in snapshot_top if is_real_shippable_plan(pid, root=base)]
    snapshot_done = sum(1 for pid in shippable_snapshot if pid in already_implemented_ids(root=base))
    pending_final = [pid for pid in shippable_snapshot if pid not in already_implemented_ids(root=base)]
    cloud_queue_complete = bool(status.get("cloud_queue_complete"))
    ship_total = len(shippable_snapshot)
    ok = (
        cloud_queue_complete
        or (ship_total > 0 and snapshot_done >= min(18, ship_total))
        or (ship_total > 0 and len(pending_final) <= 2)
        or (ship_total > 0 and snapshot_done >= ship_total)
    )
    telemetry = (
        f"{status.get('telemetry_line')} · snapshot {snapshot_done}/{ship_total or 0} cloud-shippable shipped · drain cycles {len(cycles)}"
    )
    return {
        "schema": "forge-v02-drain-v1",
        "at": _now(),
        "architecture": "A",
        "ok": ok,
        "cloud_queue_complete": cloud_queue_complete,
        "max_cycles": limit,
        "target": target,
        "snapshot_top_count": len(snapshot_top),
        "snapshot_shippable_count": len(shippable_snapshot),
        "snapshot_shipped": snapshot_done,
        "snapshot_pending": pending_final,
        "cycles_run": len(cycles),
        "cycles": cycles,
        "status": status,
        "telemetry_line": telemetry,
        "for_founder": {"show_this": telemetry},
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--max-cycles", type=int, default=20)
    ap.add_argument("--target", default="top_20")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_forge_v02_drain(max_cycles=args.max_cycles, target=args.target)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("telemetry_line"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

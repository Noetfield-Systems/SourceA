#!/usr/bin/env python3
"""Worker factory heal — revert unproven done + sync queue/inbox/orchestrator to honest head."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
sys.path.insert(0, str(SCRIPTS))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def heal(*, deliver: bool = True, sync_queue: bool = True) -> dict:
    from registry_honest_lib_v1 import audit_registry_done, enforce_honest_registry  # noqa: WPS433
    from healthy_queue_ssot_lib import (  # noqa: WPS433
        first_open_queue_pos,
        healthy_queue_state_path,
        load_healthy_queue,
        queue_items,
        registry_status_map,
    )

    before = audit_registry_done()
    enforced = enforce_honest_registry(dry_run=False)
    after = audit_registry_done()

    queue_sync: dict = {"ok": True, "skipped": not sync_queue}
    if sync_queue:
        _, raw = load_healthy_queue()
        if raw.get("phase_strict"):
            # Cursor SSOT — registry done rows must not skip CHECK→ACT→VERIFY mid-pack.
            st_pos = 1
            if healthy_queue_state_path().is_file():
                try:
                    st_pos = int(json.loads(healthy_queue_state_path().read_text()).get("next_pos") or 1)
                except (OSError, json.JSONDecodeError, TypeError, ValueError):
                    st_pos = 1
            queue_sync = {
                "ok": True,
                "skipped": True,
                "reason": "phase_strict_cursor_ssot",
                "next_pos": st_pos,
            }
        else:
            pos = first_open_queue_pos()
            items = queue_items(raw)
            total = len(items)
            if pos > total:
                pos = max(1, total)
            item = items[pos - 1] if items and 1 <= pos <= total else {}
            state_path = healthy_queue_state_path()
            cur = 1
            if state_path.is_file():
                try:
                    cur = int(json.loads(state_path.read_text()).get("next_pos") or 1)
                except (OSError, json.JSONDecodeError, TypeError, ValueError):
                    cur = 1
            if cur != pos:
                open_item = items[pos - 1] if items and 1 <= pos <= total else {}
                cur_item = items[cur - 1] if items and 1 <= cur <= total else {}
                status = registry_status_map()
                open_sid = str(open_item.get("sa_id") or "").lower()
                # Mid-slice: broker advanced past CHECK; do not roll back to first turn of same open sa.
                if (
                    cur > pos
                    and open_sid
                    and open_sid == str(cur_item.get("sa_id") or "").lower()
                    and status.get(open_sid) != "done"
                ):
                    pos = cur
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "advance_hq", SCRIPTS / "advance-healthy-queue-v1.py"
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore[union-attr]
                queue_sync = mod.set_pos(pos, reason="worker_factory_heal")
            else:
                queue_sync = {
                    "ok": True,
                    "synced": False,
                    "next_pos": pos,
                    "sa_id": item.get("sa_id"),
                    "queue_role": item.get("queue_role"),
                }

    orch_heal: dict = {"ok": True, "skipped": True}
    try:
        from worker_stuck_recovery_v1 import sync_orchestrator_from_inbox, sync_orchestrator_from_queue  # noqa: WPS433

        orch_inbox = sync_orchestrator_from_inbox()
        orch_queue = sync_orchestrator_from_queue()
        orch_heal = {"inbox": orch_inbox, "queue": orch_queue}
    except Exception as exc:
        orch_heal = {"ok": False, "error": str(exc)}

    deliver_out: dict = {"ok": True, "skipped": not deliver}
    if deliver:
        from worker_drain_lib import healthy_drain_paste  # noqa: WPS433

        deliver_out = healthy_drain_paste()

    return {
        "ok": after.get("unproven_done", 0) == 0,
        "schema": "worker-factory-heal-v1",
        "at": _now(),
        "honest_before": before.get("honest_done"),
        "honest_after": after.get("honest_done"),
        "unproven_before": before.get("unproven_done"),
        "unproven_after": after.get("unproven_done"),
        "reverted": enforced.get("reverted_count", 0),
        "queue_sync": queue_sync,
        "orchestrator": orch_heal,
        "deliver": deliver_out,
        "law": "REGISTRY done requires receipt — queue head = first open sa",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--no-deliver", action="store_true")
    p.add_argument("--no-queue-sync", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = heal(deliver=not args.no_deliver, sync_queue=not args.no_queue_sync)
    if args.json or True:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

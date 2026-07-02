#!/usr/bin/env python3
"""Signal Factory v1 — 24/7 disk-queue tick motor (synthetic · no real inbox).

Receipt: ~/.sina/signal-factory-tick-receipt-v1.json
Per-signal reports: receipts/signal-factory/<id>.json
Law: data/signal-factory-v1.json · controlled-autorun L2 IDLE_NO_WORK is healthy.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data/signal-factory-v1.json"
QUEUE = ROOT / "data/signal-factory-queue-v1.json"
SEED = ROOT / "data/signal-factory-synthetic-seed-v1.json"
RECEIPT = SINA / "signal-factory-tick-receipt-v1.json"
REPORT_DIR = ROOT / "receipts/signal-factory"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _load_core():
    sys.path.insert(0, str(SCRIPTS))
    from signal_factory_core_v1 import analyze_signal, verify_report  # noqa: WPS433

    return analyze_signal, verify_report


def replenish_queue(queue: dict[str, Any]) -> int:
    if not queue.get("replenish_synthetic", True):
        return 0
    seed = _read_json(SEED)
    items = seed.get("items") or []
    if not items:
        return 0
    seed_ids = {str(x.get("id") or "") for x in items if x.get("id")}
    done = set(queue.get("done") or [])
    pending_ids = {str(x.get("id")) for x in (queue.get("pending") or [])}

    # 24/7 synthetic cycle — when full seed set is consumed, rotate for next cron tick.
    if seed_ids and seed_ids <= done and not pending_ids:
        queue["done"] = []
        queue["pending"] = list(items)
        return len(items)

    added = 0
    for item in items:
        item_id = str(item.get("id") or "")
        if not item_id or item_id in done or item_id in pending_ids:
            continue
        queue.setdefault("pending", []).append(item)
        pending_ids.add(item_id)
        added += 1
    return added


def run_tick(
    *,
    write: bool = True,
    max_batch: int = 5,
    trigger_source: str = "cli",
    cloud_primary: bool = False,
) -> dict[str, Any]:
    ssot = _read_json(SSOT)
    max_batch = int(max_batch or ssot.get("tick", {}).get("max_batch") or 5)

    queue = _read_json(QUEUE)
    if queue.get("schema") != "signal-factory-queue-v1":
        queue = {
            "schema": "signal-factory-queue-v1",
            "replenish_synthetic": True,
            "pending": [],
            "done": [],
        }

    replenished = 0
    if not (queue.get("pending") or []):
        replenished = replenish_queue(queue)

    pending = list(queue.get("pending") or [])
    if not pending:
        row = {
            "schema": "signal-factory-tick-receipt-v1",
            "ok": True,
            "at": _now(),
            "decision": "IDLE_NO_WORK",
            "processed": 0,
            "replenished": replenished,
            "trigger_source": trigger_source,
            "execution_plane": "headless_cloud" if cloud_primary else "local_tick",
            "mac_role": "control_plane_only",
            "production_connected": False,
            "signal_factory_line": "signal-factory · IDLE_NO_WORK · synthetic queue empty",
            "next_founder_action": "Hub glance only · no Gmail · seed queue when ready",
        }
        if write:
            SINA.mkdir(parents=True, exist_ok=True)
            _write_json(RECEIPT, row)
        return row

    analyze_signal, verify_report = _load_core()
    batch = pending[:max_batch]
    results: list[dict[str, Any]] = []

    for item in batch:
        item_id = str(item.get("id") or "unknown")
        report = analyze_signal(
            str(item.get("text") or ""),
            entity_scope=item.get("entity_scope"),
            sender_claims=item.get("sender_claims"),
        )
        verification = verify_report(report)
        ok = bool(verification.get("ok"))
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        _write_json(REPORT_DIR / f"{item_id}.json", report)
        results.append(
            {
                "id": item_id,
                "ok": ok,
                "decision": report.get("decision"),
                "classification": report.get("classification"),
                "entity_scope": (report.get("receipt") or {}).get("entity_scope"),
                "errors": verification.get("errors") or [],
            }
        )

    ok_ids = [r["id"] for r in results if r.get("ok")]
    fail_ids = [r["id"] for r in results if not r.get("ok")]
    queue["pending"] = pending[max_batch:]
    queue.setdefault("done", []).extend(ok_ids)
    if replenished:
        queue["replenish_synthetic"] = True
    if not (queue.get("pending") or []):
        replenish_queue(queue)

    decision = "COMPLETE" if results and not fail_ids else ("PARTIAL" if results else "IDLE_NO_WORK")
    processed = len(results)
    line = (
        f"signal-factory · {decision} · processed={processed} · "
        f"ok={len(ok_ids)} fail={len(fail_ids)} · pending={len(queue.get('pending') or [])}"
    )

    row = {
        "schema": "signal-factory-tick-receipt-v1",
        "ok": decision in ("COMPLETE", "PARTIAL") or processed == 0,
        "at": _now(),
        "decision": decision,
        "processed": processed,
        "replenished": replenished,
        "trigger_source": trigger_source,
        "execution_plane": "headless_cloud" if cloud_primary else "local_tick",
        "mac_role": "control_plane_only",
        "production_connected": False,
        "max_batch": max_batch,
        "results": results,
        "queue_pending": len(queue.get("pending") or []),
        "queue_done": len(queue.get("done") or []),
        "signal_factory_line": line,
        "next_founder_action": "Hub glance only · synthetic signal factory tick · no Gmail",
    }

    if write:
        _write_json(QUEUE, queue)
        SINA.mkdir(parents=True, exist_ok=True)
        _write_json(RECEIPT, row)
    return row


def run_tick_cloud_first(*, write: bool = True, max_batch: int = 5, trigger_source: str = "hub") -> dict:
    sys.path.insert(0, str(SCRIPTS))
    try:
        from cloud_signal_factory_client_v1 import tick_via_cloud  # noqa: WPS433

        cloud = tick_via_cloud(max_batch=max_batch, trigger_source=trigger_source, write_receipt=False)
        if cloud.get("ok") and cloud.get("signal_factory_line"):
            raw = cloud.get("raw") or {}
            row = {
                "schema": "signal-factory-tick-receipt-v1",
                "ok": True,
                "at": _now(),
                "execution_plane": "headless_cloud",
                "cloud_primary": True,
                "mac_role": "control_plane_only",
                "trigger_source": trigger_source,
                "decision": raw.get("decision") or cloud.get("decision"),
                "processed": raw.get("processed", 0),
                "signal_factory_line": cloud.get("signal_factory_line"),
                "next_founder_action": cloud.get("next_founder_action"),
                "raw": raw,
            }
            if write:
                SINA.mkdir(parents=True, exist_ok=True)
                _write_json(RECEIPT, row)
            return row
    except Exception as exc:
        fallback = run_tick(write=write, max_batch=max_batch, trigger_source=f"{trigger_source}_local_fallback")
        fallback["cloud_error"] = str(exc)[:200]
        fallback["cloud_primary"] = False
        return fallback

    return run_tick(write=write, max_batch=max_batch, trigger_source=trigger_source)


def handle_hub_post(body: dict | None = None) -> dict:
    body = body or {}
    max_batch = int(body.get("max_batch") or 5)
    return run_tick_cloud_first(write=True, max_batch=max_batch, trigger_source="hub")


def main() -> int:
    ap = argparse.ArgumentParser(description="Signal Factory v1 tick motor")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--max-batch", type=int, default=5)
    ap.add_argument("--local-only", action="store_true", help="Skip cloud proxy")
    args = ap.parse_args()

    if args.local_only:
        row = run_tick(write=not args.no_write, max_batch=args.max_batch, trigger_source="cli_local")
    else:
        row = run_tick_cloud_first(write=not args.no_write, max_batch=args.max_batch, trigger_source="cli")

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("signal_factory_line") or row.get("decision"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())

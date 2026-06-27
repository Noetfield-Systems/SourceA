#!/usr/bin/env python3
"""Legacy helper for healthy queue refill.

Current law: all-plan backlog execution belongs to Cloud Workers.app/CF cron,
not Worker INBOX. By default this CLI delegates to
refill_cloud_forge_run_from_backlog_v1.py, which writes a 100-row Cloud Forge
Run batch. Use --legacy-healthy only for old tests or archived Goal1 flows.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
BACKLOG = ROOT / "data" / "all-remaining-plan-backlog-v1.json"
QUEUE_HOME = SINA / "healthy-queue-30-active.json"
STATE_HOME = SINA / "healthy-queue-state-v1.json"
QUEUE_REPO = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "prompts" / "healthy-queue-30-active.json"
STATE_REPO = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "prompts" / "healthy-queue-state-v1.json"
INBOX_JSON = SINA / "worker-prompt-inbox-v1.json"
INBOX_MD = ROOT / ".sina-loop" / "INBOX.md"
RECEIPT = SINA / "all-remaining-plan-backlog-refill-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
        return row if isinstance(row, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _existing_sa_floor() -> int:
    """Choose a fresh sa-* block without colliding with visible queues."""
    max_seen = 2000
    candidates = [
        QUEUE_HOME,
        QUEUE_REPO,
        ROOT / "data" / "forge-factory-queue-cycle2-v1.json",
        ROOT / "data" / "plans-unified-worker-queue-v1.json",
        ROOT / "data" / "outbound-factory-worker-queue-v1.json",
    ]
    pat = re.compile(r"\bsa-(\d{4,})\b", re.I)
    for path in candidates:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in pat.finditer(text):
            max_seen = max(max_seen, int(match.group(1)))
    return max_seen + 1


def _instruction(item: dict[str, Any]) -> str:
    prompt_path = str(item.get("prompt_path") or "").strip()
    prompt_hint = f" Prompt: {prompt_path}." if prompt_path else ""
    verify = str(item.get("verify") or "").strip()
    verify_hint = f" Verify: {verify}." if verify else ""
    return (
        f"ACT - {item.get('plan_id')}: {item.get('title')}.{prompt_hint} "
        f"Source registry: {item.get('source_registry')}. Preserve lane={item.get('lane')}. "
        f"One bounded Worker turn; write receipt/proof before closeout.{verify_hint}"
    )


def _queue_item(item: dict[str, Any], *, pos: int, sa_num: int) -> dict[str, Any]:
    return {
        "queue_pos": pos,
        "hp_id": f"allq-{pos:03d}",
        "queue_role": "act",
        "step_type": "act",
        "sa_id": f"sa-{sa_num:04d}",
        "phase": "phase-all-remaining-plan-backlog-v1",
        "title": f"[ACT] {item.get('plan_id')} - {item.get('title')}",
        "instruction": _instruction(item),
        "closeout": False,
        "one_sa_per_turn": True,
        "backlog_index": item.get("backlog_index"),
        "plan_id": item.get("plan_id"),
        "source_registry": item.get("source_registry"),
        "prompt_path": item.get("prompt_path"),
        "lane": item.get("lane"),
        "tier": item.get("tier"),
        "status": item.get("status"),
    }


def _deliver_inbox(head: dict[str, Any], *, total: int) -> dict[str, Any]:
    prompt = (
        f"WORK: {head['sa_id']} - {head.get('title')}\n\n"
        f"{head.get('instruction')}\n\n"
        "Rules: execute one plan only, preserve lane boundaries, write receipt/proof, "
        "then stop with WORKER_ROUND_REPORT."
    )
    meta = {
        "sa_id": head["sa_id"],
        "queue_role": head.get("queue_role"),
        "queue_pos": head.get("queue_pos"),
        "queue_total": total,
        "phase": head.get("phase"),
        "plan_id": head.get("plan_id"),
        "backlog_index": head.get("backlog_index"),
        "source_registry": head.get("source_registry"),
        "queue_exhausted": False,
    }
    payload = {
        "schema": "worker-prompt-inbox-v1",
        "pending": True,
        "delivered_at": _now(),
        "source": "all_remaining_plan_backlog_refill",
        "lane": "sourcea_worker",
        "workspace": str(ROOT),
        "chars": len(prompt),
        "prompt": prompt,
        "meta": meta,
        "sa_id": head["sa_id"],
        "pickup": {
            "founder_line": "Founder says RUN INBOX - read disk; no Terminal required",
            "inbox_json": str(INBOX_JSON),
            "inbox_md": str(INBOX_MD),
            "law": "RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md",
        },
    }
    _write_json(INBOX_JSON, payload)
    md = f"""<!-- WORKER_INBOX pending=1 source=all_remaining_plan_backlog_refill queue={head.get('queue_pos')}/{total} role={head.get('queue_role')} sa={head.get('sa_id')} -->
# SourceA Worker - prompt ready (all-plan backlog)

**Lane:** SourceA Worker only.

**Updated:** {payload["delivered_at"]}

---

{prompt}

---

**Worker:** execute fully, write receipt/proof, `WORKER_ROUND_REPORT`, STOP.
"""
    INBOX_MD.parent.mkdir(parents=True, exist_ok=True)
    INBOX_MD.write_text(md, encoding="utf-8")
    return {"ok": True, "sa_id": head["sa_id"], "path": str(INBOX_JSON), "md": str(INBOX_MD)}


def refill(*, window_size: int = 30, start_sa: int | None = None, write: bool = True) -> dict[str, Any]:
    backlog = _read_json(BACKLOG)
    items = backlog.get("items") or []
    if not isinstance(items, list) or not items:
        raise SystemExit(f"FAIL: missing backlog items at {BACKLOG}; run build_all_remaining_plan_backlog_v1.py")
    start = start_sa or _existing_sa_floor()
    active = items[: max(1, int(window_size))]
    queue = [_queue_item(item, pos=idx, sa_num=start + idx - 1) for idx, item in enumerate(active, start=1)]
    sa_range = [queue[0]["sa_id"], queue[-1]["sa_id"]] if queue else []
    now = _now()
    doc = {
        "schema": "healthy-queue-30-active.v1",
        "product": "SourceA all remaining plans - rolling Worker queue",
        "thread": "ALL-PLANS-BACKLOG",
        "repo": "sourcea",
        "count": len(queue),
        "rhythm": "rolling 30 from all-remaining-plan-backlog-v1; one sa per Worker turn",
        "law": "data/all-remaining-plan-backlog-v1.json",
        "generated_at": now,
        "phase": "phase-all-remaining-plan-backlog-v1",
        "plans_unified": True,
        "phase_strict": False,
        "phase_strict_complete": False,
        "queue_exhausted": False,
        "queue_window": {
            "start_backlog_index": queue[0].get("backlog_index") if queue else None,
            "end_backlog_index": queue[-1].get("backlog_index") if queue else None,
            "window_size": len(queue),
            "backlog_total": backlog.get("total_remaining"),
            "remaining_after_window": max(0, int(backlog.get("total_remaining") or 0) - len(queue)),
        },
        "sa_range": sa_range,
        "queue": queue,
    }
    state = {
        "schema": "healthy-queue-state-v1",
        "next_pos": 1,
        "queue_exhausted": False,
        "last_advanced_at": now,
        "last_completed_pos": 0,
        "reset_by": "refill_healthy_queue_from_backlog_v1",
        "backlog_path": str(BACKLOG),
        "active_window_size": len(queue),
    }
    inbox = {"ok": False, "skipped": True}
    if write:
        for path in (QUEUE_HOME, QUEUE_REPO):
            _write_json(path, doc)
        for path in (STATE_HOME, STATE_REPO):
            _write_json(path, state)
        if queue:
            inbox = _deliver_inbox(queue[0], total=len(queue))
        receipt = {
            "schema": "all-remaining-plan-backlog-refill-v1",
            "ok": True,
            "at": now,
            "queue_path": str(QUEUE_HOME),
            "state_path": str(STATE_HOME),
            "repo_queue_path": str(QUEUE_REPO),
            "backlog_path": str(BACKLOG),
            "backlog_total": backlog.get("total_remaining"),
            "active_count": len(queue),
            "sa_range": sa_range,
            "head": queue[0] if queue else None,
            "remaining_after_window": doc["queue_window"]["remaining_after_window"],
            "inbox": inbox,
        }
        _write_json(RECEIPT, receipt)
    return {
        "ok": True,
        "schema": "all-remaining-plan-backlog-refill-v1",
        "at": now,
        "backlog_total": backlog.get("total_remaining"),
        "active_count": len(queue),
        "sa_range": sa_range,
        "head": queue[0] if queue else None,
        "remaining_after_window": doc["queue_window"]["remaining_after_window"],
        "inbox": inbox,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--window-size", type=int, default=30)
    ap.add_argument("--start-sa", type=int, default=0)
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--legacy-healthy", action="store_true")
    args = ap.parse_args()
    if not args.legacy_healthy:
        from refill_cloud_forge_run_from_backlog_v1 import refill as refill_cloud  # noqa: WPS433

        row = refill_cloud(write=not args.no_write)
        row["delegated_from"] = "refill_healthy_queue_from_backlog_v1"
        row["legacy_healthy_skipped"] = True
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(
                f"CLOUD_FORGE_BACKLOG ok head={row['head']} batch={row['batch_id']} "
                f"rows={row['rows_per_turn']} tasks_per_row={row['tasks_per_row']}"
            )
        return 0
    row = refill(
        window_size=args.window_size,
        start_sa=args.start_sa or None,
        write=not args.no_write,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"REFILL ok head={row.get('head', {}).get('sa_id')} active={row.get('active_count')} total={row.get('backlog_total')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

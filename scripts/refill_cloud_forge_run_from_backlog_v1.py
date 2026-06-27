#!/usr/bin/env python3
"""Build the next Cloud Forge Run 100-row batch from the all-plan backlog.

Founder law: one Auto Runtime trigger (~10 min) sends one Cloud Forge Run POST.
That POST must hand Railway 100 CLOUD rows. Each row here carries a 100-task
plan pack, so Mac remains observe-only and Worker INBOX stays out of the path.
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
ACTIVE_POINTER = ROOT / "data" / "cloud-forge-run-queue-active-v1.json"
CONTROL_PLANE = ROOT / "data" / "cloud-workers-control-plane-v1.json"
FULL_PACK = ROOT / "data" / "cloud-forge-run-full-pack-pattern-v1.json"
VOCAB = ROOT / "data" / "cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json"
QUEUE_HOME = SINA / "healthy-queue-30-active.json"
STATE_HOME = SINA / "healthy-queue-state-v1.json"
QUEUE_REPO = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "prompts" / "healthy-queue-30-active.json"
STATE_REPO = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "prompts" / "healthy-queue-state-v1.json"
PHASE = SINA / "phase-observed-v1.json"
FACTORY_NOW = SINA / "factory-now-v1.json"
RUN_INBOX_TRUTH = SINA / "run-inbox-disk-truth-v1.json"
LIVE_SURFACES = SINA / "agent-live-surfaces-v1.json"
INBOX_JSON = SINA / "worker-prompt-inbox-v1.json"
INBOX_MD = ROOT / ".sina-loop" / "INBOX.md"
RECEIPT = SINA / "cloud-forge-run-backlog-refill-v1.json"

ROWS_PER_TURN = 100
TASKS_PER_ROW = 100
MAC_CONTROL_ROWS = 10


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
        return row if isinstance(row, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _last_cloud_sec() -> int:
    seen = 6966
    for path in sorted((ROOT / "data").glob("secondary-cloud-forge-run-batch-*-locked-v1.json")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in re.finditer(r"\bCLOUD-SEC-(\d+)\b", text):
            seen = max(seen, int(match.group(1)))
    ptr = _read(ACTIVE_POINTER)
    for key in ("cloud_sec_range",):
        text = str(ptr.get(key) or "")
        for match in re.finditer(r"CLOUD-SEC-(\d+)", text):
            seen = max(seen, int(match.group(1)))
    reset = ptr.get("phase_reset") if isinstance(ptr.get("phase_reset"), dict) else {}
    for key in ("cloud_forge_run_head", "cloud_forge_run_last_completed"):
        text = str(reset.get(key) or "")
        match = re.search(r"CLOUD-SEC-(\d+)", text)
        if match:
            seen = max(seen, int(match.group(1)))
    return seen


def _next_batch_id() -> int:
    ptr = _read(ACTIVE_POINTER)
    return max(71, int(ptr.get("batch_id") or 70) + 1)


def _pack_ref(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "backlog_index": item.get("backlog_index"),
        "plan_id": item.get("plan_id"),
        "title": item.get("title"),
        "lane": item.get("lane"),
        "tier": item.get("tier"),
        "status": item.get("status"),
        "source_registry": item.get("source_registry"),
        "prompt_path": item.get("prompt_path"),
    }


def _mac_control_rows(batch_id: int, first_cloud: int) -> list[dict[str, Any]]:
    rows = []
    for idx in range(1, MAC_CONTROL_ROWS + 1):
        rows.append(
            {
                "n": idx,
                "id": f"MAC-CTL-B{batch_id}-{idx:02d}",
                "bind": f"W-CLOUD-B{batch_id}-{idx:02d}" if idx <= 3 else None,
                "plane": "mac_control",
                "batch_id": batch_id,
                "mac_role": "observe · Cloud Workers.app/CF cron only · read receipt; no Mac body",
                "mac_build_forbidden": True,
                "mac_executes_plan_body": False,
                "title": (
                    f"Mac control observe for backlog batch {batch_id}: "
                    f"CLOUD-SEC-{first_cloud:04d}..CLOUD-SEC-{first_cloud + ROWS_PER_TURN - 1:04d}"
                ),
            }
        )
    return rows


def _cloud_row(*, n: int, cloud_num: int, batch_id: int, pack_items: list[dict[str, Any]]) -> dict[str, Any]:
    first = pack_items[0]
    last = pack_items[-1]
    pack_no = n - MAC_CONTROL_ROWS
    return {
        "n": n,
        "id": f"CLOUD-SEC-{cloud_num:04d}",
        "maps_registry": f"allq-pack-{pack_no:04d}",
        "plane": "cloud_forge",
        "batch_id": batch_id,
        "mac_executes_plan_body": False,
        "": "All remaining SourceA plan backlog",
        "workstream": "ws-backlog-pack",
        "tier": str(first.get("tier") or "T0"),
        "cost_tier": "openrouter_cap",
        "cloud_action": (
            f"Cloud execute all-plan backlog pack {pack_no:04d}: "
            f"{first.get('plan_id')}..{last.get('plan_id')} ({len(pack_items)} tasks)"
        ),
        "task_pack": {
            "schema": "all-remaining-plan-task-pack-v1",
            "pack_index": pack_no,
            "tasks_per_row": TASKS_PER_ROW,
            "count": len(pack_items),
            "backlog_index_start": first.get("backlog_index"),
            "backlog_index_end": last.get("backlog_index"),
            "items": [_pack_ref(item) for item in pack_items],
        },
    }


def _clear_worker_queue(*, head: str, batch_id: int, batch_path: Path, backlog_total: int) -> None:
    now = _now()
    queue_doc = {
        "schema": "healthy-queue-30-active.v1",
        "product": "Cloud Workers owns all-plan backlog packs",
        "thread": "CLOUD-FORGE-RUN",
        "repo": "sourcea",
        "count": 0,
        "generated_at": now,
        "phase_strict": False,
        "phase_strict_complete": True,
        "queue_exhausted": True,
        "execution_plane": "cloud_workers_app_and_cloudflare_cron",
        "cloud_forge_run": {
            "head": head,
            "batch_id": batch_id,
            "queue_path": str(batch_path.relative_to(ROOT)),
            "rows_per_turn": ROWS_PER_TURN,
            "tasks_per_row": TASKS_PER_ROW,
            "task_capacity_this_turn": ROWS_PER_TURN * TASKS_PER_ROW,
            "backlog_total": backlog_total,
        },
        "stop_reason": "worker_inbox_not_execution_queue_for_cloud_forge_run",
        "sa_range": [],
        "queue": [],
    }
    state_doc = {
        "schema": "healthy-queue-state-v1",
        "next_pos": 1,
        "queue_exhausted": True,
        "last_advanced_at": now,
        "last_completed_pos": 0,
        "reset_by": "refill_cloud_forge_run_from_backlog_v1",
        "reason": "Cloud Workers.app/CF cron owns 100-row Cloud Forge Run packs",
    }
    for path in (QUEUE_HOME, QUEUE_REPO):
        _write(path, queue_doc)
    for path in (STATE_HOME, STATE_REPO):
        _write(path, state_doc)
    prompt = (
        "INBOX cleared - Cloud Forge Run backlog packs are not Worker INBOX tasks.\n"
        f"Cloud Workers.app/CF cron owns execution: {head} batch {batch_id}, "
        f"100 rows per turn, {TASKS_PER_ROW} tasks per row.\n"
    )
    _write(
        INBOX_JSON,
        {
            "schema": "worker-prompt-inbox-v1",
            "pending": False,
            "delivered_at": now,
            "source": "refill_cloud_forge_run_from_backlog_v1",
            "lane": "cloud_workers",
            "workspace": str(ROOT),
            "chars": len(prompt),
            "prompt": prompt,
            "meta": {
                "sa_id": "",
                "queue_role": "",
                "queue_pos": 0,
                "queue_total": 0,
                "queue_exhausted": True,
                "cloud_forge_run_head": head,
                "batch_id": batch_id,
            },
        },
    )
    INBOX_MD.parent.mkdir(parents=True, exist_ok=True)
    INBOX_MD.write_text(
        f"""<!-- WORKER_INBOX pending=0 source=cloud_forge_run_backlog head={head} -->
# SourceA Worker - no Worker INBOX task

Cloud Workers.app / Cloudflare cron owns the all-plan backlog now.

- Head: `{head}`
- Batch: `{batch_id}`
- Shape: `100` Cloud Forge Run rows per trigger, `{TASKS_PER_ROW}` tasks per row
- Queue file: `{batch_path.relative_to(ROOT)}`
""",
        encoding="utf-8",
    )


def _sync_surfaces(*, head: str, last_before: str, batch_id: int, batch_path: Path, backlog_total: int) -> None:
    now = _now()
    phase = _read(PHASE)
    phase.update(
        {
            "schema": "phase-observed-v1",
            "cloud_forge_run_head": head,
            "cloud_forge_run_last_completed": last_before,
            "queue_batch_complete": False,
            "registry_exhausted": False,
            "batch_id": batch_id,
            "rows_per_turn": ROWS_PER_TURN,
            "tasks_per_row": TASKS_PER_ROW,
            "queue_path": str(batch_path.relative_to(ROOT)),
            "rebuilt_at": now,
            "rebuilt_by": "refill_cloud_forge_run_from_backlog_v1",
        }
    )
    _write(PHASE, phase)
    line = (
        f"factory-now · Cloud Workers.app owns Cloud Forge Run · head {head} · "
        f"batch {batch_id} · 100 rows/10min · {TASKS_PER_ROW} tasks/row"
    )
    factory = _read(FACTORY_NOW)
    factory.update(
        {
            "schema": "factory-now-v1",
            "at": now,
            "mode": "FREEZE",
            "execution_surface": "cloud_workers_app_cf_cron",
            "queue_sa": head,
            "inbox_sa": "",
            "cloud_forge_run_head": head,
            "cloud_forge_run_batch_id": batch_id,
            "cloud_forge_run_queue_path": str(batch_path.relative_to(ROOT)),
            "rows_per_turn": ROWS_PER_TURN,
            "tasks_per_row": TASKS_PER_ROW,
            "line": line,
        }
    )
    _write(FACTORY_NOW, factory)
    truth = _read(RUN_INBOX_TRUTH)
    truth.update(
        {
            "schema": "run-inbox-disk-truth-v1",
            "at": now,
            "execution_lane": "cloud_workers_app_cf_cron",
            "next_steps_lane": "cloud_workers_app",
            "queue": {
                "phase_strict": False,
                "pos": 1,
                "total": ROWS_PER_TURN,
                "sa_id": head,
                "role": "cloud_forge_run_pack",
                "phase": "cloud-forge-run-backlog-pack-v1",
                "queue_exhausted": False,
                "batch_id": batch_id,
                "queue_path": str(batch_path.relative_to(ROOT)),
                "rows_per_turn": ROWS_PER_TURN,
                "tasks_per_row": TASKS_PER_ROW,
            },
            "inbox": {
                "pending": False,
                "sa_id": "",
                "truth_match": True,
                "execution_mode": "cloud_workers_app",
            },
            "you_are_here": {
                "sa_id": head,
                "queue_pos": 1,
                "queue_total": ROWS_PER_TURN,
                "role": "cloud_forge_run_pack",
                "queue_exhausted": False,
                "label": "Cloud Workers.app / CF cron",
            },
        }
    )
    _write(RUN_INBOX_TRUTH, truth)
    live = _read(LIVE_SURFACES) or {"schema": "agent-live-surfaces-v1"}
    live.update(
        {
            "schema": "agent-live-surfaces-v1",
            "synced_at": now,
            "truth_bundle_at": now,
            "factory_now_line": line,
            "mode": "FREEZE",
            "queue_sa": head,
            "execution_surface": "Cloud Workers.app :13027 + Cloudflare cron",
            "inject_execution_path": (
                f"Cloud Forge Run backlog pack · {head} · batch {batch_id} · "
                f"100 rows per trigger · {TASKS_PER_ROW} tasks per row"
            ),
            "dual_pick": {
                "queue_sa": head,
                "live_pick_sa": head,
                "aligned": True,
                "idle": False,
            },
            "all_plan_backlog": {
                "backlog_total": backlog_total,
                "active_cloud_rows": ROWS_PER_TURN,
                "tasks_per_row": TASKS_PER_ROW,
                "active_task_capacity": ROWS_PER_TURN * TASKS_PER_ROW,
                "queue_path": str(batch_path.relative_to(ROOT)),
            },
            "surface_repaired_at": now,
            "surface_repair_reason": "replace stale 30 Worker queue with Cloud Forge Run 100-row pack",
        }
    )
    _write(LIVE_SURFACES, live)


def refill(*, write: bool = True) -> dict[str, Any]:
    backlog = _read(BACKLOG)
    items = backlog.get("items") or []
    if not isinstance(items, list) or not items:
        raise SystemExit(f"FAIL: missing backlog items at {BACKLOG}")

    batch_id = _next_batch_id()
    first_cloud_num = _last_cloud_sec() + 1
    last_cloud_num = first_cloud_num + ROWS_PER_TURN - 1
    batch_path = ROOT / "data" / f"secondary-cloud-forge-run-batch-{batch_id}-locked-v1.json"
    capacity = ROWS_PER_TURN * TASKS_PER_ROW
    selected = items[:capacity]
    cloud_rows: list[dict[str, Any]] = []
    for row_idx in range(ROWS_PER_TURN):
        start = row_idx * TASKS_PER_ROW
        pack_items = selected[start : start + TASKS_PER_ROW]
        if not pack_items:
            break
        cloud_rows.append(
            _cloud_row(
                n=MAC_CONTROL_ROWS + row_idx + 1,
                cloud_num=first_cloud_num + row_idx,
                batch_id=batch_id,
                pack_items=pack_items,
            )
        )

    now = _now()
    doc = {
        "schema": "secondary-cloud-forge-run-batch-v1",
        "version": "3.0.0",
        "batch_id": batch_id,
        "stack": "sourcea",
        "library": "all-remaining-plan-backlog",
        "locked": True,
        "edit_forbidden": True,
        "saved_at": now,
        "authority": "INCIDENT-042/043/044 · Cloud Workers.app full-pack 100 rows",
        "one_law": "One Auto Runtime trigger (~10 min) = one Cloud Forge Run POST = 100 rows; each row carries a 100-task backlog pack.",
        "forbidden": [
            "Worker INBOX per plan",
            "30 hot queue for all-plan backlog",
            "one plan per row on Mac",
            "Mac executes plan bodies",
        ],
        "generator": "scripts/refill_cloud_forge_run_from_backlog_v1.py",
        "registry_path": str(BACKLOG.relative_to(ROOT)),
        "registry_count": backlog.get("total_remaining"),
        "count": MAC_CONTROL_ROWS + len(cloud_rows),
        "summary": {
            "mac_control": MAC_CONTROL_ROWS,
            "cloud_forge": len(cloud_rows),
            "batch_id": batch_id,
            "rows_per_turn": ROWS_PER_TURN,
            "tasks_per_row": TASKS_PER_ROW,
            "task_capacity_this_turn": len(selected),
            "backlog_total": backlog.get("total_remaining"),
            "remaining_after_this_turn": max(0, int(backlog.get("total_remaining") or 0) - len(selected)),
            "cloud_sec_range": f"CLOUD-SEC-{first_cloud_num:04d}..CLOUD-SEC-{last_cloud_num:04d}",
        },
        "plans": _mac_control_rows(batch_id, first_cloud_num) + cloud_rows,
    }
    ptr = _read(ACTIVE_POINTER)
    archives = {k: v for k, v in ptr.items() if str(k).startswith("archive_batch")}
    if ptr.get("queue_path"):
        archives[f"archive_batch{ptr.get('batch_id') or batch_id - 1}"] = ptr.get("queue_path")
    pointer = {
        "schema": "cloud-forge-run-queue-active-v1",
        "version": "1.4.0",
        "batch_id": batch_id,
        "locked": True,
        "saved_at": now,
        "queue_path": str(batch_path.relative_to(ROOT)),
        **archives,
        "drain_status": "all_plan_backlog_active",
        "registry_exhausted": False,
        "queue_batch_complete": False,
        "cloud_sec_range": f"CLOUD-SEC-{first_cloud_num:04d}..CLOUD-SEC-{last_cloud_num:04d}",
        "maps_registry": "all-remaining-plan-backlog",
        "rows_per_turn": ROWS_PER_TURN,
        "tasks_per_row": TASKS_PER_ROW,
        "source_backlog": str(BACKLOG.relative_to(ROOT)),
        "phase_reset": {
            "cloud_forge_run_head": f"CLOUD-SEC-{first_cloud_num:04d}",
            "cloud_forge_run_last_completed": f"CLOUD-SEC-{first_cloud_num - 1:04d}",
            "queue_batch_complete": False,
        },
        "cloud_workers_feed": {
            "machine": "scripts/cloud_workers_hub_v1.py",
            "control_plane": "data/cloud-workers-control-plane-v1.json",
            "auto_runtime": "data/cloud-auto-runtime-v1.json",
        },
        "proof_url": "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1",
    }
    cp = _read(CONTROL_PLANE)
    cp.update(
        {
            "schema": cp.get("schema") or "cloud-workers-control-plane-v1",
            "version": "1.4.0",
            "saved_at": now,
            "one_law": (
                "Cloud Workers (:13027) is the founder cockpit for Railway + CF cron. "
                "Cloud Forge Run full-pack only — 100 rows per trigger every 10 min; "
                "all-plan backlog rows carry 100 tasks per row."
            ),
            "active_batch": {
                "batch_id": batch_id,
                "locked": True,
                "status": "ACTIVE",
                "head": f"CLOUD-SEC-{first_cloud_num:04d}",
                "last_completed": f"CLOUD-SEC-{first_cloud_num - 1:04d}",
                "queue_batch_complete": False,
                "maps_registry_range": "all-remaining-plan-backlog",
                "cloud_sec_range": f"CLOUD-SEC-{first_cloud_num:04d}..CLOUD-SEC-{last_cloud_num:04d}",
                "rows_per_turn": ROWS_PER_TURN,
                "tasks_per_row": TASKS_PER_ROW,
                "queue_path": str(batch_path.relative_to(ROOT)),
            },
            "ready_batch": None,
        }
    )
    receipt = {
        "schema": "cloud-forge-run-backlog-refill-v1",
        "ok": True,
        "at": now,
        "backlog_total": backlog.get("total_remaining"),
        "batch_id": batch_id,
        "queue_path": str(batch_path),
        "cloud_sec_range": pointer["cloud_sec_range"],
        "head": pointer["phase_reset"]["cloud_forge_run_head"],
        "last_completed": pointer["phase_reset"]["cloud_forge_run_last_completed"],
        "rows_per_turn": ROWS_PER_TURN,
        "tasks_per_row": TASKS_PER_ROW,
        "active_task_capacity": len(selected),
        "remaining_after_this_turn": doc["summary"]["remaining_after_this_turn"],
        "cloud_workers_app": "http://127.0.0.1:13027/",
        "cf_cron": "*/10 * * * *",
        "law": [
            str(FULL_PACK.relative_to(ROOT)),
            str(VOCAB.relative_to(ROOT)),
        ],
    }
    if write:
        _write(batch_path, doc)
        _write(ACTIVE_POINTER, pointer)
        _write(CONTROL_PLANE, cp)
        _clear_worker_queue(
            head=receipt["head"],
            batch_id=batch_id,
            batch_path=batch_path,
            backlog_total=int(backlog.get("total_remaining") or 0),
        )
        _sync_surfaces(
            head=receipt["head"],
            last_before=receipt["last_completed"],
            batch_id=batch_id,
            batch_path=batch_path,
            backlog_total=int(backlog.get("total_remaining") or 0),
        )
        _write(RECEIPT, receipt)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = refill(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"CLOUD_FORGE_BACKLOG ok head={row['head']} batch={row['batch_id']} "
            f"rows={row['rows_per_turn']} tasks_per_row={row['tasks_per_row']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

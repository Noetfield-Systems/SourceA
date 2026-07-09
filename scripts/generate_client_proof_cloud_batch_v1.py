#!/usr/bin/env python3
"""Generate Cloud Forge batch from client-proof recipe queue — 1 recipe per CLOUD-SEC row.

Law: data/client-proof-recipe-rubric-v1.json
Each CLOUD-SEC row carries full GOAL/DONE/VERIFY/proof_artifact for client demo.
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
QUEUE = ROOT / "data" / "client-proof-recipe-queue-v1.json"
ACTIVE_POINTER = ROOT / "data" / "cloud-forge-run-queue-active-v1.json"
CONTROL_PLANE = ROOT / "data" / "cloud-workers-control-plane-v1.json"
RECEIPT = SINA / "client-proof-cloud-batch-v1.json"

MAC_CONTROL_ROWS = 10
# Batch file may hold many CLOUD-SEC rows; motor advances 1 row per */10 tick (INCIDENT-045).
MOTOR_ROWS_PER_TICK = 1


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


def _last_cloud_num(*, before_batch: int) -> int:
    """Max CLOUD-SEC id from actual batch plan rows — not summary cloud_sec_range text."""
    seen = 6966
    ptr = _read(ACTIVE_POINTER)
    reset = ptr.get("phase_reset") if isinstance(ptr.get("phase_reset"), dict) else {}
    for key in ("cloud_forge_run_last_completed", "cloud_forge_run_head"):
        match = re.search(r"CLOUD-SEC-(\d+)", str(reset.get(key) or ""))
        if match:
            seen = max(seen, int(match.group(1)))
    for path in sorted((ROOT / "data").glob("secondary-cloud-forge-run-batch-*-locked-v1.json")):
        m = re.search(r"batch-(\d+)", path.name)
        if not m or int(m.group(1)) >= before_batch:
            continue
        try:
            drain = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for plan in drain.get("plans") or []:
            pid = str(plan.get("id") or "")
            if pid.startswith("CLOUD-SEC-"):
                try:
                    seen = max(seen, int(pid.rsplit("-", 1)[-1]))
                except ValueError:
                    pass
    return seen


def _next_batch_id() -> int:
    ptr = _read(ACTIVE_POINTER)
    return max(76, int(ptr.get("batch_id") or 75) + 1)


def _mac_rows(batch_id: int, first_cloud: int) -> list[dict[str, Any]]:
    rows = []
    for idx in range(1, MAC_CONTROL_ROWS + 1):
        rows.append(
            {
                "n": idx,
                "id": f"MAC-CTL-B{batch_id}-{idx:02d}",
                "plane": "mac_control",
                "batch_id": batch_id,
                "mac_role": "observe · client-proof demo only · read receipt; no Mac body",
                "mac_build_forbidden": True,
                "mac_executes_plan_body": False,
                "title": (
                    f"Mac observe client-proof batch {batch_id}: "
                    f"CLOUD-SEC-{first_cloud:04d}+ · show buyer verify PASS on call"
                ),
            }
        )
    return rows


def _cloud_row(*, n: int, cloud_num: int, batch_id: int, recipe: dict[str, Any]) -> dict[str, Any]:
    pid = str(recipe.get("plan_id") or "")
    return {
        "n": n,
        "id": f"CLOUD-SEC-{cloud_num:04d}",
        "maps_registry": pid,
        "plane": "cloud_forge",
        "batch_id": batch_id,
        "mac_executes_plan_body": False,
        "library": "client-proof-recipe",
        "": "SourceA client proof chain",
        "workstream": "ws-client-proof",
        "tier": str(recipe.get("tier") or "T0"),
        "cost_tier": "openrouter_cap",
        "client_problem": recipe.get("client_problem"),
        "goal": recipe.get("goal"),
        "done_when": recipe.get("done_when"),
        "verify": recipe.get("verify"),
        "proof_artifact": recipe.get("proof_artifact"),
        "client_demo": recipe.get("client_demo"),
        "proven": bool(recipe.get("proven")),
        "realistic": bool(recipe.get("realistic", True)),
        "cloud_action": (
            f"Client proof recipe: {recipe.get('title')} · "
            f"DONE when {recipe.get('done_when')} · demo: {recipe.get('client_demo')}"
        )[:500],
        "recipe": {
            "schema": "client-proof-recipe-v1",
            "plan_id": pid,
            "prompt_path": recipe.get("prompt_path"),
            "source_registry": recipe.get("source_registry"),
        },
    }


def generate(*, batch_id: int | None = None, offset: int = 0, write: bool = True, activate: bool = True) -> dict[str, Any]:
    queue = _read(QUEUE)
    items = queue.get("items") or []
    if not items:
        raise SystemExit(f"FAIL: empty queue at {QUEUE} — run build_client_proof_recipe_queue_v1.py first")

    bid = int(batch_id or _next_batch_id())
    selected = items[offset:]
    if not selected:
        raise SystemExit(f"FAIL: no recipes at offset {offset} (total {len(items)})")

    first_cloud = _last_cloud_num(before_batch=bid) + 1
    cloud_rows = [
        _cloud_row(n=MAC_CONTROL_ROWS + i + 1, cloud_num=first_cloud + i, batch_id=bid, recipe=r)
        for i, r in enumerate(selected)
    ]
    last_cloud = first_cloud + len(cloud_rows) - 1
    now = _now()
    batch_path = ROOT / "data" / f"secondary-cloud-forge-run-batch-{bid}-locked-v1.json"

    doc = {
        "schema": "secondary-cloud-forge-run-batch-v1",
        "version": "3.1.0",
        "batch_id": bid,
        "library": "client-proof-recipe",
        "locked": True,
        "edit_forbidden": True,
        "saved_at": now,
        "authority": "client-proof-recipe-rubric-v1 · FORGE_FACTORY_THREE_OFFERS",
        "one_law": "One CLOUD-SEC row = one client-demo recipe with GOAL · DONE · VERIFY · proof artifact.",
        "generator": "scripts/generate_client_proof_cloud_batch_v1.py",
        "queue_path": str(QUEUE.relative_to(ROOT)),
        "count": MAC_CONTROL_ROWS + len(cloud_rows),
        "summary": {
            "mac_control": MAC_CONTROL_ROWS,
            "cloud_forge": len(cloud_rows),
            "batch_id": bid,
            "rows_per_turn": MOTOR_ROWS_PER_TICK,
            "batch_cloud_rows": len(cloud_rows),
            "tasks_per_row": 1,
            "recipe_offset": offset,
            "recipe_total": len(items),
            "cloud_sec_range": f"CLOUD-SEC-{first_cloud:04d}..CLOUD-SEC-{last_cloud:04d}",
            "proven_count": sum(1 for r in selected if r.get("proven")),
        },
        "plans": _mac_rows(bid, first_cloud) + cloud_rows,
    }

    pointer = {
        "schema": "cloud-forge-run-queue-active-v1",
        "version": "1.5.0",
        "batch_id": bid,
        "locked": True,
        "saved_at": now,
        "queue_path": str(batch_path.relative_to(ROOT)),
        "library": "client-proof-recipe",
        "registry_exhausted": offset + len(selected) >= len(items),
        "queue_batch_complete": False,
        "cloud_sec_range": doc["summary"]["cloud_sec_range"],
        "rows_per_turn": MOTOR_ROWS_PER_TICK,
        "tasks_per_row": 1,
        "batch_cloud_rows": len(cloud_rows),
        "source_queue": str(QUEUE.relative_to(ROOT)),
        "phase_reset": {
            "cloud_forge_run_head": f"CLOUD-SEC-{first_cloud:04d}",
            "cloud_forge_run_last_completed": f"CLOUD-SEC-{first_cloud - 1:04d}",
            "queue_batch_complete": False,
        },
    }

    receipt = {
        "schema": "client-proof-cloud-batch-v1",
        "ok": True,
        "at": now,
        "batch_id": bid,
        "cloud_sec_range": doc["summary"]["cloud_sec_range"],
        "head": pointer["phase_reset"]["cloud_forge_run_head"],
        "recipes": len(cloud_rows),
        "proven_live": doc["summary"]["proven_count"],
        "queue_path": str(batch_path),
    }

    if write:
        _write(batch_path, doc)
        if activate:
            _write(ACTIVE_POINTER, pointer)
            cp = _read(CONTROL_PLANE)
            cp.update(
                {
                    "saved_at": now,
                    "active_batch": {
                        "batch_id": bid,
                        "locked": True,
                        "status": "ACTIVE",
                        "library": "client-proof-recipe",
                        "head": pointer["phase_reset"]["cloud_forge_run_head"],
                        "cloud_sec_range": doc["summary"]["cloud_sec_range"],
                        "rows_per_turn": MOTOR_ROWS_PER_TICK,
                        "tasks_per_row": 1,
                        "batch_cloud_rows": len(cloud_rows),
                        "queue_path": str(batch_path.relative_to(ROOT)),
                    },
                }
            )
            _write(CONTROL_PLANE, cp)
        _write(RECEIPT, receipt)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--batch-id", type=int, default=None)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--batch-only", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = generate(
        batch_id=args.batch_id,
        offset=args.offset,
        write=not args.no_write,
        activate=not args.batch_only,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK client-proof batch {row['batch_id']} head={row['head']} recipes={row['recipes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

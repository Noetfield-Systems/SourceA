"""PROGRAM_PROGRESS updates driven only by successful execution records."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[2]
PROGRESS_JSON = SOURCE_A / "PROGRAM_PROGRESS.json"

ACTION_PLAN_MAP: dict[str, str] = {
    "pos-dispatch": "PROMPTOS-DAILY",
    "pos-execute": "PROMPTOS-DAILY",
    "pos-decide": "PROMPTOS-DAILY",
    "pos-run": "PROMPTOS-DAILY",
    "pos-status": "PROMPTOS-DAILY",
    "founder-update-progress": "P0-RUNRECEIPT",
}


def plan_id_for_action(action_id: str, spec_plan: str = "") -> str:
    return spec_plan or ACTION_PLAN_MAP.get(action_id, "")


def apply_success_to_progress(record) -> dict:
    """Bump plan progress only after spine success."""
    if record.status != "success":
        return {"ok": False, "skipped": True, "reason": "not_success"}

    plan_id = record.plan_id or ACTION_PLAN_MAP.get(record.action_id, "")
    if not plan_id:
        return {"ok": False, "skipped": True, "reason": "no_plan_mapping"}

    if not PROGRESS_JSON.is_file():
        return {"ok": False, "error": "PROGRAM_PROGRESS.json missing"}

    data = json.loads(PROGRESS_JSON.read_text(encoding="utf-8"))
    plans = data.get("parallel_plans") or []
    updated = False
    for plan in plans:
        if plan.get("id") != plan_id:
            continue
        pct = plan.get("progress_pct")
        if pct is None:
            plan["progress_pct"] = 10
        elif isinstance(pct, (int, float)) and pct < 100:
            plan["progress_pct"] = min(100, int(pct) + 5)
        plan["last_spine_success"] = {
            "task_id": record.task_id,
            "action_id": record.action_id,
            "at": record.timestamp,
        }
        updated = True
        break

    if not updated:
        return {"ok": False, "skipped": True, "reason": f"plan_not_found:{plan_id}"}

    spine_sig = data.setdefault("signals_auto", {}).setdefault("execution_spine", {})
    spine_sig["last_success"] = {
        "task_id": record.task_id,
        "plan_id": plan_id,
        "action_id": record.action_id,
        "timestamp": record.timestamp,
    }
    spine_sig["success_count"] = int(spine_sig.get("success_count", 0)) + 1
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["updated_by"] = "execution_spine.progress_sync"
    PROGRESS_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "plan_id": plan_id, "task_id": record.task_id}


def spine_signals_for_progress() -> dict:
    if not PROGRESS_JSON.is_file():
        return {}
    data = json.loads(PROGRESS_JSON.read_text(encoding="utf-8"))
    spine = (data.get("signals_auto") or {}).get("execution_spine") or {}
    if not isinstance(spine, dict):
        return {}
    # Summary only — never return nested execution_spine blobs (INCIDENT bloat class)
    out: dict = {}
    if isinstance(spine.get("last_success"), dict):
        out["last_success"] = spine["last_success"]
    if spine.get("success_count") is not None:
        out["success_count"] = spine["success_count"]
    mem = spine.get("memory")
    if isinstance(mem, dict) and "total" in mem and "progress" not in mem:
        out["memory"] = mem
    inner = spine.get("progress")
    while isinstance(inner, dict):
        if isinstance(inner.get("last_success"), dict) and "last_success" not in out:
            out["last_success"] = inner["last_success"]
        if inner.get("success_count") is not None and "success_count" not in out:
            out["success_count"] = inner["success_count"]
        inner = inner.get("progress")
    return out

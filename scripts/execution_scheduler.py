#!/usr/bin/env python3
"""Select next executable task — REGISTRY pick + state machine guards."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
STATE_PATH = Path.home() / ".sina" / "execution_state_hub.json"
REGISTRY_IDLE_TASK_ID = "registry-exhausted-idle"

PICK_SCRIPTS: dict[str, tuple[Path, Path]] = {
    "sourcea": (ROOT / "scripts" / "pick-sourcea-no-asf-plan.py", ROOT),
    "mono": (
        Path.home() / "Desktop" / "SinaaiMonoRepo" / "scripts" / "pick-mono-no-asf-plan.py",
        Path.home() / "Desktop" / "SinaaiMonoRepo",
    ),
}


def _load_hub() -> dict:
    if not STATE_PATH.is_file():
        return {"tasks": {}, "running": {}}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"tasks": {}, "running": {}}


def _task_runtime_state(hub: dict, task_id: str) -> str:
    tasks = hub.get("tasks") or {}
    row = tasks.get(task_id) or {}
    return (row.get("state") or "queued").lower()


def _lane_has_active(hub: dict, lane: str) -> str | None:
    running = hub.get("running") or {}
    active = running.get(lane)
    if not active:
        return None
    st = _task_runtime_state(hub, active)
    if st in ("running", "verifying", "scheduled"):
        return active
    return None


def _pick_registry(lane: str) -> dict[str, Any] | None:
    spec = PICK_SCRIPTS.get(lane)
    if not spec:
        return None
    script, cwd = spec
    if not script.is_file():
        return None
    proc = subprocess.run(
        [sys.executable, str(script), "--any-tier", "--limit", "1", "--json"],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    return rows[0] if rows else None


def _registry_exhausted(lane: str) -> bool:
    if lane != "sourcea":
        return _pick_registry(lane) is None
    fn = Path.home() / ".sina" / "factory-now-v1.json"
    if fn.is_file():
        try:
            row = json.loads(fn.read_text(encoding="utf-8"))
            if int(row.get("backlog") or 0) == 0 and int(row.get("valid_yes") or 0) >= 1000:
                return True
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    return _pick_registry(lane) is None


def schedule_next(*, lane: str = "sourcea", force: bool = False) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from execution_state_machine import apply_transition, normalize_state  # noqa: WPS433

    hub = _load_hub()
    if not force:
        blocker = _lane_has_active(hub, lane)
        if blocker:
            return {
                "ok": False,
                "error": f"lane {lane} has active task {blocker}",
                "active_task_id": blocker,
            }

    pick = _pick_registry(lane)
    if not pick:
        if _registry_exhausted(lane):
            return {
                "ok": True,
                "idle": True,
                "lane": lane,
                "task_id": REGISTRY_IDLE_TASK_ID,
                "from_state": "idle",
                "to_state": "idle",
                "reason": f"no agent-runnable backlog for lane={lane}",
            }
        return {"ok": False, "error": f"no agent-runnable backlog for lane={lane}"}

    task_id = pick.get("id") or ""
    current = _task_runtime_state(hub, task_id)
    if current == "done":
        return {"ok": False, "error": f"task {task_id} already done in runtime SM"}

    tr = apply_transition(from_state=current, to_state="scheduled", task_id=task_id)
    if not tr.ok and normalize_state(current) not in ("queued", "failed"):
        return {"ok": False, "error": tr.error, "task_id": task_id}

    return {
        "ok": True,
        "lane": lane,
        "task_id": task_id,
        "from_state": tr.from_state,
        "to_state": "scheduled",
        "pick": pick,
        "transition": {"from": tr.from_state, "to": "scheduled", "idempotent": tr.idempotent},
    }


def persist_scheduled(*, lane: str, task_id: str, from_state: str) -> None:
    sys.path.insert(0, str(SCRIPTS))
    from execution_state_machine import apply_transition  # noqa: WPS433

    hub = _load_hub()
    tasks = hub.setdefault("tasks", {})
    tr = apply_transition(from_state=from_state, to_state="scheduled", task_id=task_id)
    if not tr.ok:
        raise ValueError(tr.error)
    tasks[task_id] = {
        "state": "scheduled",
        "lane": lane,
        "previous": tr.from_state,
    }
    hub.setdefault("running", {})[lane] = task_id
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(hub, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Execution scheduler")
    parser.add_argument("--next", action="store_true")
    parser.add_argument("--lane", default="sourcea")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--persist", action="store_true", help="Write scheduled state to hub")
    args = parser.parse_args()

    if not args.next:
        parser.error("use --next")

    out = schedule_next(lane=args.lane.strip().lower(), force=args.force)
    if out.get("ok") and args.persist:
        persist_scheduled(
            lane=out["lane"],
            task_id=out["task_id"],
            from_state=out["transition"]["from"],
        )
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

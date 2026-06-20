#!/usr/bin/env python3
"""Unified execution state — REGISTRY + agent-loop + execution_router progress."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOOP_PATH = Path.home() / ".sina" / "agent-loop.json"
STATE_PATH = Path.home() / ".sina" / "execution_state_hub.json"
LOGS_DIR = ROOT / "REPO_EXECUTION_LOGS"

REGISTRY_PATHS: dict[str, Path] = {
    "sourcea": ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json",
    "mono": Path.home() / "Desktop" / "SinaaiMonoRepo" / "os" / "plan-library" / "mono-1000" / "REGISTRY.json",
}

LOG_LANE_MAP = {
    "sourcea": "sourcea",
    "mono": "sinaai_mono",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _save_hub_state(data: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    STATE_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _load_hub_state() -> dict:
    default = {"tasks": {}, "running": {}, "last_receipt": None}
    raw = _load_json(STATE_PATH, default)
    if "tasks" not in raw:
        raw["tasks"] = {}
    if "running" not in raw:
        raw["running"] = {}
    return raw


def _load_loop() -> dict:
    return _load_json(LOOP_PATH, {})


def _load_registry(lane: str) -> dict:
    path = REGISTRY_PATHS.get(lane)
    if not path or not path.is_file():
        return {}
    return _load_json(path, {})


def _registry_counts(lane: str) -> dict[str, int]:
    reg = _load_registry(lane)
    plans = reg.get("plans") or []
    counts: dict[str, int] = {}
    for pl in plans:
        st = pl.get("status") or "unknown"
        counts[st] = counts.get(st, 0) + 1
    return counts


def _next_pick_id(lane: str) -> str | None:
    import subprocess
    import sys

    if lane == "sourcea":
        script = ROOT / "scripts" / "pick-sourcea-no-asf-plan.py"
        cwd = ROOT
    elif lane == "mono":
        script = Path.home() / "Desktop" / "SinaaiMonoRepo" / "scripts" / "pick-mono-no-asf-plan.py"
        cwd = script.parents[1]
    else:
        return None
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
        picked = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    if not picked:
        return None
    return picked[0].get("id")


def status_payload(*, lane: str = "sourcea") -> dict[str, Any]:
    loop = _load_loop()
    hub = _load_hub_state()
    running = hub.get("running") or {}
    lane_running = running.get(lane)
    runtime_tasks = {
        tid: row.get("state")
        for tid, row in (hub.get("tasks") or {}).items()
        if (row.get("lane") or lane) == lane
    }

    try:
        from runtime.execution_router.router_store import load_router_snapshot  # noqa: WPS433

        router_snap = load_router_snapshot()
    except Exception:
        router_snap = {}

    loop_active = bool(loop.get("active"))
    return {
        "ok": True,
        "lane": lane,
        "loop_active": loop_active,
        "loop_round": loop.get("round"),
        "loop_status": loop.get("status"),
        "running_task_id": lane_running,
        "next_pick_id": _next_pick_id(lane),
        "registry_counts": _registry_counts(lane),
        "router_task_progress_keys": list((router_snap.get("task_progress") or {}).keys())[:10],
        "last_receipt": hub.get("last_receipt"),
        "updated_at": hub.get("updated_at"),
        "runtime_tasks": runtime_tasks,
        "state_machine": "execution-state-machine-v1",
    }


def _transition_task(hub: dict, *, task_id: str, lane: str, to_state: str) -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from execution_state_machine import apply_transition  # noqa: WPS433

    tasks = hub.setdefault("tasks", {})
    current = (tasks.get(task_id) or {}).get("state") or "queued"
    tr = apply_transition(from_state=current, to_state=to_state, task_id=task_id)
    if not tr.ok:
        return {"ok": False, "error": tr.error}
    tasks[task_id] = {"state": to_state, "lane": lane, "previous": tr.from_state}
    return {"ok": True, "from": tr.from_state, "to": to_state, "idempotent": tr.idempotent}


def mark_verifying(*, lane: str, task_id: str) -> dict[str, Any]:
    hub = _load_hub_state()
    tr = _transition_task(hub, task_id=task_id, lane=lane, to_state="verifying")
    if not tr.get("ok"):
        return tr
    _save_hub_state(hub)
    from agent_governance_events import log_governance_event  # noqa: WPS433

    log_governance_event(
        "execution_state_verifying",
        workspace_id=lane,
        detail=f"task_id={task_id}",
        extra={"lane": lane, "task_id": task_id},
    )
    return {"ok": True, "lane": lane, "task_id": task_id, "status": "verifying"}


def mark_failed(*, lane: str, task_id: str, reason: str = "") -> dict[str, Any]:
    hub = _load_hub_state()
    tr = _transition_task(hub, task_id=task_id, lane=lane, to_state="failed")
    if not tr.get("ok"):
        return tr
    hub.setdefault("running", {}).pop(lane, None)
    if reason:
        tasks = hub.setdefault("tasks", {})
        row = tasks.setdefault(task_id, {})
        row["fail_reason"] = reason
    _save_hub_state(hub)
    from agent_governance_events import log_governance_event  # noqa: WPS433

    log_governance_event(
        "execution_state_failed",
        workspace_id=lane,
        detail=f"task_id={task_id} reason={reason[:120]}",
        extra={"lane": lane, "task_id": task_id, "reason": reason},
    )
    return {"ok": True, "lane": lane, "task_id": task_id, "status": "failed", "reason": reason}


def mark_running(*, lane: str, task_id: str) -> dict[str, Any]:
    hub = _load_hub_state()
    tr = _transition_task(hub, task_id=task_id, lane=lane, to_state="running")
    if not tr.get("ok"):
        return tr
    hub.setdefault("running", {})[lane] = task_id
    _save_hub_state(hub)
    from agent_governance_events import log_governance_event  # noqa: WPS433

    log_governance_event(
        "execution_state_running",
        workspace_id=lane,
        detail=f"task_id={task_id}",
        extra={"lane": lane, "task_id": task_id},
    )
    return {"ok": True, "lane": lane, "task_id": task_id, "status": "running"}


def mark_done(
    *,
    lane: str,
    task_id: str,
    verify_passed: bool = True,
    summary: str = "",
) -> dict[str, Any]:
    reg_path = REGISTRY_PATHS.get(lane)
    if not reg_path or not reg_path.is_file():
        return {"ok": False, "error": f"registry missing for lane={lane}"}

    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    found = False
    title = ""
    for pl in reg.get("plans") or []:
        if pl.get("id") == task_id:
            pl["status"] = "done"
            found = True
            title = pl.get("title") or ""
            break
    if not found:
        return {"ok": False, "error": f"task_id not in registry: {task_id}"}

    reg_path.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")

    log_lane = LOG_LANE_MAP.get(lane, lane)
    log_dir = LOGS_DIR / log_lane
    log_dir.mkdir(parents=True, exist_ok=True)
    slug = task_id.replace("/", "-")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M")
    yaml_body = (
        f"schema_version: 1\n"
        f"repo: {log_lane}\n"
        f"task: {summary or title or task_id}\n"
        f"status: done\n"
        f"verify_passed: {str(verify_passed).lower()}\n"
        f"evidence:\n"
        f"  task_id: {task_id}\n"
        f"tests:\n"
        f"  status: {'passed' if verify_passed else 'failed'}\n"
        f"reported_at: '{_now()}'\n"
        f"reporter: execution_state_hub\n"
    )
    detail_path = log_dir / f"{stamp}_plan-with-no-asf-{slug}.yaml"
    detail_path.write_text(yaml_body, encoding="utf-8")
    (log_dir / "latest.yaml").write_text(yaml_body, encoding="utf-8")

    hub = _load_hub_state()
    end_state = "done" if verify_passed else "failed"
    tr = _transition_task(hub, task_id=task_id, lane=lane, to_state=end_state)
    if not tr.get("ok"):
        cur = (hub.get("tasks") or {}).get(task_id, {}).get("state", "queued")
        if cur not in ("running", "verifying", "scheduled"):
            return {"ok": False, "error": tr.get("error", "transition failed")}
    hub.setdefault("running", {}).pop(lane, None)
    receipt = {
        "lane": lane,
        "task_id": task_id,
        "verify_passed": verify_passed,
        "at": _now(),
        "log": str(detail_path.relative_to(ROOT)),
    }
    hub["last_receipt"] = receipt
    _save_hub_state(hub)

    from agent_governance_events import log_governance_event  # noqa: WPS433

    log_governance_event(
        "execution_state_done",
        workspace_id=lane,
        detail=f"task_id={task_id} verify={verify_passed}",
        extra=receipt,
    )

    try:
        from runreceipt.pack_v1 import build_pack  # noqa: WPS433

        build_pack(
            status="PASS" if verify_passed else "FAIL",
            lane=lane,
            action_id=f"autonomy-stack-{task_id}",
        )
    except Exception:
        pass

    return {"ok": True, **receipt}


def main() -> None:
    parser = argparse.ArgumentParser(description="Execution state hub")
    sub = parser.add_subparsers(dest="cmd", required=True)

    st = sub.add_parser("status")
    st.add_argument("--lane", default="sourcea")
    st.add_argument("--json", action="store_true")

    run = sub.add_parser("mark-running")
    run.add_argument("--lane", default="sourcea")
    run.add_argument("--id", required=True)

    done = sub.add_parser("mark-done")
    done.add_argument("--lane", default="sourcea")
    done.add_argument("--id", required=True)
    done.add_argument("--verify-passed", action="store_true", default=True)
    done.add_argument("--verify-failed", action="store_true")
    done.add_argument("--summary", default="")

    verify = sub.add_parser("mark-verifying")
    verify.add_argument("--lane", default="sourcea")
    verify.add_argument("--id", required=True)

    fail = sub.add_parser("mark-failed")
    fail.add_argument("--lane", default="sourcea")
    fail.add_argument("--id", required=True)
    fail.add_argument("--reason", default="")

    args = parser.parse_args()

    if args.cmd == "status":
        out = status_payload(lane=args.lane)
        print(json.dumps(out, indent=2) if args.json else json.dumps(out, indent=2))
        return

    if args.cmd == "mark-running":
        print(json.dumps(mark_running(lane=args.lane, task_id=args.id), indent=2))
        return

    if args.cmd == "mark-done":
        vp = not args.verify_failed
        print(
            json.dumps(
                mark_done(lane=args.lane, task_id=args.id, verify_passed=vp, summary=args.summary),
                indent=2,
            )
        )
        return

    if args.cmd == "mark-verifying":
        print(json.dumps(mark_verifying(lane=args.lane, task_id=args.id), indent=2))
        return

    if args.cmd == "mark-failed":
        print(json.dumps(mark_failed(lane=args.lane, task_id=args.id, reason=args.reason), indent=2))


if __name__ == "__main__":
    main()

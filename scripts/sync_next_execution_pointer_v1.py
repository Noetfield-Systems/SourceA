#!/usr/bin/env python3
"""Write ~/.sina/next-execution-pointer-v1.json — single machine next-task SSOT."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POINTER = Path.home() / ".sina" / "next-execution-pointer-v1.json"
RAIL = Path.home() / ".sina" / "active-execution-rail-v1.json"
RUNTIME = Path.home() / ".sina" / "runtime" / "execution.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _healthy_queue_pick() -> dict | None:
    """Goal 1 rail SSOT — pointer follows healthy queue current item when present."""
    queue_path = Path.home() / ".sina" / "healthy-queue-30-active.json"
    state_path = Path.home() / ".sina" / "healthy-queue-state-v1.json"
    if not queue_path.is_file():
        return None
    try:
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        items = queue.get("queue") or []
        if not items:
            return None
        pos = 1
        if state_path.is_file():
            pos = int(json.loads(state_path.read_text(encoding="utf-8")).get("next_pos") or 1)
        pos = max(1, min(pos, len(items)))
        item = items[pos - 1]
        sa_id = str(item.get("sa_id") or "")
        if not sa_id.startswith("sa-"):
            return None
        return {
            "sa_id": sa_id,
            "title": str(item.get("sa_title") or item.get("title") or ""),
            "prompt_path": str(item.get("sa_path") or ""),
            "pick_ok": True,
            "queue_pos": pos,
            "queue_role": item.get("queue_role"),
        }
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return None


def _live_pick() -> dict:
    proc = subprocess.run(
        ["bash", str(ROOT / "scripts" / "plan-no-asf-run.sh"), "pick", "1"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    sa_id = ""
    title = ""
    path = ""
    for line in proc.stdout.splitlines():
        if line.startswith("sa-"):
            parts = line.split("\t")
            sa_id = parts[0].strip()
            if len(parts) > 1:
                path = parts[1].strip()
            if len(parts) > 2:
                title = parts[2].strip()
            break
    return {"sa_id": sa_id, "title": title, "prompt_path": path, "pick_ok": proc.returncode == 0}


def _rail() -> dict:
    if not RAIL.is_file():
        return {"rail": "A", "source": "default"}
    try:
        return json.loads(RAIL.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"rail": "A", "source": "parse_error"}


def build_pointer(*, writer: str = "sync_next_execution_pointer_v1.py") -> dict:
    hq = _healthy_queue_pick()
    pick = hq if hq else _live_pick()
    source = "healthy-queue-30-active.json" if hq else "plan-no-asf-run.sh pick 1"
    rail = _rail()
    row = {
        "schema": "next-execution-pointer-v1",
        "next_sa": pick.get("sa_id") or None,
        "title": pick.get("title") or "",
        "prompt_path": pick.get("prompt_path") or "",
        "source": source,
        "rail": rail.get("rail", "A"),
        "execution_authority": "sourcea_execution_core",
        "worker_handoff": "brain-os/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
        "authority_map": "brain-os/system/authority.yaml",
        "writers_allowed": ["sourcea_execution_core", "healthy-drain-orchestrator", "sync_next_execution_pointer_v1.py"],
        "written_by": writer,
        "updated_at": _now(),
    }
    if hq:
        row["queue_pos"] = hq.get("queue_pos")
        row["queue_role"] = hq.get("queue_role")
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = build_pointer()
    POINTER.parent.mkdir(parents=True, exist_ok=True)
    POINTER.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    try:
        from execution_event_log_v1 import append_event  # noqa: WPS433

        append_event(
            event="POINTER_SYNC",
            actor="healthy-drain-orchestrator",
            trace_id=str(payload.get("next_sa") or ""),
            data={
                "next_sa": payload.get("next_sa"),
                "queue_pos": payload.get("queue_pos"),
                "queue_role": payload.get("queue_role"),
            },
        )
    except Exception:
        pass

    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from authority_enforce_p1_lib import sync_tracker_executive_pointer  # noqa: WPS433

        sync_tracker_executive_pointer(pointer=payload)
    except Exception:
        pass
    try:
        from active_now_v1 import sync_active_now_from_queue  # noqa: WPS433

        sync_active_now_from_queue(pointer=payload)
    except Exception:
        pass

    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    if not RUNTIME.is_file():
        RUNTIME.write_text(
            json.dumps(
                {
                    "schema": "runtime-execution-v1",
                    "current_sa": None,
                    "worker_id": None,
                    "status": "IDLE",
                    "started_at": None,
                    "heartbeat_at": _now(),
                    "retry": 0,
                    "broker_yes": None,
                    "pointer": str(POINTER),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"OK: {POINTER} → {payload.get('next_sa')}")
    return 0 if payload.get("next_sa") else 1


if __name__ == "__main__":
    raise SystemExit(main())

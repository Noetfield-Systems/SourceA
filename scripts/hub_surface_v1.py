#!/usr/bin/env python3
"""GET /api/surface/v1 — slim header chips + nav (HUB_UNIFY U3)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHELL = ROOT / "agent-control-panel" / "command-data-shell.json"
API_PATH = "/api/surface/v1"
SCHEMA = "hub-surface-v1"

DEFAULT_NAV = (
    {"id": "command", "label": "Command", "slice": "/api/hub-sync"},
    {"id": "goal1-auto-run", "label": "Goal 1", "slice": "/api/goal1-auto-run-status"},
    {"id": "live-queue", "label": "Queue", "slice": "/api/live/queue"},
    {"id": "live-factory", "label": "Factory", "slice": "/api/live/factory"},
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_factory_now() -> dict:
    path = Path.home() / ".sina" / "factory-now-v1.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def surface_payload() -> dict:
    from hub_sync_slim_v1 import ensure_shell_generation_id, live_factory_payload, live_queue_payload  # noqa: WPS433
    from sina_command_lib import goal1_auto_run_payload  # noqa: WPS433

    shell: dict = {}
    if SHELL.is_file():
        try:
            shell = json.loads(SHELL.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            shell = {}

    g1 = goal1_auto_run_payload()
    queue = g1.get("queue") or {}
    inbox = g1.get("inbox") or {}
    fn = _read_factory_now()
    live_q = live_queue_payload()
    live_f = live_factory_payload()

    kill = bool(fn.get("kill_flag"))
    mode = str(fn.get("mode") or live_f.get("mode") or "RUN")
    freeze_status = "FREEZE" if kill or mode == "FREEZE" else mode

    nav = shell.get("hub_nav") or shell.get("nav") or list(DEFAULT_NAV)
    p0 = ((shell.get("command_center") or {}).get("founder") or {}).get("p0") or {}

    form_pending = 0
    try:
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        form_row = live_form_payload()
        if form_row.get("awaiting_founder_picks") or int(form_row.get("open_questions_count") or 0) > 0:
            form_pending = int(form_row.get("open_questions_count") or 0)
    except Exception:
        form_pending = 0

    return {
        "ok": True,
        "schema": SCHEMA,
        "api": API_PATH,
        "generation_id": ensure_shell_generation_id(),
        "built_at": shell.get("built_at") or _now(),
        "freeze_status": freeze_status,
        "queue_sa_id": queue.get("sa_id") or live_q.get("sa_id"),
        "queue_role": queue.get("queue_role") or live_q.get("queue_role"),
        "queue_pos": queue.get("queue_pos") or live_q.get("pos"),
        "queue_total": queue.get("queue_total"),
        "valid_yes": fn.get("valid_yes"),
        "brain_vy": fn.get("brain_vy"),
        "dual_proof": fn.get("dual_proof"),
        "inbox_pending": bool(inbox.get("pending") or live_q.get("pending")),
        "p0_next_action": p0.get("next_action"),
        "nav": nav,
        "proof_counter": int(shell.get("proof_counter") or 0),
        "worker_health_port": 13030,
        "founder_form_pending": form_pending,
        "hub_repair_mode": form_pending > 0,
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Hub surface v1 payload")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = surface_payload()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"SURFACE: gid={row.get('generation_id')} freeze={row.get('freeze_status')} "
            f"queue={row.get('queue_sa_id')} built_at={row.get('built_at')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

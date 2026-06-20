#!/usr/bin/env python3
"""Post-ship queue advance for outbound factory — mandatory on all VERIFY closeout paths."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OUTBOUND_PHASE = "phase-s6-outbound-factory-upgrade"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def is_outbound_factory_queue() -> bool:
    hq = _read(SINA / "healthy-queue-30-active.json")
    if str(hq.get("phase") or "") == OUTBOUND_PHASE:
        return True
    head = (hq.get("queue") or [{}])[0]
    return bool(head.get("upgrade_id"))


def _queue_head() -> dict:
    hq = _read(SINA / "healthy-queue-30-active.json")
    items = hq.get("queue") or []
    return items[0] if items else {}


def _sync_orchestrator_closeout(*, sa_id: str, upgrade_id: str) -> dict:
    orch_path = SINA / "healthy-drain-orchestrator-v1.json"
    orch = _read(orch_path)
    if not orch:
        return {"ok": False, "skipped": True, "reason": "no_orchestrator"}
    head = _queue_head()
    orch.update(
        {
            "last_completed_sa": sa_id,
            "last_completed_upgrade_id": upgrade_id,
            "last_completed_role": "verify",
            "last_completed_at": _now(),
            "expected_sa": str(head.get("sa_id") or orch.get("expected_sa") or ""),
            "expected_role": str(head.get("queue_role") or orch.get("expected_role") or "check"),
            "updated_at": _now(),
            "recovery_reason": "outbound_post_ship_v1",
        }
    )
    orch_path.write_text(json.dumps(orch, indent=2) + "\n", encoding="utf-8")

    broker_path = SINA / "goal1-lane-broker-v1.json"
    broker = _read(broker_path)
    if broker:
        snap = broker.setdefault("orchestrator_snapshot", {})
        inner = snap.setdefault("orchestrator", {})
        inner.update(
            {
                "last_completed_sa": sa_id,
                "last_completed_upgrade_id": upgrade_id,
                "last_completed_role": "verify",
                "expected_sa": orch.get("expected_sa"),
                "expected_role": orch.get("expected_role"),
            }
        )
        broker["updated_at"] = _now()
        broker_path.write_text(json.dumps(broker, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "last_completed_sa": sa_id, "last_completed_upgrade_id": upgrade_id}


def post_ship_after_verify(*, sa_id: str, upgrade_id: str = "") -> dict:
    """Rebuild queue + sync orchestrator after broker VERIFY on outbound factory."""
    if not is_outbound_factory_queue():
        return {"ok": True, "skipped": True, "reason": "not_outbound_factory"}

    head = _queue_head()
    uid = upgrade_id or str(head.get("upgrade_id") or "")
    sys.path.insert(0, str(SCRIPTS))
    from outbound_receipt_path_v1 import receipt_exists  # noqa: WPS433
    from outbound_queue_coherence_v1 import rebuild_queue_and_deliver, assess_queue_coherence  # noqa: WPS433

    mark_row: dict = {"skipped": True}
    if uid and sa_id and receipt_exists(upgrade_id=uid, sa_id=sa_id):
        try:
            from mark_outbound_upgrade_done_v1 import mark_done  # noqa: WPS433

            plan = _read(ROOT / "data/outbound-factory-100-upgrade-plan-v1.json")
            row = next((u for u in plan.get("upgrades") or [] if u.get("id") == uid), {})
            if row.get("status") != "done":
                mark_row = mark_done(uid, sa_id=sa_id, title=str(row.get("title") or ""))
        except Exception as exc:
            mark_row = {"ok": False, "error": str(exc)}

    rebuilt = rebuild_queue_and_deliver(sync=True)
    orch = _sync_orchestrator_closeout(sa_id=sa_id, upgrade_id=uid)
    after = assess_queue_coherence()
    return {
        "schema": "outbound-post-ship-v1",
        "at": _now(),
        "ok": bool(rebuilt.get("ok")) and bool(after.get("ok")),
        "sa_id": sa_id,
        "upgrade_id": uid,
        "mark_done": mark_row,
        "rebuilt": rebuilt,
        "orchestrator": orch,
        "coherence_after": after,
    }


def maybe_rebuild_if_outbound(*, sa_id: str) -> dict:
    if not is_outbound_factory_queue():
        return {"ok": True, "skipped": True}
    return post_ship_after_verify(sa_id=sa_id)

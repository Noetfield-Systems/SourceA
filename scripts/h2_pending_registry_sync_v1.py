#!/usr/bin/env python3
"""Sync H2 pending registry from live Form + disk truth — keeps Brain buckets, refreshes timestamps."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
H2_REGISTRY = SINA / "h2-pending-registry-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def sync_h2_registry(*, caller: str = "h2_pending_registry_sync") -> dict:
    registry = _read(H2_REGISTRY)
    if not registry:
        registry = {
            "schema": "h2-pending-registry-v1",
            "version": "1.1",
            "next_phase": [],
            "deferred": [],
            "ops_blocker": [],
            "maintainer_ship": [],
        }

    form: dict = {}
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        form = live_form_payload()
    except Exception:
        form = {}

    truth = _read(SINA / "run-inbox-disk-truth-v1.json")
    queue_sa = (truth.get("queue") or {}).get("sa_id") or truth.get("queue_sa") or ""

    oq = int(form.get("open_questions_count") or 0)
    registry["form_open"] = {
        **(registry.get("form_open") or {}),
        "count": oq,
        "awaiting_founder_picks": bool(form.get("awaiting_founder_picks")),
        "ids": form.get("open_question_ids") or (registry.get("form_open") or {}).get("ids") or [],
        "machine": "scripts/live_founder_decision_form_v1.py --json",
    }

    if queue_sa:
        registry["queue_head"] = {"sa_id": queue_sa, "at": _now()}
        next_phase = registry.get("next_phase") or []
        if next_phase and next_phase[0].get("id") != queue_sa:
            for row in next_phase:
                if row.get("id") == queue_sa:
                    break
            else:
                note = f"queue_head {queue_sa} not first in next_phase (Brain registry order preserved)"
                notes = registry.setdefault("sync_notes", [])
                if not notes or str(notes[-1]) != note:
                    notes.append(note)
                if len(notes) > 5:
                    registry["sync_notes"] = notes[-5:]

    try:
        from worker_hub_daily_rooms_v1 import daily_rooms_payload  # noqa: WPS433

        dr = daily_rooms_payload()
        tr = registry.get("thread_room") or {}
        tr["headline"] = (dr.get("thread_room") or {}).get("headline")
        tr["pending_draft_rows"] = (dr.get("thread_room") or {}).get("thread_drafts")
        registry["thread_room"] = tr
        registry["judge_headline"] = (dr.get("judge_center") or {}).get("headline")
    except Exception:
        pass

    registry["updated_at"] = _now()
    registry["updated_by"] = f"machine:{caller}"
    registry["law"] = registry.get("law") or "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md §2a"

    SINA.mkdir(parents=True, exist_ok=True)
    H2_REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    from h2_pending_count_lib_v1 import count_h2_pending  # noqa: WPS433

    counts = count_h2_pending(registry)
    pending_total = counts["pending_total"]
    return {
        "ok": True,
        "schema": "h2-pending-registry-sync-v1",
        "at": registry["updated_at"],
        "caller": caller,
        "pending_total": pending_total,
        "form_open": oq,
        "queue_head": queue_sa,
        "path": str(H2_REGISTRY),
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Sync H2 pending registry from live disk")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = sync_h2_registry()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"H2-SYNC: pending={row.get('pending_total')} form_open={row.get('form_open')} queue={row.get('queue_head')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

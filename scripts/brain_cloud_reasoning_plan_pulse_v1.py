#!/usr/bin/env python3
"""Brain cloud-reasoning 1000 plan pulse — strategic blocker tracking.

Writes: ~/.sina/brain-cloud-reasoning-plan-pulse-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
PLAN = ROOT / "data" / "brain-cloud-reasoning-1000-upgrade-plan-v1.json"
PULSE = SINA / "brain-cloud-reasoning-plan-pulse-v1.json"
PULSE_RECEIPT_ALIAS = SINA / "brain-cloud-reasoning-plan-pulse-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def run_pulse(*, write: bool = True) -> dict:
    plan = _read(PLAN)
    upgrades = plan.get("upgrades") or []
    pivot = plan.get("strategic_pivot") or {}
    inbox = _read(SINA / "worker-prompt-inbox-v1.json")
    active_wo = _read(SINA / "brain-outbound-work-order-active-v1.json")
    surfaces = _read(SINA / "agent-live-surfaces-v1.json")

    work_order_mode = (
        active_wo.get("execution_mode") == "brain_work_order"
        or (not inbox.get("pending") and bool(active_wo.get("work_order_id")))
    )
    local_primary = bool(inbox.get("pending")) and not work_order_mode
    cloud_contract = _read(ROOT / "data" / "loop-specialist-cloud-contract-v1.json")
    cf_phase = (cloud_contract.get("cloudflare_worker_phase_2b") or {}).get("cron")
    fbe_bundle = _read(ROOT / "data" / "fbe_factory_builder_bundle_v1.json")

    done = sum(1 for u in upgrades if u.get("status") == "done")
    active_epic = "E01"
    for w in plan.get("waves") or []:
        if w.get("status") != "pending":
            continue
        ids = set(w.get("plan_ids") or [])
        if any(u.get("id") in ids and u.get("status") != "done" for u in upgrades):
            active_epic = w["id"]
            break

    head = plan.get("critical_path", ["B0001"])[0]
    row = {
        "schema": "brain-cloud-reasoning-plan-pulse-v1",
        "version": "1.0.0",
        "at": _now(),
        "ok": True,
        "strategic_pivot": pivot,
        "brain_blocker": {
            "real": pivot.get("real_blocker", "brain_reasoning"),
            "local_worker_still_primary": local_primary,
            "inbox_pending": bool(inbox.get("pending")),
            "consequence": pivot.get("consequence"),
            "brain_must_reason": True,
            "founder_facing_error": "Treating INBOX pending as P0 blocks cloud migration",
        },
        "cloud_readiness": {
            "loop_specialist_cf_cron": bool(cf_phase),
            "fbe_bundle_present": bool(fbe_bundle),
            "mac_control_plane": bool(cloud_contract.get("mac_control_plane")),
            "phase": cloud_contract.get("phase"),
        },
        "active_epic": active_epic,
        "critical_path_head": head,
        "progress": {
            "done": done,
            "total": len(upgrades),
            "pct": round(100 * done / len(upgrades)) if upgrades else 0,
            "cloud_proven": sum(1 for u in upgrades if u.get("cloud_proof")),
            "brain_reasoning_proven": sum(1 for u in upgrades if u.get("brain_proof")),
        },
        "next_brain_picks": [
            {
                "id": u["id"],
                "title": u.get("title", "")[:72],
                "epic": u.get("epic"),
                "tier": u.get("tier"),
            }
            for u in upgrades
            if u.get("status") == "planned" and u.get("epic") == active_epic
        ][:6],
        "brain_cloud_line": (
            f"brain-cloud · epic={active_epic} · {done}/1000 · "
            f"blocker=BRAIN · local_primary={'YES' if local_primary else 'NO'} · "
            f"work_order={'YES' if work_order_mode else 'NO'} · "
            f"head={head}"
        ),
        "law": str(PLAN),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(row, indent=2) + "\n"
        PULSE.write_text(payload, encoding="utf-8")
        PULSE_RECEIPT_ALIAS.write_text(payload, encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_pulse()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("brain_cloud_line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

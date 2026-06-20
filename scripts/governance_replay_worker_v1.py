#!/usr/bin/env python3
"""G4 — context-aware replay: event → object snapshot → graph → impact → resume queue."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "governance-replay-receipt-v1.json"
QUEUE_TRUTH = SINA / "run-inbox-disk-truth-v1.json"

sys.path.insert(0, str(SCRIPTS))

from governance_event_spine_v1 import (  # noqa: E402
    append_event,
    find_by_event_id,
    find_by_replay_pointer,
    find_last,
    object_history,
    validate_row,
)
from governance_projection_g3_v1 import run_materializer  # noqa: E402
from governance_reference_graph_v1 import impact_scan  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def resolve_event(
    *,
    replay_pointer: str = "",
    event_id: str = "",
    last_event_type: str = "",
    last_status: str = "",
) -> tuple[dict | None, str]:
    if event_id:
        row = find_by_event_id(event_id)
        return (row, "event_id") if row else (None, "event_id")
    if replay_pointer:
        row = find_by_replay_pointer(replay_pointer)
        return (row, "replay_pointer") if row else (None, "replay_pointer")
    for candidate in (
        last_event_type,
        "WORKER_ROUND",
        "PROPAGATION",
        "VALIDATOR_PASS",
        "",
    ):
        if candidate is None:
            continue
        row = find_last(event_type=candidate, status=last_status)
        if row:
            return row, "last"
    return None, "last"


def object_snapshot_at_version(event: dict) -> dict:
    """Rebuild object state at event version from ledger history + disk truth."""
    object_id = str(event.get("object_id") or "")
    ver = int(event.get("version") or 0)
    history = object_history(object_id=object_id, max_version=ver)
    snapshot: dict = {
        "schema": "governance-object-snapshot-v1",
        "object_id": object_id,
        "object_kind": event.get("object_kind"),
        "version_at_replay": ver,
        "replay_pointer": event.get("replay_pointer") or event.get("replay_key"),
        "event_count": len(history),
        "events": [
            {
                "event_id": r.get("event_id"),
                "version": r.get("version"),
                "event_type": r.get("event_type"),
                "at": r.get("at"),
                "status": r.get("status"),
                "payload": r.get("payload") or {},
            }
            for r in history
        ],
        "latest_payload": (history[-1].get("payload") or {}) if history else {},
    }
    if object_id.startswith("sa-"):
        truth = _load_json(QUEUE_TRUTH)
        q = truth.get("queue") or {}
        snapshot["queue_truth"] = {
            "sa_id": q.get("sa_id"),
            "role": q.get("role"),
            "pos": q.get("pos"),
            "total": q.get("total"),
        }
        snapshot["turn_bind"] = _load_json(SINA / "goal1-worker-turn-bind-v1.json")
        snapshot["active_turn"] = _load_json(SINA / "goal1-active-turn-snapshot-v1.json")
    law_id = event.get("law_id") or (object_id if event.get("object_kind") == "law" else "")
    if law_id:
        snap = impact_scan(object_id=str(law_id))
        snapshot["law_graph_node"] = snap.get("affected") if snap.get("ok") else {}
    return snapshot


def graph_context_at_replay(event: dict) -> dict:
    """Graph edges and nodes relevant at replay point."""
    law_id = str(event.get("law_id") or "")
    if not law_id and event.get("object_kind") == "law":
        law_id = str(event.get("object_id") or "")
    graph_path = SINA / "governance-reference-graph-v1.json"
    if not graph_path.is_file():
        from governance_reference_graph_v1 import build_graph  # noqa: WPS433

        build_graph()
    graph = _load_json(graph_path)
    affected = list(event.get("affected_objects") or [])
    if law_id and law_id not in affected:
        affected.insert(0, law_id)
    nodes = [n for n in graph.get("nodes", []) if n.get("id") in affected or n.get("id") == law_id]
    edges = [
        e
        for e in graph.get("knowledge_edges", [])
        if e.get("from") in affected
        or e.get("to") in affected
        or e.get("from") == law_id
        or e.get("to") == law_id
    ]
    impact = impact_scan(object_id=law_id) if law_id else {"ok": False, "error": "no law_id"}
    if not impact.get("ok") and law_id:
        impact = impact_scan(object_id="GOV_EVENT_SPINE")
    return {
        "schema": "governance-graph-context-v1",
        "law_id": law_id or None,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes[:12],
        "edges": edges[:24],
        "impact": impact,
    }


def resume_queue(
    event: dict,
    impact: dict,
    *,
    dry_run: bool = True,
) -> dict:
    """Context-aware queue resume — not log replay only."""
    event_type = str(event.get("event_type") or "")
    actions: list[dict] = []
    ok = True

    if event_type == "WORKER_ROUND":
        sa = str(event.get("object_id") or "")
        payload = event.get("payload") or {}
        actions.append(
            {
                "action": "bind_queue_to_object",
                "sa_id": sa,
                "round_type": payload.get("round_type"),
                "dry_run": dry_run,
            }
        )
        if not dry_run:
            try:
                from worker_inject_lib import inbox_status  # noqa: WPS433

                inbox = inbox_status()
                if not inbox.get("pending"):
                    from goal1_lane_broker import _auto_deliver_next  # noqa: WPS433

                    deliver = _auto_deliver_next()
                    actions.append({"action": "auto_deliver", "result": deliver})
                    ok = ok and bool(deliver.get("ok"))
                else:
                    actions.append({"action": "skip_deliver", "reason": "inbox_already_pending", "inbox": inbox})
            except Exception as exc:
                ok = False
                actions.append({"action": "auto_deliver", "error": str(exc)})

    elif event_type in ("PROPAGATION", "LAW_TOUCHED", "IMPACT_SCAN"):
        aff = (impact.get("affected") if impact.get("ok") else {}) or {}
        projections = aff.get("projections") or event.get("projection_targets") or []
        actions.append({"action": "selective_materialize", "projections": projections, "dry_run": dry_run})
        if not dry_run:
            for proj in projections:
                res = run_materializer(str(proj), reason="g4_replay")
                actions.append({"action": "materialize", "projection": proj, "result": res})
                ok = ok and res.get("ok", False)

    else:
        actions.append({"action": "noop", "reason": f"no resume handler for {event_type}"})

    return {"ok": ok, "event_type": event_type, "actions": actions, "dry_run": dry_run}


def replay_context_aware(
    *,
    replay_pointer: str = "",
    event_id: str = "",
    last_event_type: str = "WORKER_ROUND",
    last_status: str = "",
    dry_run: bool = True,
    write_receipt: bool = True,
    append_recovery_event: bool = True,
) -> dict:
    event, how = resolve_event(
        replay_pointer=replay_pointer,
        event_id=event_id,
        last_event_type=last_event_type,
        last_status=last_status,
    )
    if not event:
        return {"ok": False, "error": "event not found", "resolved_by": how}

    valid, vmsg = validate_row(event)
    if not valid:
        return {"ok": False, "error": f"invalid event row: {vmsg}", "event_id": event.get("event_id")}

    snapshot = object_snapshot_at_version(event)
    graph_ctx = graph_context_at_replay(event)
    impact = graph_ctx.get("impact") or {}
    resume = resume_queue(event, impact, dry_run=dry_run)

    receipt = {
        "schema": "governance-replay-receipt-v1",
        "at": _now(),
        "ok": resume.get("ok", False) and impact.get("ok", True),
        "dry_run": dry_run,
        "resolved_by": how,
        "replay_pointer": event.get("replay_pointer") or event.get("replay_key"),
        "event_id": event.get("event_id"),
        "event_type": event.get("event_type"),
        "object_id": event.get("object_id"),
        "version": event.get("version"),
        "snapshot": snapshot,
        "graph_context": {
            "law_id": graph_ctx.get("law_id"),
            "node_count": graph_ctx.get("node_count"),
            "edge_count": graph_ctx.get("edge_count"),
            "impact_ok": impact.get("ok"),
        },
        "resume": resume,
    }

    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if append_recovery_event and not dry_run and receipt.get("ok"):
        append_event(
            event_type="RECOVERY_FOUND",
            object_id=str(event.get("object_id") or "governance_replay"),
            object_kind=str(event.get("object_kind") or "system"),
            agent_id="maintainer",
            parent_event_id=str(event.get("event_id") or ""),
            correlation_id=str(event.get("correlation_id") or ""),
            law_id=str(event.get("law_id") or "GOV_EVENT_SPINE"),
            skill_id="governance-replay-worker",
            validator_set=["validate-governance-replay-v1.sh"],
            affected_objects=list(event.get("affected_objects") or []),
            payload={
                "replay_of": event.get("replay_pointer"),
                "source_event_id": event.get("event_id"),
                "resume_actions": len(resume.get("actions") or []),
            },
            projection_targets=event.get("projection_targets") or [],
            gate="governance_replay_worker_v1",
            proof=str(RECEIPT_PATH),
            status="replayed",
        )

    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="G4 context-aware governance replay")
    ap.add_argument("--replay-pointer", default="")
    ap.add_argument("--event-id", default="")
    ap.add_argument("--last", action="store_true", help="last WORKER_ROUND (or --event-type)")
    ap.add_argument("--event-type", default="WORKER_ROUND")
    ap.add_argument("--status", default="")
    ap.add_argument("--resume", action="store_true", help="execute queue resume (default dry-run)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    dry_run = not args.resume
    last_type = args.event_type if args.last or not (args.replay_pointer or args.event_id) else ""
    receipt = replay_context_aware(
        replay_pointer=args.replay_pointer,
        event_id=args.event_id,
        last_event_type=last_type,
        last_status=args.status,
        dry_run=dry_run,
        write_receipt=True,
        append_recovery_event=not dry_run,
    )
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(json.dumps(receipt, indent=2))
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

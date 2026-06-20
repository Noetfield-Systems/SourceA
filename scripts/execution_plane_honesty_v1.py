#!/usr/bin/env python3
"""Execution + commercial plane honesty — anti-theater observatory.

Compares factory-now queue vs inbox vs broker vs plan receipts.
Used by: governance_gate_cart_v1 · outbound_factory_upgrade_pulse_v1 · disk_live_wire_sync_v1
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
DEBUG_LOG = ROOT / ".cursor" / "debug-e6507c.log"
PLAN = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"
RECEIPTS = ROOT / "receipts"

sys.path.insert(0, str(ROOT / "scripts"))
from outbound_receipt_path_v1 import (  # noqa: E402
    head_receipt_collision,
    receipt_done_exists,
    receipt_exists,
    resolve_receipt_file,
)


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _sa_num(sa_id: str) -> int:
    m = re.search(r"sa-(\d+)", str(sa_id or ""), re.I)
    return int(m.group(1)) if m else 0


def _dbg(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # #region agent log
    try:
        import json
        import time

        DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with DEBUG_LOG.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "sessionId": "e6507c",
                        "hypothesisId": hypothesis_id,
                        "location": location,
                        "message": message,
                        "data": data,
                        "timestamp": int(time.time() * 1000),
                        "runId": "pre-fix",
                    }
                )
                + "\n"
            )
    except OSError:
        pass
    # #endregion


def _plan_done_without_receipt() -> tuple[int, list[str]]:
    plan = _read_json(PLAN)
    missing: list[str] = []
    for u in plan.get("upgrades") or []:
        if u.get("status") != "done":
            continue
        uid = str(u.get("id") or "")
        proof = u.get("execution_proof") or u.get("shipped_evidence") or {}
        if proof.get("bulk_wiring") or u.get("bulk_wiring"):
            continue
        done_at = str(u.get("done_at") or "")
        if done_at.startswith("2026-06-18T21:40") or done_at.startswith("2026-06-18T21:42"):
            continue
        sa_id = str(proof.get("sa_id") or u.get("worker_sa_id") or "")
        if sa_id and receipt_exists(upgrade_id=uid, sa_id=sa_id):
            continue
        missing.append(uid)
    return len(missing), missing[:12]


def _queue_head_truth() -> dict:
    queue = _read_json(SINA / "healthy-queue-30-active.json")
    items = queue.get("queue") or []
    head = items[0] if items else {}
    upgrade_id = str(head.get("upgrade_id") or "")
    sa_id = str(head.get("sa_id") or "")
    from outbound_queue_coherence_v1 import _plan_row  # noqa: WPS433

    row = _plan_row(upgrade_id) if upgrade_id else {}
    head_planned = str(row.get("status") or "") != "done"
    collision = head_receipt_collision(upgrade_id=upgrade_id, sa_id=sa_id) if upgrade_id and sa_id else {}
    canon_ok = receipt_done_exists(upgrade_id=upgrade_id, sa_id=sa_id) if upgrade_id and sa_id else False
    return {
        "upgrade_id": upgrade_id,
        "sa_id": sa_id,
        "head_planned": head_planned,
        "head_done_on_disk": not head_planned,
        "receipt_collision": bool(collision.get("collision")),
        "collision_detail": collision,
        "head_receipt_exists": canon_ok,
    }


def assess_execution_plane() -> dict:
    """Machine truth for execution plane — independent of governance PASS."""
    fn = _read_json(SINA / "factory-now-v1.json")
    inbox = _read_json(SINA / "worker-prompt-inbox-v1.json")
    routing = _read_json(SINA / "run-inbox-routing-v1.json")
    broker = _read_json(SINA / "goal1-lane-broker-v1.json")
    queue = _read_json(SINA / "healthy-queue-30-active.json")

    queue_sa = str(fn.get("queue_sa") or "")
    resume_sa = str(routing.get("resume_sa") or "")
    inbox_pending = bool(inbox.get("pending"))
    inbox_sa = str(inbox.get("sa_id") or (inbox.get("meta") or {}).get("sa_id") or "")
    prompt = str(inbox.get("prompt") or "")
    cascade_poison = "cascade proof test" in prompt.lower()

    active_wo = _read_json(SINA / "brain-outbound-work-order-active-v1.json")
    head_uid = str((queue.get("queue") or [{}])[0].get("upgrade_id") or "")
    inbox_uid = str((inbox.get("meta") or {}).get("upgrade_id") or "")
    local_worker_head = (
        active_wo.get("execution_mode") == "local_worker"
        and str(active_wo.get("upgrade_ref") or "") == head_uid
        and str(active_wo.get("sa_id") or "") == str((queue.get("queue") or [{}])[0].get("sa_id") or "")
    )
    inbox_head_latched = (
        inbox_pending
        and inbox_sa == queue_sa
        and (not inbox_uid or inbox_uid == head_uid)
    )
    inbox_appropriate = (
        (inbox_pending and (local_worker_head or inbox_head_latched))
        or (not inbox_pending and not local_worker_head)
    )

    orch = (broker.get("orchestrator_snapshot") or {}).get("orchestrator") or {}
    last_report = broker.get("last_worker_report") if isinstance(broker.get("last_worker_report"), dict) else {}
    last_sa = str(
        last_report.get("sa_focus")
        or last_report.get("sa_id")
        or orch.get("last_completed_sa")
        or ""
    )
    expected_sa = str(orch.get("expected_sa") or queue_sa or "")

    routing_aligned = not resume_sa or not queue_sa or resume_sa == queue_sa

    sys.path.insert(0, str(ROOT / "scripts"))
    from outbound_queue_coherence_v1 import assess_queue_coherence  # noqa: WPS433

    coherence = assess_queue_coherence()
    head_truth = _queue_head_truth()
    head_planned = head_truth.get("head_planned", True)

    round_report = _read_json(SINA / "worker_round_report_v1.json")
    rr_sa = str(round_report.get("sa_focus") or "")
    rr_closed = bool(round_report.get("turn_closed"))

    queue_items = queue.get("queue") or []
    lawful_idle = (
        not queue_sa
        and len(queue_items) == 0
        and str(fn.get("orchestrator_status") or "") == "idle"
    )

    if lawful_idle:
        broker_fresh = True
    elif head_truth.get("head_done_on_disk"):
        broker_fresh = False
    elif head_planned and (local_worker_head or inbox_head_latched):
        broker_fresh = inbox_pending and inbox_sa == queue_sa
    elif head_planned and not inbox_pending:
        broker_fresh = (expected_sa == queue_sa) or (last_sa == expected_sa and bool(expected_sa))
    elif rr_closed and rr_sa and rr_sa == queue_sa:
        broker_fresh = True
    else:
        broker_fresh = _sa_num(last_sa) >= _sa_num(expected_sa) if expected_sa and last_sa else False
        if not broker_fresh and last_sa and expected_sa:
            broker_fresh = last_sa == expected_sa

    # #region agent log
    _dbg(
        "H4",
        "execution_plane_honesty_v1.py:assess_execution_plane",
        "lawful_idle_broker",
        {
            "lawful_idle": lawful_idle,
            "queue_sa": queue_sa,
            "queue_len": len(queue_items),
            "orchestrator_status": fn.get("orchestrator_status"),
            "broker_fresh": broker_fresh,
            "last_sa": last_sa,
            "expected_sa": expected_sa,
        },
    )
    # #endregion

    head_executed = not inbox_pending and _sa_num(last_sa) >= _sa_num(queue_sa) if queue_sa else not inbox_pending
    if inbox_pending and inbox_sa == queue_sa:
        head_executed = False
    if local_worker_head and inbox_pending and inbox_sa == queue_sa:
        head_executed = False

    if head_truth.get("head_planned") and head_truth.get("head_receipt_exists"):
        head_executed = False

    head_ready = (
        head_planned
        and inbox_sa == queue_sa
        and (
            (local_worker_head and inbox_pending)
            or inbox_head_latched
            or (not inbox_pending and expected_sa == queue_sa)
        )
    )
    queue_head_state_ok = head_ready or (head_executed and not head_planned)

    done_wo_receipt, missing_ids = _plan_done_without_receipt()

    coherence_checks = coherence.get("checks") or {}
    checks = {
        "inbox_appropriate": inbox_appropriate,
        "queue_head_ready_or_done": queue_head_state_ok,
        "broker_closeout_truth": broker_fresh,
        "routing_aligned": routing_aligned,
        "no_cascade_poison": not cascade_poison,
        "plan_done_without_receipt": done_wo_receipt == 0,
        "no_receipt_collision": not head_truth.get("receipt_collision"),
        "head_not_false_done": not (
            head_truth.get("head_planned") and head_truth.get("head_receipt_exists")
        ),
        "queue_head_not_done": bool(coherence_checks.get("queue_head_not_done")),
        "no_orphan_in_progress": bool(coherence_checks.get("no_orphan_in_progress")),
        "local_worker_inbox_latch": bool(coherence_checks.get("local_worker_inbox_latch")),
        "inbox_matches_head": bool(coherence_checks.get("inbox_matches_head_when_pending")),
    }
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    ok = passed == total

    issues: list[str] = []
    if not inbox_appropriate:
        if local_worker_head and not inbox_pending:
            issues.append(f"inbox_missing_local_worker:{inbox_sa or '?'}")
        elif not local_worker_head and inbox_pending:
            issues.append(f"inbox_pending:{inbox_sa or '?'}")
    if not routing_aligned:
        issues.append(f"routing_stale:{resume_sa}!={queue_sa}")
    if not broker_fresh and expected_sa:
        issues.append(f"broker_closeout_stale:{last_sa or 'none'}<{expected_sa}")
    for issue in coherence.get("issues") or []:
        if issue not in issues:
            issues.append(issue)
    if cascade_poison:
        issues.append("cascade_poison_in_inbox")
    if done_wo_receipt:
        issues.append(f"plan_done_no_receipt:{done_wo_receipt}")
    if head_truth.get("receipt_collision"):
        col = head_truth.get("collision_detail") or {}
        issues.append(
            f"receipt_collision:{col.get('existing_upgrade_id')}@{col.get('sa_id')}"
            f" blocks {col.get('head_upgrade_id')}"
        )
    if head_truth.get("head_planned") and head_truth.get("head_receipt_exists"):
        issues.append(f"head_false_done_receipt:{head_truth.get('upgrade_id')}")

    # #region agent log
    _dbg(
        "H3",
        "execution_plane_honesty_v1.py:assess_execution_plane",
        "execution_plane_checks",
        {
            "queue_sa": queue_sa,
            "expected_sa": expected_sa,
            "last_sa": last_sa,
            "head_truth": head_truth,
            "checks": checks,
            "passed": passed,
            "total": total,
            "issues": issues[:6],
        },
    )
    # #endregion

    legacy_note = ""
    if (head_truth.get("collision_detail") or {}).get("legacy_mismatch"):
        col = head_truth.get("collision_detail") or {}
        legacy_note = (
            f"legacy_receipt_note:{col.get('existing_upgrade_id')} on {col.get('sa_id')}"
            f" · canonical law safe for {col.get('head_upgrade_id')}"
        )

    line = (
        f"execution · {passed}/{total} honest"
        + ("" if ok else f" · BLOCK:{issues[0]}" if issues else "")
        + (f" · queue={queue_sa}" if queue_sa else "")
    )

    return {
        "schema": "execution-plane-honesty-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": ok,
        "passed": passed,
        "total": total,
        "execution_honesty_line": line,
        "queue_sa": queue_sa,
        "resume_sa": resume_sa,
        "inbox_pending": inbox_pending,
        "inbox_sa": inbox_sa,
        "local_worker_head": local_worker_head,
        "inbox_appropriate": inbox_appropriate,
        "last_worker_sa": last_sa,
        "expected_sa": expected_sa,
        "plan_done_without_receipt_count": done_wo_receipt,
        "plan_missing_receipt_ids": missing_ids,
        "queue_head_truth": head_truth,
        "queue_coherence": coherence,
        "legacy_receipt_note": legacy_note or None,
        "checks": checks,
        "issues": issues,
        "outbound_queue_active": "outbound-factory" in str(queue.get("phase") or ""),
    }


def assess_commercial_readiness() -> dict:
    """Commercial plane readiness — L3 founder send loop."""
    comm_pulse = _read_json(SINA / "commercial-command-pulse-v1.json")
    l3 = comm_pulse.get("l3_gates") or {}
    if l3:
        gates = {
            "w3_oqg": bool(l3.get("w3_oqg")),
            "w3_sina_read": bool(l3.get("w3_sina_read")),
            "w3_mail_from": bool(l3.get("w3_mail_from")),
            "w3_send_ready": bool(l3.get("w3_confirm_sent")),
        }
        ready_pct = int(comm_pulse.get("l3_ready_pct") or 0)
        line = f"commercial · L3 {ready_pct}% · " + " · ".join(
            f"{k}={'PASS' if v else 'RED'}" for k, v in gates.items()
        )
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            from execution_path_vocabulary_v1 import post_outbound_smart_loop_active  # noqa: WPS433

            if post_outbound_smart_loop_active():
                line += " · smart-loop owns L3 prep"
        except Exception:
            pass
        return {
            "schema": "commercial-readiness-v1",
            "ready_pct": ready_pct,
            "ready": bool(comm_pulse.get("l3_ready")),
            "gates": gates,
            "commercial_readiness_line": line,
            "ssot": "commercial-command-pulse-v1.json",
        }

    nerve = _read_json(SINA / "agent-nerve-system-receipt-v1.json")
    ship = nerve.get("ship_gates") or {}
    bl = _read_json(SINA / "better-loop-pulse-receipt-v1.json")
    checks_list = bl.get("ship_checks") or bl.get("founder_checks") or bl.get("checks") or []
    chk = {str(c.get("id") or ""): c for c in checks_list}
    nerve_at = str(nerve.get("at") or "")
    pulse_at = str(bl.get("at") or "")
    prefer_pulse = bool(pulse_at and (not nerve_at or pulse_at >= nerve_at))

    def _gate(*, chk_id: str, ship_key: str, ship_alt: str | None = None) -> bool:
        if prefer_pulse and chk_id in chk:
            return bool(chk[chk_id].get("ok"))
        for key in (ship_key, ship_alt):
            if key and ship.get(key) is not None:
                return bool(ship.get(key))
        return bool(chk.get(chk_id, {}).get("ok"))

    gates = {
        "w3_oqg": _gate(chk_id="w3_output_clean", ship_key="w3_oqg_pass"),
        "w3_sina_read": _gate(chk_id="w3_sina_read", ship_key="w3_sina_read_pass"),
        "w3_mail_from": _gate(
            chk_id="w3_mail_from",
            ship_key="w3_mail_from_configured",
            ship_alt="mail_from_ok",
        ),
        "w3_send_ready": _gate(chk_id="w3_send_ready", ship_key="w3_send_ready", ship_alt="send_ready"),
    }
    done = sum(1 for v in gates.values() if v)
    ready_pct = round(100 * done / len(gates)) if gates else 0

    line = f"commercial · L3 {ready_pct}% · " + " · ".join(
        f"{k}={'PASS' if v else 'RED'}" for k, v in gates.items()
    )
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from execution_path_vocabulary_v1 import post_outbound_smart_loop_active  # noqa: WPS433

        if post_outbound_smart_loop_active():
            line += " · smart-loop owns L3 prep"
    except Exception:
        pass

    return {
        "schema": "commercial-readiness-v1",
        "ready_pct": ready_pct,
        "ready": done == len(gates),
        "gates": gates,
        "commercial_readiness_line": line,
        "prefer_pulse": prefer_pulse,
    }


def assess_three_plane() -> dict:
    exec_row = assess_execution_plane()
    comm_row = assess_commercial_readiness()
    return {
        "execution_plane": exec_row,
        "commercial_plane": comm_row,
        "execution_honesty_line": exec_row.get("execution_honesty_line"),
        "commercial_readiness_line": comm_row.get("commercial_readiness_line"),
    }

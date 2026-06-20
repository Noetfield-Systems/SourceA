#!/usr/bin/env python3
"""RUN INBOX disk truth — machine SSOT shown in INBOX on every run inbox (not Next steps batch).

Law: Next steps = display only. Execution = run inbox + this file + healthy queue.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OUT = SINA / "run-inbox-disk-truth-v1.json"
EXEC_LANE = SINA / "execution-lane-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_truth(*, sync: bool = True) -> dict:
    if sync:
        try:
            sys.path.insert(0, str(SCRIPTS))
            from monitor_live_sync_v1 import sync_disk  # noqa: WPS433

            sync_disk(reason="run_inbox_disk_truth")
        except Exception:
            pass

    sys.path.insert(0, str(SCRIPTS))
    from healthy_queue_ssot_lib import healthy_queue_path, healthy_queue_state_path, load_healthy_queue  # noqa: E402
    from monitor_honesty_lib_v1 import audit_monitor, queue_context  # noqa: E402
    from queue_ssot_unify_v1 import queue_head  # noqa: E402

    _, q = load_healthy_queue()
    items = q.get("queue") or []
    head = queue_head()
    pos = int(head.get("pos") or 1)
    item = items[pos - 1] if items and 0 < pos <= len(items) else {}
    if head.get("queue_exhausted"):
        item = {}

    pulse = _read(SINA / "monitor-live-v1.json")
    audit = audit_monitor(filter_mode="road")
    prog = audit.get("progress") or {}
    y = audit.get("you_are_here") or {}
    fn = audit.get("factory_now") or {}
    ps = audit.get("phase_strict") or {}
    inbox = _read(SINA / "worker-prompt-inbox-v1.json")
    active_wo = _read(SINA / "brain-outbound-work-order-active-v1.json")

    unified_worker_pending = bool(q.get("plans_unified") and inbox.get("pending"))
    brain_wo_primary = (
        active_wo.get("execution_mode") == "brain_work_order"
        and active_wo.get("pending") is True
        and not unified_worker_pending
    )

    goal_line = ""
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "goal-progress-v1.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            g = json.loads(proc.stdout).get("goal_1") or {}
            goal_line = f"{g.get('honest_done', g.get('done', '?'))}/{g.get('total', 1000)} honest ({g.get('pct', '?')}%)"
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        goal_line = f"{audit.get('receipt_done', '?')}/1000 receipts"

    row = {
        "schema": "run-inbox-disk-truth-v1",
        "at": _now(),
        "execution_lane": "brain_work_order" if brain_wo_primary else "run_inbox",
        "next_steps_lane": "advisory_only",
        "law": "RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md",
        "progress": {
            "valid_yes": prog.get("valid_yes"),
            "receipt_done": audit.get("receipt_done"),
            "goal_line": goal_line,
        },
        "factory": {
            "mode": fn.get("mode"),
            "freeze": fn.get("kill_flag"),
            "stop_receipt_open": fn.get("stop_receipt_open"),
        },
        "queue": {
            "phase_strict": bool(q.get("phase_strict")),
            "pos": pos,
            "total": len(items),
            "sa_id": head.get("sa_id") or item.get("sa_id") or "",
            "role": head.get("role") or item.get("queue_role") or y.get("role"),
            "phase": item.get("phase"),
            "sa_range": q.get("sa_range"),
            "queue_exhausted": bool(head.get("queue_exhausted") or q.get("queue_exhausted")),
        },
        "phase_strict_order": ps.get("order"),
        "inbox": {
            "pending": bool(inbox.get("pending")),
            "sa_id": (inbox.get("meta") or {}).get("sa_id") or inbox.get("sa_id"),
            "delivered_at": inbox.get("delivered_at"),
            "truth_match": _inbox_matches(inbox, item, pos),
            "execution_mode": active_wo.get("execution_mode") if brain_wo_primary else "worker_inbox",
            "work_order_id": active_wo.get("work_order_id") if brain_wo_primary else None,
            "local_worker_deprecated": bool(active_wo.get("local_worker_deprecated")) if brain_wo_primary else False,
        },
        "monitor_live_at": pulse.get("at"),
        "you_are_here": y,
    }
    return row


def _inbox_matches(inbox: dict, item: dict, pos: int) -> bool:
    meta = inbox.get("meta") or {}
    if not inbox:
        return bool(item.get("sa_id")) or not item
    if not item.get("sa_id") and not inbox.get("pending"):
        return True
    if not item.get("sa_id") and inbox.get("pending"):
        return False
    if not inbox.get("pending") and not str(meta.get("sa_id") or inbox.get("sa_id") or "").strip():
        return bool(item.get("sa_id")) or not item
    total = int(meta.get("queue_total") or 0)
    exhausted = bool(total and pos > total)
    if exhausted and not inbox.get("pending"):
        meta_pos = int(meta.get("queue_pos") or 0)
        return meta_pos == pos or meta_pos > total
    sa_ok = str(meta.get("sa_id") or inbox.get("sa_id") or "") == str(item.get("sa_id") or "")
    pos_ok = int(meta.get("queue_pos") or 0) == int(pos)
    role_ok = str(meta.get("queue_role") or "") == str(item.get("queue_role") or "")
    if not inbox.get("pending"):
        # Cleared between turns — meta must match queue cursor (no stale CHECK redeliver).
        return sa_ok and pos_ok and role_ok
    return sa_ok and pos_ok and role_ok


def format_truth_block(truth: dict | None = None) -> str:
    t = truth or build_truth(sync=True)
    q = t.get("queue") or {}
    p = t.get("progress") or {}
    f = t.get("factory") or {}
    ib = t.get("inbox") or {}
    lines = [
        "═ DISK TRUTH (machine · run inbox SSOT — NOT Next steps batch) ═",
        f"at: {t.get('at')} · monitor_live: {t.get('monitor_live_at') or '—'}",
        f"Goal 1: {p.get('goal_line')} · Valid YES: {p.get('valid_yes')} · receipts: {p.get('receipt_done')}",
        f"Factory: {f.get('mode')} · freeze={f.get('freeze')} · stop_open={f.get('stop_receipt_open')}",
        f"Queue: {q.get('pos')}/{q.get('total')} · {q.get('sa_id')} · {str(q.get('role') or '').upper()} · phase_strict={q.get('phase_strict')}",
    ]
    try:
        from founder_directive_ssot_v1 import truth_block_lines  # noqa: WPS433

        for line in truth_block_lines():
            lines.append(line)
    except Exception:
        pass
    if t.get("phase_strict_order"):
        lines.append(f"Rail order: {t.get('phase_strict_order')}")
    lines.append(
        f"INBOX: pending={ib.get('pending')} · truth_match={ib.get('truth_match')} · delivered={ib.get('delivered_at') or '—'}"
    )
    lines.append("LAW: execute THIS turn only · WORKER_ROUND_REPORT · broker submit · STOP")
    lines.append("═ END DISK TRUTH ═")
    return "\n".join(lines)


def _sync_resume_sa(truth: dict) -> None:
    """Align run-inbox-routing resume_sa with queue head (stop routing ghost)."""
    queue_sa = str((truth.get("queue") or {}).get("sa_id") or "")
    if not queue_sa:
        return
    routing_path = SINA / "run-inbox-routing-v1.json"
    routing = _read(routing_path)
    if str(routing.get("resume_sa") or "") == queue_sa:
        return
    routing["resume_sa"] = queue_sa
    routing["synced_at"] = _now()
    routing["synced_by"] = "run_inbox_disk_truth_v1"
    routing_path.write_text(json.dumps(routing, indent=2) + "\n", encoding="utf-8")


def write_truth(*, sync: bool = True, rebuild_next10: bool = True) -> dict:
    row = build_truth(sync=sync)
    SINA.mkdir(parents=True, exist_ok=True)
    _sync_resume_sa(row)
    OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if rebuild_next10:
        try:
            from live_ongoing_prompts_v1 import rebuild  # noqa: WPS433

            rebuild(write=True, preview=False)
        except Exception:
            pass
    EXEC_LANE.write_text(
        json.dumps(
            {
                "schema": "execution-lane-v1",
                "at": row["at"],
                "execution": (
                    "loop_specialist_auto"
                    if bool(
                        _read(SINA / "loop-specialist-config-v1.json").get("loop_auto_dispatch_enabled")
                    )
                    else "run_inbox"
                ),
                "advisory": "live_next10_mirror",
                "law": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md — feed mirrors machine order; not execution gate",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return row


def _prompt_has_truth_block(inbox: dict) -> bool:
    return "DISK TRUTH" in (inbox.get("prompt") or "")


def _prompt_has_founder_block(inbox: dict) -> bool:
    try:
        from founder_directive_ssot_v1 import hub_closed  # noqa: WPS433

        if not hub_closed():
            return True
    except Exception:
        return True
    return "FOUNDER DIRECTIVE" in (inbox.get("prompt") or "")


def _disk_truth_stale(inbox: dict, truth: dict) -> bool:
    """True when INBOX prompt disk block predates current machine truth."""
    meta = inbox.get("meta") or {}
    truth_at = str(truth.get("at") or "")
    meta_at = str(meta.get("disk_truth_at") or inbox.get("disk_truth_patched_at") or "")
    if truth_at and meta_at and meta_at != truth_at:
        return True
    prompt = inbox.get("prompt") or ""
    if "cascade proof test" in prompt or "NO HUB REBUILD" in prompt:
        return True
    head_sa = str((truth.get("queue") or {}).get("sa_id") or "")
    if head_sa and head_sa not in prompt:
        return True
    return False


def ensure_inbox_truth(*, redeliver: bool = True) -> dict:
    """Machine gate: sync truth; redeliver INBOX if stale vs queue cursor."""
    truth = build_truth(sync=False)
    ib = truth.get("inbox") or {}
    inbox = _read(SINA / "worker-prompt-inbox-v1.json")
    if (
        ib.get("truth_match")
        and _prompt_has_truth_block(inbox)
        and _prompt_has_founder_block(inbox)
        and not _disk_truth_stale(inbox, truth)
    ):
        return {"ok": True, "action": "INBOX_OK", "truth": truth}

    if ib.get("truth_match") and inbox.get("pending") and (
        not _prompt_has_truth_block(inbox)
        or not _prompt_has_founder_block(inbox)
        or _disk_truth_stale(inbox, truth)
    ):
        block = format_truth_block(truth)
        prompt = (inbox.get("prompt") or "").strip()
        if "═ DISK TRUTH" in prompt:
            parts = prompt.split("═ END DISK TRUTH ═", 1)
            rest = parts[1].lstrip("\n") if len(parts) > 1 else prompt
            inbox["prompt"] = block + "\n\n" + rest
        else:
            inbox["prompt"] = block + "\n\n" + prompt
        inbox["chars"] = len(inbox["prompt"])
        inbox["disk_truth_patched_at"] = _now()
        inbox["meta"] = inbox.get("meta") or {}
        inbox["meta"]["disk_truth_at"] = truth.get("at")
        (SINA / "worker-prompt-inbox-v1.json").write_text(json.dumps(inbox, indent=2) + "\n", encoding="utf-8")
        truth = write_truth(sync=False, rebuild_next10=False)
        return {"ok": True, "action": "INBOX_PATCHED_TRUTH", "truth": truth}

    if not redeliver:
        return {"ok": False, "action": "INBOX_STALE", "truth": truth}

    q = truth.get("queue") or {}
    f = truth.get("factory") or {}
    role = str(q.get("role") or "").lower()
    hq = _read(SINA / "healthy-queue-30-active.json")
    outbound_active = (
        str(hq.get("thread") or "") == "OUTBOUND-FACTORY"
        or str(hq.get("product") or "").startswith("Outbound Factory")
    )
    if f.get("freeze") and role not in ("check", "") and not outbound_active:
        sys.path.insert(0, str(SCRIPTS))
        from worker_inject_lib import clear_inbox  # noqa: WPS433

        if inbox.get("pending"):
            clear_inbox(reason="ensure_inbox_truth_freeze_blocked")
        truth = write_truth(sync=False, rebuild_next10=False)
        return {"ok": True, "action": "INBOX_CLEARED_FREEZE_BLOCKED", "truth": truth}

    activator = SINA / "activate-run-inbox-phase-strict-v1.py"
    if activator.is_file():
        proc = subprocess.run(
            [sys.executable, str(activator), "--json", "--force-rebuild"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if proc.returncode == 0:
            truth = write_truth(sync=False, rebuild_next10=False)
            if (truth.get("inbox") or {}).get("truth_match"):
                return {"ok": True, "action": "REDELIVERED", "truth": truth}
            return {"ok": True, "action": "REDELIVER_ATTEMPT", "truth": truth, "deliver": proc.stdout[:500]}
    return {"ok": False, "action": "REDELIVER_FAILED", "truth": truth}


def gate_pickup() -> dict:
    """Called on run inbox — auto-deliver + truth block."""
    cfg = _read(SINA / "phase-strict-drain-v1.json")
    if cfg.get("enabled"):
        return ensure_inbox_truth(redeliver=True)
    return ensure_inbox_truth(redeliver=False)


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--sync", action="store_true", help="Run monitor/queue SSOT unify before build")
    p.add_argument("--json", action="store_true")
    p.add_argument("--write", action="store_true")
    p.add_argument("--format", action="store_true")
    p.add_argument("--ensure", action="store_true")
    p.add_argument("--gate-pickup", action="store_true")
    args = p.parse_args()
    if args.gate_pickup:
        row = gate_pickup()
    elif args.ensure:
        row = ensure_inbox_truth()
    elif args.format:
        print(format_truth_block())
        return 0
    else:
        row = write_truth(sync=args.sync) if args.write else build_truth(sync=args.sync)
    if args.json or args.ensure or args.gate_pickup:
        print(json.dumps(row, indent=2))
    else:
        print(format_truth_block(row))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())

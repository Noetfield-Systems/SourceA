#!/usr/bin/env python3
"""Worker factory evidence gate — recipe · turn · inbox · broker hygiene.

Law: brain-os/law/enforcement/WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md
INCIDENT-007 — blocks orphan turns, corrupt INBOX, STALE closeout claims.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LAW = ROOT / "brain-os/law/enforcement/WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md"
INBOX_JSON = Path.home() / ".sina" / "worker-prompt-inbox-v1.json"
TURN_STATE = Path.home() / ".sina" / "worker_turn_state_v1.json"
ROUND_REPORT = Path.home() / ".sina" / "worker_round_report_v1.json"
SNAPSHOT = Path.home() / ".sina" / "goal1-active-turn-snapshot-v1.json"
LOG = Path.home() / ".sina" / "worker-factory-evidence-gate-v1.jsonl"

SA_RE = re.compile(r"^sa-\d{4}$", re.I)
BIND_RE = re.compile(
    r"bound:\s*sa_id=(sa-\d{4})\s+role=(check|act|verify)",
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({**row, "at": _now()}) + "\n")
    except OSError:
        pass


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _queue_head() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from healthy_queue_ssot_lib import load_healthy_queue, queue_items  # noqa: WPS433

    _, data = load_healthy_queue()
    items = queue_items(data)
    state_path = Path.home() / ".sina" / "healthy-queue-state-v1.json"
    pos = 1
    if state_path.is_file():
        try:
            pos = int(_read_json(state_path).get("next_pos") or 1)
        except (TypeError, ValueError):
            pos = 1
    pos = max(1, min(pos, len(items) or 1))
    item = items[pos - 1] if items else {}
    return {
        "queue_pos": pos,
        "queue_total": len(items),
        "sa_id": str(item.get("sa_id") or ""),
        "queue_role": str(item.get("queue_role") or ""),
    }


def check_turn_state(*, expected_sa: str = "") -> dict:
    st = _read_json(TURN_STATE)
    if str(st.get("status") or "").lower() != "open":
        return {"ok": True, "open": False}
    open_sa = str(st.get("sa_id") or "")
    return {
        "ok": False,
        "open": True,
        "reason": "WORKER_TURN_OPEN",
        "sa_id": open_sa,
        "expected_sa": expected_sa or None,
        "opened_at": st.get("opened_at"),
        "hint": "Hub Unstick Worker or close turn with WORKER_ROUND_REPORT + broker submit",
    }


def check_inbox_recipe() -> dict:
    if not INBOX_JSON.is_file():
        return {
            "ok": False,
            "reason": "INBOX_NOT_READY",
            "hint": "Deliver INBOX — worker-prompt-inbox-v1.json missing",
        }
    data = _read_json(INBOX_JSON)
    if not data.get("pending"):
        return {
            "ok": False,
            "reason": "INBOX_NOT_READY",
            "pending": False,
            "hint": "Hub Deliver healthy drain — INBOX not pending",
        }
    prompt = str(data.get("prompt") or "").strip()
    if len(prompt) < 80:
        return {
            "ok": False,
            "reason": "INBOX_EMPTY_PROMPT",
            "chars": len(prompt),
            "hint": "Re-deliver — prompt empty or corrupt",
        }
    meta = data.get("meta") or {}
    sa = str(meta.get("sa_id") or data.get("sa_id") or "")
    role = str(meta.get("queue_role") or data.get("queue_role") or "")
    if not SA_RE.match(sa):
        return {
            "ok": False,
            "reason": "INBOX_META_INVALID",
            "sa_id": sa,
            "hint": "Re-deliver — meta sa_id must be sa-#### (not sa-BIND)",
        }
    m = BIND_RE.search(prompt)
    if m:
        bind_sa, bind_role = m.group(1).lower(), m.group(2).lower()
        if bind_sa != sa.lower() or bind_role != role.lower():
            return {
                "ok": False,
                "reason": "INBOX_BIND_DRIFT",
                "meta_sa": sa,
                "meta_role": role,
                "bind_sa": bind_sa,
                "bind_role": bind_role,
                "hint": "Re-deliver — prompt header bound: must match meta",
            }
    head = _queue_head()
    if head.get("sa_id") and sa.lower() != head["sa_id"].lower():
        return {
            "ok": False,
            "reason": "INBOX_QUEUE_HEAD_MISMATCH",
            "inbox_sa": sa,
            "queue_sa": head.get("sa_id"),
            "hint": "Sync queue or re-deliver at queue head",
        }
    if head.get("queue_role") and role.lower() != head["queue_role"].lower():
        return {
            "ok": False,
            "reason": "INBOX_ROLE_HEAD_MISMATCH",
            "inbox_role": role,
            "queue_role": head.get("queue_role"),
        }
    return {
        "ok": True,
        "sa_id": sa,
        "queue_role": role,
        "chars": len(prompt),
        "queue": f"{meta.get('queue_pos') or head.get('queue_pos')}/{meta.get('queue_total') or head.get('queue_total')}",
    }


def check_broker_hygiene(*, sa_id: str = "") -> dict:
    """Warn on STALE monitor row for sa; fail strict closeout claims."""
    reasons: list[str] = []
    sys.path.insert(0, str(SCRIPTS))
    try:
        from monitor_honesty_lib_v1 import audit_monitor  # noqa: WPS433

        payload = audit_monitor(filter_mode="road")
        summary = payload.get("summary") or {}
        stale = int(summary.get("broker_stale") or 0)
        if sa_id:
            for row in payload.get("rows") or []:
                if row.get("sa_id") == sa_id and row.get("broker") == "STALE":
                    reasons.append(f"BROKER_STALE_RECEIPT:{sa_id}")
                    break
        return {
            "ok": len(reasons) == 0,
            "reasons": reasons,
            "broker_stale_total": stale,
            "law": "INCIDENT-007",
        }
    except Exception as exc:
        return {"ok": True, "skipped": True, "error": str(exc)}


def check_reply_template(text: str) -> dict:
    """VERIFY closeout replies must include RECIPE · VALIDATION · EVIDENCE · BUILT."""
    if "WORKER_ROUND_REPORT" not in text:
        return {"ok": True, "skipped": True, "reason": "no_report"}
    lower = text.lower()
    if "round_type: verify" not in lower and "round_type: verify" not in text:
        return {"ok": True, "skipped": True, "reason": "not_verify"}
    missing = [k for k in ("RECIPE:", "VALIDATION:", "EVIDENCE:", "BUILT:") if k not in text]
    if missing:
        return {
            "ok": False,
            "reason": "CLOSEOUT_TEMPLATE_MISSING",
            "missing": missing,
            "law": "WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md §3",
        }
    return {"ok": True}


def run_factory_gate(
    *,
    caller: str = "cli",
    role: str = "worker",
    require_inbox: bool = True,
    strict_broker: bool = False,
    sa_id: str = "",
) -> dict:
    reasons: list[str] = []
    if not LAW.is_file():
        reasons.append("LAW_MISSING:WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md")

    head = _queue_head()
    expected = sa_id or head.get("sa_id") or ""
    turn = check_turn_state(expected_sa=expected)
    if not turn.get("ok"):
        open_sa = str(turn.get("sa_id") or "")
        inbox_sa = ""
        if INBOX_JSON.is_file():
            inbox_data = _read_json(INBOX_JSON)
            if inbox_data.get("pending"):
                inbox_sa = str((inbox_data.get("meta") or {}).get("sa_id") or "")
        # Session/entry gate: in-progress turn matching pending INBOX is expected — not a block.
        in_progress_ok = (
            caller in ("cursor_entry_gate", "agent_session_gate")
            and turn.get("open")
            and open_sa
            and inbox_sa
            and open_sa == inbox_sa
        )
        if not in_progress_ok:
            reasons.append(turn.get("reason") or "WORKER_TURN_OPEN")

    inbox: dict = {"ok": True, "skipped": True}
    if require_inbox:
        inbox = check_inbox_recipe()
        if not inbox.get("ok"):
            reasons.append(inbox.get("reason") or "INBOX_NOT_READY")

    broker = check_broker_hygiene(sa_id=sa_id or inbox.get("sa_id") or head.get("sa_id") or "")
    if strict_broker and not broker.get("ok"):
        reasons.extend(broker.get("reasons") or [])

    row = {
        "ok": len(reasons) == 0,
        "status": "PASS" if not reasons else "FAIL",
        "reasons": reasons,
        "caller": caller,
        "role": role,
        "queue_head": head,
        "turn": turn,
        "inbox": inbox,
        "broker_hygiene": broker,
        "law": str(LAW.relative_to(ROOT)),
    }
    _log(row)
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Worker factory evidence gate")
    p.add_argument("--caller", default="cli")
    p.add_argument("--role", default="worker")
    p.add_argument("--no-inbox", action="store_true")
    p.add_argument("--strict-broker", action="store_true")
    p.add_argument("--sa", default="")
    p.add_argument("--check-reply", default="", help="Validate closeout template in text")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.check_reply:
        out = check_reply_template(args.check_reply)
    else:
        out = run_factory_gate(
            caller=args.caller,
            role=args.role,
            require_inbox=not args.no_inbox,
            strict_broker=args.strict_broker,
            sa_id=args.sa,
        )
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

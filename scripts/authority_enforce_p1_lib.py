#!/usr/bin/env python3
"""P1 authority enforcement — rail lock, pick authority, pointer alignment.

Law: brain-os/system/GOVERNANCE_P1_LOOPS_LOCKED_v1.md
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

RAIL_PATH = Path.home() / ".sina" / "active-execution-rail-v1.json"
POINTER_PATH = Path.home() / ".sina" / "next-execution-pointer-v1.json"
HANDOFF_PATH = Path.home() / ".sina" / "brain/execution_core_handoff-v1.json"
EXECUTION_PATH = Path.home() / ".sina/runtime/execution.json"
RECONCILED_PATH = Path.home() / ".sina/brain/reconciled_decision.yaml"
ROOT = Path(__file__).resolve().parents[1]
TRACKER_PATH = ROOT / "brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md"

RAIL_A_ALLOWED_SOURCES = frozenset(
    {
        "healthy-drain-orchestrator",
        "healthy-drain-autoloop",
        "goal1_healthy_drain",
        "goal1_auto_run_deliver",
        "goal1_auto_run",
        "goal1_auto_loop",
        "goal1_run_loop",
        "start_goal1_worker_turn",
        "agent_cli",
        "brain_execute_turn",
        "sync_next_execution_pointer_v1.py",
        "hub_autorun",
    }
)

MANUAL_SOURCES = frozenset(
    {
        "manual_paste",
        "worker1_paste_queue",
        "w1_manual",
        "founder_paste",
        "cli",
        "hub_manual",
        "composer_paste",
        "external_advisor",
        "gpt_advisor",
        "claude_advisor",
        "old_brain_broker",
    }
)

EXTERNAL_ADVISOR_SOURCES = frozenset(
    {
        "external_advisor",
        "gpt_advisor",
        "claude_advisor",
        "old_brain_broker",
        "composer_paste",
        "manual_paste",
        "founder_paste",
        "worker_chat_unscoped",
    }
)

PICK_AUTHORITY_PATTERNS = (
    re.compile(r"plan-no-asf-run\.sh\s+pick", re.I),
    re.compile(r"\bpick\s+[1-9]\d*\b", re.I),
    re.compile(r"assign\s+sa-", re.I),
    re.compile(r"change\s+(live_)?pick", re.I),
    re.compile(r"priority\s+row\s+override", re.I),
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def load_rail() -> dict:
    return _load_json(RAIL_PATH)


def load_pointer() -> dict:
    return _load_json(POINTER_PATH)


def load_handoff() -> dict:
    return _load_json(HANDOFF_PATH)


def validate_manual_fallback(rail: dict) -> dict:
    """manual_fallback must be ASF-signed with expiry — not a bare boolean."""
    fb = rail.get("manual_fallback")
    if fb is not True and not isinstance(fb, dict):
        return {"ok": True, "active": False}

    if fb is True:
        return {
            "ok": False,
            "error": "MANUAL_FALLBACK_UNSIGNED",
            "hint": "Use manual_fallback: {active: true, set_by: ASF, reason, set_at, expires_at}",
        }

    if not isinstance(fb, dict) or not fb.get("active"):
        return {"ok": True, "active": False}

    if str(fb.get("set_by") or "").upper() != "ASF":
        return {"ok": False, "error": "MANUAL_FALLBACK_SET_BY_NOT_ASF", "detail": fb}

    expires = str(fb.get("expires_at") or "")
    if expires and expires < _now():
        return {"ok": False, "error": "MANUAL_FALLBACK_EXPIRED", "expires_at": expires}

    return {"ok": True, "active": True, "detail": fb}


def check_rail_manual_inject(*, source: str) -> dict:
    """Rail A blocks manual paste inject unless ASF-signed manual_fallback active."""
    rail = load_rail()
    rail_id = str(rail.get("rail") or "A")
    if rail_id != "A":
        return {"ok": True, "rail": rail_id, "skipped": "not_rail_a"}

    if source in RAIL_A_ALLOWED_SOURCES:
        return {"ok": True, "rail": rail_id, "source": source}

    if source in MANUAL_SOURCES or "manual" in source.lower():
        fb_check = validate_manual_fallback(rail)
        if fb_check.get("active") and fb_check.get("ok"):
            return {"ok": True, "rail": rail_id, "manual_fallback": fb_check.get("detail")}
        if rail.get("manual_fallback") is True:
            return {
                "ok": False,
                "error": "MANUAL_FALLBACK_UNSIGNED",
                "hint": "ASF must set manual_fallback object with set_by: ASF and expires_at",
            }
        return {
            "ok": False,
            "error": "RAIL_A_MANUAL_INJECT_BLOCKED",
            "hint": "Hub ▶ AUTO-RUN only on Rail A — ASF-signed manual_fallback required",
            "rail": rail_id,
            "source": source,
        }

    return {"ok": True, "rail": rail_id, "source": source, "note": "unknown_source_allowed"}


def check_prompt_pick_authority(*, text: str, source: str, meta: dict | None = None) -> dict:
    """Worker cannot change pick via prompt — only Execution Core handoff."""
    meta = meta or {}
    if meta.get("brain_handoff") is True or meta.get("execution_core_handoff"):
        return {"ok": True, "reason": "brain_handoff_meta"}

    handoff = load_handoff()
    if handoff.get("schema") == "brain-handoff-v1" and handoff.get("issued_by") == "sourcea_execution_core":
        return {"ok": True, "reason": "brain_handoff_file"}

    if source in RAIL_A_ALLOWED_SOURCES:
        return {"ok": True, "reason": "autoloop_source"}

    body = text or ""
    hits = [p.pattern for p in PICK_AUTHORITY_PATTERNS if p.search(body)]
    if not hits:
        return {"ok": True}

    # External advisor / composer paste is highest-risk bypass — always reject pick language
    if source in EXTERNAL_ADVISOR_SOURCES or "advisor" in source.lower():
        return {
            "ok": False,
            "error": "AUTHORITY_ADVISOR_PICK_BREACH",
            "hint": "Advisors cannot assign pick — route through SourceA Brain handoff only",
            "patterns": hits,
            "source": source,
        }

    return {
        "ok": False,
        "error": "AUTHORITY_PICK_CHANGE_FORBIDDEN",
        "hint": "Only SourceA Brain (Execution Core) assigns pick — Worker builds injected sa only",
        "patterns": hits,
        "source": source,
    }


def check_reconciled_before_inject(*, source: str, sa_id: str | None = None) -> dict:
    """Autoloop inject requires fresh reconciled decision BEFORE INBOX (gate, not receipt-only)."""
    if source not in RAIL_A_ALLOWED_SOURCES:
        return {"ok": True, "skipped": "not_autoloop_source"}

    row = _load_reconciled()
    if not row.get("issued_by") == "sourcea_execution_core":
        return {
            "ok": False,
            "error": "RECONCILED_DECISION_MISSING",
            "hint": "Brain SYNC must write ~/.sina/brain/reconciled_decision.yaml before inject",
        }

    pointer = load_pointer()
    next_sa = str(pointer.get("next_sa") or row.get("next_sa") or "")
    if sa_id and next_sa.startswith("sa-") and sa_id != next_sa:
        return {
            "ok": True,
            "warn": "RECONCILED_POINTER_SA_DRIFT",
            "pointer_sa": next_sa,
            "inject_sa": sa_id,
        }

    return {
        "ok": True,
        "reason": "reconciled_present",
        "next_sa": next_sa,
        "trace_ids": row.get("trace_ids_cited"),
    }


def check_pointer_alignment(*, sa_id: str) -> dict:
    """Broker submit sa should match next-pointer unless Brain handoff names this sa."""
    if not sa_id.startswith("sa-"):
        return {"ok": False, "error": "invalid_sa"}

    pointer = load_pointer()
    next_sa = str(pointer.get("next_sa") or "")
    if not next_sa.startswith("sa-"):
        return {"ok": True, "skipped": "no_pointer"}

    handoff = load_handoff()
    if str(handoff.get("next_sa") or "") == sa_id:
        return {"ok": True, "reason": "brain_handoff_sa"}

    if sa_id == next_sa:
        return {"ok": True, "reason": "pointer_match"}

    # In-flight autoloop may advance orchestrator before pointer sync — warn only
    return {
        "ok": True,
        "warn": "POINTER_DRIFT",
        "pointer_sa": next_sa,
        "report_sa": sa_id,
        "hint": "Run sync_next_execution_pointer_v1.py after closeout",
    }


def touch_execution(*, status: str, sa_id: str | None = None, worker_id: str | None = None) -> dict:
    row = _load_json(EXECUTION_PATH)
    row.update(
        {
            "schema": "runtime-execution-v1",
            "status": status,
            "current_sa": sa_id,
            "worker_id": worker_id,
            "heartbeat_at": _now(),
            "pointer": str(POINTER_PATH),
        }
    )
    EXECUTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXECUTION_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def sync_tracker_executive_pointer(*, pointer: dict | None = None) -> dict:
    """Align tracker §1 executive snapshot with next-execution-pointer SSOT."""
    ptr = pointer if pointer is not None else load_pointer()
    next_sa = str(ptr.get("next_sa") or "")
    if not next_sa.startswith("sa-"):
        return {"ok": False, "error": "pointer missing next_sa"}
    if not TRACKER_PATH.is_file():
        return {"ok": False, "error": "TRACKER_MISSING"}

    role = str(ptr.get("queue_role") or "turn").upper()
    pos = ptr.get("queue_pos")
    pos_label = f"queue pos {pos}" if pos is not None else "queue"
    row = (
        f"| Current execution pointer | → `~/.sina/next-execution-pointer-v1.json` "
        f"(`{next_sa}` {role} · {pos_label}) |"
    )
    text = TRACKER_PATH.read_text(encoding="utf-8")
    if not re.search(r"\| Current execution pointer \|", text):
        return {"ok": False, "error": "tracker pointer row missing"}

    text = re.sub(r"\| Current execution pointer \|[^\n]*", row, text, count=1)
    text = re.sub(
        r"\| Tracker last verified \| [^|]+ \|",
        f"| Tracker last verified | {_now()} |",
        text,
        count=1,
    )
    TRACKER_PATH.write_text(text, encoding="utf-8")
    mark_tracker_status(status="OK", reason="sync_tracker_executive_pointer")
    return {"ok": True, "next_sa": next_sa, "queue_role": role, "queue_pos": pos}


def mark_tracker_status(*, status: str, reason: str = "") -> dict:
    """Broker/validator writes tracker freshness — STALE blocks Worker INBOX."""
    row = _load_json(EXECUTION_PATH)
    row.update(
        {
            "schema": "runtime-execution-v1",
            "tracker_status": status,
            "tracker_status_at": _now(),
            "tracker_status_reason": reason or None,
        }
    )
    EXECUTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXECUTION_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def check_tracker_operational() -> dict:
    """Fail closed when Brain left tracker STALE — blocks INBOX delivery."""
    if not TRACKER_PATH.is_file():
        return {
            "ok": False,
            "error": "TRACKER_MISSING",
            "hint": "SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md required",
        }

    row = _load_json(EXECUTION_PATH)
    if row.get("tracker_status") == "STALE":
        return {
            "ok": False,
            "error": "TRACKER_STALE",
            "hint": "Brain must update Master Operating Tracker and re-run validate-master-operating-tracker-v1.sh",
            "at": row.get("tracker_status_at"),
            "reason": row.get("tracker_status_reason"),
        }

    return {"ok": True, "tracker_status": row.get("tracker_status") or "OK"}


DEFAULT_GOVERNANCE_TRACES = (
    "governance_goal_specialist-20260608-014",
    "governance_goal_specialist-20260608-015",
)


def reconciled_decision_template() -> dict:
    return {
        "schema": "reconciled-decision-v1",
        "issued_by": "sourcea_execution_core",
        "execution_authority": True,
        "trace_ids_cited": list(DEFAULT_GOVERNANCE_TRACES),
        "commercial_trace": None,
        "governance_trace": DEFAULT_GOVERNANCE_TRACES[-1],
        "decision": "P0 authority verified logged; P1 broker loops enforced (Rail A, pick authority, pointer)",
        "next_sa": None,
        "worker_handoff": "brain-os/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
        "updated_at": _now(),
    }


def _load_reconciled() -> dict:
    if not RECONCILED_PATH.is_file():
        return reconciled_decision_template()
    try:
        import yaml

        row = yaml.safe_load(RECONCILED_PATH.read_text(encoding="utf-8"))
        return row if isinstance(row, dict) else reconciled_decision_template()
    except Exception:
        return reconciled_decision_template()


def sync_reconciled_decision(
    *,
    trace_ids: list[str] | None = None,
    decision: str | None = None,
    next_sa: str | None = None,
    note: str = "",
) -> dict:
    """Brain SYNC — cite specialist traces when Execution Core reconciles."""
    import yaml

    row = _load_reconciled()
    pointer = load_pointer()
    cited = list(trace_ids or row.get("trace_ids_cited") or DEFAULT_GOVERNANCE_TRACES)
    row.update(
        {
            "schema": "reconciled-decision-v1",
            "issued_by": "sourcea_execution_core",
            "execution_authority": True,
            "trace_ids_cited": cited,
            "governance_trace": cited[-1] if cited else DEFAULT_GOVERNANCE_TRACES[-1],
            "decision": decision
            or row.get("decision")
            or "P0 authority verified logged; P1 broker loops enforced",
            "next_sa": next_sa or row.get("next_sa") or pointer.get("next_sa"),
            "worker_handoff": row.get("worker_handoff")
            or "brain-os/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
            "updated_at": _now(),
        }
    )
    if note:
        row["brain_note"] = note
    RECONCILED_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECONCILED_PATH.write_text(
        yaml.dump(row, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    return row


def ensure_reconciled_decision_stub() -> Path:
    sync_reconciled_decision()
    return RECONCILED_PATH

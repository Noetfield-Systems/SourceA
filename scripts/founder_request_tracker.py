#!/usr/bin/env python3
"""Founder request registry — never lose ASF ideas, requests, or build orders."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / ".sina" / "founder-requests"
REQUESTS_PATH = ROOT / "requests.jsonl"
SUMMARY_PATH = ROOT / "summary.json"
from governance_paths_v1 import FOUNDER_FIRST_ASSISTANT_TRACKING as LAW_PATH

STATUSES = frozenset({"open", "in_progress", "shipped", "deferred", "cancelled"})
KINDS = frozenset({"order", "idea", "request", "question"})
PRIORITIES = frozenset({"critical", "high", "normal", "low"})

SEED_ROWS: list[dict] = [
    {
        "id": "FR-2026-06-05-001",
        "title": "Always track founder ideas and requests — never forget",
        "detail": "Primary job of Founder First Assistant on Mac. Register every order/idea; surface on Today + Track.",
        "kind": "order",
        "status": "shipped",
        "priority": "critical",
        "thread": "THREAD-MAINTAINER",
        "source": "chat",
        "never_forget": True,
        "shipped_evidence": "FOUNDER_FIRST_ASSISTANT_TRACKING_LAW_LOCKED_v1.md + founder_request_tracker.py + hub Today/Track",
    },
    {
        "id": "FR-2026-06-05-002",
        "title": "D2 Graph Fusion (WTM next strategic build)",
        "detail": "World Target Model step after D1 — graph fusion layer not started.",
        "kind": "order",
        "status": "open",
        "priority": "high",
        "thread": "THREAD-SUPERBRAIN",
        "source": "sprint_audit",
    },
    {
        "id": "FR-2026-06-05-003",
        "title": "Lock GPT paste default to report-only mode",
        "detail": "D-GPT-01 — EXTERNAL_CRITIC must not auto-apply build specs.",
        "kind": "order",
        "status": "open",
        "priority": "high",
        "thread": "THREAD-MAINTAINER",
        "source": "sprint_audit",
    },
    {
        "id": "FR-2026-06-05-004",
        "title": "Supervisor dashboard tab",
        "detail": "Traffic lights, weekly digest, links to scoreboard/vault/essay.",
        "kind": "idea",
        "status": "open",
        "priority": "normal",
        "thread": "THREAD-MAINTAINER",
        "source": "sprint_audit",
    },
    {
        "id": "FR-2026-06-05-005",
        "title": "Authority index hub visibility tile",
        "detail": "Optional founder-only tile pointing to SINA_AUTHORITY_INDEX_MAP.",
        "kind": "idea",
        "status": "open",
        "priority": "normal",
        "thread": "THREAD-MAINTAINER",
        "source": "sprint_audit",
    },
    {
        "id": "FR-2026-06-05-006",
        "title": "Council Phase 2 formal ballots",
        "detail": "After Phase 1 advisory votes + essay discourse mature.",
        "kind": "order",
        "status": "deferred",
        "priority": "normal",
        "thread": "THREAD-MAINTAINER",
        "source": "sprint_audit",
        "defer_reason": "Gate: Phase 1 stable + fleet discourse",
    },
    {
        "id": "FR-2026-06-05-007",
        "title": "Trust ledger schema v1",
        "detail": "Formal schema for agent-governance-events.jsonl.",
        "kind": "order",
        "status": "open",
        "priority": "high",
        "thread": "THREAD-MAINTAINER",
        "source": "sprint_audit",
    },
    {
        "id": "FR-2026-06-05-008",
        "title": "Fleet essay discourse — governance drift (6/8 remaining)",
        "detail": "Subject governance-drift-detection; only 2/8 agents posted.",
        "kind": "order",
        "status": "open",
        "priority": "high",
        "thread": "THREAD-MAINTAINER",
        "source": "sprint_audit",
    },
    {
        "id": "FR-2026-06-05-009",
        "title": "Scoreboard fleet reports + ASF verify checkmarks",
        "detail": "System built; 1 report, 0 verified — all 8 agents must report sessions.",
        "kind": "order",
        "status": "open",
        "priority": "high",
        "thread": "THREAD-MAINTAINER",
        "source": "sprint_audit",
    },
    {
        "id": "FR-2026-06-05-010",
        "title": "Lazy-load / split COMMAND_DATA (~2MB)",
        "detail": "Hub perf — index.html embeds full payload.",
        "kind": "order",
        "status": "open",
        "priority": "normal",
        "thread": "THREAD-MAINTAINER",
        "source": "sprint_audit",
    },
    {
        "id": "FR-2026-06-05-011",
        "title": "Import historical ASF chat rules → founder-directives.jsonl",
        "detail": "Backlog — unify scattered founder orders into machine ledger.",
        "kind": "order",
        "status": "open",
        "priority": "normal",
        "thread": "THREAD-MAINTAINER",
        "source": "sprint_audit",
    },
    {
        "id": "FR-2026-06-05-012",
        "title": "Essay assignment auto-nudges in hub",
        "detail": "Remind agents with missing essays on active subjects.",
        "kind": "order",
        "status": "open",
        "priority": "normal",
        "thread": "THREAD-MAINTAINER",
        "source": "sprint_audit",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_root() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)


def _load_rows(limit: int = 2000) -> list[dict]:
    if not REQUESTS_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in REQUESTS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    rows.sort(key=lambda r: r.get("updated_at") or r.get("created_at") or "", reverse=True)
    return rows[:limit]


def _append_row(row: dict) -> None:
    _ensure_root()
    with REQUESTS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    try:
        REQUESTS_PATH.chmod(0o600)
    except OSError:
        pass


def _title_key(title: str) -> str:
    norm = " ".join((title or "").lower().split())[:120]
    return hashlib.sha256(norm.encode()).hexdigest()[:16]


def _write_summary(rows: list[dict]) -> None:
    open_rows = [r for r in rows if r.get("status") in ("open", "in_progress")]
    summary = {
        "updated_at": _now(),
        "total": len(rows),
        "open_count": len(open_rows),
        "in_progress_count": sum(1 for r in rows if r.get("status") == "in_progress"),
        "shipped_count": sum(1 for r in rows if r.get("status") == "shipped"),
        "deferred_count": sum(1 for r in rows if r.get("status") == "deferred"),
        "law_path": str(LAW_PATH),
        "tagline": "Founder ideas & orders — never forgotten",
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def seed_if_empty() -> int:
    if REQUESTS_PATH.is_file() and REQUESTS_PATH.stat().st_size > 0:
        return 0
    now = _now()
    for seed in SEED_ROWS:
        row = {
            **seed,
            "never_forget": True,
            "created_at": now,
            "updated_at": now,
            "title_key": _title_key(seed.get("title", "")),
        }
        _append_row(row)
    rows = _load_rows()
    _write_summary(rows)
    return len(SEED_ROWS)


def register(
    *,
    title: str,
    detail: str = "",
    kind: str = "request",
    priority: str = "high",
    thread: str = "",
    source: str = "hub",
    status: str = "open",
) -> dict:
    title = (title or "").strip()
    if not title:
        return {"ok": False, "error": "title required"}
    kind = kind if kind in KINDS else "request"
    priority = priority if priority in PRIORITIES else "high"
    status = status if status in STATUSES else "open"
    tk = _title_key(title)
    for row in _load_rows(400):
        if row.get("title_key") == tk and row.get("status") in ("open", "in_progress"):
            return {"ok": True, "duplicate": True, "request": row}
    rid = f"FR-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{uuid.uuid4().hex[:6]}"
    now = _now()
    row = {
        "id": rid,
        "title": title[:240],
        "detail": (detail or "")[:2000],
        "kind": kind,
        "status": status,
        "priority": priority,
        "thread": (thread or "")[:64],
        "source": source[:32],
        "never_forget": True,
        "title_key": tk,
        "created_at": now,
        "updated_at": now,
    }
    _append_row(row)
    rows = _load_rows()
    _write_summary(rows)
    return {"ok": True, "request": row}


def update_status(
    *,
    request_id: str,
    status: str,
    shipped_evidence: str = "",
    defer_reason: str = "",
) -> dict:
    if status not in STATUSES:
        return {"ok": False, "error": f"invalid status: {status}"}
    rows = _load_rows(5000)
    match = next((r for r in rows if r.get("id") == request_id), None)
    if not match:
        return {"ok": False, "error": "request not found"}
    updated = {
        **match,
        "status": status,
        "updated_at": _now(),
    }
    if shipped_evidence:
        updated["shipped_evidence"] = shipped_evidence[:1000]
    if defer_reason:
        updated["defer_reason"] = defer_reason[:500]
    _append_row(updated)
    all_rows = _dedupe_latest(_load_rows(5000))
    _write_summary(all_rows)
    return {"ok": True, "request": updated}


def _dedupe_latest(rows: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for row in sorted(rows, key=lambda r: r.get("updated_at") or "", reverse=True):
        rid = row.get("id")
        if rid and rid not in seen:
            seen[rid] = row
    return list(seen.values())


def requests_payload(*, limit: int = 80) -> dict:
    seed_if_empty()
    rows = _dedupe_latest(_load_rows(5000))
    rows.sort(key=lambda r: r.get("updated_at") or "", reverse=True)
    open_rows = [r for r in rows if r.get("status") in ("open", "in_progress")]
    open_rows.sort(
        key=lambda r: (
            0 if r.get("priority") == "critical" else 1 if r.get("priority") == "high" else 2,
            r.get("updated_at") or "",
        )
    )
    summary = {}
    if SUMMARY_PATH.is_file():
        try:
            summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            summary = {}
    if not summary:
        _write_summary(rows)
        summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    return {
        "ok": True,
        "tagline": summary.get("tagline") or "Founder ideas & orders — never forgotten",
        "law": LAW_PATH.name,
        "open_count": len(open_rows),
        "summary": summary,
        "open_top": open_rows[:12],
        "recent": rows[:limit],
        "primary_job": "Track every founder idea and request — never let them get lost",
    }


def sync_shipped_from_disk() -> dict:
    """Mark FR rows shipped/in_progress from machine SSOT — no ASF actor (sa-0310–0312)."""
    SOURCE_A = Path(__file__).resolve().parents[1]
    SINA_HOME = Path.home() / ".sina"
    updates: list[str] = []

    def _mark(rid: str, status: str, evidence: str = "") -> None:
        res = update_status(request_id=rid, status=status, shipped_evidence=evidence)
        if res.get("ok"):
            updates.append(rid)

    if (SOURCE_A / "brain-os/law/TRUST_LEDGER_SCHEMA_LOCKED_v1.md").is_file():
        _mark("FR-2026-06-05-007", "shipped", "brain-os/law/TRUST_LEDGER_SCHEMA_LOCKED_v1.md")
    idx = SOURCE_A / "agent-control-panel" / "index.html"
    if idx.is_file() and "__COMMAND_DATA_LAZY" in idx.read_text(encoding="utf-8", errors="replace"):
        _mark("FR-2026-06-05-010", "shipped", "index.html lazy-load shell")
    directives = SINA_HOME / "founder-directives.jsonl"
    if directives.is_file() and directives.stat().st_size > 0:
        _mark("FR-2026-06-05-011", "shipped", str(directives))

    try:
        from agent_essay_discourse import essay_discourse_payload  # noqa: WPS433

        nudges = int(essay_discourse_payload().get("nudge_count") or 0)
        if nudges <= 2:
            _mark("FR-2026-06-05-008", "shipped", f"essay nudges {nudges}")
        else:
            _mark("FR-2026-06-05-008", "in_progress", f"essay nudges {nudges}")
    except Exception:
        pass

    try:
        from agent_scoreboard import scoreboard_payload  # noqa: WPS433

        sb = scoreboard_payload()
        auto_n = int(sb.get("auto_pass_count") or 0)
        if auto_n >= 6:
            _mark("FR-2026-06-05-009", "shipped", f"auto_pass_count {auto_n}")
        else:
            _mark("FR-2026-06-05-009", "in_progress", f"auto_pass_count {auto_n}")
    except Exception:
        pass

    phase2 = SOURCE_A / "SOURCEA_PHASE2_INTEGRITY_PICK_RECEIPT_2026-06-11_LOCKED_v1.md"
    if phase2.is_file():
        _mark(
            "FR-2026-06-11-a6192f",
            "shipped",
            "SOURCEA_PHASE2_INTEGRITY_PICK_RECEIPT_2026-06-11_LOCKED_v1.md",
        )

    form_answers = (
        SOURCE_A
        / "archive/attachments/2026-06-11/SOURCEA_LIVE_FOUNDER_DECISION_FORM_V2_ANSWERS_RECEIPT_2026-06-11_LOCKED_v1.md"
    )
    if form_answers.is_file():
        try:
            from external_critic_default_v1 import is_wired, validate_wiring  # noqa: WPS433

            ok_fr, _ = validate_wiring()
            if ok_fr and is_wired():
                _mark(
                    "FR-2026-06-05-003",
                    "shipped",
                    "external_critic_default_v1.py · ~/.sina/external-critic-default-v1.json",
                )
            else:
                _mark(
                    "FR-2026-06-05-003",
                    "in_progress",
                    "ASF Q-CRITIC YES — wire external_critic_default_v1",
                )
        except Exception:
            _mark(
                "FR-2026-06-05-003",
                "in_progress",
                "ASF Q-CRITIC YES — EXTERNAL_CRITIC report-only",
            )

    direction_receipt = (
        SOURCE_A
        / "archive/attachments/2026-06-12/SOURCEA_FOUNDER_DIRECTION_LOCK_RECEIPT_2026-06-12_LOCKED_v1.md"
    )
    if direction_receipt.is_file():
        dtitle = "Commercial direction lock 040 — proof + W3 first"
        dkey = _title_key(dtitle)
        if not any(r.get("title_key") == dkey for r in _load_rows(400)):
            register(
                title=dtitle,
                detail="3.07 NO · 9.07 A · ENFORCEMENT + W3 parallel · no GOV_UNIFY batch",
                kind="order",
                priority="high",
                thread="THREAD-ENFORCEMENT",
                source="commercial_specialist",
                status="shipped",
            )

    return {"ok": True, "updated": updates, "count": len(updates)}


def handle_action(body: dict | None) -> dict:
    body = body or {}
    action = (body.get("action") or "list").strip().lower()
    if action in ("list", "get", ""):
        return requests_payload()
    if action == "register":
        return register(
            title=body.get("title") or body.get("text") or "",
            detail=body.get("detail") or "",
            kind=body.get("kind") or "request",
            priority=body.get("priority") or "high",
            thread=body.get("thread") or "",
            source=body.get("source") or "hub",
            status=body.get("status") or "open",
        )
    if action == "update":
        return update_status(
            request_id=body.get("id") or body.get("request_id") or "",
            status=body.get("status") or "open",
            shipped_evidence=body.get("shipped_evidence") or body.get("evidence") or "",
            defer_reason=body.get("defer_reason") or body.get("reason") or "",
        )
    if action == "seed":
        n = seed_if_empty()
        return {"ok": True, "seeded": n, **requests_payload()}
    return {"ok": False, "error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "seed":
        print(json.dumps({"seeded": seed_if_empty()}, indent=2))
    else:
        print(json.dumps(requests_payload(), indent=2))

#!/usr/bin/env python3
"""Essay discourse — tagged subjects, all agents post essays, compare and pick best in hub.

Council ``essay_nudges`` payload for hub UI (sa-0316).
"""
from __future__ import annotations

import json
import re
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from agent_workspace_registry import AGENT_WORKSPACES, get_workspace

SINA_HOME = Path.home() / ".sina"
ESSAY_ROOT = SINA_HOME / "essay-discourse"
ESSAYS_PATH = ESSAY_ROOT / "essays.jsonl"
ASSIGNMENTS_PATH = ESSAY_ROOT / "assignments.json"
BEST_PATH = ESSAY_ROOT / "best-by-subject.json"

LAW_DOC = "AGENT_ESSAY_DISCOURSE_LOCKED_v1.md"
MIN_ESSAY_CHARS = 120
MARK_BEST_ACTORS = frozenset({"founder", "maintainer"})
ATTEST_PATH = SINA_HOME / "essay-mark-best-attestation-v1.json"
RECEIPTS_PATH = ESSAY_ROOT / "mark-best-receipts.jsonl"

DEFAULT_ASSIGNMENTS: list[dict] = [
    {
        "subject": "governance-drift-detection",
        "title": "Governance drift detection",
        "tags": ["governance", "drift", "audit", "supervision"],
        "prompt": "Every agent chat writes an essay: how does your lane detect and prevent governance drift?",
        "active": True,
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _norm_subject(subject: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (subject or "").lower()).strip("-")[:64] or "general"


def _parse_tags(raw: str | list | None) -> list[str]:
    if isinstance(raw, list):
        return [str(t).strip()[:32] for t in raw if str(t).strip()][:12]
    if not raw:
        return []
    return [t.strip()[:32] for t in str(raw).replace(",", " ").split() if t.strip()][:12]


def _load_essays(limit: int = 500) -> list[dict]:
    if not ESSAYS_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in ESSAYS_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def _append_essay(row: dict) -> None:
    ESSAY_ROOT.mkdir(parents=True, exist_ok=True)
    with ESSAYS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_assignments() -> list[dict]:
    ESSAY_ROOT.mkdir(parents=True, exist_ok=True)
    if not ASSIGNMENTS_PATH.is_file():
        data = {"assignments": DEFAULT_ASSIGNMENTS, "updated_at": _now()}
        ASSIGNMENTS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        data = json.loads(ASSIGNMENTS_PATH.read_text(encoding="utf-8"))
        return data.get("assignments") or DEFAULT_ASSIGNMENTS
    except json.JSONDecodeError:
        return DEFAULT_ASSIGNMENTS


def _load_best() -> dict[str, str]:
    if not BEST_PATH.is_file():
        return {}
    try:
        return json.loads(BEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_best(data: dict[str, str]) -> None:
    ESSAY_ROOT.mkdir(parents=True, exist_ok=True)
    BEST_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def ensure_mark_best_attestation() -> dict:
    """Disk token for mark_best POST — founder or maintainer co-actor (sa-0799)."""
    SINA_HOME.mkdir(parents=True, exist_ok=True)
    if ATTEST_PATH.is_file():
        try:
            row = json.loads(ATTEST_PATH.read_text(encoding="utf-8"))
            if row.get("token"):
                return row
        except json.JSONDecodeError:
            pass
    row = {
        "schema": "essay-mark-best-attestation-v1",
        "token": uuid.uuid4().hex,
        "actors": sorted(MARK_BEST_ACTORS),
        "created_at": _now(),
        "law": "AGENT_ESSAY_DISCOURSE_LOCKED_v1.md",
        "note": "mark_best requires actor + attestation — not fleet verify",
    }
    ATTEST_PATH.write_text(json.dumps(row, indent=2), encoding="utf-8")
    return row


def _verify_mark_best_actor(*, actor: str, attestation: str) -> dict:
    who = (actor or "").strip().lower()
    if who not in MARK_BEST_ACTORS:
        return {
            "ok": False,
            "error": f"mark_best requires actor in {sorted(MARK_BEST_ACTORS)}",
            "code": "mark_best_actor_required",
        }
    token = (attestation or "").strip()
    if not token:
        return {"ok": False, "error": "mark_best requires attestation token", "code": "mark_best_attestation_required"}
    row = ensure_mark_best_attestation()
    if token != row.get("token"):
        return {"ok": False, "error": "mark_best attestation invalid", "code": "mark_best_attestation_invalid"}
    return {"ok": True, "actor": who}


def _append_mark_best_receipt(*, actor: str, subject_norm: str, essay_id: str) -> None:
    ESSAY_ROOT.mkdir(parents=True, exist_ok=True)
    row = {"at": _now(), "actor": actor, "subject_norm": subject_norm, "essay_id": essay_id}
    with RECEIPTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def submit_essay(
    agent_id: str,
    *,
    subject: str,
    body: str,
    title: str = "",
    tags: list[str] | str | None = None,
) -> dict:
    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}
    subject_norm = _norm_subject(subject)
    if not subject_norm or subject_norm == "general":
        return {"ok": False, "error": "subject required (e.g. governance-drift-detection)"}
    text = (body or "").strip()
    if len(text) < MIN_ESSAY_CHARS:
        return {"ok": False, "error": f"Essay must be at least {MIN_ESSAY_CHARS} characters"}
    tag_list = _parse_tags(tags)
    assignments = _load_assignments()
    assign = next((a for a in assignments if _norm_subject(a.get("subject", "")) == subject_norm), None)
    if assign and not tag_list:
        tag_list = list(assign.get("tags") or [])[:12]

    row = {
        "id": f"ESSAY-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "agent_id": agent_id,
        "label": spec.get("label"),
        "lane": spec.get("lane"),
        "repo_root": spec.get("repo_root"),
        "subject": subject.strip()[:80],
        "subject_norm": subject_norm,
        "title": (title or f"Essay — {subject}").strip()[:160],
        "tags": tag_list,
        "body": text[:12000],
        "word_count": len(text.split()),
        "status": "submitted",
    }
    _append_essay(row)
    try:
        from agent_governance_events import log_governance_event  # noqa: WPS433

        log_governance_event("essay_submitted", workspace_id=agent_id, detail=subject_norm, extra={"essay_id": row["id"]})
    except Exception as exc:
        try:
            from agent_governance_events import log_governance_event  # noqa: WPS433

            log_governance_event(
                "essay_governance_event_failed",
                workspace_id=agent_id,
                detail=str(exc)[:200],
                extra={"essay_id": row["id"], "hook": "governance_event"},
            )
        except Exception:
            pass
    try:
        from agent_workspace_vault import deposit_document, log_activity  # noqa: WPS433

        deposit_document(
            agent_id,
            title=row["title"],
            content=text,
            kind="report",
            source="essay_discourse",
            tags=["essay", subject_norm, *tag_list[:4]],
        )
        log_activity(agent_id, action="essay_submitted", detail=subject_norm, kind="learn", source="essay")
    except Exception as exc:
        try:
            from agent_governance_events import log_governance_event  # noqa: WPS433

            log_governance_event(
                "essay_vault_hook_failed",
                workspace_id=agent_id,
                detail=str(exc)[:200],
                extra={"essay_id": row["id"], "hook": "vault_deposit_log_activity"},
            )
        except Exception:
            pass
    return {"ok": True, "essay": row}


def mark_best_essay(*, subject: str, essay_id: str, actor: str = "", attestation: str = "") -> dict:
    auth = _verify_mark_best_actor(actor=actor, attestation=attestation)
    if not auth.get("ok"):
        try:
            from agent_governance_events import log_governance_event  # noqa: WPS433

            log_governance_event(
                "essay_best_mark_denied",
                workspace_id="essay_discourse",
                detail=(auth.get("code") or "denied")[:64],
                extra={"subject": subject, "essay_id": essay_id, "actor": actor or ""},
            )
        except Exception:
            pass
        return auth
    who = auth["actor"]
    subject_norm = _norm_subject(subject)
    essays = [e for e in _load_essays() if e.get("subject_norm") == subject_norm]
    match = next((e for e in essays if e.get("id") == essay_id), None)
    if not match:
        return {"ok": False, "error": "Essay not found for this subject"}
    best = _load_best()
    best[subject_norm] = essay_id
    _save_best(best)
    _append_mark_best_receipt(actor=who, subject_norm=subject_norm, essay_id=essay_id)
    try:
        from agent_governance_events import log_governance_event  # noqa: WPS433

        log_governance_event(
            "essay_best_marked",
            workspace_id=match.get("agent_id"),
            detail=subject_norm,
            extra={"essay_id": essay_id, "marked_by": who},
        )
    except Exception:
        pass
    return {
        "ok": True,
        "subject_norm": subject_norm,
        "best_essay_id": essay_id,
        "marked_by": who,
        "essay": match,
    }


def _topics_from_essays(essays: list[dict], best_map: dict[str, str]) -> list[dict]:
    by_subject: dict[str, list[dict]] = defaultdict(list)
    for e in essays:
        by_subject[e.get("subject_norm") or "general"].append(e)
    assignments = {_norm_subject(a.get("subject", "")): a for a in _load_assignments()}
    topics: list[dict] = []
    all_subjects = set(by_subject.keys()) | set(assignments.keys())
    for sn in sorted(all_subjects):
        if not sn:
            continue
        rows = sorted(by_subject.get(sn, []), key=lambda r: r.get("at") or "", reverse=True)
        agents = sorted({r.get("agent_id") for r in rows if r.get("agent_id")})
        assign = assignments.get(sn) or {}
        best_id = best_map.get(sn)
        best_row = next((r for r in rows if r.get("id") == best_id), None)
        tags: set[str] = set(assign.get("tags") or [])
        for r in rows:
            tags.update(r.get("tags") or [])
        topics.append(
            {
                "subject_norm": sn,
                "subject": assign.get("subject") or (rows[0].get("subject") if rows else sn),
                "title": assign.get("title") or sn.replace("-", " ").title(),
                "prompt": assign.get("prompt") or "",
                "tags": sorted(tags),
                "essay_count": len(rows),
                "agent_count": len(agents),
                "agents": agents,
                "missing_agents": [w["id"] for w in AGENT_WORKSPACES if w["id"] not in agents],
                "best_essay_id": best_id,
                "best_essay": best_row,
                "essays": rows,
            }
        )
    return topics


def essay_discourse_payload(*, subject: str = "") -> dict:
    ESSAY_ROOT.mkdir(parents=True, exist_ok=True)
    essays = _load_essays()
    best_map = _load_best()
    topics = _topics_from_essays(essays, best_map)
    if subject:
        sn = _norm_subject(subject)
        topics = [t for t in topics if t["subject_norm"] == sn]
    nudges: list[dict] = []
    for topic in topics:
        if not topic.get("missing_agents"):
            continue
        for aid in topic.get("missing_agents") or []:
            spec = get_workspace(aid) or {}
            nudges.append(
                {
                    "agent_id": aid,
                    "label": spec.get("label") or aid,
                    "subject": topic.get("subject_norm"),
                    "title": topic.get("title"),
                    "message": f"Essay missing for «{topic.get('title')}» — open hub Essay discourse tab.",
                }
            )
    return {
        "ok": True,
        "built_at": _now(),
        "law_doc": LAW_DOC,
        "agent_count": len(AGENT_WORKSPACES),
        "assignments": _load_assignments(),
        "topics": topics,
        "topic_count": len(topics),
        "essay_count": len(essays),
        "essay_nudges": nudges,
        "nudge_count": len(nudges),
        "storage_root": str(ESSAY_ROOT),
        "essays_path": str(ESSAYS_PATH),
        "tagline": "Same subject — all agents write — compare in hub — mark best essay",
        "mark_best_contract": {
            "actors": sorted(MARK_BEST_ACTORS),
            "requires_attestation": True,
            "attestation_schema": "essay-mark-best-attestation-v1",
            "not_fleet_verify": True,
            "sa": "sa-0799",
        },
    }


def handle_essay_action(body: dict) -> dict:
    action = (body.get("action") or "list").strip().lower()
    if action == "submit_essay":
        return submit_essay(
            (body.get("agent_id") or body.get("id") or "").strip(),
            subject=body.get("subject") or "",
            body=body.get("body") or body.get("text") or body.get("essay") or "",
            title=body.get("title") or "",
            tags=body.get("tags"),
        )
    if action == "mark_best":
        return mark_best_essay(
            subject=body.get("subject") or "",
            essay_id=body.get("essay_id") or "",
            actor=body.get("actor") or body.get("marked_by") or "",
            attestation=body.get("attestation") or body.get("token") or "",
        )
    if action in ("list", ""):
        return essay_discourse_payload(subject=body.get("subject") or "")
    return {"ok": False, "error": f"unknown action: {action}"}

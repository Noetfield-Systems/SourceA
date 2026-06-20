#!/usr/bin/env python3
"""
Agent reviews for Sina Command — any Cursor agent may REPORT; only ASF + SinaaiDataBase chat may EDIT app code.

Storage: ~/.sina/agent-command-reviews.jsonl
Lock manifest: ~/.sina/command-edit-lock.json
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
REVIEWS_PATH = Path.home() / ".sina" / "agent-command-reviews.jsonl"
LOCK_PATH = Path.home() / ".sina" / "command-edit-lock.json"
OVERRIDES_PATH = Path.home() / ".sina" / "agent-review-overrides.json"

# Cursor workspace folder names (basename) allowed to edit ~/Desktop/SourceA
ALLOWED_EDIT_WORKSPACES = frozenset({
    "SinaaiDataBase",
})

LAW_DOC = "SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md"
PROTECTED_ROOT = str(SOURCE_A)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_lock_manifest() -> dict:
    if LOCK_PATH.is_file():
        return json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    manifest = {
        "version": 1,
        "protected_root": PROTECTED_ROOT,
        "protected_globs": [
            "agent-control-panel/**",
            "scripts/sina-command*.py",
            "scripts/agent_loop.py",
            "scripts/loop_*.py",
            "scripts/site_guide.py",
            "scripts/command_audit_backlog.py",
            "scripts/agent_command_reviews.py",
            "scripts/build-sina-command-panel.py",
            "scripts/clipboard_safe.py",
            "scripts/semej*.py",
        ],
        "allowed_edit_workspaces": sorted(ALLOWED_EDIT_WORKSPACES),
        "allowed_editors": ["ASF (founder human)", "SinaaiDataBase Cursor chat only"],
        "all_agents_must": "POST /api/agent-review action=submit — never edit SourceA files",
        "law_doc": f"~/Desktop/SourceA/{LAW_DOC}",
        "updated_at": _now(),
    }
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCK_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    try:
        LOCK_PATH.chmod(0o600)
    except OSError:
        pass
    return manifest


def edit_lock_payload() -> dict:
    m = _load_lock_manifest()
    return {
        "ok": True,
        "protected_root": m.get("protected_root"),
        "allowed_edit_workspaces": m.get("allowed_edit_workspaces"),
        "allowed_editors": m.get("allowed_editors"),
        "law_doc": m.get("law_doc"),
        "report_api": "POST http://127.0.0.1:13020/api/agent-review",
    }


def _load_overrides() -> dict:
    if not OVERRIDES_PATH.is_file():
        return {"status": {}, "notes": {}}
    return json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))


def _save_overrides(data: dict) -> None:
    OVERRIDES_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    OVERRIDES_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _read_reviews() -> list[dict]:
    if not REVIEWS_PATH.is_file():
        return []
    rows = []
    for line in REVIEWS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _append_review(row: dict) -> None:
    REVIEWS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REVIEWS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _norm_workspace(ws: str) -> str:
    ws = (ws or "").strip()
    if not ws:
        return "unknown"
    return Path(ws).name


def submit_review(
    *,
    title: str,
    detail: str,
    severity: str = "medium",
    category: str = "bug",
    workspace: str = "",
    reporter: str = "",
    file_path: str = "",
    suggested_fix: str = "",
) -> dict:
    title = (title or "").strip()[:200]
    detail = (detail or "").strip()[:8000]
    if not title or not detail:
        return {"ok": False, "error": "title and detail required"}

    sev = (severity or "medium").lower()
    if sev not in ("critical", "high", "medium", "low"):
        sev = "medium"
    cat = (category or "bug").lower()
    if cat not in ("bug", "ux", "regression", "law", "request", "security"):
        cat = "bug"

    ws_name = _norm_workspace(workspace)

    rid = f"AR-{uuid.uuid4().hex[:10]}"
    row = {
        "id": rid,
        "created_at": _now(),
        "title": title,
        "detail": detail,
        "severity": sev,
        "category": cat,
        "workspace": ws_name,
        "reporter": (reporter or "agent")[:120],
        "file_path": (file_path or "")[:500],
        "suggested_fix": (suggested_fix or "")[:2000],
        "status": "open",
    }
    _append_review(row)
    try:
        from agent_governance_events import log_governance_event  # noqa: WPS433

        log_governance_event(
            "review_submitted",
            workspace_id=ws_name,
            detail=title,
            extra={"review_id": rid, "severity": sev},
        )
    except Exception:
        pass
    return {"ok": True, "id": rid, "message": f"Report {rid} filed — ASF / SinaaiDataBase chat will triage"}


def _path_under_source_a(path: str) -> bool:
    if not path:
        return False
    try:
        p = Path(path).expanduser().resolve()
        root = SOURCE_A.resolve()
        return p == root or root in p.parents
    except (OSError, ValueError):
        return PROTECTED_ROOT in path


def set_review_status(review_id: str, status: str, note: str = "") -> dict:
    if status not in ("open", "triaged", "in_progress", "done", "wontfix"):
        return {"ok": False, "error": "invalid status"}
    rid = (review_id or "").strip()
    if not rid:
        return {"ok": False, "error": "id required"}
    ov = _load_overrides()
    ov.setdefault("status", {})[rid] = status
    if note:
        ov.setdefault("notes", {})[rid] = note[:2000]
    _save_overrides(ov)
    return {"ok": True, "message": f"{rid} → {status}"}


def reviews_payload() -> dict:
    _load_lock_manifest()
    overrides = _load_overrides()
    status_map = overrides.get("status") or {}
    notes_map = overrides.get("notes") or {}
    items = []
    for row in reversed(_read_reviews()):
        rid = row.get("id", "")
        st = status_map.get(rid, row.get("status", "open"))
        items.append({**row, "status": st, "user_note": notes_map.get(rid, "")})
    open_items = [i for i in items if i["status"] not in ("done", "wontfix")]
    by_sev: dict[str, list] = {}
    for it in open_items:
        by_sev.setdefault(it.get("severity", "medium"), []).append(it)
    lock = edit_lock_payload()
    return {
        "ok": True,
        "built_at": _now(),
        "open_count": len(open_items),
        "total_count": len(items),
        "items": items[:80],
        "edit_lock": lock,
        "tagline": "Agents report here — only ASF + SinaaiDataBase chat may edit Sina Command code.",
        "reviews_path": str(REVIEWS_PATH),
        "submit_hint": 'POST /api/agent-review {"action":"submit","title":"…","detail":"…","workspace":"…"}',
    }


def handle_review_action(body: dict) -> dict:
    action = (body.get("action") or "list").strip().lower()
    if action == "submit":
        return submit_review(
            title=body.get("title", ""),
            detail=body.get("detail", ""),
            severity=body.get("severity", "medium"),
            category=body.get("category", "bug"),
            workspace=body.get("workspace", body.get("cursor_workspace", "")),
            reporter=body.get("reporter", body.get("agent", "")),
            file_path=body.get("file_path", ""),
            suggested_fix=body.get("suggested_fix", ""),
        )
    if action == "set_status":
        return set_review_status(body.get("id", ""), body.get("status", "open"), body.get("note", ""))
    if action == "lock":
        return edit_lock_payload()
    return {"ok": True, **reviews_payload()}

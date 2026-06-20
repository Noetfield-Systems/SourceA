#!/usr/bin/env python3
"""Full workspace mirror — second Cursor: all private + repo lane state in hub."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent_workspace_registry import get_workspace

SINA_HOME = Path.home() / ".sina"
WORKSPACES_ROOT = SINA_HOME / "agent-workspaces"
SOURCE_A = Path(__file__).resolve().parents[1]
SKILLS_ROOT = SOURCE_A / "agent-skills"

WORKSPACE_MD_FILES = (
    "INBOX.md",
    "NEEDS.md",
    "notes.md",
    "GOVERNANCE_LOCKED.md",
    "WORKSPACE_SESSION_PROMPT_LOCKED.md",
    "README.md",
    "INCIDENT_MY_INSIGHTS.md",
    "DOC_TAG_STANDARD.md",
    "CONTROL_LAYER_STATUS.md",
    "RESEARCH_MEMORY_INDEX.md",
    "START_10_ROUND_LOOP.md",
)

WORKSPACE_GLOB_MD = (
    "GOVERNANCE_*.md",
    "INCIDENT_*.md",
    "*ESSAY*.md",
    "*INSIGHT*.md",
    "CONTROL_*.md",
    "RESEARCH_*.md",
    "START_*.md",
)

WORKSPACE_SUBDIRS = ("memory", "prompts")

CONFIDENTIAL_PATH_MARKERS = ("auto_confidential", "docs/internal/")


def _is_confidential_path(path: str) -> bool:
    p = (path or "").lower()
    return "auto_confidential" in p or ("docs/internal/" in p and "/auto_" in p)


def _sanitize_ref_row(row: dict) -> dict:
    path = row.get("repo_path") or row.get("detail") or row.get("path") or ""
    if _is_confidential_path(path):
        return {
            **row,
            "repo_path": "[internal ref — redacted on hub]",
            "detail": "[internal ref — redacted on hub]",
            "title": row.get("title") or "Internal lane doc",
            "redacted": True,
        }
    return row

# Never inline full body — incident always-report can be 100k+ chars
HUGE_FILE_NAMES = frozenset({"INCIDENT_REPORT_ALWAYS.md"})
HUGE_FILE_EXCERPT = 1800
DEFAULT_READ_LIMIT = 12000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _read_text(path: Path, *, limit: int = 16000) -> str:
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n… [truncated in hub mirror]"


def _read_workspace_doc(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"name": path.name, "content": "", "exists": False}
    size = _file_size(path)
    limit = HUGE_FILE_EXCERPT if path.name in HUGE_FILE_NAMES or size > 50_000 else DEFAULT_READ_LIMIT
    content = _read_text(path, limit=limit)
    return {
        "name": path.name,
        "content": content,
        "exists": True,
        "size_bytes": size,
        "truncated": size > limit or path.name in HUGE_FILE_NAMES,
    }


def _load_jsonl(path: Path, *, limit: int = 200) -> list[dict]:
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def _parse_inbox_rows(text: str) -> list[dict]:
    rows: list[dict] = []
    for line in (text or "").splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        if "Added" in line and "Task" in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 3:
            rows.append({"added": parts[0], "task": parts[1], "status": parts[2]})
    return rows


def _repo_plan(spec: dict) -> dict[str, Any]:
    root = Path(spec.get("repo_root") or "")
    plan_path = root / "os" / "plan.json"
    if not plan_path.is_file():
        return {"ok": False, "path": str(plan_path)}
    try:
        data = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {"ok": False, "error": str(e), "path": str(plan_path)}
    return {
        "ok": True,
        "path": str(plan_path),
        "phase": data.get("phase"),
        "active_focus": data.get("active_focus"),
        "next_tasks": data.get("next_tasks") or [],
        "done": (data.get("done") or [])[-8:],
        "blocked": data.get("blocked") or [],
        "deferred_paid": data.get("deferred_paid") or [],
        "last_verify": data.get("last_verify"),
        "updated_at": data.get("updated_at"),
    }


def _skill_for_agent(agent_id: str) -> dict[str, Any]:
    skill_path = SKILLS_ROOT / agent_id / "SKILL.md"
    shared = SKILLS_ROOT / "shared" / "research-intake" / "SKILL.md"
    excerpt = _read_text(skill_path, limit=2500) if skill_path.is_file() else ""
    return {
        "agent_skill": str(skill_path) if skill_path.is_file() else "",
        "cursor_name": f"sina-{agent_id.replace('_', '-')}" if agent_id != "sinaai_maintainer" else "sina-sinaai-maintainer",
        "shared_skill": str(shared) if shared.is_file() else "",
        "sync_script": "scripts/sync-cursor-agent-skills.sh",
        "exists": skill_path.is_file(),
        "excerpt": excerpt,
    }


def _workspace_files_index(private_root: Path, *, include_vault: bool = False) -> list[dict]:
    items: list[dict] = []
    if not private_root.is_dir():
        return items
    for p in sorted(private_root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(private_root).as_posix()
        if rel.startswith(".cursor/"):
            continue
        if not include_vault and rel.startswith("vault/"):
            continue
        try:
            st = p.stat()
            items.append(
                {
                    "path": rel,
                    "size": st.st_size,
                    "mtime": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
                }
            )
        except OSError:
            continue
    return items


def _subdir_documents(private_root: Path, *, slim: bool) -> dict[str, Any]:
    """memory/ and prompts/ — second Cursor sub-libraries."""
    out: dict[str, Any] = {}
    for sub in WORKSPACE_SUBDIRS:
        base = private_root / sub
        if not base.is_dir():
            continue
        files: list[dict] = []
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(private_root).as_posix()
            if _is_confidential_path(rel):
                files.append({"path": rel, "redacted": True, "size_bytes": _file_size(p)})
                continue
            if p.suffix.lower() in (".md", ".mdc", ".txt"):
                limit = 400 if slim else 4000
                files.append(
                    {
                        "path": rel,
                        "content": _read_text(p, limit=limit),
                        "size_bytes": _file_size(p),
                        "truncated": _file_size(p) > limit,
                    }
                )
            elif p.suffix.lower() == ".json" and not slim:
                try:
                    raw = p.read_text(encoding="utf-8", errors="replace")
                    files.append(
                        {
                            "path": rel,
                            "content": raw[:2000] + ("…" if len(raw) > 2000 else ""),
                            "size_bytes": _file_size(p),
                            "kind": "json",
                        }
                    )
                except OSError:
                    continue
            else:
                files.append({"path": rel, "size_bytes": _file_size(p), "binary": True})
        out[sub] = files
    return out


def _cursor_rules(private_root: Path) -> list[dict]:
    rules_dir = private_root / ".cursor" / "rules"
    if not rules_dir.is_dir():
        return []
    out: list[dict] = []
    for p in sorted(rules_dir.glob("*.mdc")):
        out.append(
            {
                "name": p.name,
                "path": str(p),
                "excerpt": _read_text(p, limit=600),
                "size_bytes": _file_size(p),
            }
        )
    return out


def _doc_full_body(path: Path, *, limit: int = 8000) -> str:
    text = _read_text(path, limit=limit + 500)
    if text.startswith("---") and "---" in text[3:]:
        parts = text.split("---", 2)
        if len(parts) > 2:
            return parts[2].strip()[:limit]
    return text[:limit]


def _filter_reviews(agent_id: str, spec: dict) -> list[dict]:
    try:
        from agent_command_reviews import reviews_payload  # noqa: WPS433

        items = reviews_payload().get("items") or []
    except Exception:
        return []
    label = (spec.get("label") or "").lower()
    lane = (spec.get("lane") or "").lower()
    hits: list[dict] = []
    for row in items:
        ws = (row.get("workspace") or "").lower()
        if agent_id in ws or (label and label.split()[0] in ws) or (lane and lane.lower() in ws):
            hits.append(
                {
                    "id": row.get("id"),
                    "title": row.get("title"),
                    "status": row.get("status"),
                    "severity": row.get("severity"),
                    "detail": (row.get("detail") or "")[:500],
                    "at": row.get("at") or row.get("created_at"),
                }
            )
    return hits[:20]


def _filter_research(agent_id: str) -> list[dict]:
    try:
        from agent_research_pipeline import research_pipeline_payload  # noqa: WPS433

        items = research_pipeline_payload(limit=80).get("items") or []
    except Exception:
        return []
    hits: list[dict] = []
    for row in items:
        src = row.get("source_agent") or ""
        targets = row.get("target_agents") or row.get("related_agents") or []
        if src == agent_id or agent_id in targets:
            hits.append(
                {
                    "id": row.get("id"),
                    "title": row.get("title"),
                    "stage": row.get("stage"),
                    "source_agent": src,
                    "body_excerpt": (row.get("body") or "")[:400],
                    "scores": row.get("scores"),
                    "updated_at": row.get("updated_at"),
                }
            )
    return hits[:15]


def workspace_mirror_payload(agent_id: str, *, detail: str = "full") -> dict[str, Any]:
    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}

    from agent_workspace_vault import _list_documents, _list_refs, _load_activity  # noqa: WPS433

    private_root = WORKSPACES_ROOT / agent_id

    slim = detail == "summary"
    inbox_text = _read_text(private_root / "INBOX.md", limit=2000 if slim else 16000)
    needs_text = _read_text(private_root / "NEEDS.md", limit=600 if slim else 4000)
    notes_text = _read_text(private_root / "notes.md", limit=400 if slim else 4000)
    governance_text = _read_text(private_root / "GOVERNANCE_LOCKED.md", limit=1200 if slim else 6000)
    session_prompt_text = _read_text(
        private_root / "WORKSPACE_SESSION_PROMPT_LOCKED.md", limit=600 if slim else 8000
    )

    workspace_docs: dict[str, Any] = {}
    if not slim:
        for name in WORKSPACE_MD_FILES:
            doc = _read_workspace_doc(private_root / name)
            if doc.get("exists"):
                workspace_docs[name] = doc
        for pattern in WORKSPACE_GLOB_MD:
            for p in sorted(private_root.glob(pattern)):
                if p.name not in workspace_docs and p.name not in HUGE_FILE_NAMES:
                    doc = _read_workspace_doc(p)
                    if doc.get("exists"):
                        workspace_docs[p.name] = doc

    always_doc = _read_workspace_doc(private_root / "INCIDENT_REPORT_ALWAYS.md") if not slim else {"exists": False}
    if always_doc.get("exists"):
        workspace_docs["INCIDENT_REPORT_ALWAYS.md"] = always_doc

    vault_docs = _list_documents(agent_id, limit=12 if slim else 50)
    if not slim:
        for d in vault_docs:
            doc_path = Path(d.get("path") or "")
            if doc_path.is_file():
                d["body"] = _doc_full_body(doc_path)

    activity_all = _load_activity(agent_id, limit=12 if slim else 500)
    activity_total = _load_activity(agent_id, limit=5000)
    activity_all_rev = list(reversed(activity_all))
    lessons = [a for a in activity_total if a.get("kind") == "learn"]
    actions = [a for a in activity_total if a.get("kind") in ("work", "action", "deposit")]

    conflicts = _load_jsonl(private_root / "conflict-reports.jsonl")
    asks = [
        {
            "type": "conflict",
            "id": c.get("id"),
            "title": c.get("title"),
            "status": c.get("status"),
            "description": (c.get("description") or "")[:500],
            "at": c.get("created_at"),
        }
        for c in conflicts
    ]

    incident_summary: dict = {}
    conflict_summary: dict = {}
    try:
        from agent_incident_system import agent_incident_summary  # noqa: WPS433

        incident_summary = agent_incident_summary(agent_id)
    except Exception:
        incident_summary = {}
    try:
        from agent_conflict_room import agent_conflict_summary  # noqa: WPS433

        conflict_summary = agent_conflict_summary(agent_id)
    except Exception:
        conflict_summary = {}

    governance_trace: list[dict] = []
    try:
        from agent_governance_events import tail_events  # noqa: WPS433

        governance_trace = tail_events(workspace_id=agent_id, limit=5 if slim else 15)
    except Exception:
        governance_trace = []

    scoreboard_row: dict = {}
    try:
        from agent_scoreboard import scoreboard_row  # noqa: WPS433

        scoreboard_row = scoreboard_row(spec)
    except Exception:
        scoreboard_row = {}

    workspace_manifest: dict = {}
    manifest_path = private_root / "manifest.json"
    if manifest_path.is_file():
        try:
            workspace_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            workspace_manifest = {"raw_error": "invalid json"}

    plan = _repo_plan(spec)
    mission = {
        "lane": spec.get("lane"),
        "thread": spec.get("thread"),
        "plane": spec.get("plane"),
        "governance_focus": spec.get("governance_focus"),
        "real_needs": spec.get("real_needs") or [],
        "p0": (plan.get("next_tasks") or [None])[0] if plan.get("ok") else None,
        "next_tasks": plan.get("next_tasks") if plan.get("ok") else [],
        "phase": plan.get("phase") if plan.get("ok") else None,
        "active_focus": plan.get("active_focus") if plan.get("ok") else None,
        "blocked": plan.get("blocked") if plan.get("ok") else [],
        "deferred_paid": plan.get("deferred_paid") if plan.get("ok") else [],
        "last_verify": plan.get("last_verify") if plan.get("ok") else None,
    }

    inbox_rows = _parse_inbox_rows(inbox_text)
    reviews = _filter_reviews(agent_id, spec)
    research = _filter_research(agent_id)

    skill = _skill_for_agent(agent_id)
    if slim:
        skill = {k: v for k, v in skill.items() if k != "excerpt"}

    return {
        "ok": True,
        "schema": "workspace_mirror_v1.1",
        "detail": detail,
        "built_at": _now(),
        "agent_id": agent_id,
        "label": spec.get("label"),
        "hub_tab": f"workspace-{agent_id}",
        "private_root": str(private_root),
        "repo_root": spec.get("repo_root"),
        "tagline": "Second Cursor — full workspace mirror in Sina Command",
        "stats": {
            "inbox_open": len([r for r in inbox_rows if (r.get("status") or "").lower() != "done"]),
            "vault_docs": len(vault_docs),
            "activity": len(activity_total),
            "lessons": len(lessons),
            "asks": len(asks),
            "reviews": len(reviews),
            "research": len(research),
            "files": len(_workspace_files_index(private_root)),
        },
        "mission": mission,
        "targets": {
            "plan": plan,
            "inbox_open": [r for r in inbox_rows if (r.get("status") or "").lower() != "done"],
            "inbox_done": [r for r in inbox_rows if (r.get("status") or "").lower() == "done"],
        },
        "inbox": {"raw": inbox_text, "rows": inbox_rows},
        "needs": needs_text,
        "notes": notes_text,
        "governance_excerpt": governance_text[:4000],
        "session_prompt": session_prompt_text,
        "skills": skill,
        "cursor_rules": [] if slim else _cursor_rules(private_root),
        "workspace_documents": workspace_docs,
        "workspace_document_names": sorted(workspace_docs.keys()) if workspace_docs else (
            [p.name for p in private_root.glob("*.md")] if slim and private_root.is_dir() else []
        ),
        "workspace_manifest": workspace_manifest,
        "subdir_documents": _subdir_documents(private_root, slim=slim),
        "vault": (lambda _refs: {
            "documents": vault_docs,
            "refs": [_sanitize_ref_row(r) for r in _refs],
            "doc_count": len(vault_docs),
            "ref_count": len(_refs),
            "activity_count": len(activity_total),
        })(_list_refs(agent_id, limit=30)),
        "memory": {
            "activity": activity_all_rev,
            "lessons": lessons[-12:] if slim else lessons,
            "actions": actions[-30:],
            "history_count": len(activity_total),
        },
        "asks_and_feedback": asks,
        "agent_reviews": reviews,
        "research": research,
        "governance_trace": governance_trace,
        "scoreboard": scoreboard_row,
        "conflict_room": conflict_summary,
        "incident": {
            "summary": incident_summary,
            "state": {},
            "my_insights": _read_text(private_root / "INCIDENT_MY_INSIGHTS.md", limit=3000),
            "report_excerpt": incident_summary.get("report_preview") or always_doc.get("content", "")[:HUGE_FILE_EXCERPT],
            "report_size_bytes": always_doc.get("size_bytes", 0),
        },
        "files_index": [] if slim else _workspace_files_index(private_root, include_vault=False),
        "vault_files_index": [] if slim else _workspace_files_index(private_root, include_vault=True),
        "sync_note": (
            "Summary mirror in hub — open page or Refresh mirror for full disk scan"
            if slim
            else "Filesystem scan at hub build — deposits on disk appear here even without vault API POST"
        ),
    }


def handle_mirror_action(body: dict) -> dict:
    action = (body.get("action") or "get").strip().lower()
    agent_id = (body.get("agent_id") or body.get("id") or "").strip()
    if action in ("get", "mirror", "list", "refresh", ""):
        if not agent_id:
            return {"ok": False, "error": "agent_id required"}
        return workspace_mirror_payload(agent_id)
    return {"ok": False, "error": f"unknown action: {action}"}

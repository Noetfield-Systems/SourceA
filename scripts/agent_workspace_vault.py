#!/usr/bin/env python3
"""Workspace vault — app middle layer: every agent deposits docs + activity in ~/.sina/agent-workspaces/<id>/."""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agent_workspace_registry import get_workspace

SINA_HOME = Path.home() / ".sina"
WORKSPACES_ROOT = SINA_HOME / "agent-workspaces"

DOC_KINDS = frozenset(
    {
        "deliverable",
        "evidence",
        "report",
        "procedure",
        "export",
        "note",
        "ref",
        "loop_round",
        "mind_share",
        "conflict",
        "incident",
        "activity",
    }
)
ACTIVITY_KINDS = frozenset({"work", "deposit", "loop", "report", "learn", "sync", "ref"})

VAULT_LAW = "AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(text: str, limit: int = 48) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:limit] or "doc"


def vault_paths(agent_id: str) -> dict[str, Path]:
    root = WORKSPACES_ROOT / agent_id
    vault = root / "vault"
    return {
        "root": root,
        "vault": vault,
        "documents": vault / "documents",
        "refs": vault / "refs",
        "activity": root / "activity.jsonl",
        "manifest": vault / "manifest.json",
        "readme": vault / "README.md",
    }


def ensure_vault(agent_id: str) -> dict:
    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}
    paths = vault_paths(agent_id)
    for key in ("vault", "documents", "refs"):
        paths[key].mkdir(parents=True, exist_ok=True)
    if not paths["readme"].is_file():
        paths["readme"].write_text(
            f"""# Workspace vault — {spec["label"]}

**Law:** `{VAULT_LAW}`

Sina Command is the **middle layer**. Deposit here:

- Every deliverable, report, evidence export, procedure you write
- Every significant work session (activity log)
- Repo file references when you ship artifacts in `{spec.get("repo_root", "")}`

**API:** `POST /api/workspace-vault` with `agent_id`, `action`.

**UI:** Private agent page → **Workspace vault** card.

Do not keep work only in repo chats or Finder — the app gathers everything for ASF and other agents (repo lens).
""",
            encoding="utf-8",
        )
    if not paths["activity"].is_file():
        paths["activity"].write_text(
            json.dumps(
                {
                    "at": _now(),
                    "kind": "sync",
                    "action": "vault_initialized",
                    "detail": f"Workspace vault ready — {spec['label']}",
                    "source": "system",
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
    if not paths["manifest"].is_file():
        paths["manifest"].write_text(
            json.dumps({"agent_id": agent_id, "created_at": _now(), "doc_count": 0, "ref_count": 0}, indent=2),
            encoding="utf-8",
        )
    return {"ok": True, "agent_id": agent_id, "vault_root": str(paths["vault"])}


def ensure_all_vaults() -> dict:
    from agent_workspace_registry import AGENT_WORKSPACES  # noqa: WPS433

    ids = []
    for spec in AGENT_WORKSPACES:
        ensure_vault(spec["id"])
        ids.append(spec["id"])
    return {"ok": True, "agents": ids}


def _append_activity(agent_id: str, *, kind: str, action: str, detail: str = "", source: str = "app", extra: dict | None = None) -> None:
    paths = vault_paths(agent_id)
    paths["root"].mkdir(parents=True, exist_ok=True)
    row = {
        "at": _now(),
        "kind": kind if kind in ACTIVITY_KINDS else "work",
        "action": (action or "work")[:120],
        "detail": (detail or "")[:2000],
        "source": source,
    }
    if extra:
        row.update(extra)
    with paths["activity"].open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_activity(agent_id: str, limit: int = 40) -> list[dict]:
    path = vault_paths(agent_id)["activity"]
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


def _list_documents(agent_id: str, limit: int = 30) -> list[dict]:
    docs_dir = vault_paths(agent_id)["documents"]
    if not docs_dir.is_dir():
        return []
    items: list[dict] = []
    for path in sorted(docs_dir.glob("DOC-*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        meta = _read_doc_meta(path)
        items.append(meta)
    return items


def _read_doc_meta(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"id": path.stem, "path": str(path), "title": path.stem}
    title = path.stem
    kind = "deliverable"
    deposited_at = ""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            block = text[3:end]
            for line in block.splitlines():
                if line.startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"')
                elif line.startswith("kind:"):
                    kind = line.split(":", 1)[1].strip()
                elif line.startswith("deposited_at:"):
                    deposited_at = line.split(":", 1)[1].strip()
    preview = text
    if "---" in text:
        parts = text.split("---", 2)
        preview = parts[2] if len(parts) > 2 else text
    preview = preview.strip()[:400]
    return {
        "id": path.stem,
        "title": title,
        "kind": kind,
        "deposited_at": deposited_at,
        "path": str(path),
        "preview": preview,
        "size": path.stat().st_size,
    }


def _list_refs(agent_id: str, limit: int = 20) -> list[dict]:
    refs_dir = vault_paths(agent_id)["refs"]
    if not refs_dir.is_dir():
        return []
    items: list[dict] = []
    for path in sorted(refs_dir.glob("REF-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        try:
            items.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return items


def _bump_manifest(agent_id: str) -> None:
    paths = vault_paths(agent_id)
    doc_n = len(list(paths["documents"].glob("DOC-*.md"))) if paths["documents"].is_dir() else 0
    ref_n = len(list(paths["refs"].glob("REF-*.json"))) if paths["refs"].is_dir() else 0
    act_n = len(_load_activity(agent_id, limit=10000))
    manifest = {
        "agent_id": agent_id,
        "updated_at": _now(),
        "doc_count": doc_n,
        "ref_count": ref_n,
        "activity_count": act_n,
        "last_activity_at": (_load_activity(agent_id, limit=1) or [{}])[-1].get("at", ""),
    }
    paths["manifest"].write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def deposit_document(
    agent_id: str,
    *,
    title: str,
    content: str,
    kind: str = "deliverable",
    source: str = "app",
    tags: list[str] | None = None,
    repo_path: str = "",
) -> dict:
    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}
    ensure_vault(agent_id)
    title = (title or "Untitled").strip()[:200]
    content = (content or "").strip()
    if len(content) < 10:
        return {"ok": False, "error": "Document body must be at least 10 characters"}
    kind = (kind or "deliverable").strip().lower()
    if kind not in DOC_KINDS:
        return {"ok": False, "error": f"kind must be one of: {sorted(DOC_KINDS)}"}

    doc_id = f"DOC-{uuid.uuid4().hex[:10]}"
    deposited_at = _now()
    tag_line = ", ".join(tags or [])
    paths = vault_paths(agent_id)
    body = f"""---
id: {doc_id}
agent_id: {agent_id}
title: "{title.replace('"', "'")}"
kind: {kind}
deposited_at: {deposited_at}
source: {source}
tags: [{tag_line}]
repo_path: {repo_path}
law: {VAULT_LAW}
---

# {title}

{content}
"""
    out_path = paths["documents"] / f"{doc_id}.md"
    out_path.write_text(body, encoding="utf-8")
    _append_activity(
        agent_id,
        kind="deposit",
        action="document_deposited",
        detail=title,
        source=source,
        extra={"doc_id": doc_id, "doc_kind": kind},
    )
    _bump_manifest(agent_id)
    return {
        "ok": True,
        "document": {
            "id": doc_id,
            "title": title,
            "kind": kind,
            "path": str(out_path),
            "deposited_at": deposited_at,
        },
    }


def register_repo_ref(
    agent_id: str,
    *,
    repo_path: str,
    title: str = "",
    kind: str = "evidence",
    note: str = "",
) -> dict:
    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}
    ensure_vault(agent_id)
    repo_path = (repo_path or "").strip()
    if len(repo_path) < 3:
        return {"ok": False, "error": "repo_path required"}
    title = (title or Path(repo_path).name).strip()[:200]
    ref_id = f"REF-{uuid.uuid4().hex[:10]}"
    row = {
        "id": ref_id,
        "agent_id": agent_id,
        "title": title,
        "kind": kind,
        "repo_path": repo_path,
        "note": (note or "")[:2000],
        "registered_at": _now(),
    }
    paths = vault_paths(agent_id)
    (paths["refs"] / f"{ref_id}.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
    _append_activity(agent_id, kind="ref", action="repo_ref_registered", detail=repo_path, extra={"ref_id": ref_id})
    _bump_manifest(agent_id)
    return {"ok": True, "ref": row}


def log_activity(
    agent_id: str,
    *,
    action: str,
    detail: str = "",
    kind: str = "work",
    source: str = "app",
) -> dict:
    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}
    ensure_vault(agent_id)
    action = (action or "").strip()
    if len(action) < 3:
        return {"ok": False, "error": "action required (min 3 chars)"}
    _append_activity(agent_id, kind=kind, action=action, detail=detail, source=source)
    _bump_manifest(agent_id)
    return {"ok": True, "logged": action}


def auto_deposit_loop_round(
    agent_id: str,
    *,
    round_num: int,
    title: str,
    summary: str,
    response: str,
) -> None:
    if not agent_id:
        return
    content = f"""## Round {round_num}: {title}

### Summary
{summary}

### Full response
{response[:12000]}
"""
    deposit_document(
        agent_id,
        title=f"Loop round {round_num}: {title or 'work'}",
        content=content,
        kind="loop_round",
        source="loop_auto",
        tags=["loop", f"round-{round_num}"],
    )


def auto_mirror_mind_share(agent_id: str, mind_row: dict) -> None:
    if not agent_id:
        return
    body = mind_row.get("body") or ""
    topic = mind_row.get("topic") or "general"
    kind = mind_row.get("kind") or "insight"
    deposit_document(
        agent_id,
        title=f"Mind share · {topic} ({kind})",
        content=body,
        kind="mind_share",
        source="council_auto",
        tags=["mind-share", kind, topic],
    )


def vault_summary(agent_id: str, *, doc_limit: int = 8, activity_limit: int = 12) -> dict:
    ensure_vault(agent_id)
    paths = vault_paths(agent_id)
    manifest = {}
    if paths["manifest"].is_file():
        try:
            manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}
    docs = _list_documents(agent_id, limit=doc_limit)
    refs = _list_refs(agent_id, limit=8)
    activity = _load_activity(agent_id, limit=activity_limit)
    return {
        "ok": True,
        "agent_id": agent_id,
        "vault_root": str(paths["vault"]),
        "vault_ready": paths["vault"].is_dir(),
        "activity_path": str(paths["activity"]),
        "doc_count": manifest.get("doc_count", len(docs)),
        "ref_count": manifest.get("ref_count", len(refs)),
        "activity_count": manifest.get("activity_count", len(activity)),
        "last_activity_at": manifest.get("last_activity_at") or (activity[-1].get("at") if activity else ""),
        "recent_documents": docs,
        "recent_refs": refs,
        "recent_activity": activity,
        "law_doc": VAULT_LAW,
        "tagline": "App middle layer — deposit all work here",
    }


def vault_payload(agent_id: str | None = None) -> dict:
    from agent_workspace_registry import AGENT_WORKSPACES  # noqa: WPS433

    ensure_all_vaults()
    if agent_id:
        return vault_summary(agent_id)
    totals = {"documents": 0, "refs": 0, "activity": 0}
    agents = []
    for spec in AGENT_WORKSPACES:
        s = vault_summary(spec["id"], doc_limit=5, activity_limit=5)
        totals["documents"] += int(s.get("doc_count") or 0)
        totals["refs"] += int(s.get("ref_count") or 0)
        totals["activity"] += int(s.get("activity_count") or 0)
        agents.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "doc_count": s.get("doc_count"),
                "ref_count": s.get("ref_count"),
                "activity_count": s.get("activity_count"),
                "last_activity_at": s.get("last_activity_at"),
                "hub_tab": f"workspace-{spec['id']}",
            }
        )
    return {
        "ok": True,
        "built_at": _now(),
        "law_doc": VAULT_LAW,
        "ecosystem_totals": totals,
        "agents": agents,
    }


def handle_vault_action(body: dict) -> dict:
    action = (body.get("action") or "list").strip().lower()
    agent_id = (body.get("agent_id") or body.get("id") or "").strip()
    if action == "ensure":
        if agent_id:
            return ensure_vault(agent_id)
        return ensure_all_vaults()
    if action == "deposit":
        return deposit_document(
            agent_id,
            title=body.get("title") or "",
            content=body.get("content") or body.get("body") or body.get("text") or "",
            kind=body.get("kind") or "deliverable",
            source=body.get("source") or "app",
            tags=body.get("tags"),
            repo_path=body.get("repo_path") or "",
        )
    if action == "register_ref":
        return register_repo_ref(
            agent_id,
            repo_path=body.get("repo_path") or "",
            title=body.get("title") or "",
            kind=body.get("kind") or "evidence",
            note=body.get("note") or body.get("detail") or "",
        )
    if action == "log_activity":
        return log_activity(
            agent_id,
            action=body.get("action_label") or body.get("label") or body.get("work") or "",
            detail=body.get("detail") or "",
            kind=body.get("kind") or "work",
            source=body.get("source") or "app",
        )
    if action == "list" and agent_id:
        return vault_summary(agent_id)
    if action in ("list", ""):
        return vault_payload(agent_id or None)
    return {"ok": False, "error": f"unknown action: {action}"}

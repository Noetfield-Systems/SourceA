#!/usr/bin/env python3
"""
Conflict Room — agents report clashes; ACE v3 auto-triage; never block repo progress.

Storage: ~/.sina/conflict-room/cases.jsonl
Law: AUTO_CONFLICT_ENGINE_V3_LOCKED.md + SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agent_workspace_registry import AGENT_WORKSPACES, get_workspace

SOURCE_A = Path(__file__).resolve().parents[1]
SINA_HOME = Path.home() / ".sina"
ROOM_ROOT = SINA_HOME / "conflict-room"
CASES_PATH = ROOM_ROOT / "cases.jsonl"
WORKSPACES_ROOT = SINA_HOME / "agent-workspaces"
ACE_DOC = "AUTO_CONFLICT_ENGINE_V3_LOCKED.md"
LAW_DOC = "SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md"
GLOBAL_BLOCKERS = SOURCE_A / "GLOBAL_BLOCKERS.json"

WORKFLOW_LAW = (
    "Report → ACE auto-triage → read guidance → **return to your task**. "
    "Never stop the whole project waiting for ASF or another agent. "
    "If unresolved, note it in INBOX and pick the next item in plan.json."
)

CONTINUE_RULE = (
    "**Do not block progress.** This case is logged for ASF/team visibility. "
    "Keep working on items that are not gated by this conflict unless safety (Type C critical) says stop that slice only."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_cases(limit: int = 80) -> list[dict]:
    if not CASES_PATH.is_file():
        return []
    rows = []
    for line in CASES_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    rows.sort(key=lambda c: c.get("created_at") or "", reverse=True)
    return rows[:limit]


def _append_case(case: dict) -> None:
    ROOM_ROOT.mkdir(parents=True, exist_ok=True)
    with CASES_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(case, ensure_ascii=False) + "\n")
    aid = case.get("agent_id")
    if aid:
        local = WORKSPACES_ROOT / aid / "conflict-reports.jsonl"
        local.parent.mkdir(parents=True, exist_ok=True)
        with local.open("a", encoding="utf-8") as f:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower().strip())


def _detect_planes(text: str) -> list[str]:
    low = _norm(text)
    planes = []
    if any(k in low for k in ("ssot", "registry", "mono", "design", "ecosystem map", "source a law")):
        planes.append("DESIGN")
    if any(k in low for k in ("runtime", "port", "pm2", "tailscale", "railway", "vercel", "deploy", "wire", "g3")):
        planes.append("EXECUTION")
    if any(k in low for k in ("repo", "github", "product_truth", "ship", "frontend", "mergepack", "noetfield github")):
        planes.append("DELIVERY")
    return planes or ["DELIVERY"]


def _blocker_hints() -> list[str]:
    if not GLOBAL_BLOCKERS.is_file():
        return []
    try:
        data = json.loads(GLOBAL_BLOCKERS.read_text(encoding="utf-8"))
        return [
            f"{b.get('project_id', '?')}: {b.get('item', '')}"
            for b in (data.get("blockers") or [])[:6]
        ]
    except (json.JSONDecodeError, OSError):
        return []


def ace_auto_triage(
    *,
    title: str,
    description: str,
    request_text: str,
    agent_id: str,
    spec: dict,
    related_paths: str = "",
) -> dict:
    """Rule-based ACE v3 intermediary — not LLM; fast; always allows continue_work."""
    blob = _norm(f"{title} {description} {request_text} {related_paths}")
    planes = _detect_planes(blob)
    may_edit_sa = bool(spec.get("may_edit_source_a"))
    forbidden = spec.get("forbidden_roots") or []

    ace_type = "B"
    status = "queued_asf"
    auto_resolved = False
    verdict = "defer_asf"
    actions = [
        "Continue your current plan.json next task that does not depend on this clash.",
        f"Log one line in `{WORKSPACES_ROOT / agent_id}/INBOX.md` with case id when done reporting.",
    ]
    guidance_parts = [CONTINUE_RULE, "", f"**Planes detected:** {', '.join(f'[{p}]' for p in planes)}"]

    # Type C — boundary / SourceA / forbidden roots
    if (
        not may_edit_sa
        and any(
            k in blob
            for k in (
                "sourcea",
                "source a",
                "sina command",
                "agent-control-panel",
                "sina-command-server",
                "edit lock",
                "hub code",
            )
        )
    ) or ("forbidden" in blob and "edit" in blob):
        ace_type = "C"
        verdict = "escalate_boundary"
        status = "queued_asf"
        guidance_parts.extend(
            [
                "**ACE Type C — boundary.** You must not edit forbidden roots.",
                f"Forbidden for you includes: `{'`, `'.join(Path(p).name for p in forbidden[:3])}` or see governance on your Private agents page.",
                "→ File `POST /api/agent-review` or Backlog → Agent reports. **Do not wait** — continue product work in your repo.",
            ]
        )
        actions.insert(0, "POST /api/agent-review with title + suggested one-tap Action (not Terminal).")

    # TrustField / law / B-001 style
    elif any(
        k in blob
        for k in (
            "b-001",
            "postgres",
            "no-card",
            "global_blockers",
            "law collision",
            "infra truth",
        )
    ):
        ace_type = "B"
        verdict = "proceed_with_doc"
        status = "auto_answered"
        auto_resolved = True
        hints = _blocker_hints()
        guidance_parts.extend(
            [
                "**ACE Type B — structural (infra/law).** Check GLOBAL_BLOCKERS + TrustField plan.",
                "→ Sina Command **Actions** or **Today** blocker card — not Terminal.",
                "→ Work on non-infra tasks (docs, UI in repo, tests) while ASF resolves infra.",
            ]
        )
        if hints:
            guidance_parts.append("**Known blockers:** " + "; ".join(hints[:4]))
        actions.insert(0, "Open GLOBAL_BLOCKERS via Actions → law (one tap).")

    # Wait / block language — override
    elif any(
        k in blob
        for k in (
            "wait for",
            "waiting for",
            "blocked until",
            "cannot proceed until",
            "need response before",
            "stop work",
        )
    ):
        ace_type = "A"
        verdict = "proceed"
        status = "auto_answered"
        auto_resolved = True
        guidance_parts.extend(
            [
                "**ACE override — no project freeze.** Waiting for ASF/another agent is not a stop rule.",
                "→ You reported here; **return to work** on independent tasks.",
                "→ Revisit this case when you finish the current loop round — not before stopping everything.",
            ]
        )

    # Port / drift / naming
    elif any(
        k in blob
        for k in (
            "port ",
            ":8000",
            ":13020",
            "drift",
            "naming",
            "regime",
            "topology",
        )
    ):
        ace_type = "A"
        verdict = "proceed"
        status = "auto_answered"
        auto_resolved = True
        guidance_parts.extend(
            [
                "**ACE Type A — informational drift.** Label with [DESIGN] vs [EXECUTION] vs [DELIVERY] (ACE R9).",
                "→ Document in your private notes; do not treat as halt.",
                f"→ Read `{ACE_DOC}` § Drift classification.",
            ]
        )

    # SSOT vs repo / plane clash
    elif len(planes) >= 2 or any(k in blob for k in ("ssot says", "repo says", "contradiction", "which wins")):
        ace_type = "B"
        verdict = "proceed_with_doc"
        status = "auto_answered"
        auto_resolved = True
        guidance_parts.extend(
            [
                "**ACE Type B — multi-plane.** No single layer owns all truth (ACE v3 core principle).",
                "→ DELIVERY repo ships; DESIGN SSOT describes; EXECUTION proves.",
                "→ Read `NOETFIELD_REPO_ALIGNMENT.md` or `AUTO_CONFLICT_ENGINE_V3_LOCKED.md` for your thread.",
                "→ Ship in your repo plane; do not edit Desktop SourceA unless you are maintainer.",
            ]
        )

    # Placeholder / paste commands
    elif any(k in blob for k in ("paste", "placeholder", "run_<", "<from-phone>", "paste-real-url")):
        ace_type = "A"
        verdict = "proceed"
        status = "auto_answered"
        auto_resolved = True
        guidance_parts.extend(
            [
                "**ACE Type A — doc/command hazard (near-miss class).**",
                "→ Never paste placeholders; use real run ids / URLs from screen.",
                "→ See repo `INCIDENT_*` docs in Bridge or MergePack if deploy/wire.",
                "→ Fix your next command block; continue other tasks.",
            ]
        )

    else:
        guidance_parts.extend(
            [
                "**ACE Type B — default structural.** Logged for ASF thread review.",
                "→ Try one concrete next step in your repo; if still stuck after 30 min, add Agent report — not a full stop.",
                f"→ Law: `{LAW_DOC}`",
            ]
        )

    guidance = "\n".join(guidance_parts)
    return {
        "ace_type": ace_type,
        "ace_verdict": verdict,
        "ace_planes": planes,
        "ace_guidance": guidance,
        "ace_auto_resolved": auto_resolved,
        "status": status,
        "continue_work": True,
        "suggested_actions": actions,
        "workflow_law": WORKFLOW_LAW,
    }


def agent_conflict_summary(agent_id: str) -> dict:
    cases = [c for c in _load_cases(200) if c.get("agent_id") == agent_id]
    open_n = sum(1 for c in cases if c.get("status") in ("open", "queued_asf"))
    return {
        "agent_id": agent_id,
        "open_count": open_n,
        "total_count": len(cases),
        "last_case": cases[0] if cases else None,
    }


def conflict_room_payload(agent_id: str | None = None) -> dict:
    ROOM_ROOT.mkdir(parents=True, exist_ok=True)
    cases = _load_cases(60)
    open_cases = [c for c in cases if c.get("status") in ("open", "queued_asf")]
    agents = []
    for spec in AGENT_WORKSPACES:
        aid = spec["id"]
        summ = agent_conflict_summary(aid)
        agents.append(
            {
                "id": aid,
                "label": spec["label"],
                "open_count": summ["open_count"],
                "total_count": summ["total_count"],
            }
        )
    sel = agent_id or AGENT_WORKSPACES[0]["id"]
    my_cases = [c for c in cases if c.get("agent_id") == sel][:12]
    return {
        "ok": True,
        "law_doc": LAW_DOC,
        "ace_doc": ACE_DOC,
        "room_root": str(ROOM_ROOT),
        "workflow_law": WORKFLOW_LAW,
        "cases": cases,
        "open_count": len(open_cases),
        "agents": agents,
        "selected_agent_id": sel,
        "my_cases": my_cases,
        "my_summary": agent_conflict_summary(sel),
        "tagline": "Report clash → ACE auto-triage → guidance → keep working (never block the project).",
    }


def handle_conflict_room_action(body: dict) -> dict:
    action = (body.get("action") or "list").strip().lower()
    agent_id = (body.get("agent_id") or body.get("id") or "").strip()

    if action in ("ensure", "sync", "refresh", "list"):
        return conflict_room_payload(agent_id or None)

    if not agent_id:
        spec = get_workspace((body.get("workspace_id") or ""))
        agent_id = spec["id"] if spec else ""
    if not agent_id:
        return {"ok": False, "error": "agent_id required"}

    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}

    if action == "submit":
        title = (body.get("title") or "").strip() or f"{spec['label']} — conflict"
        description = (body.get("description") or body.get("conflict") or "").strip()
        request_text = (body.get("request") or body.get("ask") or "").strip()
        related = (body.get("related_paths") or body.get("paths") or "").strip()
        if len(description) < 15:
            return {"ok": False, "error": "Describe the conflict (at least 15 characters)"}

        triage = ace_auto_triage(
            title=title,
            description=description,
            request_text=request_text,
            agent_id=agent_id,
            spec=spec,
            related_paths=related,
        )
        case = {
            "id": str(uuid.uuid4())[:12],
            "agent_id": agent_id,
            "agent_label": spec["label"],
            "thread": spec.get("thread", ""),
            "lane": spec.get("lane", ""),
            "title": title[:200],
            "description": description[:4000],
            "request": request_text[:2000],
            "related_paths": related[:1000],
            "created_at": _now(),
            **triage,
        }
        _append_case(case)
        msg = (
            "ACE auto-answer ready — return to work"
            if triage.get("ace_auto_resolved")
            else "Reported — ASF queued; continue other tasks"
        )
        return {
            "ok": True,
            "message": msg,
            "case": case,
            **conflict_room_payload(agent_id),
        }

    if action == "close":
        case_id = (body.get("case_id") or "").strip()
        # jsonl append-only: mark close via new event line
        close_evt = {
            "id": str(uuid.uuid4())[:12],
            "kind": "close",
            "closes": case_id,
            "agent_id": agent_id,
            "closed_at": _now(),
            "status": "closed",
        }
        _append_case(close_evt)
        return {"ok": True, "message": "Case marked closed", **conflict_room_payload(agent_id)}

    return {"ok": False, "error": f"unknown action: {action}"}

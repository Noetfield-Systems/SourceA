#!/usr/bin/env python3
"""Agent Council Room — Mind Share, repo lens, paradox scan, advisory votes."""
from __future__ import annotations

import json
import re
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from agent_private_workspaces import WORKSPACES_ROOT, ensure_all_workspaces, loop_workspaces_payload
from agent_workspace_registry import AGENT_WORKSPACES, GOVERNANCE_VERSION, get_workspace

SOURCE_A = Path(__file__).resolve().parents[1]
SINA_HOME = Path.home() / ".sina"
COUNCIL_ROOT = SINA_HOME / "council-room"
MIND_SHARE_PATH = COUNCIL_ROOT / "mind-share.jsonl"

PHASE = 1
PHASE_LABEL = "Mind Share · repo lens · advisory votes"

TOPICS_PATH = COUNCIL_ROOT / "topics.jsonl"
VOTES_PATH = COUNCIL_ROOT / "votes.jsonl"
TOPIC_CATEGORIES = frozenset({"product", "hub", "law", "lane", "process", "ecosystem"})

MIND_KINDS = frozenset({"insight", "opinion", "procedure", "question", "paradox"})

FEEDBACK_CHANNELS: list[dict] = [
    {
        "id": "mind-share",
        "label": "Mind Share",
        "tab": "council-room",
        "api": "/api/council-room",
        "purpose": "Cross-agent insights, opinions, procedures — learn from each repo lens",
        "who": "all_registered_agents",
    },
    {
        "id": "agent-review",
        "label": "Agent reports",
        "tab": "backlog",
        "api": "/api/agent-review",
        "purpose": "Hub bugs, missing Actions — never edit SourceA yourself",
        "who": "all_registered_agents",
    },
    {
        "id": "conflict-room",
        "label": "Conflict Room",
        "tab": "conflict-room",
        "api": "/api/conflict-room",
        "purpose": "ACE triage when laws or strategies disagree",
        "who": "all_registered_agents",
    },
    {
        "id": "incident-room",
        "label": "Incident Room",
        "tab": "incident-room",
        "api": "/api/incident-room",
        "purpose": "Weekly incident share, insights, certification",
        "who": "all_registered_agents",
    },
    {
        "id": "workspace-page",
        "label": "Private agent page",
        "tab": "workspace-<id>",
        "api": None,
        "purpose": "Governance, 10-pack loop, round submit",
        "who": "per_agent",
    },
    {
        "id": "council-room",
        "label": "Council Room",
        "tab": "council-room",
        "api": "/api/council-room",
        "purpose": "Shared rules, repo lens, mind share, paradox board",
        "who": "all_registered_agents",
    },
]

ROLE_LIMITS: dict[str, dict] = {
    "maintainer": {
        "may_edit_source_a": True,
        "may_edit_own_repo": True,
        "report_via": ["mind-share", "agent-review", "council-room"],
    },
    "portfolio": {
        "may_edit_source_a": False,
        "may_edit_own_repo": True,
        "report_via": ["mind-share", "agent-review", "conflict-room", "incident-room", "council-room"],
    },
    "product": {
        "may_edit_source_a": False,
        "may_edit_own_repo": True,
        "report_via": ["mind-share", "agent-review", "conflict-room", "incident-room", "council-room"],
    },
    "automation": {
        "may_edit_source_a": False,
        "may_edit_own_repo": False,
        "report_via": ["mind-share", "agent-review", "incident-room", "council-room"],
    },
}

STANCE_POS = frozenset({"yes", "ship", "now", "approve", "go", "must", "should", "agree", "pro"})
STANCE_NEG = frozenset({"no", "defer", "wait", "block", "stop", "reject", "disagree", "against", "dont", "don't"})

MIND_SHARE_LAW = "AGENT_MIND_SHARE_LOCKED_v1.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _norm_topic(topic: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (topic or "").lower()).strip("-")[:48]


def _preview_file(path: Path, limit: int = 420) -> str:
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "…"


def _stance_hint(text: str) -> str:
    low = re.sub(r"\s+", " ", (text or "").lower())
    pos = sum(1 for w in STANCE_POS if re.search(rf"\b{re.escape(w)}\b", low))
    neg = sum(1 for w in STANCE_NEG if re.search(rf"\b{re.escape(w)}\b", low))
    if pos > neg and pos > 0:
        return "lean_yes"
    if neg > pos and neg > 0:
        return "lean_no"
    return "neutral"


def _load_mind_share(limit: int = 60) -> list[dict]:
    if not MIND_SHARE_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in MIND_SHARE_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    rows.sort(key=lambda r: r.get("at") or "", reverse=True)
    return rows[:limit]


def _append_mind_share(row: dict) -> None:
    COUNCIL_ROOT.mkdir(parents=True, exist_ok=True)
    with MIND_SHARE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _append_jsonl(path: Path, row: dict) -> None:
    COUNCIL_ROOT.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_jsonl(path: Path, limit: int = 200) -> list[dict]:
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


def _load_topics() -> list[dict]:
    rows = _load_jsonl(TOPICS_PATH, 100)
    rows.sort(key=lambda r: r.get("at") or "", reverse=True)
    return rows


def _load_votes() -> list[dict]:
    return _load_jsonl(VOTES_PATH, 500)


def _topic_vote_tally(topic_id: str, votes: list[dict]) -> dict:
    latest: dict[str, str] = {}
    for v in votes:
        if v.get("topic_id") != topic_id:
            continue
        aid = v.get("agent_id") or ""
        if aid:
            latest[aid] = (v.get("option_id") or "?").upper()
    tally: dict[str, int] = {}
    for oid in latest.values():
        tally[oid] = tally.get(oid, 0) + 1
    return {"tally": tally, "voters": latest, "vote_count": len(latest)}


def create_topic(body: dict) -> dict:
    agent_id = (body.get("agent_id") or body.get("created_by") or "").strip()
    if agent_id not in {w["id"] for w in AGENT_WORKSPACES}:
        return {"ok": False, "error": "agent_id required (registered agent)"}
    title = (body.get("title") or "").strip()
    if len(title) < 8:
        return {"ok": False, "error": "title min 8 chars"}
    category = (body.get("category") or "ecosystem").strip().lower()
    if category not in TOPIC_CATEGORIES:
        return {"ok": False, "error": f"category must be one of: {sorted(TOPIC_CATEGORIES)}"}
    options = body.get("options") or []
    if not options:
        options = [{"id": "A", "label": "Approve / proceed"}, {"id": "B", "label": "Defer / needs more"}]
    row = {
        "id": f"COUNCIL-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "title": title[:240],
        "category": category,
        "status": "open",
        "created_by": agent_id,
        "related_agents": body.get("related_agents") or [agent_id],
        "options": options[:6],
        "note": (body.get("note") or "")[:2000],
    }
    _append_jsonl(TOPICS_PATH, row)
    return {"ok": True, "topic": row}


def vote_topic(body: dict) -> dict:
    agent_id = (body.get("agent_id") or "").strip()
    topic_id = (body.get("topic_id") or "").strip()
    option_id = (body.get("option_id") or "").strip().upper()
    if agent_id not in {w["id"] for w in AGENT_WORKSPACES}:
        return {"ok": False, "error": "agent_id required"}
    if not topic_id or not option_id:
        return {"ok": False, "error": "topic_id and option_id required"}
    topics = {t["id"]: t for t in _load_topics()}
    topic = topics.get(topic_id)
    if not topic or topic.get("status") != "open":
        return {"ok": False, "error": "topic not open"}
    valid = {str(o.get("id", "")).upper() for o in topic.get("options") or []}
    if option_id not in valid:
        return {"ok": False, "error": "invalid option_id"}
    row = {
        "at": _now(),
        "topic_id": topic_id,
        "agent_id": agent_id,
        "option_id": option_id,
        "note": (body.get("note") or "")[:800],
    }
    _append_jsonl(VOTES_PATH, row)
    return {"ok": True, "vote": row}


def close_topic(body: dict) -> dict:
    topic_id = (body.get("topic_id") or "").strip()
    if not topic_id:
        return {"ok": False, "error": "topic_id required"}
    topics = _load_topics()
    found = None
    for t in topics:
        if t.get("id") == topic_id:
            found = t
            break
    if not found:
        return {"ok": False, "error": "topic not found"}
    found["status"] = "closed"
    found["closed_at"] = _now()
    _append_jsonl(TOPICS_PATH, found)
    return {"ok": True, "topic": found}


def _topics_with_votes() -> list[dict]:
    votes = _load_votes()
    out = []
    for t in _load_topics():
        if t.get("status") == "archived":
            continue
        tally = _topic_vote_tally(t["id"], votes)
        out.append({**t, **tally})
    return out


def _blueprint_nav_sections() -> list[dict]:
    path = SOURCE_A / "AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md"
    if not path.is_file():
        return []
    sections: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^## (\d+)\.\s+(.+)$", line.strip())
        if m:
            n = int(m.group(1))
            sections.append(
                {
                    "n": n,
                    "title": m.group(2).strip(),
                    "path": "AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md",
                    "scope": "exclusive" if n == 4 else "inclusive",
                }
            )
    return sections


def _shared_rules_digest_enriched() -> list[dict]:
    chain = _shared_rules_digest_raw()
    try:
        from agent_rules_in_charge import enrich_shared_rules_digest  # noqa: WPS433

        return enrich_shared_rules_digest(chain)
    except Exception:
        return chain


def _shared_rules_digest_raw() -> list[dict]:
    try:
        from hub_essentials_index import READ_CHAIN  # noqa: WPS433

        chain = list(READ_CHAIN)
    except Exception:
        chain = []
    extra = [
        {"path": MIND_SHARE_LAW, "title": "Mind Share law", "why": "Cross-agent learning + paradox rules."},
        {"path": "AGENT_OPERATING_ROLES_LOCKED_v1.md", "title": "Operating roles", "why": "ROLE-IMPLEMENTER vs maintainer boundaries."},
        {"path": "SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md", "title": "Private workspaces", "why": "Where private scratch lives vs repo code."},
    ]
    seen = {c["path"] for c in chain}
    for e in extra:
        if e["path"] not in seen:
            chain.append(e)
    return chain


def _repo_lens(spec: dict, private_root: Path) -> dict:
    insight = _preview_file(private_root / "INCIDENT_MY_INSIGHTS.md", 500)
    needs = _preview_file(private_root / "NEEDS.md", 400)
    notes = _preview_file(private_root / "notes.md", 280)
    conflicts = 0
    try:
        from agent_conflict_room import agent_conflict_summary  # noqa: WPS433

        conflicts = int(agent_conflict_summary(spec["id"]).get("open_count") or 0)
    except Exception:
        pass
    vault_docs = 0
    vault_last = ""
    try:
        from agent_workspace_vault import vault_summary  # noqa: WPS433

        vs = vault_summary(spec["id"], doc_limit=1, activity_limit=1)
        vault_docs = int(vs.get("doc_count") or 0)
        vault_last = vs.get("last_activity_at") or ""
    except Exception:
        pass
    return {
        "agent_id": spec["id"],
        "label": spec.get("label"),
        "role": spec.get("role"),
        "lane": spec.get("lane"),
        "plane": spec.get("plane"),
        "repo_root": spec.get("repo_root"),
        "governance_focus": spec.get("governance_focus", ""),
        "real_needs": spec.get("real_needs") or [],
        "forbidden_summary": "; ".join(Path(p).name for p in (spec.get("forbidden_roots") or [])[:3]),
        "insight_snippet": insight,
        "needs_snippet": needs,
        "notes_snippet": notes,
        "open_conflicts": conflicts,
        "vault_doc_count": vault_docs,
        "vault_last_activity_at": vault_last,
        "hub_tab": f"workspace-{spec['id']}",
    }


def _detect_paradoxes(
    mind_rows: list[dict],
    repo_lenses: list[dict],
) -> list[dict]:
    paradoxes: list[dict] = []
    by_topic: dict[str, list[dict]] = defaultdict(list)
    for row in mind_rows:
        tag = _norm_topic(row.get("topic") or "")
        if tag:
            by_topic[tag].append(row)

    for tag, rows in by_topic.items():
        agents = {r.get("agent_id") for r in rows if r.get("agent_id")}
        stances = {r.get("stance_hint") for r in rows if r.get("stance_hint")}
        if len(agents) >= 2 and "lean_yes" in stances and "lean_no" in stances:
            paradoxes.append(
                {
                    "id": f"PARADOX-TOPIC-{tag}",
                    "kind": "divergent_opinions",
                    "topic": tag,
                    "title": f"Divergent opinions on «{tag}»",
                    "agents": sorted(agents),
                    "detail": "Multiple agents posted opposing stances on the same topic tag.",
                    "severity": "medium",
                }
            )

    paradox_kinds = [r for r in mind_rows if r.get("kind") == "paradox"]
    for row in paradox_kinds[:8]:
        paradoxes.append(
            {
                "id": row.get("id"),
                "kind": "agent_flagged",
                "topic": row.get("topic"),
                "title": f"Paradox flagged by {row.get('label')}",
                "agents": [row.get("agent_id")],
                "detail": (row.get("body") or "")[:300],
                "severity": "high",
            }
        )

    try:
        from agent_conflict_room import _load_cases  # noqa: WPS433

        for case in _load_cases(12):
            if case.get("status") in ("closed", "resolved"):
                continue
            paradoxes.append(
                {
                    "id": case.get("case_id") or case.get("id"),
                    "kind": "conflict_case",
                    "topic": _norm_topic(case.get("title") or "conflict"),
                    "title": case.get("title") or "Open conflict",
                    "agents": [case.get("agent_id")],
                    "detail": (case.get("description") or "")[:240],
                    "severity": "high" if case.get("ace_type") == "C" else "medium",
                    "ace_type": case.get("ace_type"),
                }
            )
    except Exception:
        pass

    boundaries = [
        ("noetfield_local", "noetfield_cloud", "Local docs SSOT vs cloud ship repo — intentional lane split"),
        ("semej", "sinaai_maintainer", "Browser automation read-only vs Command maintainer edit rights"),
    ]
    lens_by_id = {l["agent_id"]: l for l in repo_lenses}
    for a, b, note in boundaries:
        if a in lens_by_id and b in lens_by_id:
            paradoxes.append(
                {
                    "id": f"BOUNDARY-{a}-{b}",
                    "kind": "lane_boundary",
                    "topic": "lane-boundary",
                    "title": f"{lens_by_id[a]['label']} ↔ {lens_by_id[b]['label']}",
                    "agents": [a, b],
                    "detail": note,
                    "severity": "info",
                }
            )

    seen_ids: set[str] = set()
    out: list[dict] = []
    for p in paradoxes:
        pid = str(p.get("id") or "")
        if pid in seen_ids:
            continue
        seen_ids.add(pid)
        out.append(p)
    return out[:20]


def workspace_integration_readiness(
    spec: dict,
    *,
    private_root: Path,
    pack_ready: bool,
    incident: dict,
) -> dict:
    repo = Path(spec.get("repo_root") or "")
    repo_marker = repo / ".sina-agent" / "README.md"
    checks = [
        {"id": "governance", "label": "GOVERNANCE_LOCKED.md", "ok": (private_root / "GOVERNANCE_LOCKED.md").is_file(), "required": True},
        {"id": "inbox", "label": "INBOX.md", "ok": (private_root / "INBOX.md").is_file(), "required": True},
        {"id": "repo_marker", "label": ".sina-agent/README.md", "ok": not repo.is_dir() or repo_marker.is_file(), "required": True},
        {"id": "pack_or_lane", "label": "10-pack or custom lane", "ok": pack_ready or not spec.get("pack_id"), "required": True},
        {"id": "incident_files", "label": "Incident always-read files", "ok": (private_root / "INCIDENT_REPORT_ALWAYS.md").is_file(), "required": True},
        {"id": "hub_page", "label": "Hub private page wired", "ok": True, "required": True},
        {"id": "source_a_lock", "label": "SourceA edit lock", "ok": bool(spec.get("may_edit_source_a")) or bool(spec.get("forbidden_roots")), "required": True},
        {"id": "mind_share_read", "label": "Can read Council Mind Share", "ok": True, "required": True},
        {
            "id": "vault",
            "label": "Workspace vault (middle layer)",
            "ok": (private_root / "vault").is_dir(),
            "required": True,
        },
        {
            "id": "vault_activity",
            "label": "Activity log wired",
            "ok": (private_root / "activity.jsonl").is_file(),
            "required": True,
        },
    ]
    mandatory = [c for c in checks if c["required"]]
    passed = sum(1 for c in mandatory if c["ok"])
    total = len(mandatory)
    return {
        "checks": checks,
        "passed": passed,
        "total": total,
        "pct": round(100 * passed / total) if total else 100,
        "ready": all(c["ok"] for c in mandatory),
    }


def _job_surfaces(spec: dict) -> dict:
    aid = spec["id"]
    role = spec.get("role") or "portfolio"
    limits = ROLE_LIMITS.get(role, ROLE_LIMITS["portfolio"])
    surfaces = [
        {"tab": f"workspace-{aid}", "label": "Private workspace page", "kind": "work"},
        {"tab": f"workspace-{aid}", "label": "Workspace vault · deposit all work", "kind": "vault"},
        {"tab": "council-room", "label": "Council Room · Mind Share", "kind": "learn"},
        {"tab": "council-room", "label": "Repo lens compare", "kind": "learn"},
        {"tab": "backlog", "label": "Agent reports", "kind": "report"},
        {"tab": "conflict-room", "label": "Conflict Room", "kind": "report"},
        {"tab": "incident-room", "label": "Incident Room", "kind": "report"},
        {"tab": "agent-loop", "label": "Agent hub index", "kind": "nav"},
    ]
    if aid == "semej":
        surfaces.insert(1, {"tab": "semej", "label": "SEMEJ browser chain", "kind": "work"})
    return {"surfaces": surfaces, "role": role, "limits": limits}


def share_mind(body: dict) -> dict:
    agent_id = (body.get("agent_id") or body.get("id") or "").strip()
    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}
    kind = (body.get("kind") or "insight").strip().lower()
    if kind not in MIND_KINDS:
        return {"ok": False, "error": f"kind must be one of: {sorted(MIND_KINDS)}"}
    topic = (body.get("topic") or "general").strip()[:64]
    text = (body.get("body") or body.get("text") or "").strip()
    if len(text) < 20:
        return {"ok": False, "error": "Write at least 20 characters"}
    if re.search(r"edit\s+sourcea|patch\s+sina-command|git\s+access.*sourcea", text, re.I):
        return {"ok": False, "error": "Mind share cannot request SourceA edits — use Agent reports"}

    row = {
        "id": f"MIND-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "agent_id": agent_id,
        "label": spec.get("label"),
        "lane": spec.get("lane"),
        "repo_root": spec.get("repo_root"),
        "kind": kind,
        "topic": topic,
        "topic_norm": _norm_topic(topic),
        "body": text[:4000],
        "stance_hint": _stance_hint(text),
    }
    _append_mind_share(row)
    try:
        from agent_governance_events import log_governance_event  # noqa: WPS433

        log_governance_event(
            "mind_share",
            workspace_id=agent_id,
            detail=f"{kind}:{topic}",
            extra={"mind_id": row["id"]},
        )
    except Exception:
        pass
    try:
        from agent_workspace_vault import auto_mirror_mind_share, log_activity  # noqa: WPS433

        auto_mirror_mind_share(agent_id, row)
        log_activity(agent_id, action="mind_share_posted", detail=f"{kind}:{topic}", kind="learn", source="council")
    except Exception:
        pass
    return {"ok": True, "shared": row}


def council_room_payload() -> dict:
    ensure_all_workspaces()
    COUNCIL_ROOT.mkdir(parents=True, exist_ok=True)
    loop = loop_workspaces_payload()
    mind_rows = _load_mind_share()
    repo_lenses: list[dict] = []
    agents_out = []
    ready_count = 0

    for row in loop.get("loop_workspaces") or []:
        spec = next((w for w in AGENT_WORKSPACES if w["id"] == row["id"]), row)
        private_root = Path(row.get("private_root") or WORKSPACES_ROOT / row["id"])
        integration = workspace_integration_readiness(
            spec,
            private_root=private_root,
            pack_ready=bool(row.get("pack_ready")),
            incident=row.get("incident") or {},
        )
        if integration["ready"]:
            ready_count += 1
        lens = _repo_lens(spec, private_root)
        repo_lenses.append(lens)
        agent_mind = [m for m in mind_rows if m.get("agent_id") == spec["id"]][:5]
        job = _job_surfaces(spec)
        agents_out.append(
            {
                **row,
                "id": row["id"],
                "label": row.get("label") or spec.get("label"),
                "role": spec.get("role"),
                "lane": spec.get("lane"),
                "plane": spec.get("plane"),
                "pack_ready": bool(row.get("pack_ready")),
                "pack_id": spec.get("pack_id"),
                "may_edit_source_a": bool(spec.get("may_edit_source_a")),
                "integration": integration,
                "job_surfaces": job["surfaces"],
                "role_limits": job["limits"],
                "hub_tab": f"workspace-{row['id']}",
                "repo_lens": lens,
                "mind_shares": agent_mind,
            }
        )

    paradoxes = _detect_paradoxes(mind_rows, repo_lenses)
    total = len(agents_out)
    fleet_pct = round(100 * ready_count / total) if total else 0

    strategic_brief: dict = {}
    try:
        from council_strategic_brief import strategic_brief_payload  # noqa: WPS433

        strategic_brief = strategic_brief_payload()
    except Exception:
        strategic_brief = {"ok": False, "error": "strategic brief unavailable"}

    return {
        "ok": True,
        "built_at": _now(),
        "phase": PHASE,
        "phase_label": PHASE_LABEL,
        "strategic_brief": strategic_brief,
        "phase_1_gate": {
            "required_agents": total,
            "ready_agents": ready_count,
            "fleet_ready_pct": fleet_pct,
            "all_ready": ready_count == total and total > 0,
            "audits": ["audit_private_agent_pages.py", "audit_agent_governance_e2e.py"],
        },
        "policy_doc": "AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md",
        "council_doc": "AGENT_COUNCIL_ROOM_LOCKED_v1.md",
        "mind_share_doc": MIND_SHARE_LAW,
        "unifying_hub_doc": "AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md",
        "governance_version": GOVERNANCE_VERSION,
        "channels": FEEDBACK_CHANNELS,
        "forbidden_global": [
            "Edit ~/Desktop/SourceA for non-maintainer agents",
            "Patch agent-control-panel or sina-command-server.py",
            "Ask founder for Terminal or SourceA git access",
        ],
        "shared_rules": _shared_rules_digest_enriched(),
        "repo_lenses": repo_lenses,
        "mind_share": mind_rows,
        "mind_share_count": len(mind_rows),
        "paradoxes": paradoxes,
        "paradox_count": len(paradoxes),
        "agents": agents_out,
        "topics": _topics_with_votes(),
        "topics_open": len([t for t in _topics_with_votes() if t.get("status") == "open"]),
        "voting_live": True,
        "topics_note": "Advisory votes live — ASF + maintainer decide implementation",
        "blueprint_nav": _blueprint_nav_sections(),
        "blueprint_doc": "AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md",
        "storage_root": str(COUNCIL_ROOT),
        "mind_share_path": str(MIND_SHARE_PATH),
        "topics_path": str(TOPICS_PATH),
        "votes_path": str(VOTES_PATH),
    }


def handle_post(body: dict) -> dict:
    action = (body.get("action") or "").strip().lower()
    if action in ("list", ""):
        return council_room_payload()
    if action == "share_mind":
        result = share_mind(body)
        if result.get("ok"):
            result["room"] = council_room_payload()
        return result
    if action == "create_topic":
        result = create_topic(body)
        if result.get("ok"):
            result["room"] = council_room_payload()
        return result
    if action == "vote":
        result = vote_topic(body)
        if result.get("ok"):
            result["room"] = council_room_payload()
        return result
    if action in ("close_topic", "close"):
        result = close_topic(body)
        if result.get("ok"):
            result["room"] = council_room_payload()
        return result
    return {"ok": False, "error": f"unknown action: {action}"}

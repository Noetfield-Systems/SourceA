#!/usr/bin/env python3
"""Agent Hub research pipeline — intake → brainstorm → evaluate → promote."""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent_workspace_registry import AGENT_WORKSPACES, get_workspace

SOURCE_A = Path(__file__).resolve().parents[1]
SINA_HOME = Path.home() / ".sina"
RESEARCH_ROOT = SINA_HOME / "agent-research"
ITEMS_PATH = RESEARCH_ROOT / "items.jsonl"
LAW_DOC = "AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md"

STAGES = ("intake", "brainstorm", "evaluate", "promoted", "archived")
SOURCE_TYPES = frozenset(
    {
        "maintainer_research",
        "agent_research",
        "external_critic",
        "council_insight",
        "user_paste",
    }
)
PROMOTE_TARGETS = frozenset({"skill_draft", "council_topic", "agent_report", "deferred"})
STANCES = frozenset({"support", "challenge", "extend", "neutral"})

GOV_KEYWORDS = re.compile(
    r"\b(ssot|locked|l0|l1|l2|l3|l4|l5|l6|l7|l8|l9|l10|l11|l12|validator|audit|governance|external_critic)\b",
    re.I,
)
ACTION_KEYWORDS = re.compile(
    r"\b(next step|implement|ship|fix|add|wire|build|action:|todo|must)\b",
    re.I,
)
EVIDENCE_KEYWORDS = re.compile(
    r"\b(http|~/|/users/|\.py|\.md|validate-|audit_|pass|fail|evidence|proof)\b",
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_dirs() -> None:
    RESEARCH_ROOT.mkdir(parents=True, exist_ok=True)
    drafts = SOURCE_A / "agent-skills" / "drafts"
    drafts.mkdir(parents=True, exist_ok=True)


def _append_jsonl(path: Path, row: dict) -> None:
    _ensure_dirs()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_items() -> list[dict]:
    if not ITEMS_PATH.is_file():
        return []
    by_id: dict[str, dict] = {}
    for line in ITEMS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = row.get("id")
        if rid:
            by_id[rid] = row
    return sorted(by_id.values(), key=lambda r: r.get("at") or "", reverse=True)


def _registered_ids() -> set[str]:
    return {w["id"] for w in AGENT_WORKSPACES}


def _score_text(text: str) -> dict[str, int]:
    t = text or ""
    gov = min(100, 20 + 15 * len(GOV_KEYWORDS.findall(t)))
    act = min(100, 15 + 20 * len(ACTION_KEYWORDS.findall(t)))
    ev = min(100, 10 + 18 * len(EVIDENCE_KEYWORDS.findall(t)))
    length_bonus = min(25, len(t) // 40)
    composite = round(0.3 * gov + 0.3 * act + 0.25 * ev + 0.15 * min(100, 40 + length_bonus))
    return {
        "governance_alignment": gov,
        "actionability": act,
        "evidence_quality": ev,
        "composite": composite,
        "recommend_promote": composite >= 65,
    }


def _agent_fit_score(body: str, targets: list[str]) -> int:
    if not targets:
        return 50
    text = (body or "").lower()
    hits = 0
    for aid in targets:
        spec = get_workspace(aid) or {}
        for token in [aid, spec.get("lane", ""), spec.get("label", "")]:
            if token and str(token).lower() in text:
                hits += 1
                break
    return min(100, 40 + hits * 25)


def submit_research(body: dict) -> dict:
    title = (body.get("title") or "").strip()
    content = (body.get("body") or body.get("content") or "").strip()
    source_agent = (body.get("source_agent") or body.get("agent_id") or "sinaai_maintainer").strip()
    source_type = (body.get("source_type") or "maintainer_research").strip().lower()
    if len(title) < 8:
        return {"ok": False, "error": "title min 8 chars"}
    if len(content) < 40:
        return {"ok": False, "error": "body min 40 chars"}
    if source_agent not in _registered_ids():
        return {"ok": False, "error": "source_agent must be registered agent id"}
    if source_type not in SOURCE_TYPES:
        return {"ok": False, "error": f"source_type must be one of: {sorted(SOURCE_TYPES)}"}
    targets = body.get("target_agents") or []
    if isinstance(targets, str):
        targets = [t.strip() for t in targets.split(",") if t.strip()]
    targets = [t for t in targets if t in _registered_ids()]
    row = {
        "id": f"RES-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "updated_at": _now(),
        "stage": "intake",
        "title": title[:240],
        "body": content[:12000],
        "source_agent": source_agent,
        "source_type": source_type,
        "target_agents": targets,
        "brainstorm": [],
        "scores": None,
        "promotion": None,
    }
    _append_jsonl(ITEMS_PATH, row)
    return {"ok": True, "item": row}


def add_brainstorm(body: dict) -> dict:
    item_id = (body.get("item_id") or body.get("id") or "").strip()
    note = (body.get("note") or body.get("body") or "").strip()
    agent_id = (body.get("agent_id") or body.get("source_agent") or "").strip()
    stance = (body.get("stance") or "neutral").strip().lower()
    if not item_id or len(note) < 12:
        return {"ok": False, "error": "item_id and note (12+ chars) required"}
    if agent_id and agent_id not in _registered_ids():
        return {"ok": False, "error": "invalid agent_id"}
    if stance not in STANCES:
        return {"ok": False, "error": f"stance must be one of: {sorted(STANCES)}"}
    items = _load_items()
    item = next((i for i in items if i.get("id") == item_id), None)
    if not item:
        return {"ok": False, "error": "item not found"}
    if item.get("stage") in ("promoted", "archived"):
        return {"ok": False, "error": "item closed"}
    entry = {
        "at": _now(),
        "agent_id": agent_id or "sinaai_maintainer",
        "stance": stance,
        "note": note[:4000],
    }
    brainstorm = list(item.get("brainstorm") or [])
    brainstorm.append(entry)
    item["brainstorm"] = brainstorm
    item["stage"] = "brainstorm"
    item["updated_at"] = _now()
    _append_jsonl(ITEMS_PATH, item)
    return {"ok": True, "item": item}


def evaluate_item(body: dict) -> dict:
    item_id = (body.get("item_id") or body.get("id") or "").strip()
    if not item_id:
        return {"ok": False, "error": "item_id required"}
    items = _load_items()
    item = next((i for i in items if i.get("id") == item_id), None)
    if not item:
        return {"ok": False, "error": "item not found"}
    if len(item.get("brainstorm") or []) < 1:
        return {"ok": False, "error": "add at least one brainstorm note first"}
    combined = item.get("body") or ""
    for b in item.get("brainstorm") or []:
        combined += "\n" + (b.get("note") or "")
    scores = _score_text(combined)
    scores["agent_fit"] = _agent_fit_score(combined, item.get("target_agents") or [])
    scores["composite"] = round(
        0.25 * scores["governance_alignment"]
        + 0.25 * scores["actionability"]
        + 0.2 * scores["evidence_quality"]
        + 0.2 * scores["agent_fit"]
        + 0.1 * min(100, len(combined) // 50)
    )
    scores["recommend_promote"] = scores["composite"] >= 65
    scores["evaluated_at"] = _now()
    item["scores"] = scores
    item["stage"] = "evaluate"
    item["updated_at"] = _now()
    _append_jsonl(ITEMS_PATH, item)
    return {"ok": True, "item": item, "scores": scores}


def promote_item(body: dict) -> dict:
    item_id = (body.get("item_id") or body.get("id") or "").strip()
    target = (body.get("target") or body.get("promote_to") or "").strip().lower()
    note = (body.get("note") or "").strip()
    agent_id = (body.get("agent_id") or "sinaai_maintainer").strip()
    if not item_id or target not in PROMOTE_TARGETS:
        return {"ok": False, "error": f"item_id and target required ({sorted(PROMOTE_TARGETS)})"}
    items = _load_items()
    item = next((i for i in items if i.get("id") == item_id), None)
    if not item:
        return {"ok": False, "error": "item not found"}
    if not item.get("scores"):
        return {"ok": False, "error": "evaluate first"}
    promotion: dict[str, Any] = {
        "at": _now(),
        "target": target,
        "by": agent_id,
        "note": note[:2000],
        "refs": {},
    }
    if target == "council_topic":
        from agent_council_room import create_topic  # noqa: WPS433

        title = f"[Research] {item.get('title', '')[:200]}"
        ct = create_topic(
            {
                "agent_id": agent_id,
                "title": title,
                "category": "process",
                "note": (item.get("body") or "")[:2000],
                "related_agents": item.get("target_agents") or [agent_id],
            }
        )
        if not ct.get("ok"):
            return ct
        promotion["refs"]["council_topic_id"] = ct["topic"]["id"]
    elif target == "skill_draft":
        aid = (item.get("target_agents") or [agent_id])[0]
        draft_dir = SOURCE_A / "agent-skills" / "drafts"
        draft_dir.mkdir(parents=True, exist_ok=True)
        draft_path = draft_dir / f"{item_id}-{aid}.md"
        draft_path.write_text(
            f"# Draft skill — from {item_id}\n\n"
            f"**Title:** {item.get('title')}\n\n"
            f"**Scores:** {json.dumps(item.get('scores'), indent=2)}\n\n"
            f"## Body\n\n{item.get('body')}\n\n"
            f"## Brainstorm\n\n"
            + "\n\n".join(f"- **{b.get('stance')}** ({b.get('agent_id')}): {b.get('note')}" for b in item.get("brainstorm") or [])
            + f"\n\n## Promotion note\n\n{note}\n",
            encoding="utf-8",
        )
        promotion["refs"]["skill_draft_path"] = str(draft_path)
    elif target == "agent_report":
        from agent_command_reviews import submit_review  # noqa: WPS433

        rv = submit_review(
            title=item.get("title") or "Research promotion",
            detail=(item.get("body") or "")[:4000],
            severity="medium",
            category="request",
            workspace=agent_id,
            reporter=agent_id,
            suggested_fix=note[:800],
        )
        if not rv.get("ok"):
            return rv
        promotion["refs"]["agent_review_id"] = rv.get("id") or rv.get("review", {}).get("id")
    item["promotion"] = promotion
    item["stage"] = "promoted"
    item["updated_at"] = _now()
    _append_jsonl(ITEMS_PATH, item)
    return {"ok": True, "item": item, "promotion": promotion}


def archive_item(body: dict) -> dict:
    item_id = (body.get("item_id") or "").strip()
    items = _load_items()
    item = next((i for i in items if i.get("id") == item_id), None)
    if not item:
        return {"ok": False, "error": "item not found"}
    item["stage"] = "archived"
    item["updated_at"] = _now()
    _append_jsonl(ITEMS_PATH, item)
    return {"ok": True, "item": item}


def research_pipeline_payload(*, limit: int = 30) -> dict[str, Any]:
    items = _load_items()[:limit]
    open_items = [i for i in items if i.get("stage") not in ("promoted", "archived")]
    law_path = SOURCE_A / LAW_DOC
    return {
        "ok": True,
        "schema": "agent_research_pipeline_v1",
        "built_at": _now(),
        "law_doc": LAW_DOC,
        "law_exists": law_path.is_file(),
        "storage": str(ITEMS_PATH),
        "stages": list(STAGES),
        "source_types": sorted(SOURCE_TYPES),
        "promote_targets": sorted(PROMOTE_TARGETS),
        "items": items,
        "open_count": len(open_items),
        "total_count": len(items),
        "agents": [{"id": w["id"], "label": w["label"]} for w in AGENT_WORKSPACES],
        "flow": [
            "INTAKE — submit research (any agent)",
            "BRAINSTORM — ≥1 perspective note",
            "EVALUATE — auto scores (composite ≥65 → recommend promote)",
            "PROMOTE — skill_draft | council_topic | agent_report | deferred",
        ],
    }


def handle_action(body: dict, *, hub: dict | None = None) -> dict:
    action = (body.get("action") or "list").strip().lower()
    if action in ("list", "get", ""):
        return research_pipeline_payload()
    if action == "submit":
        return submit_research(body)
    if action == "brainstorm":
        return add_brainstorm(body)
    if action == "evaluate":
        return evaluate_item(body)
    if action == "promote":
        return promote_item(body)
    if action == "archive":
        return archive_item(body)
    return {"ok": False, "error": f"unknown action: {action}"}

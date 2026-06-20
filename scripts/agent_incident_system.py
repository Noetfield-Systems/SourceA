#!/usr/bin/env python3
"""
Per-agent always-on incident report + weekly Incident Room (share, learn, certify).

Storage:
  ~/.sina/agent-workspaces/<id>/INCIDENT_REPORT_ALWAYS.md
  ~/.sina/agent-workspaces/<id>/INCIDENT_MY_INSIGHTS.md
  ~/.sina/agent-workspaces/<id>/incident-agent-state.json
  ~/.sina/incident-room/weeks/<ISO-week>/posts.jsonl
  ~/.sina/incident-room/weeks/<ISO-week>/certifications.json
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
WORKSPACES_ROOT = SINA_HOME / "agent-workspaces"
ROOM_ROOT = SINA_HOME / "incident-room"
LOCKED_REPORT = SOURCE_A / "brain-os/incidents/SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md"
LAW_DOC = "SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md"
LOCKED_VERSION = "1.0"
PERSONAL_MARKER = "<!-- AGENT_PERSONAL_BELOW -->"

QUIZ_QUESTIONS = [
    {
        "id": "q1",
        "question": "What was the primary cause of auto-paste spam into Cursor?",
        "options": [
            {"id": "a", "text": "Live agents calling inject_cursor_chat (clipboard + Return)", "correct": True},
            {"id": "b", "text": "Founder manually pasting too often", "correct": False},
            {"id": "c", "text": "Git pull hooks only", "correct": False},
        ],
    },
    {
        "id": "q2",
        "question": "After closing Sina Command.app, what often kept running?",
        "options": [
            {"id": "a", "text": "The hub on 127.0.0.1:13020 (sina-command-server)", "correct": True},
            {"id": "b", "text": "Only the Desktop icon", "correct": False},
            {"id": "c", "text": "Nothing — everything always stops", "correct": False},
        ],
    },
    {
        "id": "q3",
        "question": "Emergency stop script for auto-paste?",
        "options": [
            {"id": "a", "text": "scripts/kill-sina-command.sh", "correct": True},
            {"id": "b", "text": "scripts/start-everything.sh", "correct": False},
            {"id": "c", "text": "rm -rf ~/.cursor", "correct": False},
        ],
    },
    {
        "id": "q4",
        "question": "Where should Live agents / maintainer replies live?",
        "options": [
            {"id": "a", "text": "Sina Command app only — no background paste into Cursor", "correct": True},
            {"id": "b", "text": "Auto-paste every minute into maintainer chat", "correct": False},
            {"id": "c", "text": "Telegram only", "correct": False},
        ],
    },
    {
        "id": "q5",
        "question": "What caused Cursor “8 Queued to Send”?",
        "options": [
            {"id": "a", "text": "Repeated injects stacking in the composer queue", "correct": True},
            {"id": "b", "text": "A single long prompt", "correct": False},
            {"id": "c", "text": "Browser cache", "correct": False},
        ],
    },
]

MIN_QUIZ_SCORE = 4
PASS_QUIZ_TOTAL = len(QUIZ_QUESTIONS)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def iso_week_id(dt: datetime | None = None) -> str:
    d = dt or datetime.now(timezone.utc)
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def _week_dir(week_id: str | None = None) -> Path:
    wid = week_id or iso_week_id()
    p = ROOM_ROOT / "weeks" / wid
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load_json(path: Path, default: dict | list) -> dict | list:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _locked_body() -> str:
    if LOCKED_REPORT.is_file():
        return LOCKED_REPORT.read_text(encoding="utf-8", errors="replace")
    return "# Incident report missing\n\nRestore `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` in SourceA.\n"


def _personal_section(agent_id: str, label: str) -> str:
    return f"""{PERSONAL_MARKER}

## My workspace — {label} (`{agent_id}`)

**This section is yours.** Add what you learned this week, near-misses, and guardrails for your repo.

- Do not delete the locked report above.
- Weekly: share in **Incident Room** tab and pass the certification quiz.
"""


def _build_always_report(agent_id: str, label: str, existing_personal: str = "") -> str:
    header = f"""# INCIDENT REPORT — ALWAYS READ ({label})

**Agent:** `{agent_id}`  
**Locked SSOT:** `{LOCKED_REPORT}` · version **{LOCKED_VERSION}**  
**Synced:** {_now()}

> Read this file **every Cursor session** before editing code. Your copy lives in private storage so you always have it offline from the hub.

---

"""
    body = _locked_body().strip()
    personal = existing_personal.strip() if existing_personal else _personal_section(agent_id, label)
    if PERSONAL_MARKER not in personal:
        personal = _personal_section(agent_id, label) + "\n" + personal
    return header + body + "\n\n" + personal + "\n"


def _extract_personal(text: str) -> str:
    if PERSONAL_MARKER in text:
        return text.split(PERSONAL_MARKER, 1)[1].strip()
    return ""


def _incident_cursor_rule(agent_id: str, label: str, private_root: Path) -> str:
    return f"""---
description: Mandatory incident report — read every session ({agent_id})
alwaysApply: true
---

# Incident — always read

1. Session gate — `agent_session_gate_run_v1.py` (**not** read-all-incidents compendium).
2. Optional: legacy archive **Incident Room** — maintainer weekly only; not daily founder path.
3. Never re-enable Live-agent paste into Cursor without ASF + new locked incident version.
4. Emergency: `~/Desktop/SourceA/scripts/kill-sina-command.sh`

Law: `~/Desktop/SourceA/{LAW_DOC}`
"""


def _default_state(agent_id: str) -> dict:
    return {
        "agent_id": agent_id,
        "locked_report_version": LOCKED_VERSION,
        "last_ack_at": None,
        "last_ack_week": None,
        "personal_insight": "",
        "certifications": {},
        "updated_at": _now(),
    }


def _state_path(private_root: Path) -> Path:
    return private_root / "incident-agent-state.json"


def _load_state(private_root: Path, agent_id: str) -> dict:
    st = _load_json(_state_path(private_root), _default_state(agent_id))
    if not isinstance(st, dict):
        st = _default_state(agent_id)
    st.setdefault("agent_id", agent_id)
    st.setdefault("certifications", {})
    return st


def ensure_agent_incident_files(agent_id: str) -> dict:
    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}

    private_root = WORKSPACES_ROOT / agent_id
    private_root.mkdir(parents=True, exist_ok=True)
    label = spec["label"]
    always_path = private_root / "INCIDENT_REPORT_ALWAYS.md"
    insights_path = private_root / "INCIDENT_MY_INSIGHTS.md"

    existing_personal = ""
    if always_path.is_file():
        existing_personal = _extract_personal(always_path.read_text(encoding="utf-8", errors="replace"))

    always_path.write_text(_build_always_report(agent_id, label, existing_personal), encoding="utf-8")

    if not insights_path.is_file():
        insights_path.write_text(
            f"# Insights log — {label}\n\n"
            f"Append dated bullets when you learn something in Incident Room or after a near-miss.\n\n"
            f"| Date | Insight |\n|------|--------|\n",
            encoding="utf-8",
        )

    st = _load_state(private_root, agent_id)
    st["updated_at"] = _now()
    _save_json(_state_path(private_root), st)

    rules_dir = private_root / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "incident-always-read.mdc").write_text(
        _incident_cursor_rule(agent_id, label, private_root), encoding="utf-8"
    )

    return {
        "ok": True,
        "agent_id": agent_id,
        "always_report_path": str(always_path),
        "insights_path": str(insights_path),
    }


def ensure_all_agent_incidents() -> dict:
    ids = []
    for spec in AGENT_WORKSPACES:
        ensure_agent_incident_files(spec["id"])
        ids.append(spec["id"])
    ROOM_ROOT.mkdir(parents=True, exist_ok=True)
    state_path = ROOM_ROOT / "state.json"
    st = _load_json(state_path, {"version": 1, "current_week": iso_week_id()})
    if isinstance(st, dict):
        st["current_week"] = iso_week_id()
        st["updated_at"] = _now()
        _save_json(state_path, st)
    _week_dir()
    return {"ok": True, "agents": ids, "week": iso_week_id()}


def _preview(path: Path, limit: int = 900) -> str:
    if not path.is_file():
        return ""
    try:
        t = path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return ""
    return t if len(t) <= limit else t[:limit] + "\n…"


def _append_insight_log(private_root: Path, label: str, line: str) -> None:
    p = private_root / "INCIDENT_MY_INSIGHTS.md"
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    row = f"| {date} | {line.replace('|', '/')} |\n"
    if p.is_file():
        text = p.read_text(encoding="utf-8", errors="replace")
        if "| Date |" in text and row not in text:
            p.write_text(text.rstrip() + "\n" + row, encoding="utf-8")
    else:
        p.write_text(f"# Insights log — {label}\n\n| Date | Insight |\n|------|--------|\n{row}", encoding="utf-8")


def agent_incident_summary(agent_id: str) -> dict:
    ensure_agent_incident_files(agent_id)
    spec = get_workspace(agent_id) or {}
    private_root = WORKSPACES_ROOT / agent_id
    week = iso_week_id()
    st = _load_state(private_root, agent_id)
    cert = (st.get("certifications") or {}).get(week) or {}
    certified = bool(cert.get("certified_at"))
    ack_ok = st.get("last_ack_week") == week
    always_path = private_root / "INCIDENT_REPORT_ALWAYS.md"
    return {
        "agent_id": agent_id,
        "label": spec.get("label", agent_id),
        "week_id": week,
        "always_report_path": str(always_path),
        "always_report_rel": f"~/.sina/agent-workspaces/{agent_id}/INCIDENT_REPORT_ALWAYS.md",
        "report_preview": _preview(always_path, 1100),
        "insights_path": str(private_root / "INCIDENT_MY_INSIGHTS.md"),
        "locked_source": str(LOCKED_REPORT),
        "last_ack_at": st.get("last_ack_at"),
        "last_ack_week": st.get("last_ack_week"),
        "ack_current_week": ack_ok,
        "personal_insight": st.get("personal_insight") or "",
        "certified_this_week": certified,
        "certification": cert,
        "needs_ack": not ack_ok,
        "needs_certification": not certified,
    }


def _load_week_posts(week_id: str) -> list[dict]:
    path = _week_dir(week_id) / "posts.jsonl"
    if not path.is_file():
        return []
    posts = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            posts.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    posts.sort(key=lambda p: p.get("created_at") or "", reverse=True)
    return posts


def _save_post(week_id: str, post: dict) -> None:
    path = _week_dir(week_id) / "posts.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(post, ensure_ascii=False) + "\n")


def _week_certs(week_id: str) -> dict:
    path = _week_dir(week_id) / "certifications.json"
    data = _load_json(path, {})
    return data if isinstance(data, dict) else {}


def _set_cert(week_id: str, agent_id: str, entry: dict) -> None:
    path = _week_dir(week_id) / "certifications.json"
    certs = _week_certs(week_id)
    certs[agent_id] = entry
    _save_json(path, certs)


def _score_quiz(answers: dict) -> tuple[int, bool]:
    score = 0
    for q in QUIZ_QUESTIONS:
        qid = q["id"]
        chosen = (answers or {}).get(qid) or (answers or {}).get(qid.replace("q", ""))
        if not chosen:
            continue
        for opt in q["options"]:
            if opt["id"] == chosen and opt.get("correct"):
                score += 1
                break
    return score, score >= MIN_QUIZ_SCORE


def incident_room_payload(agent_id: str | None = None) -> dict:
    ensure_all_agent_incidents()
    week = iso_week_id()
    posts = _load_week_posts(week)
    certs = _week_certs(week)
    agents = []
    uncertified = 0
    for spec in AGENT_WORKSPACES:
        aid = spec["id"]
        summ = agent_incident_summary(aid)
        if summ.get("needs_certification"):
            uncertified += 1
        agents.append(
            {
                "id": aid,
                "label": spec["label"],
                "certified": bool((certs.get(aid) or {}).get("certified_at")),
                "needs_ack": summ.get("needs_ack"),
                "has_post": any(p.get("agent_id") == aid for p in posts),
            }
        )
    sel = agent_id or (posts[0].get("agent_id") if posts else AGENT_WORKSPACES[0]["id"])
    my = agent_incident_summary(sel) if sel else {}
    return {
        "ok": True,
        "week_id": week,
        "week_label": f"Week {week}",
        "law_doc": LAW_DOC,
        "locked_report_path": str(LOCKED_REPORT),
        "room_root": str(ROOM_ROOT),
        "quiz_questions": QUIZ_QUESTIONS,
        "min_quiz_score": MIN_QUIZ_SCORE,
        "pass_total": PASS_QUIZ_TOTAL,
        "posts": posts,
        "certifications": certs,
        "agents": agents,
        "uncertified_count": uncertified,
        "selected_agent_id": sel,
        "my": my,
        "tagline": "Weekly: read your always report → share one incident/lesson → write insight → pass quiz → certified.",
    }


def handle_incident_room_action(body: dict) -> dict:
    action = (body.get("action") or "").strip().lower()
    agent_id = (body.get("agent_id") or body.get("id") or "").strip()
    week = iso_week_id()

    if action in ("ensure", "sync", "refresh"):
        return {**ensure_all_agent_incidents(), **incident_room_payload(agent_id or None)}

    if not agent_id:
        spec = get_workspace((body.get("workspace_id") or ""))
        agent_id = spec["id"] if spec else ""
    if not agent_id:
        return {"ok": False, "error": "agent_id required"}

    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}

    private_root = WORKSPACES_ROOT / agent_id
    ensure_agent_incident_files(agent_id)
    st = _load_state(private_root, agent_id)

    if action == "ack_report":
        st["last_ack_at"] = _now()
        st["last_ack_week"] = week
        st["updated_at"] = _now()
        _save_json(_state_path(private_root), st)
        return {
            "ok": True,
            "message": f"{spec['label']} — incident report acknowledged for {week}",
            **incident_room_payload(agent_id),
        }

    if action == "save_insight":
        insight = (body.get("insight") or body.get("personal_insight") or "").strip()
        if len(insight) < 12:
            return {"ok": False, "error": "Write at least 12 characters of insight"}
        st["personal_insight"] = insight
        st["updated_at"] = _now()
        _save_json(_state_path(private_root), st)
        _append_insight_log(private_root, spec["label"], insight[:500])
        always_path = private_root / "INCIDENT_REPORT_ALWAYS.md"
        if always_path.is_file():
            text = always_path.read_text(encoding="utf-8", errors="replace")
            personal = _extract_personal(text)
            block = f"\n\n### Latest insight ({week})\n\n{insight}\n"
            if f"### Latest insight ({week})" not in personal:
                personal = personal.rstrip() + block
                always_path.write_text(
                    _build_always_report(agent_id, spec["label"], personal), encoding="utf-8"
                )
        return {
            "ok": True,
            "message": "Insight saved to your private storage",
            **incident_room_payload(agent_id),
        }

    if action == "submit_weekly":
        title = (body.get("title") or "").strip() or f"{spec['label']} — weekly incident"
        what = (body.get("what_happened") or body.get("incident") or "").strip()
        lesson = (body.get("lesson") or "").strip()
        insight = (body.get("insight") or st.get("personal_insight") or "").strip()
        if len(what) < 20:
            return {"ok": False, "error": "Describe what happened (at least 20 characters)"}
        if len(lesson) < 15:
            return {"ok": False, "error": "Share the lesson learned (at least 15 characters)"}
        post = {
            "id": str(uuid.uuid4())[:12],
            "agent_id": agent_id,
            "agent_label": spec["label"],
            "week_id": week,
            "title": title[:200],
            "what_happened": what[:4000],
            "lesson": lesson[:2000],
            "insight": insight[:2000],
            "created_at": _now(),
        }
        _save_post(week, post)
        if insight:
            st["personal_insight"] = insight
        st["updated_at"] = _now()
        _save_json(_state_path(private_root), st)
        return {
            "ok": True,
            "message": "Shared in Incident Room — complete the quiz to certify",
            "post_id": post["id"],
            **incident_room_payload(agent_id),
        }

    if action == "submit_quiz":
        answers = body.get("answers") or {}
        score, passed = _score_quiz(answers)
        posts = _load_week_posts(week)
        has_post = any(p.get("agent_id") == agent_id for p in posts)
        ack_ok = st.get("last_ack_week") == week
        if not ack_ok:
            return {"ok": False, "error": "Acknowledge your always-read incident report first"}
        if not has_post:
            return {"ok": False, "error": "Submit your weekly incident share before the quiz"}
        if not passed:
            return {
                "ok": False,
                "error": f"Quiz score {score}/{PASS_QUIZ_TOTAL} — need {MIN_QUIZ_SCORE} to certify",
                "score": score,
            }
        cert_entry = {
            "certified_at": _now(),
            "week_id": week,
            "quiz_score": score,
            "quiz_total": PASS_QUIZ_TOTAL,
        }
        st.setdefault("certifications", {})[week] = cert_entry
        st["updated_at"] = _now()
        _save_json(_state_path(private_root), st)
        _set_cert(week, agent_id, {**cert_entry, "agent_label": spec["label"]})
        return {
            "ok": True,
            "message": f"Certified for {week} — {spec['label']}",
            "score": score,
            **incident_room_payload(agent_id),
        }

    if action == "list":
        return incident_room_payload(agent_id)

    return {"ok": False, "error": f"unknown action: {action}"}

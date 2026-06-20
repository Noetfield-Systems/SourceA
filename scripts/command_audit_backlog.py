#!/usr/bin/env python3
"""
Audit & backlog — findings from deep review, visible in Sina Command for later fixes.
User can mark items deferred / done in ~/.sina/command-audit-overrides.json
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
OVERRIDES_PATH = Path.home() / ".sina" / "command-audit-overrides.json"
REGISTRY_PATH = SOURCE_A / "sina-bowl" / "COMMAND_AUDIT_BACKLOG.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_overrides() -> dict:
    if not OVERRIDES_PATH.is_file():
        return {"status": {}, "notes": {}}
    return json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))


def _save_overrides(data: dict) -> None:
    OVERRIDES_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    OVERRIDES_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


# Canonical backlog — bump version when audit changes
AUDIT_ITEMS: list[dict] = [
    # --- Fixed (keep for history) ---
    {
        "id": "AUD-F01",
        "category": "fixed",
        "priority": "P0",
        "title": "SEMEJ missing from Track when loop idle",
        "detail": "Standing workstreams now include work-semej until dismissed.",
        "tab": "track",
        "validation_id": "V-20",
    },
    {
        "id": "AUD-F02",
        "category": "fixed",
        "priority": "P0",
        "title": "Track showed 47 duplicate todos",
        "detail": "Merged into ~12 subjects by topic (SEMEJ, MergePack, Portfolio, …).",
        "tab": "track",
    },
    {
        "id": "AUD-F03",
        "category": "fixed",
        "priority": "P1",
        "title": "/api/commitments missing founder + repos context",
        "detail": "Server uses _commitments_context() so must-do and portfolio lines stay correct.",
        "tab": "track",
        "validation_id": "V-20",
    },
    {
        "id": "AUD-F04",
        "category": "fixed",
        "priority": "P1",
        "title": "Brief button only played audio / wrong copy",
        "detail": "Header Brief copies universal Cursor session brief; audio stays on Audio tab.",
        "tab": "command",
    },
    {
        "id": "AUD-F05",
        "category": "fixed",
        "priority": "P2",
        "title": "Home label still said All threads",
        "detail": "Renamed to Ecosystem map across Home/Today.",
        "tab": "command",
    },
    {
        "id": "AUD-F06",
        "category": "fixed",
        "priority": "P1",
        "title": "Playful Path UI — locked honorary certificate",
        "detail": "theme-duo.css + path cards + lane tiles; law: SINA_COMMAND_UI_PLAYFUL_LOCKED_v1.md — do not regress.",
        "tab": "command",
    },
    {
        "id": "AUD-F07",
        "category": "fixed",
        "priority": "P0",
        "title": "Clipboard hijack on Live / Refresh / nav clicks",
        "detail": "Loop inject restores pasteboard after Cursor paste; Brief only on Brief tap; Repos lane copy no nested buttons.",
        "tab": "command",
    },
    {
        "id": "AUD-F08",
        "category": "fixed",
        "priority": "P1",
        "title": "Submit round hidden + site Search / Ask guide",
        "detail": "Sticky Submit bar + Submit card top on Agent loop; /api/site-guide search + Ask chat.",
        "tab": "agent-loop",
    },
    {
        "id": "AUD-F09",
        "category": "fixed",
        "priority": "P0",
        "title": "Sina Command edit lock + agent review reports",
        "detail": "Only ASF + SinaaiDataBase chat edit SourceA; all other agents POST /api/agent-review. Backlog → Agent reports.",
        "tab": "backlog",
    },
    {
        "id": "AUD-F10",
        "category": "fixed",
        "priority": "P1",
        "title": "Private agent workspaces (per heavy app user)",
        "detail": "Private agents sidebar: in-app workspace per agent (10-round loop) — not Finder-first; optional notes folder for agents.",
        "tab": "agents",
    },
    {
        "id": "AUD-F11",
        "category": "fixed",
        "priority": "P1",
        "title": "Workspace governance v2 + 777 + Noetfield cloud",
        "detail": "GOVERNANCE_LOCKED.md per agent; seven77 + noetfield_cloud packs; real needs on Agents cards.",
        "tab": "agents",
    },
    # --- Open gaps ---
    {
        "id": "AUD-O01",
        "category": "fixed",
        "priority": "P1",
        "title": "Run AI Advisory before universal Brief",
        "detail": "Today tab hints when advisory not run; Brief still works without it.",
        "tab": "ai-advisory",
        "validation_id": "V-40",
    },
    {
        "id": "AUD-O02",
        "category": "fixed",
        "priority": "P1",
        "title": "SEMEJ — install Playwright + start Chrome",
        "detail": "SEMEJ tab links to Install tools + Start Chrome actions; validation V-60.",
        "tab": "semej",
        "validation_id": "V-60",
    },
    {
        "id": "AUD-O03",
        "category": "fixed",
        "priority": "P1",
        "title": "Prompt library not in Sina Command UI",
        "detail": "Prompt OS tab → Open Prompt OS UI + start action.",
        "tab": "prompt-os",
    },
    {
        "id": "AUD-O04",
        "category": "fixed",
        "priority": "P2",
        "title": "Agent loop not fully autonomous",
        "detail": "Frozen Phase 2 — manual Private agents rounds by design (SA-019).",
        "tab": "agent-loop",
        "validation_id": "V-50",
    },
    {
        "id": "AUD-O05",
        "category": "fixed",
        "priority": "P2",
        "title": "Ecosystem map cache can go stale",
        "detail": "Actions → Rebuild ecosystem map refreshes ~/.sina/ecosystem-subjects-full.json.",
        "tab": "threads",
        "validation_id": "V-14",
    },
    {
        "id": "AUD-O06",
        "category": "fixed",
        "priority": "P2",
        "title": "Reference threads hidden from Track",
        "detail": "Wont-fix: reference threads stay on Ecosystem map only — reduces Track noise.",
        "tab": "threads",
    },
    {
        "id": "AUD-O07",
        "category": "fixed",
        "priority": "P3",
        "title": "Subagent Cursor transcripts excluded",
        "detail": "Documented: parent chats only; subagent JSONL skipped intentionally.",
        "tab": "threads",
    },
    {
        "id": "AUD-O08",
        "category": "fixed",
        "priority": "P3",
        "title": "Track “Other open items” bucket vague",
        "detail": "Track labels bowl-sourced vs manual in commitment cards.",
        "tab": "track",
    },
    # --- Recommendations ---
    {
        "id": "AUD-R01",
        "category": "recommendation",
        "priority": "P1",
        "title": "Validation pass V-01 → V-45",
        "detail": "Use audit validation table: server, ecosystem map, Track, Brief, SEMEJ, Advisor, agent loop.",
        "tab": "guide",
    },
    {
        "id": "AUD-R02",
        "category": "recommendation",
        "priority": "P1",
        "title": "Restart server after hub code changes",
        "detail": "Restart worker hub server if needed — then Cmd+Shift+R on Worker Hub tab.",
        "tab": "command",
        "validation_id": "V-01",
    },
    {
        "id": "AUD-R03",
        "category": "recommendation",
        "priority": "P2",
        "title": "Per-repo work: Repos → Copy lane brief",
        "detail": "Home Brief = ecosystem; TrustField/Noetfield/etc. = lane paste on Repos or Daily.",
        "tab": "repos",
    },
    # --- Product questions ---
    {
        "id": "AUD-Q01",
        "category": "question",
        "priority": "P2",
        "title": "Show investor + Cursor OS Pro on Track always?",
        "detail": "Currently reference/parallel — only on Ecosystem map unless ops mention them.",
        "tab": "track",
    },
    {
        "id": "AUD-Q02",
        "category": "question",
        "priority": "P2",
        "title": "Every Cursor chat → Track row?",
        "detail": "33 chat subjects on map; Track uses 12 merged subjects. Map enough?",
        "tab": "track",
    },
    {
        "id": "AUD-Q03",
        "category": "question",
        "priority": "P3",
        "title": "Force all todos into named subjects?",
        "detail": "Eliminate “Other open items” by stricter subject matching.",
        "tab": "track",
    },
    # --- Naming / UX clarity ---
    {
        "id": "AUD-U01",
        "category": "clarity",
        "priority": "P3",
        "title": "Ecosystem tab vs Ecosystem map",
        "detail": "Ecosystem tab = flywheel/KPI. Ecosystem map (◇) = full archive of subjects/chats/docs.",
        "tab": "ecosystem",
    },
    {
        "id": "AUD-U02",
        "category": "clarity",
        "priority": "P3",
        "title": "Brief vs Audio brief",
        "detail": "Header Brief = copy Cursor prompt. Audio tab = Mac voice morning brief.",
        "tab": "audio",
    },
]


def audit_backlog_payload() -> dict:
    overrides = _load_overrides()
    status_map = overrides.get("status") or {}
    notes_map = overrides.get("notes") or {}
    items: list[dict] = []
    for row in AUDIT_ITEMS:
        st = status_map.get(row["id"], row.get("category") if row["category"] == "fixed" else "open")
        if row["category"] == "fixed" and row["id"] not in status_map:
            st = "done"
        items.append(
            {
                **row,
                "status": st,
                "user_note": notes_map.get(row["id"], ""),
                "open_tab": row.get("tab", "backlog"),
            }
        )
    by_cat: dict[str, list] = {}
    for it in items:
        cat = it["category"]
        by_cat.setdefault(cat, []).append(it)
    open_items = [i for i in items if i["status"] not in ("done", "deferred")]
    return {
        "ok": True,
        "built_at": _now(),
        "version": "2026-06-04-audit-v1",
        "open_count": len(open_items),
        "total_count": len(items),
        "items": items,
        "by_category": [
            {
                "id": k,
                "label": _cat_label(k),
                "count": len(v),
                "items": v,
            }
            for k, v in [
                ("open_gap", by_cat.get("open_gap", [])),
                ("recommendation", by_cat.get("recommendation", [])),
                ("question", by_cat.get("question", [])),
                ("clarity", by_cat.get("clarity", [])),
                ("fixed", by_cat.get("fixed", [])),
            ]
            if v
        ],
        "tagline": "Audit from deep review — tackle open gaps when ready; fixed items kept for history.",
        "overrides_path": str(OVERRIDES_PATH),
    }


def _cat_label(cat: str) -> str:
    return {
        "open_gap": "Open gaps",
        "fixed": "Fixed",
        "recommendation": "Do next",
        "question": "Decide",
        "clarity": "Naming & UX",
    }.get(cat, cat)


def home_priority_cards(commitments: dict | None, ecosystem: dict | None = None) -> list[dict]:
    """Clean Home row — from Track subjects, not raw ops/todo flood."""
    commits = commitments or {}
    order_status = {"needs_you": 0, "blocked": 1, "in_progress": 2, "open": 3}
    order_pri = {"critical": 0, "high": 1, "normal": 2}
    subjects = sorted(
        commits.get("by_subject") or [],
        key=lambda s: (
            order_pri.get(s.get("priority"), 9),
            order_status.get(s.get("status"), 9),
            s.get("label", ""),
        ),
    )
    out: list[dict] = []
    seen: set[str] = set()
    for sub in subjects:
        item = sub.get("item") or {}
        key = sub.get("key") or item.get("id")
        if not key or key in seen:
            continue
        seen.add(key)
        accent = "gold"
        if item.get("status") == "needs_you":
            accent = "red"
        elif item.get("status") == "blocked":
            accent = "amber"
        elif item.get("status") == "in_progress":
            accent = "blue"
        dk = item.get("drill_kind") or "subject"
        did = item.get("drill_id") or key
        tab = item.get("tab") or ""
        if dk in ("", "track") and tab:
            dk = "thread"
            did = tab
        out.append(
            {
                "id": item.get("id") or key,
                "title": sub.get("label") or item.get("title", key),
                "subtitle": (item.get("detail") or "")[:140],
                "thread": item.get("thread", ""),
                "accent": accent,
                "badge": item.get("status", "open"),
                "drill_kind": dk,
                "drill_id": did,
                "hub_tab": tab if dk == "thread" else "",
                "sort": order_status.get(item.get("status"), 9),
            }
        )
        if len(out) >= 6:
            break
    if out:
        return out
    # Fallback ecosystem today
    for s in (ecosystem or {}).get("today_subjects") or []:
        out.append(
            {
                "id": s.get("id", ""),
                "title": s.get("title", ""),
                "subtitle": s.get("subtitle", s.get("summary", "")),
                "thread": s.get("asf_thread", ""),
                "accent": "gold",
                "drill_kind": "subject",
                "drill_id": s.get("id", ""),
                "badge": s.get("status", "active"),
                "sort": 0,
            }
        )
    return out[:6]


def set_audit_status(item_id: str, status: str, note: str = "") -> dict:
    if status not in ("open", "done", "deferred", "in_progress"):
        return {"ok": False, "error": "invalid status"}
    ov = _load_overrides()
    ov.setdefault("status", {})[item_id] = status
    if note:
        ov.setdefault("notes", {})[item_id] = note[:2000]
    _save_overrides(ov)
    return {"ok": True, "message": f"{item_id} → {status}"}


def handle_audit_action(body: dict) -> dict:
    action = (body.get("action") or "list").strip().lower()
    if action == "set_status":
        return set_audit_status(
            body.get("id", ""),
            body.get("status", "open"),
            body.get("note", ""),
        )
    return {"ok": True, **audit_backlog_payload()}

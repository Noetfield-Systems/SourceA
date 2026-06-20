#!/usr/bin/env python3
"""
Founder threads — full map of ASF + Cursor chat work vs today priorities.

Persists scan to ~/.sina/founder-threads-full.json (refreshed on hub build).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from sina_link_graph import THREAD_NODES, hub_url, link, links_for_thread

CACHE_PATH = Path.home() / ".sina" / "founder-threads-full.json"
TRANSCRIPT_GLOB = Path.home() / ".cursor/projects"

# Static work threads (you + Cursor agent) — merged with registry + transcript scan
WORK_THREADS: list[dict] = [
    {
        "id": "work-mergepack-ship",
        "thread_id": "THREAD-MERGEPACK",
        "title": "MergePack ship · Form to PDF",
        "category": "Revenue",
        "summary": "Live form-to-pdf, KPI trio, Vercel deployment, Railway API.",
        "priority_today": True,
        "status": "active",
        "tabs": ["products", "today"],
        "sort": 1,
    },
    {
        "id": "work-sina-command",
        "thread_id": "THREAD-ECOSYSTEM",
        "title": "Sina Command hub",
        "category": "Platform",
        "summary": "Founder control panel :13020 — pages, Guide, Actions, drill-down, no Terminal.",
        "priority_today": True,
        "status": "active",
        "tabs": ["command", "guide", "actions"],
        "sort": 2,
    },
    {
        "id": "work-agent-loop",
        "thread_id": "THREAD-ECOSYSTEM",
        "title": "Agent loop (10× autopilot)",
        "category": "Automation",
        "summary": "One trigger → Planner AI injects prompts into Cursor; executor builds; Advisor separate.",
        "priority_today": True,
        "status": "active",
        "tabs": ["agent-loop"],
        "sort": 3,
    },
    {
        "id": "work-semej",
        "thread_id": "THREAD-ECOSYSTEM",
        "title": "SEMEJ · Chrome multi-AI chain",
        "category": "Automation",
        "summary": "Gemini → ChatGPT → Perplexity → Grok in signed-in Chrome; idea → artifact.",
        "priority_today": True,
        "status": "active",
        "tabs": ["semej"],
        "sort": 4,
    },
    {
        "id": "work-advisor",
        "thread_id": "THREAD-ECOSYSTEM",
        "title": "Advisor (Cursor / OpenRouter)",
        "category": "Coach",
        "summary": "Strategic chat before loop — not the coding agent.",
        "priority_today": True,
        "status": "active",
        "tabs": ["agent-loop"],
        "sort": 5,
    },
    {
        "id": "work-p0-runreceipt",
        "thread_id": "THREAD-FACTORY",
        "title": "P0 RunReceipt",
        "category": "Factory",
        "summary": "Agent run PASS/FAIL receipt — run.jsonl + summary + HTML pack.",
        "priority_today": True,
        "status": "active",
        "tabs": ["today", "plans"],
        "sort": 6,
    },
    {
        "id": "work-prompt-os",
        "thread_id": "THREAD-PROMPTOS",
        "title": "Sina Prompt OS",
        "category": "Platform",
        "summary": "Five-repo dispatch, ingest, prompt library, OpenRouter, :8765 UI.",
        "priority_today": False,
        "status": "active",
        "tabs": ["apps", "prompt-os", "daily"],
        "sort": 14,
    },
    {
        "id": "work-desktop-apps",
        "thread_id": "THREAD-ECOSYSTEM",
        "title": "Desktop apps & icons",
        "category": "Platform",
        "summary": "Sina Command.app, Prompt OS.app, engine apps — real macOS shortcuts.",
        "priority_today": False,
        "status": "done",
        "tabs": ["apps", "guide"],
        "sort": 8,
    },
    {
        "id": "work-ai-advisory",
        "thread_id": "THREAD-ECOSYSTEM",
        "title": "AI Advisory · golden links",
        "category": "Coach",
        "summary": "OpenRouter reads live snapshot → connections + upgrade ideas.",
        "priority_today": False,
        "status": "active",
        "tabs": ["ai-advisory"],
        "sort": 11,
    },
    {
        "id": "work-ui-guide",
        "thread_id": "THREAD-ECOSYSTEM",
        "title": "UI · Guide · Duolingo path",
        "category": "Platform",
        "summary": "Teacher lessons, multi-page layout, connected drill-downs.",
        "priority_today": False,
        "status": "active",
        "tabs": ["guide", "plans"],
        "sort": 9,
    },
    {
        "id": "work-superbrain",
        "thread_id": "THREAD-SUPERBRAIN",
        "title": "Super Brain · Personal DB",
        "category": "Intelligence",
        "summary": "L0–L4 layers, chat consolidation, mono training links.",
        "priority_today": False,
        "status": "active",
        "tabs": ["personal-db", "plans"],
        "sort": 20,
    },
    {
        "id": "work-chat-consolidation",
        "thread_id": "THREAD-CHAT-CONSOLIDATION",
        "title": "Chat consolidation (100 → L2)",
        "category": "Intelligence",
        "summary": "Export Cursor chats into Super Brain pipeline.",
        "priority_today": False,
        "status": "open",
        "tabs": ["personal-db"],
        "sort": 21,
    },
    {
        "id": "work-wire-m8",
        "thread_id": "THREAD-WIRE",
        "title": "Wire · M8 · Remote ops",
        "category": "Automation",
        "summary": "Phone→Mac, Tailscale G3, click server :8899.",
        "priority_today": False,
        "status": "active",
        "tabs": ["apps", "fleet"],
        "sort": 22,
    },
    {
        "id": "work-portfolio",
        "thread_id": "THREAD-PORTFOLIO",
        "title": "Five-repo portfolio",
        "category": "Delivery",
        "summary": "TrustField, VIRLUX, Noetfield, 777, Mono — plans and blockers.",
        "priority_today": False,
        "status": "active",
        "tabs": ["repos", "agents"],
        "sort": 25,
    },
    {
        "id": "work-virlux",
        "thread_id": "THREAD-PORTFOLIO",
        "title": "VIRLUX",
        "category": "Product",
        "summary": "API, web, app; Railway/Vercel health.",
        "priority_today": False,
        "status": "active",
        "tabs": ["products", "repos"],
        "sort": 30,
    },
    {
        "id": "work-trustfield",
        "thread_id": "THREAD-PORTFOLIO",
        "title": "TrustField",
        "category": "Product",
        "summary": "Postgres validation, prod demo.",
        "priority_today": False,
        "status": "active",
        "tabs": ["repos"],
        "sort": 31,
    },
    {
        "id": "work-noetfield",
        "thread_id": "THREAD-PORTFOLIO",
        "title": "Noetfield OS",
        "category": "Product",
        "summary": "Financial OS codebase, bank-grade API, maps.",
        "priority_today": False,
        "status": "active",
        "tabs": ["repos"],
        "sort": 32,
    },
    {
        "id": "work-777",
        "thread_id": "THREAD-PORTFOLIO",
        "title": "777 Foundation",
        "category": "Legal",
        "summary": "Bylaws, governance, legal corpus.",
        "priority_today": False,
        "status": "active",
        "tabs": ["repos"],
        "sort": 33,
    },
    {
        "id": "work-cursor-os-pro",
        "thread_id": "THREAD-CURSOR-OS-PRO",
        "title": "Cursor OS Pro SKU",
        "category": "SKU",
        "summary": "App Store reference app — parallel build.",
        "priority_today": False,
        "status": "parallel",
        "tabs": ["plans"],
        "sort": 40,
    },
    {
        "id": "work-investor",
        "thread_id": "THREAD-INVESTOR",
        "title": "Investor · deck · narrative",
        "category": "Fundraising",
        "summary": "Whitepaper, roadmap, materials.",
        "priority_today": False,
        "status": "reference",
        "tabs": ["orders"],
        "sort": 45,
    },
    {
        "id": "work-fleet",
        "thread_id": "THREAD-AGENT-DESK",
        "title": "Agent fleet · desk",
        "category": "Ops",
        "summary": "Cursor workspace activity, VERIFY, lanes.",
        "priority_today": False,
        "status": "active",
        "tabs": ["fleet", "agents"],
        "sort": 28,
    },
    {
        "id": "work-architect",
        "thread_id": "THREAD-ARCHITECT",
        "title": "Permanent Architect",
        "category": "Law",
        "summary": "Read-only audits and architect blockers.",
        "priority_today": False,
        "status": "active",
        "tabs": ["hq", "rules"],
        "sort": 50,
    },
    {
        "id": "work-phase2-truth",
        "thread_id": "THREAD-PHASE2-TRUTH",
        "title": "Phase 2 truth · evaluator",
        "category": "Ops",
        "summary": "Execution truth background.",
        "priority_today": False,
        "status": "background",
        "tabs": ["runtime"],
        "sort": 55,
    },
    {
        "id": "work-factory-done",
        "thread_id": "THREAD-FACTORY",
        "title": "Product factory (30 ideas)",
        "category": "Factory",
        "summary": "Winner = MergePack — thread closed.",
        "priority_today": False,
        "status": "done",
        "tabs": ["plans"],
        "sort": 60,
    },
    {
        "id": "work-audience-hub",
        "thread_id": "THREAD-AUDIENCE-HUB",
        "title": "Audience Hub SKU",
        "category": "SKU",
        "summary": "Paused product line.",
        "priority_today": False,
        "status": "paused",
        "tabs": ["plans"],
        "sort": 70,
    },
    {
        "id": "work-source-b",
        "thread_id": "THREAD-SOURCE-B",
        "title": "Source B · ecosystem map",
        "category": "Reference",
        "summary": "Conflicts and map reference.",
        "priority_today": False,
        "status": "reference",
        "tabs": ["ecosystem"],
        "sort": 75,
    },
]

# Classify Cursor chat opening lines → ASF thread
_CHAT_CLASSIFIERS: list[tuple[str, str, str]] = [
    ("sina command", "THREAD-ECOSYSTEM", "Sina Command / hub"),
    ("agent loop", "THREAD-ECOSYSTEM", "Agent loop"),
    ("semej", "THREAD-ECOSYSTEM", "SEMEJ"),
    ("prompt os", "THREAD-PROMPTOS", "Prompt OS"),
    ("mergepack", "THREAD-MERGEPACK", "MergePack"),
    ("form-to-pdf", "THREAD-MERGEPACK", "Form to PDF"),
    ("runreceipt", "THREAD-FACTORY", "RunReceipt"),
    ("noetfield", "THREAD-PORTFOLIO", "Noetfield"),
    ("virlux", "THREAD-PORTFOLIO", "VIRLUX"),
    ("trustfield", "THREAD-PORTFOLIO", "TrustField"),
    ("777", "THREAD-PORTFOLIO", "777"),
    ("wire", "THREAD-WIRE", "Wire"),
    ("devbridge", "THREAD-WIRE", "DevBridge"),
    ("super brain", "THREAD-SUPERBRAIN", "Super Brain"),
    ("personal db", "THREAD-SUPERBRAIN", "Personal DB"),
    ("investor", "THREAD-INVESTOR", "Investor"),
    ("kavodax", "THREAD-PORTFOLIO", "External research"),
    ("clone the provided interface", "THREAD-PORTFOLIO", "UI clone project"),
]


def _extract_user_query(raw: str) -> str:
    m = re.search(r"<user_query>(.*?)</user_query>", raw, re.DOTALL | re.I)
    if m:
        return m.group(1).strip()
    if "[Image]" in raw:
        m2 = re.search(r"<user_query>(.*?)</user_query>", raw, re.DOTALL | re.I)
        if m2:
            return m2.group(1).strip()
    return raw.strip()


def _classify_chat(text: str) -> tuple[str, str]:
    low = text.lower()
    for needle, tid, label in _CHAT_CLASSIFIERS:
        if needle in low:
            return tid, label
    if len(low) > 200 and "you are" in low[:80]:
        return "THREAD-PORTFOLIO", "Deep build session"
    return "THREAD-ECOSYSTEM", "Cursor work session"


def _title_from_message(text: str, max_len: int = 72) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    if t.lower().startswith("you are "):
        # role-prompt — use second sentence or truncate
        parts = t.split(".", 2)
        if len(parts) > 1 and len(parts[1].strip()) > 20:
            t = parts[1].strip()
    return (t[: max_len - 1] + "…") if len(t) > max_len else t


def scan_cursor_chats(*, max_sessions: int = 40) -> list[dict]:
    """Scan ~/.cursor/projects/*/agent-transcripts/*/*.jsonl (parent chats only)."""
    sessions: list[dict] = []
    if not TRANSCRIPT_GLOB.is_dir():
        return sessions
    paths = sorted(
        TRANSCRIPT_GLOB.rglob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for path in paths:
        if "subagents" in path.parts:
            continue
        conv_id = path.parent.name
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        first_msg = ""
        msg_count = 0
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if msg_count > 200:
                break
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            if o.get("role") != "user":
                continue
            c = o.get("message", {}).get("content") or o.get("content") or ""
            if isinstance(c, list):
                c = " ".join(
                    b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text"
                )
            text = _extract_user_query(str(c))
            if len(text) < 25 or "DEVBRIDGE G1 VERIFY PING" in text:
                continue
            msg_count += 1
            if not first_msg:
                first_msg = text
        if not first_msg:
            continue
        tid, bucket = _classify_chat(first_msg)
        title = _title_from_message(first_msg)
        sessions.append(
            {
                "id": f"chat-{conv_id[:12]}",
                "thread_id": tid,
                "title": title,
                "category": "Cursor chats",
                "summary": f"{bucket} · {msg_count} founder messages",
                "priority_today": False,
                "status": "chat",
                "tabs": ["threads"],
                "sort": 100 + len(sessions),
                "conv_id": conv_id,
                "chat_at": mtime.isoformat(),
                "source": "cursor_transcript",
            }
        )
        if len(sessions) >= max_sessions:
            break
    return sessions


def _enrich_row(row: dict) -> dict:
    tid = row.get("thread_id") or ""
    tabs = row.get("tabs") or ["command"]
    primary_tab = tabs[0] if tabs else "command"
    drill_kind = row.get("drill_kind") or "thread"
    drill_id = row.get("drill_id") or tid
    out = {
        **row,
        "thread": tid,
        "accent": row.get("accent") or _accent_for_thread(tid),
        "drill_kind": drill_kind,
        "drill_id": drill_id,
        "badge": row.get("status", "active"),
        "subtitle": (row.get("summary") or "")[:120],
        "hub_tab": primary_tab,
        "links": links_for_thread(tid)[:6] if tid.startswith("THREAD-") else [],
    }
    out["open_tab"] = link("hub", f"Open {primary_tab}", url=hub_url(primary_tab))
    return out


def _accent_for_thread(tid: str) -> str:
    if "MERGEPACK" in tid or "FACTORY" in tid:
        return "green" if "MERGEPACK" in tid else "gold"
    if "WIRE" in tid:
        return "amber"
    if "SUPERBRAIN" in tid or "CHAT" in tid:
        return "violet"
    if "PORTFOLIO" in tid:
        return "blue"
    return "gold"


def _merge_threads(*, include_chats: bool = True) -> list[dict]:
    by_id: dict[str, dict] = {}
    # Registry nodes (ASF locked threads)
    for tid, node in THREAD_NODES.items():
        by_id[f"reg-{tid}"] = _enrich_row(
            {
                "id": f"reg-{tid}",
                "thread_id": tid,
                "title": node.get("label") or tid,
                "category": "ASF registry",
                "summary": f"Locked program thread — plans: {', '.join(node.get('plan_ids') or []) or '—'}",
                "priority_today": tid in ("THREAD-MERGEPACK", "THREAD-FACTORY", "THREAD-ECOSYSTEM"),
                "status": "registry",
                "tabs": node.get("tabs") or ["command"],
                "sort": 5 if tid == "THREAD-MERGEPACK" else 50,
                "source": "asf_registry",
            }
        )
    for w in WORK_THREADS:
        by_id[w["id"]] = _enrich_row({**w, "source": w.get("source", "work_session")})
    if include_chats:
        for c in scan_cursor_chats():
            # skip if duplicate title with work thread
            if not any(
                c["title"].lower() in (x.get("title") or "").lower()
                for x in WORK_THREADS
                if len(c["title"]) > 30
            ):
                by_id[c["id"]] = _enrich_row(c)
    rows = list(by_id.values())
    rows.sort(key=lambda x: (x.get("sort", 99), x.get("title", "")))
    return rows


def today_priorities(full: list[dict], *, bowl: dict | None = None, ops: list | None = None) -> list[dict]:
    """Minimal set for Home / Today — high priority only."""
    today_ids = {
        "work-mergepack-ship",
        "work-sina-command",
        "work-agent-loop",
        "work-semej",
        "work-advisor",
        "work-p0-runreceipt",
        "reg-THREAD-MERGEPACK",
        "reg-THREAD-FACTORY",
    }
    out: list[dict] = []
    seen: set[str] = set()

    def add(r: dict) -> None:
        if r["id"] in seen:
            return
        seen.add(r["id"])
        out.append(r)

    for r in full:
        if r.get("priority_today") or r["id"] in today_ids:
            add(r)
    # Boost live ops blockers
    for o in ops or []:
        if o.get("severity") not in ("high", "critical"):
            continue
        tid = "THREAD-MERGEPACK" if "MP" in o.get("id", "") else "THREAD-WIRE" if "WIRE" in o.get("id", "") else "THREAD-ECOSYSTEM"
        add(
            _enrich_row(
                {
                    "id": f"today-ops-{o['id']}",
                    "thread_id": tid,
                    "title": o.get("title", o["id"]),
                    "category": "Today · blocker",
                    "summary": (o.get("action") or "")[:120],
                    "priority_today": True,
                    "status": o.get("severity", "ops"),
                    "tabs": ["today"],
                    "sort": 0,
                    "drill_kind": "ops",
                    "drill_id": o["id"],
                    "source": "ops",
                }
            )
        )
        if len(out) >= 8:
            break
    p0 = (bowl or {}).get("p0") or {}
    if p0.get("id") and len(out) < 8:
        add(
            _enrich_row(
                {
                    "id": f"today-{p0['id']}",
                    "thread_id": p0.get("thread", "THREAD-FACTORY"),
                    "title": p0.get("title", "P0"),
                    "category": "Today · P0",
                    "summary": (p0.get("next_action") or "")[:120],
                    "priority_today": True,
                    "status": "p0",
                    "tabs": ["today", "plans"],
                    "sort": 1,
                    "drill_kind": "plan",
                    "drill_id": p0["id"],
                    "source": "bowl",
                }
            )
        )
    out.sort(key=lambda x: (x.get("sort", 99), x.get("title", "")))
    return out[:8]


def founder_threads_payload(
    *,
    bowl: dict | None = None,
    ops: list | None = None,
    refresh_scan: bool = False,
) -> dict:
    if refresh_scan or not CACHE_PATH.is_file():
        full = _merge_threads(include_chats=True)
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(
            json.dumps(
                {"built_at": datetime.now(timezone.utc).isoformat(), "full": full},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    else:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        full = data.get("full") or _merge_threads(include_chats=True)

    today = today_priorities(full, bowl=bowl, ops=ops)
    by_cat: dict[str, list] = {}
    for r in full:
        cat = r.get("category") or "Other"
        by_cat.setdefault(cat, []).append(r)

    return {
        "ok": True,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "full_count": len(full),
        "today_count": len(today),
        "full": full,
        "today": today,
        "by_category": [
            {"category": k, "threads": v, "count": len(v)}
            for k, v in sorted(by_cat.items(), key=lambda x: (-len(x[1]), x[0]))
        ],
        "cache_path": str(CACHE_PATH),
    }


def today_subjects_for_home(
    bowl: dict,
    progress: dict,
    ops: list[dict],
    mp_prog: dict | None,
) -> list[dict]:
    """Replace bloated recent_subjects on Home with today-only priorities."""
    ft = founder_threads_payload(bowl=bowl, ops=ops, refresh_scan=False)
    return ft.get("today") or []

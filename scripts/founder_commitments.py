#!/usr/bin/env python3
"""
Founder commitments — nothing started is left behind.

Aggregates open todos, notes, ops, active loops, queues, plans, duties.
Manual items persist in ~/.sina/founder-commitments.json.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sina_link_graph import hub_url, link

try:
    from founder_threads import WORK_THREADS  # noqa: WPS433
except ImportError:
    WORK_THREADS = []

STORE_PATH = Path.home() / ".sina" / "founder-commitments.json"
AGENT_LOOP_PATH = Path.home() / ".sina" / "agent-loop.json"
SEMEJ_LOOP_PATH = Path.home() / ".sina" / "semej-loop.json"
QUEUE_PATH = Path.home() / ".sina" / "prompt-queue.json"


def _load_store() -> dict:
    if not STORE_PATH.is_file():
        return {"manual": [], "pinned_ids": [], "started_log": {}}
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def _save_store(data: dict) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    STORE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        STORE_PATH.chmod(0o600)
    except OSError:
        pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row(
    *,
    cid: str,
    title: str,
    detail: str = "",
    source: str,
    source_id: str = "",
    status: str = "open",
    priority: str = "normal",
    thread: str = "",
    tab: str = "track",
    drill_kind: str = "",
    drill_id: str = "",
    started_at: str | None = None,
    never_drop: bool = False,
) -> dict:
    return {
        "id": cid,
        "title": title[:200],
        "detail": (detail or "")[:500],
        "source": source,
        "source_id": source_id,
        "status": status,
        "priority": priority,
        "thread": thread,
        "tab": tab,
        "drill_kind": drill_kind or tab,
        "drill_id": drill_id or source_id,
        "started_at": started_at,
        "updated_at": _now(),
        "never_drop": never_drop,
        "open_tab": link("hub", f"Open {tab}", url=hub_url(tab)),
        "source_label": {
            "manual": "Manual Track item",
            "bowl": "Daily bowl",
            "duty": "ASF duty",
            "drift": "Drift",
            "repos": "Live repos",
            "workstream": "Workstream",
            "subject": "Subject",
        }.get(source, source.replace("_", " ")),
    }


# Only these standing build threads appear on Track (not all 25 WORK_THREADS).
TRACK_WORKSTREAM_IDS = {
    "work-semej",
    "work-agent-loop",
    "work-advisor",
    "work-sina-command",
    "work-prompt-direction",
    "work-prompt-os",
    "work-p0-runreceipt",
    "work-mergepack-ship",
}

SKIP_WORKSTREAM_STATUS = frozenset(
    {"done", "reference", "background", "paused", "parallel"}
)

STATUS_RANK = {"needs_you": 0, "blocked": 1, "in_progress": 2, "open": 3}
PRIORITY_RANK = {"critical": 0, "high": 1, "normal": 2}

# Canonical subjects — duplicates merge here.
SUBJECT_DEFS: list[dict] = [
    {
        "key": "semej",
        "label": "SEMEJ · Chrome AI chain",
        "thread": "THREAD-ECOSYSTEM",
        "tab": "semej",
        "drill_kind": "subject",
        "drill_id": "subj-semej",
        "work_ids": {"work-semej"},
        "match_ids": {"loop-semej-live"},
        "keywords": ("semej",),
    },
    {
        "key": "agent-loop",
        "label": "Agent loop · 10× autopilot",
        "thread": "THREAD-ECOSYSTEM",
        "tab": "agent-loop",
        "drill_kind": "subject",
        "drill_id": "subj-agent-loop",
        "work_ids": {"work-agent-loop"},
        "match_ids": {"loop-agent"},
        "keywords": ("agent loop",),
    },
    {
        "key": "coach",
        "label": "Coach · Advisor & AI Advisory",
        "thread": "THREAD-ECOSYSTEM",
        "tab": "ai-advisory",
        "drill_kind": "subject",
        "drill_id": "subj-advisor",
        "work_ids": {"work-advisor", "work-ai-advisory"},
        "keywords": ("advisor", "advisory"),
    },
    {
        "key": "sina-command",
        "label": "Sina Command hub",
        "thread": "THREAD-ECOSYSTEM",
        "tab": "command",
        "drill_kind": "subject",
        "drill_id": "subj-sina-command",
        "work_ids": {"work-sina-command", "work-ui-guide"},
        "match_ids": {"track-strategic-slice-v1"},
        "keywords": ("sina command", "command hub", "guide"),
    },
    {
        "key": "prompt-os",
        "label": "Prompt OS · dispatch & direction",
        "thread": "THREAD-PROMPTOS",
        "tab": "prompt-os",
        "drill_kind": "subject",
        "drill_id": "subj-promptos-repo",
        "work_ids": {"work-prompt-direction", "work-prompt-os"},
        "match_ids": {"queue-prompt", "direction-feed", "direction-proposed"},
        "keywords": ("prompt queue", "prompt direction", "prompt os"),
    },
    {
        "key": "factory-p0",
        "label": "Factory · P0 RunReceipt",
        "thread": "THREAD-FACTORY",
        "tab": "today",
        "drill_kind": "plan",
        "drill_id": "P0-RUNRECEIPT",
        "work_ids": {"work-p0-runreceipt"},
        "plan_ids": {"P0-RUNRECEIPT"},
        "keywords": ("runreceipt", "p0-runreceipt"),
    },
    {
        "key": "mergepack",
        "label": "MergePack · ship & Evidence Factory",
        "thread": "THREAD-MERGEPACK",
        "tab": "products",
        "drill_kind": "subject",
        "drill_id": "THREAD-MERGEPACK",
        "work_ids": {"work-mergepack-ship"},
        "plan_ids": {"MERGEPACK-L1"},
        "ops_ids": {"MP-SHIP"},
        "keywords": ("mergepack", "form to pdf", "mp-ship"),
    },
    {
        "key": "wire",
        "label": "AI Dev Bridge · Wire / M8",
        "thread": "THREAD-WIRE",
        "tab": "apps",
        "drill_kind": "subject",
        "drill_id": "subj-wire-repo",
        "work_ids": {"work-wire-m8"},
        "plan_ids": {"M8-WIRE"},
        "match_ids": {"track-wire-slice-v1"},
        "keywords": ("wire", "m8", "devbridge", "tailscale"),
    },
    {
        "key": "portfolio",
        "label": "Portfolio · delivery lanes (5 repos)",
        "thread": "THREAD-PORTFOLIO",
        "tab": "repos",
        "drill_kind": "subject",
        "drill_id": "THREAD-PORTFOLIO",
        "work_ids": {"work-portfolio", "work-trustfield", "work-virlux", "work-noetfield", "work-777"},
        "match_ids": {"track-trustfield-slice-v1"},
        "keywords": ("trustfield", "virlux", "noetfield", "777", "mono"),
    },
    {
        "key": "superbrain",
        "label": "Super Brain · Personal DB",
        "thread": "THREAD-SUPERBRAIN",
        "tab": "personal-db",
        "drill_kind": "subject",
        "drill_id": "THREAD-SUPERBRAIN",
        "work_ids": {"work-superbrain", "work-chat-consolidation"},
        "keywords": ("super brain", "personal db", "chat consolidation"),
    },
    {
        "key": "daily",
        "label": "Daily rhythm · ASF",
        "thread": "THREAD-ECOSYSTEM",
        "tab": "today",
        "drill_kind": "",
        "drill_id": "",
        "source_types": {"duty"},
        "keywords": ("must do", "pick one active thread", "daily bowl", "drift"),
    },
    {
        "key": "notes-fixes",
        "label": "Your notes & fixes",
        "thread": "THREAD-ECOSYSTEM",
        "tab": "notes",
        "drill_kind": "note",
        "drill_id": "",
        "source_types": {"note"},
        "keywords": (),
    },
    {
        "key": "other",
        "label": "Other open items",
        "thread": "THREAD-ECOSYSTEM",
        "tab": "track",
        "drill_kind": "",
        "drill_id": "",
        "keywords": (),
    },
]

# Platform / product build threads — always on Track until founder dismisses (never only when loop active).
WORK_TO_SUBJECT: dict[str, str] = {
    "work-semej": "subj-semej",
    "work-agent-loop": "subj-agent-loop",
    "work-advisor": "subj-advisor",
    "work-sina-command": "subj-sina-command",
    "work-prompt-direction": "subj-prompt-direction",
    "work-prompt-os": "subj-promptos-repo",
    "work-mergepack-ship": "THREAD-MERGEPACK",
    "work-p0-runreceipt": "P0-RUNRECEIPT",
}


def _platform_stream_status(
    work_id: str,
    *,
    semej: dict | None,
    agent_loop: dict | None,
) -> tuple[str, str]:
    """Return (commitment_status, detail_suffix)."""
    sm = semej or _load_json(SEMEJ_LOOP_PATH)
    al = agent_loop or _load_json(AGENT_LOOP_PATH)
    if work_id == "work-semej":
        if sm.get("active"):
            st = "needs_you" if sm.get("needs_manual") else "in_progress"
            extra = sm.get("idea") or sm.get("current_prompt_preview") or ""
            if sm.get("current_provider"):
                extra = f"{sm['current_provider']}: {extra}"
            return st, (extra or "Chain running in Chrome")[:200]
        parts = []
        if not sm.get("playwright_ready"):
            parts.append("Install SEMEJ browser tools (Actions tab)")
        if not sm.get("chrome_ready"):
            parts.append("Start Chrome for SEMEJ + sign in to AIs")
        if parts:
            return "needs_you", " · ".join(parts)
        return "open", "Build/validate SEMEJ: chain providers → test idea → artifact"
    if work_id == "work-agent-loop":
        if al.get("active"):
            r, mx = al.get("round") or 0, al.get("max_rounds") or 10
            st = "needs_you" if al.get("needs_manual") else "in_progress"
            return st, f"Round {r}/{mx} — {al.get('current_title') or al.get('goal', '')}"[:200]
        return "open", "10× autopilot: planner injects prompts; executor builds in Cursor"
    if work_id == "work-advisor":
        return "open", "Strategic coach — OpenRouter / Cursor Cloud / IDE (not coding agent)"
    if work_id == "work-sina-command":
        return "in_progress", "Hub :13020 — Track, ecosystem map, briefs, Guide"
    if work_id == "work-prompt-direction":
        return "open", "Live next-10 SSOT — optional commentary stamp only (INCIDENT-024/028)"
    if work_id == "work-prompt-os":
        return "open", "Five-repo dispatch + ingest + prompt library"
    if work_id == "work-mergepack-ship":
        return "open", "Form to PDF live · KPI trio · Vercel ship"
    if work_id == "work-p0-runreceipt":
        return "in_progress", "run.jsonl + summary.json + HTML receipt pack"
    return "open", ""


def _subject_for_row(r: dict) -> str:
    rid = r.get("id") or ""
    sid = r.get("source_id") or ""
    src = r.get("source") or ""
    blob = f"{rid} {sid} {r.get('title','')} {r.get('detail','')}".lower()
    for subj in SUBJECT_DEFS:
        work_ids = subj.get("work_ids") or frozenset()
        match_ids = subj.get("match_ids") or frozenset()
        plan_ids = subj.get("plan_ids") or frozenset()
        ops_ids = subj.get("ops_ids") or frozenset()
        if rid in work_ids or rid in match_ids:
            return subj["key"]
        if sid in plan_ids or sid in ops_ids:
            return subj["key"]
        if src in (subj.get("source_types") or frozenset()):
            return subj["key"]
        if any(k in blob for k in (subj.get("keywords") or ())):
            return subj["key"]
    if src == "manual":
        return "other"
    if src == "todo":
        return "daily"
    if src == "drift":
        return "daily"
    return "other"


def _pick_primary(members: list[dict]) -> dict:
    source_rank = {
        "ops": 0,
        "semej": 1,
        "agent_loop": 2,
        "workstream": 3,
        "p0": 4,
        "plan": 5,
        "prompt_direction": 6,
        "prompt_queue": 7,
        "note": 8,
        "duty": 9,
        "todo": 10,
        "drift": 11,
        "manual": 12,
    }
    return sorted(
        members,
        key=lambda m: (
            0 if m.get("pinned") else 1,
            STATUS_RANK.get(m.get("status"), 9),
            PRIORITY_RANK.get(m.get("priority"), 9),
            source_rank.get(m.get("source"), 99),
        ),
    )[0]


def _merge_subject_group(key: str, members: list[dict]) -> dict:
    meta = next(s for s in SUBJECT_DEFS if s["key"] == key)
    primary = _pick_primary(members)
    statuses = [m.get("status") for m in members]
    status = min(statuses, key=lambda s: STATUS_RANK.get(s, 9))
    priorities = [m.get("priority") for m in members]
    priority = min(priorities, key=lambda p: PRIORITY_RANK.get(p, 9))
    sub_items: list[dict] = []
    seen_detail: set[str] = set()
    for m in members:
        if m.get("id") == primary.get("id"):
            continue
        d = (m.get("detail") or m.get("title") or "").strip()
        if not d or d in seen_detail or d == primary.get("detail"):
            continue
        seen_detail.add(d)
        sub_items.append(
            {
                "title": m.get("title", ""),
                "detail": d[:220],
                "source": m.get("source", ""),
                "status": m.get("status", "open"),
            }
        )
    detail = primary.get("detail") or ""
    if sub_items and len(sub_items) <= 4:
        extras = "; ".join(s["detail"][:80] for s in sub_items[:3])
        if extras and extras not in detail:
            detail = f"{detail} — Also: {extras}" if detail else extras
    use_primary_title = (
        str(primary.get("id") or "").startswith("track-")
        or (primary.get("pinned") and primary.get("source") == "manual")
    )
    card_title = primary.get("title") if use_primary_title else meta["label"]
    return {
        **primary,
        "id": f"subject-{key}",
        "subject_key": key,
        "subject_label": meta["label"],
        "title": card_title,
        "detail": detail[:500],
        "status": status,
        "priority": priority,
        "thread": meta.get("thread") or primary.get("thread", ""),
        "tab": meta.get("tab") or primary.get("tab", "track"),
        "drill_kind": meta.get("drill_kind") or primary.get("drill_kind", ""),
        "drill_id": meta.get("drill_id") or primary.get("drill_id", ""),
        "sub_items": sub_items[:8],
        "merged_count": len(members),
        "merged_sources": sorted({m.get("source") for m in members}),
        "never_drop": any(m.get("never_drop") for m in members),
        "source": "subject",
        "source_id": key,
    }


def organize_commitments(
    raw: list[dict],
    *,
    founder: dict | None = None,
    repos: list[dict] | None = None,
) -> tuple[list[dict], list[dict]]:
    """Merge duplicates into one card per subject; return (items, by_subject)."""
    founder = founder or {}
    buckets: dict[str, list[dict]] = {s["key"]: [] for s in SUBJECT_DEFS}

    # Daily rhythm — one card from must_do + duties (not 5 separate lines)
    must = list(founder.get("must_do_today") or [])[:6]
    drift_duties = [r for r in raw if r.get("source") in ("duty", "drift")]
    if must or drift_duties:
        lines = [f"• {m}" for m in must]
        for d in drift_duties:
            t = d.get("title") or d.get("detail")
            if t and t not in must:
                lines.append(f"• {t}")
        buckets["daily"].append(
            _row(
                cid="subject-daily",
                title="Daily rhythm · ASF",
                detail="\n".join(lines)[:500],
                source="daily",
                source_id="must_do",
                status="open",
                priority="high",
                thread="THREAD-ECOSYSTEM",
                tab="today",
            )
        )

    for r in raw:
        if r.get("source") in ("duty", "drift"):
            continue
        if r.get("id", "").startswith("subject-"):
            continue
        key = _subject_for_row(r)
        buckets.setdefault(key, []).append(r)

    # Enrich portfolio from live repo plans
    if repos:
        plines: list[str] = []
        blocked = 0
        for repo in repos:
            rid = repo.get("id") or ""
            if rid in ("mergepack", "wire", "promptos", "sourcea", "hq"):
                continue
            nt = repo.get("next_tasks") or []
            task = ""
            if nt:
                t0 = nt[0]
                task = t0.get("text", str(t0)) if isinstance(t0, dict) else str(t0)
            task = (task or repo.get("active_focus") or "—")[:120]
            if repo.get("global_blocker") or repo.get("blocked"):
                blocked += 1
                task = f"[BLOCKED] {task}"
            plines.append(f"• {repo.get('name', rid)}: {task}")
        if plines:
            st = "blocked" if blocked else "open"
            buckets["portfolio"].append(
                _row(
                    cid="subject-portfolio-live",
                    title="Portfolio · five delivery repos",
                    detail="\n".join(plines)[:500],
                    source="repos",
                    source_id="portfolio",
                    status=st,
                    priority="high" if blocked else "normal",
                    thread="THREAD-PORTFOLIO",
                    tab="repos",
                    drill_kind="subject",
                    drill_id="THREAD-PORTFOLIO",
                    never_drop=True,
                )
            )

    merged: list[dict] = []
    by_subject: list[dict] = []
    order_keys = [s["key"] for s in SUBJECT_DEFS if s["key"] != "other"]
    order_keys.append("other")

    for key in order_keys:
        members = buckets.get(key) or []
        if not members:
            continue
        if key == "daily" and len(members) == 1:
            card = {**members[0], "subject_key": key, "subject_label": "Daily rhythm · ASF", "merged_count": 1}
        elif len(members) == 1:
            card = {
                **members[0],
                "subject_key": key,
                "subject_label": next(s["label"] for s in SUBJECT_DEFS if s["key"] == key),
                "merged_count": 1,
                "sub_items": [],
            }
        else:
            card = _merge_subject_group(key, members)
        merged.append(card)
        by_subject.append(
            {
                "key": key,
                "label": card["subject_label"],
                "count": card.get("merged_count", 1),
                "status": card.get("status"),
                "priority": card.get("priority"),
                "item": card,
            }
        )

    merged.sort(
        key=lambda x: (
            PRIORITY_RANK.get(x.get("priority"), 9),
            STATUS_RANK.get(x.get("status"), 9),
            x.get("subject_label", x.get("title", "")),
        )
    )
    by_subject.sort(
        key=lambda x: (
            PRIORITY_RANK.get(x.get("priority"), 9),
            STATUS_RANK.get(x.get("status"), 9),
            x.get("label", ""),
        )
    )
    return merged, by_subject


def collect_platform_workstreams(
    store: dict,
    *,
    semej: dict | None = None,
    agent_loop: dict | None = None,
) -> list[dict]:
    dismissed = set(store.get("dismissed_workstreams") or [])
    rows: list[dict] = []
    for w in WORK_THREADS:
        st = (w.get("status") or "").lower()
        if st in SKIP_WORKSTREAM_STATUS:
            continue
        wid = w.get("id") or ""
        if wid not in TRACK_WORKSTREAM_IDS:
            continue
        if not wid or wid in dismissed:
            continue
        tabs = w.get("tabs") or ["track"]
        tab = tabs[0] if tabs else "track"
        st, extra = _platform_stream_status(wid, semej=semej, agent_loop=agent_loop)
        detail = w.get("summary") or ""
        if extra:
            detail = f"{detail} — {extra}" if detail else extra
        subj = WORK_TO_SUBJECT.get(wid, "")
        rows.append(
            _row(
                cid=wid,
                title=w.get("title", wid),
                detail=detail[:500],
                source="workstream",
                source_id=wid,
                status=st,
                priority="critical" if w.get("priority_today") else "high",
                thread=w.get("thread_id", "THREAD-ECOSYSTEM"),
                tab=tab,
                drill_kind="subject" if subj.startswith("subj-") else "plan",
                drill_id=subj or wid,
                never_drop=True,
                started_at=store.get("started_log", {}).get(wid),
            )
        )
    return rows


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def collect_commitments(
    *,
    bowl: dict | None = None,
    progress: dict | None = None,
    ops: list | None = None,
    founder_notes: list | None = None,
    prompt_queue: dict | None = None,
    agent_loop: dict | None = None,
    semej: dict | None = None,
    prompt_direction: dict | None = None,
    ecosystem: dict | None = None,
    founder: dict | None = None,
    repos: list[dict] | None = None,
) -> list[dict]:
    bowl = bowl or {}
    progress = progress or {}
    ops = ops or []
    rows: list[dict] = []
    seen: set[str] = set()

    def add(r: dict) -> None:
        key = f"{r.get('source')}:{r.get('source_id') or r.get('id')}"
        if key in seen:
            return
        seen.add(key)
        rows.append(r)

    store = _load_store()

    # Platform build threads (SEMEJ, agent loop, Command, …) — always visible until dismissed
    for pw in collect_platform_workstreams(store, semej=semej, agent_loop=agent_loop):
        add(pw)

    # Manual + persisted (never auto-delete)
    for m in store.get("manual") or []:
        if m.get("status") == "done":
            continue
        add(
            _row(
                cid=m.get("id") or f"manual-{uuid.uuid4().hex[:8]}",
                title=m.get("title") or m.get("text", "Commitment"),
                detail=m.get("detail") or m.get("text", ""),
                source="manual",
                source_id=m.get("id", ""),
                status=m.get("status", "open"),
                priority=m.get("priority", "high"),
                thread=m.get("thread", ""),
                tab=m.get("tab", "track"),
                never_drop=True,
                started_at=m.get("started_at"),
            )
        )

    # Founder notes (open)
    for n in founder_notes or []:
        if n.get("status") == "done":
            continue
        pri = "high" if n.get("category") == "fix" else "normal"
        add(
            _row(
                cid=f"note-{n.get('id')}",
                title=(n.get("text") or "Note")[:120],
                detail=n.get("text", ""),
                source="note",
                source_id=n.get("id", ""),
                status="needs_you",
                priority=pri,
                thread="THREAD-ECOSYSTEM",
                tab="notes",
                drill_kind="note",
                drill_id=n.get("id", ""),
            )
        )

    # Program todos
    for t in (progress.get("todos") or bowl.get("open_todos") or []):
        if t.get("status") != "open":
            continue
        add(
            _row(
                cid=f"todo-{t.get('id')}",
                title=f"Todo · {t.get('id')}",
                detail=t.get("text", ""),
                source="todo",
                source_id=t.get("id", ""),
                status="open",
                priority="high" if t.get("owner") == "ASF" else "normal",
                thread="THREAD-ECOSYSTEM",
                tab="today",
                drill_kind="todo",
                drill_id=t.get("id", ""),
            )
        )

    # Ops blockers — always visible
    for o in ops:
        sev = o.get("severity", "high")
        pri = "critical" if sev == "critical" else "high"
        add(
            _row(
                cid=f"ops-{o.get('id')}",
                title=o.get("title", o.get("id", "Blocker")),
                detail=o.get("action", ""),
                source="ops",
                source_id=o.get("id", ""),
                status="blocked",
                priority=pri,
                thread="THREAD-MERGEPACK" if "MP" in str(o.get("id")) else "THREAD-WIRE",
                tab="today",
                drill_kind="ops",
                drill_id=o.get("id", ""),
                never_drop=True,
            )
        )

    # Drift
    for i, d in enumerate(bowl.get("drift") or []):
        add(
            _row(
                cid=f"drift-{i}",
                title=d.get("title", "Drift"),
                detail=d.get("action", ""),
                source="drift",
                source_id=str(i),
                status="open",
                priority="high" if d.get("severity") == "high" else "normal",
                tab="today",
            )
        )

    # ASF duties — merged into daily subject (not separate cards)
    for i, duty in enumerate((bowl.get("asf_duties") or [])[:8]):
        add(
            _row(
                cid=f"duty-{i}",
                title=duty[:100],
                detail=duty[:200],
                source="duty",
                source_id=str(i),
                status="open",
                priority="high",
                tab="today",
            )
        )

    p0 = bowl.get("p0") or {}
    p0_id = p0.get("id")

    # Parallel plans (active, not done) — merged by subject with workstreams
    for p in (progress.get("parallel_plans") or bowl.get("parallel_plans") or []):
        st = (p.get("status") or "").lower()
        if st in ("done", "paused", "cancelled"):
            continue
        pid = p.get("id")
        if not pid:
            continue
        # P0 plan row skipped — work-p0-runreceipt + factory-p0 subject merge handles it
        if pid == p0_id:
            continue
        pct = p.get("progress_pct") or 0
        add(
            _row(
                cid=f"plan-{pid}",
                title=p.get("title", pid),
                detail=p.get("next_action") or p.get("phase", ""),
                source="plan",
                source_id=pid,
                status="in_progress" if pct > 0 else "open",
                priority="high" if "MERGEPACK" in pid else "normal",
                thread=p.get("thread", pid),
                tab="plans",
                drill_kind="plan",
                drill_id=pid,
                never_drop=True,
                started_at=p.get("started_at"),
            )
        )

    # Agent loop — started work
    al = agent_loop or _load_json(AGENT_LOOP_PATH)
    if al.get("active"):
        r = al.get("round") or 0
        mx = al.get("max_rounds") or 10
        st = al.get("status", "active")
        status = "needs_you" if al.get("needs_manual") or st == "awaiting_manual" else "in_progress"
        add(
            _row(
                cid="loop-agent",
                title=f"Agent loop · round {r}/{mx}",
                detail=al.get("current_title") or al.get("goal", "")[:200],
                source="agent_loop",
                source_id="agent-loop",
                status=status,
                priority="critical",
                thread="THREAD-ECOSYSTEM",
                tab="agent-loop",
                never_drop=True,
                started_at=al.get("awaiting_since"),
            )
        )

    # SEMEJ loop — live round (in addition to standing work-semej workstream)
    sm = semej or _load_json(SEMEJ_LOOP_PATH)
    if sm.get("active"):
        status = "needs_you" if sm.get("needs_manual") else "in_progress"
        add(
            _row(
                cid="loop-semej-live",
                title=f"SEMEJ live · {sm.get('current_provider') or 'Chrome AI'}",
                detail=(sm.get("idea") or sm.get("current_prompt_preview") or "")[:200],
                source="semej",
                source_id="semej-active",
                status=status,
                priority="critical",
                thread="THREAD-ECOSYSTEM",
                tab="semej",
                drill_kind="subject",
                drill_id="subj-semej",
                never_drop=True,
            )
        )

    # Prompt queue pending
    pq = prompt_queue or _load_json(QUEUE_PATH)
    pending = pq.get("pending_count") or 0
    if pending:
        nxt = pq.get("next") or {}
        add(
            _row(
                cid="queue-prompt",
                title=f"Prompt queue · {pending} waiting",
                detail=(nxt.get("title") or nxt.get("preview") or "Send next in Next steps")[:200],
                source="prompt_queue",
                source_id=pq.get("session_id", ""),
                status="in_progress",
                priority="high",
                tab="prompt-feed",
                never_drop=True,
            )
        )

    # Prompt direction feeding
    pd = prompt_direction or {}
    if pd.get("status") == "feeding":
        add(
            _row(
                cid="direction-feed",
                title="Prompt direction · optional commentary",
                detail=pd.get("direction_title") or "Live next-10 SSOT — commentary stamp only (no auto-send)",
                source="prompt_direction",
                source_id="feed",
                status="in_progress",
                priority="high",
                tab="prompt-feed",
                never_drop=True,
            )
        )
    elif pd.get("status") == "proposed":
        add(
            _row(
                cid="direction-proposed",
                title="Prompt direction · optional commentary",
                detail=(pd.get("proposal") or {}).get("direction_title", "Optional stamp — machine order unchanged · no auto-send"),
                source="prompt_direction",
                source_id="proposed",
                status="needs_you",
                priority="high",
                tab="prompt-feed",
            )
        )

    # Pin boost
    pinned = set(store.get("pinned_ids") or [])
    for r in rows:
        if r["id"] in pinned:
            r["pinned"] = True
            r["priority"] = "critical"

    order = {"critical": 0, "high": 1, "normal": 2}
    status_order = {"needs_you": 0, "blocked": 1, "in_progress": 2, "open": 3}
    rows.sort(
        key=lambda x: (
            order.get(x.get("priority"), 9),
            status_order.get(x.get("status"), 9),
            x.get("title", ""),
        )
    )
    return rows


def commitments_payload(**kwargs) -> dict:
    raw = collect_commitments(**kwargs)
    founder = kwargs.get("founder") or {}
    repos = kwargs.get("repos")
    rows, by_subject = organize_commitments(raw, founder=founder, repos=repos)
    by_status: dict[str, list] = {}
    for r in rows:
        st = r.get("status") or "open"
        by_status.setdefault(st, []).append(r)
    open_count = len(rows)
    critical = [r for r in rows if r.get("priority") == "critical"]
    needs_you = [r for r in rows if r.get("status") == "needs_you"]
    in_progress = [r for r in rows if r.get("status") == "in_progress"]
    return {
        "ok": True,
        "open_count": open_count,
        "raw_count": len(raw),
        "critical_count": len(critical),
        "needs_you_count": len(needs_you),
        "in_progress_count": len(in_progress),
        "items": rows,
        "by_subject": by_subject,
        "by_status": {k: {"count": len(v), "items": v} for k, v in by_status.items()},
        "lanes": [
            {
                "id": "by_subject",
                "label": "By subject",
                "count": len(by_subject),
                "subjects": by_subject,
            },
            {
                "id": "needs_you",
                "label": "Needs you",
                "count": len(needs_you),
                "items": needs_you,
            },
            {
                "id": "in_progress",
                "label": "In progress",
                "count": len(in_progress),
                "items": in_progress,
            },
            {
                "id": "blocked",
                "label": "Blocked",
                "count": len(by_status.get("blocked", [])),
                "items": by_status.get("blocked", []),
            },
            {
                "id": "open",
                "label": "Open",
                "count": len(by_status.get("open", [])),
                "items": by_status.get("open", []),
            },
        ],
        "tagline": "Organized by subject — duplicates merged. Nothing important dropped.",
    }


def add_manual_commitment(
    text: str,
    *,
    title: str | None = None,
    priority: str = "high",
    thread: str = "",
) -> dict:
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "text required"}
    store = _load_store()
    item = {
        "id": str(uuid.uuid4())[:10],
        "title": (title or text)[:200],
        "detail": text[:2000],
        "text": text,
        "status": "open",
        "priority": priority if priority in ("critical", "high", "normal") else "high",
        "thread": thread,
        "tab": "track",
        "started_at": _now(),
        "never_drop": True,
    }
    store.setdefault("manual", []).insert(0, item)
    _save_store(store)
    return {"ok": True, "item": item}


def set_commitment_done(commitment_id: str, *, source: str | None = None) -> dict:
    store = _load_store()
    if source == "manual" or commitment_id.startswith("manual-"):
        cid = commitment_id.replace("manual-", "")
        for m in store.get("manual") or []:
            if m.get("id") == cid or m.get("id") == commitment_id:
                m["status"] = "done"
                m["done_at"] = _now()
                _save_store(store)
                return {"ok": True, "message": "Marked done", "id": commitment_id}
    # Delegate to note/todo handlers via return hint
    if commitment_id.startswith("note-"):
        from founder_notes import set_note_status  # noqa: WPS433

        return set_note_status(commitment_id.replace("note-", ""), "done")
    return {
        "ok": False,
        "error": "Use linked page to complete this item (todo, ops, loop)",
        "hint": commitment_id,
    }


def pin_commitment(commitment_id: str, pinned: bool = True) -> dict:
    store = _load_store()
    pins = set(store.get("pinned_ids") or [])
    if pinned:
        pins.add(commitment_id)
    else:
        pins.discard(commitment_id)
    store["pinned_ids"] = sorted(pins)
    _save_store(store)
    return {"ok": True, "pinned": pinned, "id": commitment_id}


def handle_commitments_action(body: dict, *, hub_context: dict | None = None) -> dict:
    action = (body.get("action") or "list").strip().lower()
    ctx = hub_context or {}
    if action == "list" or action == "status":
        return {"ok": True, **commitments_payload(**ctx)}
    if action == "add":
        return add_manual_commitment(
            body.get("text") or body.get("title", ""),
            title=body.get("title"),
            priority=body.get("priority", "high"),
            thread=body.get("thread", ""),
        )
    if action == "done":
        return set_commitment_done(
            body.get("id", ""),
            source=body.get("source"),
        )
    if action == "pin":
        return pin_commitment(body.get("id", ""), pinned=body.get("pinned", True) is not False)
    if action == "dismiss_workstream":
        wid = body.get("id") or body.get("workstream_id", "")
        if not wid:
            return {"ok": False, "error": "id required"}
        store = _load_store()
        dismissed = set(store.get("dismissed_workstreams") or [])
        dismissed.add(wid)
        store["dismissed_workstreams"] = sorted(dismissed)
        _save_store(store)
        return {"ok": True, "message": f"Removed {wid} from standing workstreams (can re-add manually)"}
    if action == "start_workstream":
        wid = body.get("id", "")
        if not wid:
            return {"ok": False, "error": "id required"}
        store = _load_store()
        log = store.setdefault("started_log", {})
        log[wid] = _now()
        dismissed = set(store.get("dismissed_workstreams") or [])
        dismissed.discard(wid)
        store["dismissed_workstreams"] = sorted(dismissed)
        _save_store(store)
        return {"ok": True, "message": f"Logged start for {wid}"}
    return {"ok": False, "error": f"unknown action: {action}"}

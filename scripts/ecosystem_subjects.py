#!/usr/bin/env python3
"""
Ecosystem subjects — FULL map of every distinct topic/thread in Sina OS.

Harvests: ASF registry, plans, repos, products, all LOCKED/docs, master orders,
Prompt OS projects, investor package, fleet workspaces, ALL Cursor transcripts,
and work-stream topics (Command, agent loop, SEMEJ, etc.) — each connected to details.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sina_link_graph import (
    FORM_TO_PDF_LIVE,
    MERGEPACK_ROOT,
    PLAN_NODES,
    REPO_PLAN_REL,
    REPO_ROOTS,
    REPO_THREADS,
    THREAD_NODES,
    hub_url,
    link,
    links_for_plan,
    links_for_product,
    links_for_repo,
    links_for_thread,
)

SOURCE_A = Path(__file__).resolve().parents[1]
CACHE_PATH = Path.home() / ".sina" / "ecosystem-subjects-full.json"
TRANSCRIPT_ROOT = Path.home() / ".cursor/projects"
PROMPTOS_ROOT = Path.home() / "Desktop/SinaPromptOS"
INVESTOR_DIR = SOURCE_A / "investor"
REGISTRY_MD = SOURCE_A / "ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md"

# Canonical ASF + product + work-stream subjects (hubs)
HUB_SUBJECTS: list[dict] = [
    {"id": "THREAD-SUPERBRAIN", "title": "Super Brain · Personal SoT", "category": "Foundation", "status": "active"},
    {"id": "THREAD-CHAT-CONSOLIDATION", "title": "Chat consolidation (100→L2)", "category": "Foundation", "status": "open"},
    {"id": "THREAD-ECOSYSTEM", "title": "Sina OS · Source A ecosystem", "category": "Governance", "status": "locked"},
    {"id": "THREAD-SOURCE-B", "title": "Source B · conflicts map", "category": "Reference", "status": "reference"},
    {"id": "THREAD-PROMPTOS", "title": "Sina Prompt OS · five-repo dispatch", "category": "Automation", "status": "active"},
    {"id": "THREAD-ARCHITECT", "title": "Permanent Architect", "category": "Governance", "status": "active"},
    {"id": "THREAD-AGENT-DESK", "title": "Agent desk · fleet monitor", "category": "Ops", "status": "active"},
    {"id": "THREAD-PHASE2-TRUTH", "title": "Phase 2 · execution truth", "category": "Ops", "status": "background"},
    {"id": "THREAD-WIRE", "title": "AI Dev Bridge · Wire / M8", "category": "Automation", "status": "active"},
    {"id": "THREAD-CURSOR-OS-PRO", "title": "Cursor OS Pro · App Store SKU", "category": "SKU", "status": "parallel"},
    {"id": "THREAD-FACTORY", "title": "Product factory (30 ideas)", "category": "Factory", "status": "done"},
    {"id": "THREAD-MERGEPACK", "title": "MergePack · Evidence Factory", "category": "Revenue", "status": "active"},
    {"id": "THREAD-AUDIENCE-HUB", "title": "Audience Hub", "category": "SKU", "status": "paused"},
    {"id": "THREAD-INVESTOR", "title": "Investor · deck & narrative", "category": "Fundraising", "status": "reference"},
    {"id": "THREAD-PORTFOLIO", "title": "Portfolio · five company lanes", "category": "Delivery", "status": "active"},
    {"id": "THREAD-TRUSTFIELD-INFRA", "title": "TrustField · free infra rule", "category": "Infra", "status": "locked"},
    {"id": "subj-trustfield", "title": "TrustField Technologies", "category": "Company", "parent": "THREAD-PORTFOLIO", "repo_id": "trustfield"},
    {"id": "subj-mono", "title": "Sinaai Mono · PAIOS", "category": "Company", "parent": "THREAD-SUPERBRAIN", "repo_id": "mono"},
    {"id": "subj-virlux", "title": "VIRLUX", "category": "Company", "parent": "THREAD-PORTFOLIO", "repo_id": "virlux"},
    {"id": "subj-noetfield", "title": "Noetfield OS", "category": "Company", "parent": "THREAD-PORTFOLIO", "repo_id": "noetfield"},
    {"id": "subj-777", "title": "777 Foundation", "category": "Company", "parent": "THREAD-PORTFOLIO", "repo_id": "seven77"},
    {"id": "subj-mergepack-repo", "title": "MergePack repo", "category": "Product", "parent": "THREAD-MERGEPACK", "repo_id": "mergepack"},
    {"id": "subj-wire-repo", "title": "AI Dev Bridge OS", "category": "Automation", "parent": "THREAD-WIRE", "repo_id": "wire"},
    {"id": "subj-promptos-repo", "title": "SinaPromptOS repo", "category": "Automation", "parent": "THREAD-PROMPTOS", "repo_id": "promptos"},
    {"id": "subj-sina-command", "title": "Sina Command app", "category": "Platform", "parent": "THREAD-ECOSYSTEM", "tab": "command"},
    {"id": "subj-agent-loop", "title": "Agent loop (10×)", "category": "Platform", "parent": "THREAD-ECOSYSTEM", "tab": "agent-loop"},
    {"id": "subj-semej", "title": "SEMEJ · Chrome AI chain", "category": "Platform", "parent": "THREAD-ECOSYSTEM", "tab": "semej"},
    {"id": "subj-advisor", "title": "Advisor AI (Cursor/OpenRouter)", "category": "Platform", "parent": "THREAD-ECOSYSTEM", "tab": "agent-loop"},
    {"id": "subj-track", "title": "Track · nothing missed", "category": "Platform", "parent": "THREAD-ECOSYSTEM", "tab": "track"},
    {"id": "subj-form-pdf", "title": "Form to PDF (live)", "category": "Live product", "parent": "THREAD-MERGEPACK", "product_id": "mergepack-form-pdf"},
]

WORKSPACE_SUBJECT: dict[str, str] = {
    "Users-sinakazemnezhad-Desktop-SinaaiDataBase": "THREAD-ECOSYSTEM",
    "Users-sinakazemnezhad-Desktop-SourceA": "THREAD-ECOSYSTEM",
    "Users-sinakazemnezhad-Desktop-TrustField-Technologies": "subj-trustfield",
    "Users-sinakazemnezhad-Desktop-SinaaiMonoRepo": "subj-mono",
    "Users-sinakazemnezhad-Desktop-Virlux": "subj-virlux",
    "Users-sinakazemnezhad-Desktop-Noetfield-All-Documents": "subj-noetfield",
    "Users-sinakazemnezhad-Desktop-Noetfield": "subj-noetfield",
    "Users-sinakazemnezhad-Projects-noetfeld-os": "subj-noetfield",
    "Users-sinakazemnezhad-Desktop-The-777-Foundation": "subj-777",
    "Users-sinakazemnezhad-Desktop-AI-Dev-Bridge-OS": "subj-wire-repo",
    "Users-sinakazemnezhad-Desktop-Cursor-OS-Pro": "THREAD-CURSOR-OS-PRO",
    "Users-sinakazemnezhad-Desktop-mergepack": "subj-mergepack-repo",
    "Users-sinakazemnezhad-Desktop-SinaPromptOS": "subj-promptos-repo",
}

DOC_RULES: list[tuple[str, str, str]] = [
    (r"investor/", "THREAD-INVESTOR", "Investor"),
    (r"product/mergepack|mergepack|form-to-pdf|form_to_pdf", "THREAD-MERGEPACK", "MergePack"),
    (r"product/factory|PRODUCT_FACTORY", "THREAD-FACTORY", "Factory"),
    (r"wire|devbridge|m8|full_m8", "THREAD-WIRE", "Wire"),
    (r"noetfield|noetfeld", "subj-noetfield", "Noetfield"),
    (r"virlux|wirelux", "subj-virlux", "VIRLUX"),
    (r"trustfield", "subj-trustfield", "TrustField"),
    (r"777|seven77|foundation", "subj-777", "777"),
    (r"promptos|prompt_os|sina_prompt", "THREAD-PROMPTOS", "Prompt OS"),
    (r"cursor.os.pro|cursor-os-pro", "THREAD-CURSOR-OS-PRO", "Cursor OS Pro"),
    (r"personal.db|superbrain|paios|chat.consolidation", "THREAD-SUPERBRAIN", "Super Brain"),
    (r"sina.command|command.panel|agent.loop|semej", "subj-sina-command", "Sina Command"),
    (r"agent.loop|agent_loop", "subj-agent-loop", "Agent loop"),
    (r"semej", "subj-semej", "SEMEJ"),
    (r"architect", "THREAD-ARCHITECT", "Architect"),
    (r"fleet|agent.desk", "THREAD-AGENT-DESK", "Fleet"),
    (r"master.order|MASTER_ORDERS", "THREAD-ECOSYSTEM", "Master orders"),
    (r"SINA_OS_SSOT|SSOT", "THREAD-ECOSYSTEM", "SSOT"),
    (r"THREAD|ASF_PROGRAM_THREADS", "THREAD-ECOSYSTEM", "Threads law"),
    (r"portfolio|GLOBAL_BLOCKER|five.repo", "THREAD-PORTFOLIO", "Portfolio"),
    (r"evidence.factory|runreceipt|run.receipt", "THREAD-FACTORY", "RunReceipt"),
]

CHAT_KEYWORDS: list[tuple[str, str]] = [
    ("mergepack", "THREAD-MERGEPACK"),
    ("form to pdf", "subj-form-pdf"),
    ("form-to-pdf", "subj-form-pdf"),
    ("agent loop", "subj-agent-loop"),
    ("semej", "subj-semej"),
    ("advisor", "subj-advisor"),
    ("sina command", "subj-sina-command"),
    ("prompt os", "THREAD-PROMPTOS"),
    ("promptos", "subj-promptos-repo"),
    ("noetfield", "subj-noetfield"),
    ("virlux", "subj-virlux"),
    ("trustfield", "subj-trustfield"),
    ("777", "subj-777"),
    ("wire", "THREAD-WIRE"),
    ("devbridge", "subj-wire-repo"),
    ("investor", "THREAD-INVESTOR"),
    ("super brain", "THREAD-SUPERBRAIN"),
    ("personal db", "THREAD-SUPERBRAIN"),
    ("cursor os pro", "THREAD-CURSOR-OS-PRO"),
    ("openrouter", "THREAD-ECOSYSTEM"),
    ("duolingo", "subj-sina-command"),
    ("ecosystem map", "THREAD-ECOSYSTEM"),
    ("kavodax", "THREAD-PORTFOLIO"),
    ("bank-grade", "subj-noetfield"),
    ("fastapi", "subj-noetfield"),
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:48]


def _extract_user_query(raw: str) -> str:
    m = re.search(r"<user_query>(.*?)</user_query>", raw, re.DOTALL | re.I)
    if m:
        return m.group(1).strip()
    if "[Image]" in raw:
        m2 = re.search(r"<user_query>(.*?)</user_query>", raw, re.DOTALL | re.I)
        if m2:
            return m2.group(1).strip()
    return raw.strip()


def _classify_text(text: str) -> list[str]:
    low = text.lower()
    hits: list[str] = []
    for needle, sid in CHAT_KEYWORDS:
        if needle in low and sid not in hits:
            hits.append(sid)
    for pattern, sid, _ in DOC_RULES:
        if re.search(pattern, low, re.I) and sid not in hits:
            hits.append(sid)
    return hits or ["THREAD-ECOSYSTEM"]


def _doc_subject_ids(rel: str) -> list[str]:
    r = rel.lower()
    out: list[str] = []
    for pattern, sid, _ in DOC_RULES:
        if re.search(pattern, r, re.I) and sid not in out:
            out.append(sid)
    return out or ["THREAD-ECOSYSTEM"]


def _init_subjects() -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    for h in HUB_SUBJECTS:
        sid = h["id"]
        by_id[sid] = {
            "id": sid,
            "title": h["title"],
            "category": h.get("category", "Topic"),
            "parent_id": h.get("parent"),
            "status": h.get("status", "active"),
            "summary": "",
            "asf_thread": sid if sid.startswith("THREAD-") else h.get("parent", ""),
            "repo_id": h.get("repo_id"),
            "product_id": h.get("product_id"),
            "plan_ids": [],
            "tabs": [h["tab"]] if h.get("tab") else [],
            "docs": [],
            "chats": [],
            "orders": [],
            "plans": [],
            "products": [],
            "repos": [],
            "links": [],
            "topic_tags": [],
            "sources": ["catalog"],
            "priority_today": sid in ("THREAD-MERGEPACK", "THREAD-FACTORY", "subj-sina-command", "subj-agent-loop"),
            "drill_kind": "subject",
            "drill_id": sid,
            "hub_tab": h.get("tab") or "threads",
        }
    return by_id


def _attach_doc(subjects: dict[str, dict], rel: str, title: str | None = None) -> None:
    from sina_command_lib import resolve_doc_path  # noqa: WPS433

    resolved = resolve_doc_path(rel)
    row = {
        "path": rel,
        "title": title or Path(rel).name,
        "exists": bool(resolved and resolved[0].is_file()),
    }
    if resolved and resolved[0].is_file():
        row["updated_at"] = datetime.fromtimestamp(
            resolved[0].stat().st_mtime, tz=timezone.utc
        ).isoformat()
    for sid in _doc_subject_ids(rel):
        if sid not in subjects:
            continue
        docs = subjects[sid]["docs"]
        if not any(d.get("path") == rel for d in docs):
            docs.append(row)
        subjects[sid]["sources"] = list(set(subjects[sid]["sources"]) | {"doc"})


def harvest_all_docs(subjects: dict[str, dict]) -> int:
    from sina_command_lib import all_docs_flat  # noqa: WPS433

    n = 0
    for row in all_docs_flat():
        rel = row.get("path", "")
        if not rel:
            continue
        _attach_doc(subjects, rel, row.get("title"))
        n += 1
    # Investor folder (may not all be in SourceA scan if only md under investor/)
    if INVESTOR_DIR.is_dir():
        for p in sorted(INVESTOR_DIR.rglob("*.md")):
            rel = f"investor/{p.relative_to(INVESTOR_DIR).as_posix()}"
            _attach_doc(subjects, rel, p.stem.replace("_", " "))
            n += 1
    return n


def harvest_plans_repos_products(subjects: dict[str, dict]) -> None:
    from sina_command_lib import REPOS_REGISTRY, live_products_registry, parse_repo_plan  # noqa: WPS433

    for spec in REPOS_REGISTRY:
        rid = spec.get("id") or spec.get("name", "")
        tid = REPO_THREADS.get(rid, "THREAD-PORTFOLIO")
        sid = f"subj-{rid}" if f"subj-{rid}" in subjects else tid
        if sid not in subjects:
            subjects[sid] = {**subjects.get(tid, {}), "id": sid}
        subj = subjects[sid]
        subj["repo_id"] = rid
        plan = parse_repo_plan(spec)
        subj["plans"].append({"repo": rid, "plan": plan})
        subj["repos"] = list({*(subj.get("repos") or []), rid})
        subj["links"] = links_for_repo(rid, spec)[:8]
        subj["sources"] = list(set(subj["sources"]) | {"repo", "plan"})

    for p in live_products_registry():
        pid = p.get("id", "")
        tid = p.get("thread", "THREAD-MERGEPACK")
        sid = "subj-form-pdf" if pid == "mergepack-form-pdf" else f"subj-product-{_slug(pid)}"
        if sid not in subjects:
            subjects[sid] = {
                "id": sid,
                "title": p.get("title", pid),
                "category": "Live product",
                "parent_id": tid,
                "status": "active" if p.get("live") else "planned",
                "docs": [],
                "chats": [],
                "orders": [],
                "plans": [],
                "products": [],
                "repos": [],
                "links": links_for_product(pid, p)[:8],
                "topic_tags": [],
                "sources": ["product"],
                "priority_today": pid == "mergepack-form-pdf",
                "drill_kind": "subject",
                "drill_id": sid,
                "hub_tab": "products",
                "tabs": ["products"],
                "asf_thread": tid,
            }
        subj = subjects[sid]
        subj["products"] = [pid]
        if p.get("open_url"):
            subj["products"].append({"id": pid, "url": p["open_url"], "title": p.get("title")})

    for plan_id, node in PLAN_NODES.items():
        tid = node.get("thread", "THREAD-ECOSYSTEM")
        if tid in subjects:
            if plan_id not in subjects[tid]["plan_ids"]:
                subjects[tid]["plan_ids"].append(plan_id)
            subjects[tid]["plans"].append({"id": plan_id, "hook": node.get("hook")})
            subjects[tid]["links"] = links_for_thread(tid)[:10]
            subjects[tid]["sources"] = list(set(subjects[tid]["sources"]) | {"plan"})


def harvest_master_orders(subjects: dict[str, dict]) -> None:
    path = SOURCE_A / "sina-bowl/MASTER_ORDERS.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    sid = "THREAD-ECOSYSTEM"
    for sec in data.get("sections") or []:
        subjects[sid]["orders"].append(
            {
                "section": sec.get("title"),
                "items": [i.get("text") for i in (sec.get("items") or [])[:6]],
            }
        )
    subjects[sid]["sources"] = list(set(subjects[sid]["sources"]) | {"orders"})
    _attach_doc(subjects, "sina-bowl/MASTER_ORDERS.json", "Master orders JSON")
    _attach_doc(subjects, "ASF_MASTER_ORDERS_ORGANIZED_LOCKED_v1.md", "Master orders law")


def harvest_rules(subjects: dict[str, dict]) -> None:
    try:
        from sina_command_lib import rules_registry  # noqa: WPS433

        rr = rules_registry()
        for grp in rr.get("groups") or []:
            for r in grp.get("rules") or []:
                path = r.get("path") or r.get("file") or ""
                if path:
                    _attach_doc(subjects, path, r.get("title") or Path(path).name)
        sid = "THREAD-ECOSYSTEM"
        if sid in subjects:
            subjects[sid]["sources"] = list(set(subjects[sid]["sources"]) | {"rules"})
    except Exception:
        pass


def harvest_registry_hooks(subjects: dict[str, dict]) -> None:
    _attach_doc(subjects, "ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md", "Program threads registry")
    _attach_doc(subjects, "SINA_OS_SSOT_LOCKED.md", "Sina OS SSOT")
    _attach_doc(subjects, "brain-os/system/SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md", "Document sequence")
    _attach_doc(subjects, "brain-os/law/PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md", "Product factory roadmap")
    _attach_doc(subjects, "brain-os/law/SINAAI_ECOSYSTEM_FINAL_STATE_AND_NEXT_PLAN_LOCKED_v1.md", "Ecosystem final state")
    if REGISTRY_MD.is_file():
        text = REGISTRY_MD.read_text(encoding="utf-8", errors="replace")
        for tid in THREAD_NODES:
            if tid in subjects and tid in text:
                subjects[tid]["sources"] = list(set(subjects[tid]["sources"]) | {"registry"})


def harvest_all_transcripts(subjects: dict[str, dict]) -> int:
    if not TRANSCRIPT_ROOT.is_dir():
        return 0
    count = 0
    paths = sorted(TRANSCRIPT_ROOT.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in paths:
        if "subagents" in path.parts:
            continue
        workspace = ""
        for part in path.parts:
            if part == "agent-transcripts":
                idx = path.parts.index(part)
                if idx > 0:
                    workspace = path.parts[idx - 1]
                break
        conv_id = path.parent.name
        msgs: list[str] = []
        user_count = 0
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
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
            if len(text) < 20 or "DEVBRIDGE G1 VERIFY PING" in text:
                continue
            user_count += 1
            msgs.append(text)
        if not msgs:
            continue
        blob = "\n".join(msgs)
        topic_ids = _classify_text(blob)
        primary = WORKSPACE_SUBJECT.get(workspace) or topic_ids[0]
        title = _extract_user_query(msgs[0])[:100]
        if len(title) > 90:
            title = title[:87] + "…"
        chat = {
            "conv_id": conv_id,
            "workspace": workspace,
            "title": title,
            "user_messages": user_count,
            "mtime": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
            "topic_ids": topic_ids,
        }
        chat_id = f"chat-{conv_id[:12]}"
        # Dedicated chat subject (every conversation = visible thread)
        if chat_id not in subjects:
            subjects[chat_id] = {
                "id": chat_id,
                "title": f"Chat · {title[:60]}",
                "category": "Cursor conversation",
                "parent_id": primary,
                "status": "chat",
                "summary": f"{user_count} messages · workspace {workspace or 'unknown'}",
                "docs": [],
                "chats": [chat],
                "orders": [],
                "plans": [],
                "products": [],
                "repos": [],
                "links": [link("hub", "Ecosystem map", url=hub_url("threads"))],
                "topic_tags": topic_ids,
                "sources": ["cursor_transcript"],
                "priority_today": False,
                "drill_kind": "subject",
                "drill_id": chat_id,
                "hub_tab": "threads",
                "tabs": ["threads"],
                "asf_thread": primary,
            }
            count += 1
        for tid in topic_ids:
            if tid not in subjects:
                continue
            if not any(c.get("conv_id") == conv_id for c in subjects[tid]["chats"]):
                subjects[tid]["chats"].append(chat)
            for tag in topic_ids:
                if tag not in subjects[tid]["topic_tags"]:
                    subjects[tid]["topic_tags"].append(tag)
            subjects[tid]["sources"] = list(set(subjects[tid]["sources"]) | {"cursor_transcript"})
    return count


def _finalize_subject(s: dict) -> dict:
    sid = s["id"]
    tid = s.get("asf_thread") or (sid if sid.startswith("THREAD-") else s.get("parent_id", ""))
    if tid and tid.startswith("THREAD-"):
        s["links"] = (s.get("links") or [])[:12] or links_for_thread(tid)[:12]
    if s.get("repo_id"):
        s["links"] = (s.get("links") or [])[:12] or links_for_repo(s["repo_id"])[:12]
    s["stats"] = {
        "docs": len(s.get("docs") or []),
        "chats": len(s.get("chats") or []),
        "plans": len(s.get("plans") or []),
        "orders": len(s.get("orders") or []),
        "products": len(s.get("products") or []),
    }
    s["subtitle"] = (
        f"{s['stats']['docs']} docs · {s['stats']['chats']} chats · "
        f"{s['stats']['plans']} plans"
    )
    if not s.get("summary"):
        s["summary"] = s["subtitle"]
    s["open_tab"] = link("hub", "Open", url=hub_url(s.get("hub_tab") or "threads"))
    return s


def build_ecosystem(*, refresh: bool = False) -> list[dict]:
    if not refresh and CACHE_PATH.is_file():
        try:
            data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            if data.get("subjects"):
                return data["subjects"]
        except json.JSONDecodeError:
            pass
    subjects = _init_subjects()
    harvest_registry_hooks(subjects)
    harvest_rules(subjects)
    harvest_plans_repos_products(subjects)
    harvest_master_orders(subjects)
    doc_n = harvest_all_docs(subjects)
    chat_n = harvest_all_transcripts(subjects)
    rows = [_finalize_subject(s) for s in subjects.values()]
    rows.sort(key=lambda x: (-(x["stats"]["chats"] + x["stats"]["docs"]), x.get("title", "")))
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(
            {
                "built_at": _now(),
                "doc_count": doc_n,
                "chat_count": chat_n,
                "subjects": rows,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return rows


def ecosystem_payload(*, refresh: bool = False, bowl: dict | None = None, ops: list | None = None) -> dict:
    subjects = build_ecosystem(refresh=refresh)
    by_cat: dict[str, list] = {}
    for s in subjects:
        cat = s.get("category") or "Other"
        by_cat.setdefault(cat, []).append(s)
    total_docs = sum(s["stats"]["docs"] for s in subjects)
    total_chats = sum(s["stats"]["chats"] for s in subjects)
    today = [s for s in subjects if s.get("priority_today")]
    # Also surface live ops on MergePack subject
    for o in ops or []:
        if o.get("id") == "MP-SHIP" and "THREAD-MERGEPACK" in subjects:
            pass
    big_picture = [
        "Every LOCKED doc, plan, repo, product, Cursor chat, and ASF thread is a subject node.",
        "Subjects link to docs, chats, plans, orders, and hub tabs — full ecosystem, not just recent messages.",
        f"Totals: {len(subjects)} subjects · {total_docs} doc links · {total_chats} chat links.",
        "Pick one ASF thread per Cursor session; use this map to see everything else connected.",
    ]
    return {
        "ok": True,
        "built_at": _now(),
        "subject_count": len(subjects),
        "doc_links": total_docs,
        "chat_links": total_chats,
        "subjects": subjects,
        "today_subjects": today[:8],
        "by_category": [
            {"category": k, "count": len(v), "subjects": v}
            for k, v in sorted(by_cat.items(), key=lambda x: (-len(x[1]), x[0]))
        ],
        "big_picture": big_picture,
        "tagline": "Full ecosystem map — every topic, doc, chat, plan, and lock connected.",
        "cache_path": str(CACHE_PATH),
    }


def subject_as_thread_card(s: dict) -> dict:
    """Shape for Sina Command thread grid + drill."""
    tid = s.get("asf_thread") or s.get("parent_id") or ""
    return {
        "id": s["id"],
        "title": s["title"],
        "subtitle": s.get("subtitle") or s.get("summary", ""),
        "summary": s.get("summary", ""),
        "thread": tid if isinstance(tid, str) else "",
        "thread_id": tid if isinstance(tid, str) and tid.startswith("THREAD-") else "",
        "category": s.get("category", "Topic"),
        "badge": s.get("status", "active"),
        "status": s.get("status", "active"),
        "accent": "gold" if s.get("priority_today") else ("violet" if s.get("category") == "Cursor conversation" else "blue"),
        "priority_today": bool(s.get("priority_today")),
        "drill_kind": "subject",
        "drill_id": s["id"],
        "hub_tab": s.get("hub_tab") or "threads",
        "stats": s.get("stats") or {},
        "source": ",".join(s.get("sources") or []),
    }


def founder_threads_from_ecosystem(eco: dict) -> dict:
    """Backward-compatible founder_threads payload from ecosystem map."""
    by_cat = []
    full_cards = [subject_as_thread_card(s) for s in eco.get("subjects") or []]
    for block in eco.get("by_category") or []:
        cards = [subject_as_thread_card(s) for s in block.get("subjects") or []]
        by_cat.append({"category": block["category"], "count": block["count"], "threads": cards})
    today_cards = [subject_as_thread_card(s) for s in eco.get("today_subjects") or []]
    return {
        "ok": eco.get("ok", True),
        "built_at": eco.get("built_at"),
        "full_count": eco.get("subject_count", len(full_cards)),
        "today_count": len(today_cards),
        "full": full_cards,
        "today": today_cards,
        "by_category": by_cat,
        "cache_path": eco.get("cache_path"),
        "ecosystem": True,
        "tagline": eco.get("tagline"),
        "big_picture": eco.get("big_picture"),
    }


def today_from_ecosystem(subjects: list[dict], *, bowl: dict | None = None, ops: list | None = None) -> list[dict]:
    """Minimal home list from ecosystem priorities + ops."""
    from founder_threads import today_priorities  # noqa: WPS433

    # Convert ecosystem today subjects to home card shape
    out: list[dict] = []
    seen: set[str] = set()

    def add_card(s: dict) -> None:
        if s["id"] in seen:
            return
        seen.add(s["id"])
        out.append(
            {
                "id": s["id"],
                "title": s["title"],
                "subtitle": s.get("subtitle") or s.get("summary", ""),
                "thread": s.get("asf_thread") or s["id"],
                "accent": "gold" if s.get("priority_today") else "blue",
                "drill_kind": "subject",
                "drill_id": s["id"],
                "badge": s.get("status", "active"),
                "sort": 0 if s.get("priority_today") else 10,
            }
        )

    for s in subjects:
        if s.get("priority_today"):
            add_card(s)
    for row in today_priorities([], bowl=bowl, ops=ops):  # type: ignore[arg-type]
        add_card(
            {
                "id": row["id"],
                "title": row["title"],
                "subtitle": row.get("subtitle", ""),
                "thread": row.get("thread", ""),
                "priority_today": True,
                "status": row.get("badge", "ops"),
                "stats": {"docs": 0, "chats": 0, "plans": 0},
            }
        )
    return out[:8]

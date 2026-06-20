"""Lightweight site guide: search hub tabs + answer founder questions without Terminal."""
from __future__ import annotations

import re
from typing import Any


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower().strip())


def build_site_index(payload: dict | None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in ((payload or {}).get("guides") or {}).get("mandatory_reads", {}).get("items") or []:
        rows.append({
            "kind": "mandatory_read",
            "id": item.get("id", ""),
            "title": f"Mandatory: {item.get('title', '')}",
            "text": item.get("why", ""),
            "tab": "rules",
            "path": item.get("path", ""),
        })
    rows.append({
        "kind": "mandatory_read",
        "id": "incident-stop",
        "title": "Emergency stop",
        "text": "Top bar ⛔ Stop or emergency-stop.sh — hub off, auto-paste blocked",
        "tab": "actions",
    })
    try:
        from hub_essentials_index import NAV_TABS  # noqa: WPS433

        nav_labels = {
            "command": ("Home", "Dashboard — P0, Track, compact reads, quick tiles"),
            "advisor-discussion": (
                "Advisor track",
                "PINNED Advisor track — D1–D4 founder decisions · crisis subjects · live factory/S10 · suppressed docs",
            ),
            "essentials": ("Essentials", "Unified map — every important tab, app, doc — no duplicates"),
            "personal-db": ("Personal DB", "Layer A SSOT — train copy agents"),
            "track": ("Track", "Open commitments — nothing missed"),
            "backlog": ("Backlog", "Audit findings to fix"),
            "today": ("Today", "P0, blockers, KPI, todos"),
            "actions": ("Actions", "One-tap dispatch, ingest, engines — no Terminal"),
            "agent-loop": ("Agent hub", "Private agents — one full page per agent"),
            "incident-room": ("Incident Room", "Weekly agent incidents — share, learn, certify"),
            "conflict-room": ("Conflict Room", "ACE auto-triage — report & keep working"),
            "intelligence": ("Live agents", "OpenRouter / Cursor Cloud / IDE bridge"),
            "semej": ("SEMEJ", "Multi-AI Chrome chain"),
            "track": ("Track", "Open commitments — RUN INBOX path"),
            "threads": ("Ecosystem map", "Threads, docs, chats, repos connected"),
            "work": ("Recent work", "Products & repos — quick cards"),
            "apps": ("Connected Apps", "Prompt OS, engines, Mac Health Guard"),
            "notes": ("Your notes", "Fixes & ideas for Cursor"),
            "ai-advisory": ("AI Advisory", "Golden links + coach"),
            "guide": ("Guide", "Teacher walkthrough"),
            "agents": ("Agents", "Private workspace per agent"),
            "repos": ("Repos", "Per-repo plan and blockers"),
            "daily": ("Daily", "ASF card, bowl, paste prompts"),
            "audio": ("Audio", "Morning brief EN / FA"),
            "products": ("Live products", "Form to PDF, MergePack, VIRLUX"),
            "ecosystem": ("Ecosystem", "Flywheel, L1–L5, KPI trio"),
            "orders": ("Your orders", "Organized founder messages"),
            "hq": ("HQ & team", "Duties & supervision"),
            "fleet": ("Fleet", "Workspaces by lane"),
            "roles": ("Roles", "ASF, lanes, PAIOS, Runtime"),
            "plans": ("Program path", "Duolingo-style steps"),
            "prompt-os": ("Prompt OS", "Five-repo dispatch snapshot"),
            "runtime": ("Runtime", "Telegram workers health"),
            "doc-library": ("Doc library", "Curated laws — deduped index"),
            "sources": ("Sources", "Tier-1 quick links"),
        }
        nav = [(tab, *nav_labels.get(tab, (tab, ""))) for tab in NAV_TABS]
    except Exception:
        nav = [
            ("essentials", "Essentials", "Unified map — every important tab, app, doc"),
            ("personal-db", "Personal DB", "Layer A SSOT for agents"),
            ("track", "Track", "Open commitments — nothing missed"),
            ("command", "Home", "Dashboard — P0, Track, quick tiles"),
        ]
    for tab, title, desc in nav:
        rows.append({"kind": "tab", "id": tab, "title": title, "text": desc, "tab": tab})

    al = (payload or {}).get("agent_loop") or {}
    if al.get("active"):
        rows.append({
            "kind": "loop",
            "id": "loop-active",
            "title": f"Private agent loop round {al.get('round')}/{al.get('max_rounds')}",
            "text": al.get("status_hint") or "Submit round on that agent's Private agents page when Cursor finishes.",
            "tab": "agent-loop",
        })

    for item in (payload or {}).get("audit_backlog", {}).get("items") or []:
        if item.get("category") != "open_gap":
            continue
        rows.append({
            "kind": "audit",
            "id": item.get("id", ""),
            "title": item.get("title", ""),
            "text": item.get("detail", ""),
            "tab": item.get("tab") or "backlog",
        })

    p0 = ((payload or {}).get("command_center") or {}).get("founder", {}).get("p0") or {}
    if p0:
        rows.append({
            "kind": "p0",
            "id": p0.get("id", "P0"),
            "title": p0.get("title", "P0"),
            "text": p0.get("next_action", ""),
            "tab": "today",
        })
    return rows


def _token_in_blob(token: str, blob: str) -> bool:
    """Avoid false matches like 'hi' inside 'hidden'."""
    if len(token) < 3:
        return False
    return re.search(rf"\b{re.escape(token)}\b", blob) is not None


def search_site(query: str, payload: dict | None, *, limit: int = 12) -> list[dict[str, str]]:
    q = _norm(query)
    if not q:
        return []
    index = build_site_index(payload)
    scored: list[tuple[int, dict[str, str]]] = []
    for row in index:
        blob = _norm(f"{row.get('title')} {row.get('text')} {row.get('id')}")
        score = 0
        if len(q) >= 3 and q in blob:
            score += 10
        for token in q.split():
            if _token_in_blob(token, blob):
                score += 3
        if score:
            scored.append((score, row))
    scored.sort(key=lambda x: (-x[0], x[1].get("title", "")))
    return [r for _, r in scored[:limit]]


def answer_site_question(question: str, payload: dict | None) -> dict[str, Any]:
    q = (question or "").strip()
    if not q:
        return {"ok": False, "error": "question required"}

    low = _norm(q)
    hits = search_site(q, payload, limit=6)

    canned = []
    al = (payload or {}).get("agent_loop") or {}

    if re.match(r"^(hi|hello|hey|yo|help|start|howdy)\b", low) or low in ("hi", "hello", "help"):
        canned.append(
            "**Welcome — founder never runs Terminal commands.**\n\n"
            "If an agent needs a shell step, they must give you a **one-tap button** in Sina Command "
            "(usually **Actions** for that repo), not “open Terminal and run …”.\n\n"
            "Quick map:\n"
            "1. **Submit round** — that agent's page under **Private agents** (gold card when loop runs).\n"
            "2. **Repo commands** (checks, open docs) — **Actions** tab.\n"
            "3. **Brief** — top **Brief** only; lane briefs on **Repos**.\n"
            "4. **Refresh** — gold button. **Live** = hub connected."
        )
        if al.get("active"):
            canned.append(
                f"**Your loop is active** — round {al.get('round')}/{al.get('max_rounds')}. "
                "Open that agent under **Private agents** and use **Submit round** when Cursor finishes."
            )

    if re.search(r"where.*submit|submit\s*round|find\s*submit|agent\s*loop|sina_loop|loop\s*stop", low):
        canned.append(
            "**Private agents:** Sidebar group **Private agents** — each agent has its **own page** "
            "(TrustField, 777, Noetfield, …). On that page: governance, private folder, **10 prompts**, "
            "**Start loop**, **Submit round**. Not stacked on Home or one shared tab. No Terminal."
        )
    if re.search(r"what.*brief|brief.*copy|brief\s*button|brief|clipboard|trustfield|copy|paste", low):
        canned.append(
            "**Brief button** (top right) only copies when you tap **Brief** — not when you tap Live, Refresh, "
            "or sidebar links. On **Private agents** pages / **Home** it copies the **universal hub brief**, not a lane "
            "lane prompt. Lane prompts: **Repos** → **Copy lane brief** on a repo card."
        )
    if re.search(r"refresh|live|offline|hub", low):
        canned.append(
            "**Live** pill = server connected. **Refresh** (gold) rebuilds bowl, KPI, loop state. If Offline, "
            "double-click **Sina Command** on Desktop or tap the pill when red."
        )
    if re.search(r"p0|runreceipt|receipt|strategic", low):
        canned.append(
            "**Founder P0: STRATEGIC-SLICE** (execution spine north star). **RunReceipt** is factory parallel only "
            "(THREAD-FACTORY) — run.jsonl + summary.json in workspace runreceipt/. Cite **factory-now** line under FREEZE."
        )
    if re.search(r"trustfield|trust field", low):
        canned.append(
            "**TrustField:** Sidebar → **Private agents** → **TrustField Technologies** (own page) → "
            "**Refresh** → **Start loop with this →**. Open TrustField repo in Cursor. No Terminal."
        )
    if re.search(r"virlux", low):
        canned.append(
            "**VIRLUX:** Sidebar → **Private agents** → **VIRLUX** page → Start loop with a prompt row. "
            "Prompts live in `~/Desktop/VIRLUX/prompts/`. No Terminal."
        )
    if re.search(r"dev bridge|devbridge|wire pack", low):
        canned.append(
            "**AI Dev Bridge:** Sidebar → **Private agents** → **AI Dev Bridge OS** page → Start. "
            "Wire G1/G2/G3 prompts in `~/Desktop/AI Dev Bridge OS/prompts/`. No Terminal."
        )
    if re.search(r"noetfield|noet field", low):
        canned.append(
            "**Noetfield — two agents:** (1) **noetfield_local** = `Noetfield-All-Documents` SSOT. "
            "(2) **noetfield_cloud** = `Desktop/Noetfield` GitHub ship. **Agents** tab → pick the right card → Loop pack. Never mix folders."
        )
    if re.search(r"777|seven77|seven 77", low):
        canned.append(
            "**777 Foundation:** **Agents** tab → **The 777 Foundation** → Open repo / Loop pack. "
            "Gate 0, C3 translation, web deploy — one-tap Actions, not Terminal."
        )
    if re.search(r"private.workspace|agent.workspace|open.private|scratch", low):
        canned.append(
            "**Private agent workspaces:** sidebar **Private agents** → each page is the workspace (10-round loop, submit) — "
            "and **Open repo** (code). TrustField, VIRLUX, Dev Bridge, Noetfield, SEMEJ, MergePack, maintainer — "
            "no Terminal; private dirs under `~/.sina/agent-workspaces/`."
        )
    if re.search(r"intelligence circle|live agent|live advisor|cursor cloud|talk to advisor", low):
        canned.append(
            "**Live agents** tab: OpenRouter API, Cursor Cloud, **Cursor — SinaaiDataBase (this chat)**, SEMEJ when running. "
            "**Ping live agents** checks they are reachable. Messages are **hub ↔ live agent** — not Cursor repo chats. "
            "Per-repo work → **Private agents** sidebar."
        )
    if re.search(r"governance|forbidden|permission|traceability|who may edit", low):
        canned.append(
            "**Governance:** Read `AGENT_GOVERNANCE_INDEX_LOCKED_v1.md` (Sources / Rules). "
            "Each **Private agents** page shows forbidden roots, governance version, and recent trace events. "
            "Logs: `~/.sina/agent-governance-events.jsonl`, agent reports, loop state."
        )
    if re.search(r"agent.report|edit.lock|who.*edit|change.*sina.command|report.*bug", low):
        canned.append(
            "**Edit lock:** Only **ASF** and **SinaaiDataBase** Cursor chat may change Sina Command code (`SourceA`). "
            "All other agents: **Backlog → Agent reports** (or API `POST /api/agent-review` action submit). "
            "Never patch `~/Desktop/SourceA` from TrustField/VIRLUX/other chats."
        )
    if re.search(
        r"advisor\s*track|founder\s*advisor|pending\s*discuss|d1|d2|d3|d4|disposition|015.conduct|crisis\s*table",
        low,
    ):
        ad = (payload or {}).get("founder_advisor_discussion") or {}
        pending = ad.get("pending_decisions") or ad.get("pending_total") or 4
        canned.append(
            f"**Advisor track** — sidebar **Founder → 📌 Advisor track** (2nd item under Home). "
            f"Direct link: `http://127.0.0.1:13020/?tab=advisor-discussion`. "
            f"Also: orange **📌 Advisor track** banner at top of **Home**. "
            f"**{pending}** items pending (D1–D4 decisions + crisis subjects). "
            "Not the same as **AI Advisory** tab (that is upgrade coach)."
        )
    if re.search(r"no terminal|terminal|bash|shell|python3", low):
        canned.append(
            "**Founder law:** Never open Terminal because an agent said so. They must add a **one-tap Action** "
            "in the right tab (e.g. TrustField → **Actions** for wire/Tailscale checks) or run the command themselves. "
            "You only tap: Refresh, Actions, Private agents (per repo), Repos, Live products, Ask."
        )

    lines = canned[:]
    show_hits = bool(hits) and len(low) >= 4 and not re.match(r"^(hi|hello|hey|yo)\b", low)
    if show_hits:
        lines.append("**Matching pages:**")
        for h in hits:
            tab = h.get("tab") or ""
            lines.append(f"- **{h.get('title')}** (`?tab={tab}`) — {h.get('text', '')[:160]}")

    if not lines:
        lines.append(
            "Try: “Where is Submit round?”, “What does Brief copy?”, “How do I refresh?”, "
            "“What is P0 RunReceipt?”"
        )

    return {
        "ok": True,
        "answer": "\n\n".join(lines),
        "hits": hits,
    }

#!/usr/bin/env python3
"""Unified link graph — every entity connects to threads, tabs, URLs, repos, docs."""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlencode

SOURCE_A = Path(__file__).resolve().parents[1]
MONO_ROOT = Path.home() / "Desktop/SinaaiMonoRepo/SinaaiDataBase"
MERGEPACK_ROOT = Path.home() / "Desktop/mergepack"
FORM_TO_PDF_LIVE = "https://frontend-bice-ten-x2gt8cr50b.vercel.app/form-to-pdf"


def hub_url(tab: str | None = None, **query: str) -> str:
    port = int(os.environ.get("SINA_COMMAND_PORT", "13020"))
    base = f"http://127.0.0.1:{port}/"
    if not tab and not query:
        return base
    q: dict[str, str] = {}
    if tab:
        q["tab"] = tab
    q.update({k: str(v) for k, v in query.items() if v is not None})
    return base + "?" + urlencode(q)


def link(kind: str, label: str, **payload: str) -> dict:
    row = {"kind": kind, "label": label}
    row.update(payload)
    return row


# Thread → plans, repos, products, hub tabs, law docs
THREAD_NODES: dict[str, dict] = {
    "THREAD-MERGEPACK": {
        "label": "MergePack · Evidence Factory",
        "plan_ids": ["MERGEPACK-L1"],
        "repo_ids": ["mergepack"],
        "product_ids": ["mergepack-form-pdf", "mergepack-site", "mergepack-api"],
        "role_ids": ["MERGEPACK"],
        "tabs": ["command", "products", "ecosystem", "today", "plans", "apps"],
        "docs": [
            ("MergePack START_HERE", str(MERGEPACK_ROOT / "START_HERE.md"), "abs"),
            ("Program progress", str(MERGEPACK_ROOT / "PROGRAM_PROGRESS.json"), "abs"),
            ("Evidence factory law", "EVIDENCE_FACTORY_LOCKED.md", "src"),
        ],
    },
    "THREAD-FACTORY": {
        "label": "Product factory · RunReceipt P0",
        "plan_ids": ["P0-RUNRECEIPT"],
        "repo_ids": ["sourcea", "hq"],
        "product_ids": [],
        "role_ids": ["ROLE-CURSOR-HQ"],
        "tabs": ["command", "today", "rules", "plans", "fleet"],
        "docs": [
            ("Factory P0 law", "product/PRODUCT_FACTORY_RESCORE_NO_ADS_LOCKED_v1.md", "src"),
            ("Factory roadmap", "brain-os/law/PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md", "src"),
        ],
    },
    "THREAD-WIRE": {
        "label": "DevBridge · phone → Mac",
        "plan_ids": ["M8-WIRE"],
        "repo_ids": ["wire"],
        "product_ids": [],
        "role_ids": ["ROLE-WIRE"],
        "tabs": ["command", "today", "fleet", "apps"],
        "docs": [
            ("Wire lane progress", "brain-os/law/WIRE_LANE_PROGRESS.md", "src"),
            ("Wire + phone", "founder/ASF_WIRE_AND_PHONE.md", "src"),
        ],
        "apps": ["remote-ops"],
    },
    "THREAD-PROMPTOS": {
        "label": "Prompt OS · five-repo dispatch",
        "plan_ids": ["PROMPTOS-DAILY"],
        "repo_ids": ["promptos"],
        "product_ids": [],
        "role_ids": ["ROLE-ORCHESTRATOR"],
        "tabs": ["daily", "prompt-os", "apps", "agents", "repos"],
        "docs": [
            ("ASF daily card", "founder/ASF_DAILY_CARD.md", "src"),
        ],
        "apps": ["promptos-ui", "sina-dispatch", "sina-decide", "sina-run", "sina-status"],
    },
    "THREAD-SUPERBRAIN": {
        "label": "PAIOS · Personal DB / Super Brain",
        "plan_ids": ["SUPERBRAIN-P0"],
        "repo_ids": ["mono", "hq"],
        "product_ids": ["sinaai-mono"],
        "role_ids": ["LANE-2", "PAIOS-4"],
        "tabs": ["personal-db", "repos", "plans", "command"],
        "docs": [
            ("Mono README", str(MONO_ROOT / "README.md"), "abs"),
            ("Chat consolidation", "docs/operational/chat-consolidation-pipeline.md", "mono"),
        ],
        "apps": ["mono-next"],
    },
    "THREAD-PORTFOLIO": {
        "label": "Five company lanes",
        "plan_ids": ["PORTFOLIO"],
        "repo_ids": ["trustfield", "virlux", "noetfield", "seven77"],
        "product_ids": ["virlux-api", "virlux-web", "virlux-app", "trustfield"],
        "role_ids": ["LANE-1", "LANE-3", "LANE-4", "LANE-5"],
        "tabs": ["repos", "agents", "plans", "products", "ecosystem"],
        "docs": [
            ("Global blockers", "GLOBAL_BLOCKERS.json", "src"),
            ("Thread registry", "ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md", "src"),
        ],
    },
    "THREAD-ECOSYSTEM": {
        "label": "Sina OS · Source A law",
        "plan_ids": [],
        "repo_ids": ["sourcea", "hq"],
        "product_ids": [],
        "role_ids": ["ASF", "ROLE-CURSOR-HQ", "ROLE-ARCHITECT"],
        "tabs": ["rules", "guide", "command", "hq", "orders"],
        "docs": [
            ("Sina OS SSOT", "SINA_OS_SSOT_LOCKED.md", "src"),
            ("Command guide", "SINA_COMMAND_GUIDE_LOCKED_v1.md", "src"),
        ],
    },
    "THREAD-CURSOR-OS-PRO": {
        "label": "Cursor OS Pro · App Store lane",
        "plan_ids": ["CURSOR-OS-PRO"],
        "repo_ids": [],
        "product_ids": [],
        "tabs": ["guide", "plans"],
        "docs": [
            ("Parallel boundaries", str(Path.home() / "Desktop/Cursor OS Pro/docs/PARALLEL_LANE_BOUNDARIES.md"), "abs"),
        ],
    },
}

PLAN_NODES: dict[str, dict] = {
    "MERGEPACK-L1": {"thread": "THREAD-MERGEPACK", "hook": str(MERGEPACK_ROOT / "START_HERE.md"), "hook_abs": True},
    "P0-RUNRECEIPT": {"thread": "THREAD-FACTORY", "hook": "product/PRODUCT_FACTORY_RESCORE_NO_ADS_LOCKED_v1.md"},
    "M8-WIRE": {"thread": "THREAD-WIRE", "hook": "brain-os/law/WIRE_LANE_PROGRESS.md"},
    "PROMPTOS-DAILY": {"thread": "THREAD-PROMPTOS", "hook": "founder/ASF_DAILY_CARD.md"},
    "SUPERBRAIN-P0": {"thread": "THREAD-SUPERBRAIN", "hook": "docs/operational/chat-consolidation-pipeline.md", "hook_mono": True},
    "PORTFOLIO": {"thread": "THREAD-PORTFOLIO", "hook": "GLOBAL_BLOCKERS.json"},
    "CURSOR-OS-PRO": {"thread": "THREAD-CURSOR-OS-PRO", "hook_abs": str(Path.home() / "Desktop/Cursor OS Pro/docs/PARALLEL_LANE_BOUNDARIES.md")},
    "INVESTOR": {"thread": "THREAD-ECOSYSTEM", "hook_abs": str(Path.home() / "Desktop/Sina-Investor-Package-FINAL/START_HERE.txt")},
}

OPS_NODES: dict[str, dict] = {
    "MP-SHIP": {
        "thread": "THREAD-MERGEPACK",
        "products": ["mergepack-form-pdf", "mergepack-site"],
        "repos": ["mergepack"],
        "tabs": ["products", "today", "ecosystem"],
    },
    "WIRE-G3": {"thread": "THREAD-WIRE", "repos": ["wire"], "tabs": ["today", "fleet"]},
    "B-001": {
        "thread": "THREAD-ECOSYSTEM",
        "repos": ["trustfield", "mono"],
        "tabs": ["repos", "rules", "today"],
        "docs": ["GLOBAL_BLOCKERS.json", "ARCHITECT_REPORT.yaml"],
    },
}

REPO_ROOTS: dict[str, Path] = {
    "trustfield": Path.home() / "Desktop/TrustField Technologies",
    "mono": Path.home() / "Desktop/SinaaiMonoRepo",
    "virlux": Path.home() / "Desktop/VIRLUX",
    "noetfield": Path.home() / "Desktop/Noetfield All Documents",
    "seven77": Path.home() / "Desktop/The 777 Foundation",
    "mergepack": MERGEPACK_ROOT,
    "wire": Path.home() / "Desktop/AI Dev Bridge OS",
    "promptos": Path.home() / "Desktop/SinaPromptOS",
    "sourcea": SOURCE_A,
    "hq": Path.home() / "Desktop/SinaaiDataBase",
}

REPO_PLAN_REL: dict[str, str] = {
    "trustfield": "os/plan.json",
    "mono": "os/plan.json",
    "virlux": "os/plan.json",
    "noetfield": "noetfield/os/plan.json",
    "seven77": "os/plan.json",
    "mergepack": "PROGRAM_PROGRESS.json",
    "wire": "config/locked_plan.json",
    "promptos": "os/plan.json",
}

REPO_THREADS: dict[str, str] = {
    "trustfield": "THREAD-PORTFOLIO",
    "mono": "THREAD-SUPERBRAIN",
    "virlux": "THREAD-PORTFOLIO",
    "noetfield": "THREAD-PORTFOLIO",
    "seven77": "THREAD-PORTFOLIO",
    "mergepack": "THREAD-MERGEPACK",
    "wire": "THREAD-WIRE",
    "promptos": "THREAD-PROMPTOS",
    "sourcea": "THREAD-ECOSYSTEM",
    "hq": "THREAD-ECOSYSTEM",
}

REPO_EXTRA: dict[str, dict] = {
    "mergepack": {"products": ["mergepack-form-pdf", "mergepack-api"], "plans": ["MERGEPACK-L1"]},
    "virlux": {"products": ["virlux-api", "virlux-web", "virlux-app"], "plans": ["PORTFOLIO"]},
    "trustfield": {"plans": ["PORTFOLIO"]},
    "mono": {"plans": ["SUPERBRAIN-P0"], "apps": ["mono-next"]},
    "wire": {"plans": ["M8-WIRE"], "apps": ["remote-ops"]},
    "promptos": {"plans": ["PROMPTOS-DAILY"], "apps": ["promptos-ui"]},
    "hq": {"plans": ["P0-RUNRECEIPT", "SUPERBRAIN-P0"]},
    "sourcea": {"tabs": ["rules", "guide", "orders"]},
}

APP_URLS: dict[str, str] = {
    "promptos-ui": "http://127.0.0.1:8765",
    "remote-ops": "http://127.0.0.1:8899/t/status",
    "mono-next": "http://127.0.0.1:13022",
    "sina-command": hub_url("command"),
    "mac-health-guard": "http://127.0.0.1:13024/",
    "apple-health": "http://127.0.0.1:13025/",
    "chat-unify": "http://127.0.0.1:13023/",
    "n8n-integration": "http://127.0.0.1:13026/",
}


def _doc_link(title: str, path: str, mode: str) -> dict:
    if mode == "abs":
        return link("abs", title, path=path)
    if mode == "mono":
        return link("mono", title, path=path)
    return link("path", title, path=path)


def _thread_links(thread_id: str, *, limit_tabs: int = 5) -> list[dict]:
    node = THREAD_NODES.get(thread_id) or {}
    out: list[dict] = []
    seen: set[str] = set()

    def push(item: dict) -> None:
        key = f"{item['kind']}:{item.get('tab') or item.get('path') or item.get('url') or item.get('drill_id') or item.get('product_id') or item.get('label')}"
        if key in seen:
            return
        seen.add(key)
        out.append(item)

    push(link("thread", node.get("label") or thread_id, thread_id=thread_id))
    for tab in (node.get("tabs") or [])[:limit_tabs]:
        push(link("tab", f"Hub · {tab.replace('-', ' ').title()}", tab=tab))
    for doc in node.get("docs") or []:
        if len(doc) == 3:
            push(_doc_link(doc[0], doc[1], doc[2]))
    for pid in node.get("plan_ids") or []:
        push(link("drill", f"Plan · {pid}", drill_kind="plan", drill_id=pid))
    for rid in node.get("repo_ids") or []:
        push(link("drill", f"Repo · {rid}", drill_kind="repo", drill_id=rid))
    for prod in node.get("product_ids") or []:
        push(link("product", f"Live · {prod}", product_id=prod))
    for app_id in node.get("apps") or []:
        push(link("app", f"App · {app_id}", app_id=app_id))
    return out


def links_for_thread(thread_id: str) -> list[dict]:
    return _thread_links(thread_id, limit_tabs=6)


def links_for_plan(plan_id: str) -> list[dict]:
    meta = PLAN_NODES.get(plan_id) or {}
    thread = meta.get("thread")
    out: list[dict] = []
    if thread:
        out.extend(_thread_links(thread, limit_tabs=4))
    if meta.get("hook"):
        if meta.get("hook_abs"):
            out.insert(0, link("abs", "Primary doc", path=meta["hook"]))
        elif meta.get("hook_mono"):
            out.insert(0, link("mono", "Primary doc", path=meta["hook"]))
        else:
            out.insert(0, link("path", "Primary doc", path=meta["hook"]))
    out.append(link("tab", "Program path", tab="plans"))
    if plan_id == "MERGEPACK-L1":
        out.insert(0, link("url", "Form to PDF (live)", url=FORM_TO_PDF_LIVE))
    return _dedupe(out)


def links_for_repo(repo_id: str, repo_row: dict | None = None) -> list[dict]:
    root = REPO_ROOTS.get(repo_id)
    if not root and repo_row:
        root = Path(repo_row["root_path"]) if repo_row.get("root_path") else None
    if not root:
        return []
    name = (repo_row or {}).get("name") or repo_id
    extra = REPO_EXTRA.get(repo_id) or {}
    thread = (repo_row or {}).get("thread") or REPO_THREADS.get(repo_id)
    out: list[dict] = [
        link("folder", f"Open {name}", abs_path=str(root)),
    ]
    plan_rel = REPO_PLAN_REL.get(repo_id)
    if plan_rel:
        plan_p = root / plan_rel
        if plan_p.is_file():
            out.append(link("folder", "plan / progress file", abs_path=str(plan_p)))
    if thread:
        out.extend(_thread_links(thread, limit_tabs=3))
    for pid in extra.get("plans") or []:
        out.append(link("drill", f"Plan · {pid}", drill_kind="plan", drill_id=pid))
    for prod in extra.get("products") or []:
        out.append(link("product", f"Product · {prod}", product_id=prod))
    for app_id in extra.get("apps") or []:
        out.append(link("app", f"App · {app_id}", app_id=app_id))
    for tab in extra.get("tabs") or []:
        out.append(link("tab", f"Hub · {tab}", tab=tab))
    if repo_row and repo_row.get("global_blocker"):
        out.append(link("path", "Global blockers", path="GLOBAL_BLOCKERS.json"))
    out.append(link("tab", "All repos", tab="repos"))
    return _dedupe(out)


def links_for_product(product_id: str, product_row: dict | None = None) -> list[dict]:
    out: list[dict] = []
    if product_row:
        if product_row.get("open_url"):
            out.append(link("url", "Open live", url=product_row["open_url"]))
        if product_row.get("local_path"):
            out.append(link("folder", "Repo folder", abs_path=product_row["local_path"]))
        if product_row.get("doc_path"):
            out.append(link("folder", "Start doc", abs_path=product_row["doc_path"]))
        thread = product_row.get("thread")
        if thread:
            out.extend(_thread_links(thread, limit_tabs=3))
        pid = product_row.get("program_id")
        if pid:
            out.append(link("drill", f"Plan · {pid}", drill_kind="plan", drill_id=pid))
    out.append(link("tab", "Live products", tab="products"))
    if product_id == "mergepack-form-pdf":
        out.append(link("drill", "Blocker · MP-SHIP", drill_kind="ops", drill_id="MP-SHIP"))
    return _dedupe(out)


def links_for_ops(ops_id: str) -> list[dict]:
    meta = OPS_NODES.get(ops_id) or {}
    thread = meta.get("thread")
    out: list[dict] = []
    if thread:
        out.extend(_thread_links(thread, limit_tabs=4))
    for prod in meta.get("products") or []:
        out.append(link("product", f"Live · {prod}", product_id=prod))
    for rid in meta.get("repos") or []:
        out.append(link("drill", f"Repo · {rid}", drill_kind="repo", drill_id=rid))
    for tab in meta.get("tabs") or []:
        out.append(link("tab", f"Hub · {tab}", tab=tab))
    for doc in meta.get("docs") or []:
        out.append(link("path", doc, path=doc))
    out.append(link("tab", "Today · blockers", tab="today"))
    return _dedupe(out)


def links_for_app(app_id: str) -> list[dict]:
    out: list[dict] = []
    if app_id in APP_URLS:
        out.append(link("url", "Open UI", url=APP_URLS[app_id]))
    out.append(link("tab", "Connected Apps", tab="apps"))
    if app_id.startswith("sina-"):
        out.append(link("tab", "Prompt OS snapshot", tab="prompt-os"))
        out.extend(_thread_links("THREAD-PROMPTOS", limit_tabs=2))
    if app_id == "remote-ops":
        out.extend(_thread_links("THREAD-WIRE", limit_tabs=2))
    if app_id == "mono-next":
        out.extend(_thread_links("THREAD-SUPERBRAIN", limit_tabs=2))
    if app_id == "sina-command":
        out.extend(_thread_links("THREAD-ECOSYSTEM", limit_tabs=2))
    if app_id in ("apple-health", "mac-health-guard"):
        out.append(link("tab", "Roadmaps & goals", tab="roadmaps"))
    return _dedupe(out)


WORKSPACE_THREADS: dict[str, str] = {
    "SinaaiDataBase": "THREAD-ECOSYSTEM",
    "TrustField Technologies": "THREAD-PORTFOLIO",
    "SinaaiMonoRepo": "THREAD-SUPERBRAIN",
    "Virlux": "THREAD-PORTFOLIO",
    "VIRLUX": "THREAD-PORTFOLIO",
    "Noetfield All Documents": "THREAD-PORTFOLIO",
    "The 777 Foundation": "THREAD-PORTFOLIO",
    "AI Dev Bridge OS": "THREAD-WIRE",
    "mergepack": "THREAD-MERGEPACK",
}


def links_for_agent(workspace: str, agent_row: dict | None = None) -> list[dict]:
    thread = (agent_row or {}).get("thread") or WORKSPACE_THREADS.get(workspace)
    out: list[dict] = []
    if thread:
        out.extend(_thread_links(thread, limit_tabs=4))
    out.append(link("tab", "Fleet", tab="fleet"))
    out.append(link("tab", "Agents", tab="agents"))
    repo_ws = workspace
    if repo_ws:
        out.append(link("drill", f"Repo lane · {repo_ws}", drill_kind="repo", drill_id=_workspace_to_repo_id(repo_ws)))
    return _dedupe(out)


def _workspace_to_repo_id(workspace: str) -> str:
    mapping = {
        "TrustField Technologies": "trustfield",
        "SinaaiMonoRepo": "mono",
        "Virlux": "virlux",
        "VIRLUX": "virlux",
        "Noetfield All Documents": "noetfield",
        "The 777 Foundation": "seven77",
        "AI Dev Bridge OS": "wire",
        "SinaaiDataBase": "hq",
        "mergepack": "mergepack",
    }
    return mapping.get(workspace, workspace.lower().replace(" ", "-")[:24])


def links_for_role(role_id: str) -> list[dict]:
    thread_by_role = {
        "MERGEPACK": "THREAD-MERGEPACK",
        "ROLE-WIRE": "THREAD-WIRE",
        "ROLE-ORCHESTRATOR": "THREAD-PROMPTOS",
        "ROLE-CURSOR-HQ": "THREAD-ECOSYSTEM",
        "LANE-1": "THREAD-PORTFOLIO",
        "LANE-2": "THREAD-SUPERBRAIN",
        "LANE-3": "THREAD-PORTFOLIO",
        "LANE-4": "THREAD-PORTFOLIO",
        "LANE-5": "THREAD-PORTFOLIO",
        "ASF": "THREAD-ECOSYSTEM",
        "PAIOS-4": "THREAD-SUPERBRAIN",
        "RUNTIME": "THREAD-ECOSYSTEM",
    }
    thread = thread_by_role.get(role_id)
    out: list[dict] = [link("tab", "HQ & team", tab="hq"), link("tab", "Roles", tab="roles")]
    if thread:
        out = _thread_links(thread, limit_tabs=4) + out
    return _dedupe(out)


def links_for_duty(_duty_text: str) -> list[dict]:
    return _dedupe(
        [
            link("tab", "Daily card", tab="daily"),
            link("tab", "Command home", tab="command"),
            link("path", "ASF daily card", path="founder/ASF_DAILY_CARD.md"),
            link("tab", "Today", tab="today"),
        ]
    )


def links_for_drill(drill_kind: str, drill_id: str, row: dict | None = None) -> list[dict]:
    if drill_kind == "plan":
        return links_for_plan(drill_id)
    if drill_kind == "repo":
        return links_for_repo(drill_id, row)
    if drill_kind == "product":
        return links_for_product(drill_id, row)
    if drill_kind == "ops":
        return links_for_ops(drill_id)
    if drill_kind == "app":
        return links_for_app(drill_id)
    if drill_kind == "agent":
        return links_for_agent(drill_id, row)
    if drill_kind == "role":
        return links_for_role(drill_id)
    if drill_kind == "duty":
        return links_for_duty(drill_id)
    if drill_kind == "thread":
        return links_for_thread(drill_id)
    return []


def _dedupe(links: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for item in links:
        key = "|".join(f"{k}={item.get(k)}" for k in sorted(item.keys()))
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def thread_index_registry(
    live_products: list[dict],
    repos: list[dict],
) -> list[dict]:
    products_by_id = {p["id"]: p for p in live_products}
    repos_by_id = {r["id"]: r for r in repos}
    rows = []
    for tid, node in THREAD_NODES.items():
        related_products = [
            {**products_by_id[pid], "links": links_for_product(pid, products_by_id.get(pid))}
            for pid in (node.get("product_ids") or [])
            if pid in products_by_id
        ]
        related_repos = [
            {**repos_by_id[rid], "links": links_for_repo(rid, repos_by_id.get(rid))}
            for rid in (node.get("repo_ids") or [])
            if rid in repos_by_id
        ]
        rows.append(
            {
                "id": tid,
                "label": node.get("label") or tid,
                "plan_ids": node.get("plan_ids") or [],
                "repo_ids": node.get("repo_ids") or [],
                "product_ids": node.get("product_ids") or [],
                "links": links_for_thread(tid),
                "related_products": related_products,
                "related_repos": related_repos,
            }
        )
    return rows


def attach_links_to_subjects(subjects: list[dict], live_products: list[dict], repos: list[dict]) -> list[dict]:
    prod_by_id = {p["id"]: p for p in live_products}
    repo_by_id = {r["id"]: r for r in repos}
    for s in subjects:
        kind, did = s.get("drill_kind"), s.get("drill_id")
        row = None
        if kind == "product":
            row = prod_by_id.get(did)
        elif kind == "repo":
            row = repo_by_id.get(did) or repo_by_id.get(_workspace_to_repo_id(did))
        s["links"] = links_for_drill(kind, did, row)
        tid = s.get("thread")
        if tid and tid.startswith("THREAD-"):
            s["thread_links"] = links_for_thread(tid)[:4]
    return subjects

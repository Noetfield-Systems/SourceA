#!/usr/bin/env python3
"""Shared data layer for Sina Command — bowl, fleet, KPI, personal DB."""
from __future__ import annotations

import json
import os
import re
import ssl
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
PANEL_DIR = SOURCE_A / "agent-control-panel"
BOWL_STATE = SOURCE_A / "sina-bowl" / "state.json"
MASTER_ORDERS = SOURCE_A / "sina-bowl" / "MASTER_ORDERS.json"
DRIFT_JSON = SOURCE_A / "sina-bowl" / "DRIFT.json"
PROGRESS = SOURCE_A / "PROGRAM_PROGRESS.json"
MERGEPACK_PROGRESS = Path.home() / "Desktop/mergepack/PROGRAM_PROGRESS.json"
FLEET = SOURCE_A / "data/agent_fleet/AGENT_FLEET_REGISTRY.json"
MONO_DATA = Path.home() / "Desktop/SinaaiMonoRepo/SinaaiDataBase/data"
MONO_ROOT = Path.home() / "Desktop/SinaaiMonoRepo/SinaaiDataBase"
MERGEPACK_KPI_URL = "https://mergepack-api-production.up.railway.app/v1/kpi"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

from founder_notes import add_note as add_founder_note, list_notes, set_note_status  # noqa: E402
from agent_loop import loop_payload  # noqa: E402
from prompt_direction import direction_payload, handle_action as prompt_direction_handle  # noqa: E402
from prompt_queue import handle_action as prompt_queue_handle, queue_payload  # noqa: E402
from sina_link_graph import (  # noqa: E402
    attach_links_to_subjects,
    links_for_agent,
    links_for_app,
    links_for_ops,
    links_for_plan,
    links_for_product,
    links_for_repo,
    links_for_role,
    thread_index_registry,
)

WORKSPACE_META: dict[str, dict] = {
    "SinaaiDataBase": {"thread": "THREAD-ECOSYSTEM", "lane_group": "HQ", "lane": "ROLE-CURSOR-HQ"},
    "TrustField Technologies": {"thread": "THREAD-PORTFOLIO", "lane_group": "Lane 1", "lane": "TrustField"},
    "SinaaiMonoRepo": {"thread": "THREAD-SUPERBRAIN", "lane_group": "Lane 2", "lane": "Mono"},
    "Virlux": {"thread": "THREAD-PORTFOLIO", "lane_group": "Lane 3", "lane": "VIRLUX"},
    "VIRLUX": {"thread": "THREAD-PORTFOLIO", "lane_group": "Lane 3", "lane": "VIRLUX"},
    "Noetfield All Documents": {"thread": "THREAD-PORTFOLIO", "lane_group": "Lane 4", "lane": "Noetfield"},
    "The 777 Foundation": {"thread": "THREAD-PORTFOLIO", "lane_group": "Lane 5", "lane": "777"},
    "AI Dev Bridge OS": {"thread": "THREAD-WIRE", "lane_group": "Wire", "lane": "DevBridge"},
    "Cursor OS Pro": {"thread": "THREAD-CURSOR-OS-PRO", "lane_group": "SKU", "lane": "Cursor OS Pro"},
    "mergepack": {"thread": "THREAD-MERGEPACK", "lane_group": "Utility", "lane": "MergePack"},
    "Wirelux": {"thread": "THREAD-PORTFOLIO", "lane_group": "Lane 3", "lane": "VIRLUX"},
}

HQ_DUTIES_FULL = [
    "Read law first (Source A, thread registry, command center)",
    "Refresh signals (update-program-progress, fleet scan, bowl)",
    "Maintain Source A locks — upgrade when ASF clears blockers",
    "Help Layer A personal database (L0–L4, ingestion)",
    "Implement SKUs when THREAD says (mergepack, wire, deploy)",
    "Organize knowledge (iphone Cloud, _TOPICS, canon)",
    "Coordinate five lanes — notices, no scope bleed",
    "Report fleet + Sina Command + self-audit for ASF",
    "Supervise Cursor subagents only when spawned in HQ session",
    "Never: override Architect, auto-dispatch 5 repos, M8=MP-*, parked growth",
]

ROLES_DETAIL = [
    {"id": "ASF", "title": "Architect / Founder / Supervisor",
     "summary": "Final law, P0 pick, registry edits, drift resolution.",
     "duties": ["Pick one THREAD per chat", "Resolve drift", "Sign off blockers", "Activate growth when ready"]},
    {"id": "ROLE-CURSOR-HQ", "title": "HQ Cursor agent (SinaaiDataBase)",
     "summary": "Cross-repo steward — bowl, Source A, fleet, mono pointers.",
     "duties": ["Keep bowl + panel accurate", "Unify locks when ASF asks", "Never park MergePack growth"]},
    {"id": "ROLE-ARCHITECT", "title": "Permanent Architect",
     "summary": "Read-only diagnosis via ARCHITECT_REPORT.yaml.",
     "duties": ["Surface blockers", "No dispatch", "No plan.json edits"]},
    {"id": "ROLE-ORCHESTRATOR", "title": "SinaPromptOS Orchestrator",
     "summary": "Ranks five repos, ready_to_paste prompts.",
     "duties": ["dispatch-day.sh", "Lane 0 meta only"]},
    {"id": "LANE-1", "title": "TrustField Technologies", "summary": "Delivery lane.", "duties": ["One plan.json task", "B-001 respect"]},
    {"id": "LANE-2", "title": "SinaaiMonoRepo", "summary": "Design — PAIOS, Layer A.", "duties": ["Governance", "Command center home"]},
    {"id": "LANE-3", "title": "VIRLUX", "summary": "Delivery — commerce.", "duties": ["Scoped tasks only"]},
    {"id": "LANE-4", "title": "Noetfield", "summary": "Design — spec.", "duties": ["Spec-first"]},
    {"id": "LANE-5", "title": "The 777 Foundation", "summary": "Delivery — web.", "duties": ["Site per thread"]},
    {"id": "ROLE-WIRE", "title": "DevBridge Wire", "summary": "Phone → Mac M8.", "duties": ["G1/G2/G3", "full_m8"]},
    {"id": "MERGEPACK", "title": "MergePack Evidence Factory", "summary": "L1 events + growth.",
     "duties": ["MP-SHIP MP-PAY", "KPI trio", "SEO/paid when ASF activates"]},
    {"id": "PAIOS-4", "title": "Super Brain", "summary": "Analyst → Brain → CoS → Operator.",
     "duties": ["Brain proposes", "ASF approves"]},
    {"id": "RUNTIME", "title": "SinaaiRuntime", "summary": "Telegram :8000.", "duties": ["Workers health"]},
]


def load_json(path: Path) -> dict | list | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


_MERGEPACK_KPI_CACHE: dict | None = None
_MERGEPACK_KPI_AT: float = 0.0
_MERGEPACK_KPI_TTL_SEC = 300.0
_MASTER_ORDERS_STALE_SEC = 300.0


def fetch_mergepack_kpi() -> dict:
    global _MERGEPACK_KPI_CACHE, _MERGEPACK_KPI_AT
    now = time.monotonic()
    if _MERGEPACK_KPI_CACHE is not None and (now - _MERGEPACK_KPI_AT) < _MERGEPACK_KPI_TTL_SEC:
        return dict(_MERGEPACK_KPI_CACHE)
    out: dict = {"ok": False, "url": MERGEPACK_KPI_URL, "error": None, "data": {}}
    try:
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            ctx = ssl.create_default_context()
        req = urllib.request.Request(MERGEPACK_KPI_URL, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            out["data"] = json.loads(resp.read().decode())
            out["ok"] = True
    except Exception as e:
        out["error"] = str(e)
    _MERGEPACK_KPI_CACHE = out
    _MERGEPACK_KPI_AT = now
    return out


def _maybe_export_master_orders(*, force: bool = False) -> None:
    orders_path = SOURCE_A / "scripts/export-master-orders-json.py"
    if not orders_path.is_file():
        return
    if not force and MASTER_ORDERS.is_file():
        if time.time() - MASTER_ORDERS.stat().st_mtime < _MASTER_ORDERS_STALE_SEC:
            return
    subprocess.run(["python3", str(orders_path)], check=False, cwd=SOURCE_A)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    meta: dict = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"\'')
    return meta


def personal_db_detail() -> dict:
    base = {"path": str(MONO_DATA), "entry_count": 0, "layers": {}, "recent": [], "by_status": {}}
    if not MONO_DATA.is_dir():
        return base
    entries: list[dict] = []
    for path in sorted(MONO_DATA.rglob("*.md")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        meta = parse_frontmatter(text)
        if not meta.get("id"):
            continue
        stat = path.stat()
        layer = path.parent.name if path.parent.name.startswith("L") else "other"
        status = meta.get("status", "unknown")
        entries.append({
            "id": meta.get("id"),
            "title": meta.get("title", path.stem),
            "layer": layer,
            "status": status,
            "access": meta.get("access", ""),
            "path": str(path.relative_to(MONO_ROOT)),
            "updated_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        })
    entries.sort(key=lambda e: e["updated_at"], reverse=True)
    layers: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for e in entries:
        layers[e["layer"]] = layers.get(e["layer"], 0) + 1
        by_status[e["status"]] = by_status.get(e["status"], 0) + 1
    base["entry_count"] = len(entries)
    base["layers"] = layers
    base["by_status"] = by_status
    base["recent"] = entries[:12]
    base["ingestion_spec"] = "data/L0-meta/004-ingestion-pipeline.md"
    base["agent_template"] = "data/L4-agents/"
    return base


def _personal_db_payload() -> dict:
    try:
        from personal_db_ops import personal_db_payload  # noqa: WPS433

        return personal_db_payload()
    except Exception as e:
        out = personal_db_detail()
        out["ok"] = False
        out["error"] = str(e)
        return out


def transcript_verify_hint(jsonl: Path) -> dict:
    hint = {"has_verify": False, "has_thread": False, "thread_guess": None}
    try:
        lines = jsonl.read_text(encoding="utf-8", errors="replace").splitlines()[-80:]
    except OSError:
        return hint
    tail = "\n".join(lines)
    if re.search(r"\bVERIFY\b", tail, re.I):
        hint["has_verify"] = True
    m = re.search(r"Active thread:\s*(THREAD-[A-Z0-9-]+)", tail, re.I)
    if m:
        hint["has_thread"] = True
        hint["thread_guess"] = m.group(1)
    return hint


def enrich_fleet_workspace(ws: dict) -> dict:
    name = ws.get("display_name", "")
    meta = WORKSPACE_META.get(name, {"thread": None, "lane_group": "Other", "lane": "—"})
    ws = {**ws, **meta}
    sessions = []
    for s in ws.get("sessions") or []:
        tid = s.get("transcript_id")
        tr_path = Path(ws.get("path_hint", "")) / "agent-transcripts" / tid / f"{tid}.jsonl"
        vh = transcript_verify_hint(tr_path) if tr_path.is_file() else {}
        sessions.append({**s, "verify": vh})
    ws["sessions"] = sessions
    latest = sessions[0]["verify"] if sessions else {}
    ws["latest_verify"] = latest.get("has_verify", False)
    ws["latest_thread_hint"] = latest.get("thread_guess") or meta.get("thread")
    return ws


def group_fleet(workspaces: list[dict]) -> list[dict]:
    order = ["HQ", "Lane 1", "Lane 2", "Lane 3", "Lane 4", "Lane 5", "Wire", "Utility", "SKU", "Other"]
    groups: dict[str, list] = {g: [] for g in order}
    for ws in workspaces:
        g = ws.get("lane_group", "Other")
        groups.setdefault(g, []).append(ws)
    result = []
    for g in order:
        if groups.get(g):
            result.append({"lane_group": g, "workspaces": groups[g]})
    for g, items in groups.items():
        if g not in order and items:
            result.append({"lane_group": g, "workspaces": items})
    return result


def ops_blockers(progress: dict, wire: dict, mp_prog: dict | None) -> list[dict]:
    cards = []
    ms = (mp_prog or {}).get("milestones") or {}
    mp_ship = ms.get("MP-SHIP", "unknown")
    if mp_ship != "pass":
        cards.append({
            "id": "MP-SHIP",
            "severity": "high",
            "title": "MergePack public ship",
            "action": "Disable Vercel Deployment Protection on frontend project — then verify /health",
            "status": mp_ship,
            "founder_actions": [
                {"id": "founder-open-form-pdf", "label": "Open Form to PDF live"},
                {"id": "founder-verify-mp-health", "label": "Verify MergePack health"},
                {"id": "founder-refresh", "label": "Refresh panel"},
            ],
        })
    if wire.get("g3_tailscale") == "pending":
        cards.append({
            "id": "WIRE-G3",
            "severity": "medium",
            "title": "Wire G3 Tailscale",
            "action": "Run g3 proof + record in WIRE_LANE_PROGRESS.md",
            "status": "pending",
            "founder_actions": [
                {"id": "founder-wire-preflight", "label": "Wire preflight check"},
                {"id": "founder-open-wire-progress", "label": "Open wire progress doc"},
            ],
        })
    for b in (progress.get("signals_auto") or {}).get("architect_blockers") or []:
        if "B-001" in b or "law collision" in b.lower():
            cards.append({
                "id": "B-001",
                "severity": "critical",
                "title": "Active law collision — infra",
                "action": "Resolve TrustField postgres vs no-card infra per GLOBAL_BLOCKERS",
                "status": "open",
                "founder_actions": [
                    {"id": "founder-open-global-blockers", "label": "Open GLOBAL_BLOCKERS"},
                    {"id": "founder-open-architect-report", "label": "Open architect report"},
                ],
            })
            break
    bowl_blockers = (load_json(BOWL_STATE) or {}).get("blockers") or []
    for b in bowl_blockers:
        if b.get("id") == "B-001" and not any(c["id"] == "B-001" for c in cards):
            cards.append({
                "id": "B-001",
                "severity": b.get("severity", "critical"),
                "title": b.get("title", "B-001"),
                "action": "See ARCHITECT_REPORT.yaml and GLOBAL_BLOCKERS.json",
                "status": "open",
                "founder_actions": [
                    {"id": "founder-open-global-blockers", "label": "Open GLOBAL_BLOCKERS"},
                    {"id": "founder-open-architect-report", "label": "Open architect report"},
                ],
            })
    try:
        from live_founder_decision_form_v1 import payload as _form_payload  # noqa: WPS433
        from rt_live_gate_v1 import receipt_pass  # noqa: WPS433

        _form = _form_payload()
        if receipt_pass() and int(_form.get("open_questions_count") or 0) == 0:
            cards.insert(
                0,
                {
                    "id": "PHASE-3-RESUME",
                    "severity": "medium",
                    "title": "Phase 3 integrity resume",
                    "action": "SYS-INTEGRITY-100 index-only · Q-SYS-INTEGRITY-RESUME YES · 3.07 NO",
                    "status": "active",
                    "founder_actions": [
                        {"id": "founder-open-phase3-playbook", "label": "Open Phase 3 playbook"},
                        {"id": "founder-open-integrity-form", "label": "Official form (0 pending)"},
                    ],
                },
            )
            try:
                from w3_outbound_batch_approve_v1 import card_status, hub_card_visible  # noqa: WPS433

                if hub_card_visible() and not card_status().get("founder_approved"):
                    w3 = card_status()
                    cards.insert(
                        0,
                        {
                            "id": "W3-APPROVE-OUTBOUND",
                            "severity": "medium",
                            "title": "Approve outbound batch",
                            "action": w3.get("summary") or "W3 NF outreach — founder one tap before send",
                            "status": w3.get("status") or "dry_run_ready",
                            "founder_actions": [
                                {"id": "founder-approve-outbound-batch", "label": "Approve outbound batch"},
                                {"id": "founder-w3-nf-outreach", "label": "Open W3 workflow spec"},
                            ],
                        },
                    )
            except Exception:
                pass
    except Exception:
        pass
    return cards


def prompt_os_snapshot() -> dict:
    base = PROMPTOS_ROOT
    card = SOURCE_A / "founder/ASF_DAILY_CARD.md"
    repos = [
        ("TrustField", Path.home() / "Desktop/TrustField Technologies/os/plan.json"),
        ("Mono", MONO_ROOT / "noetfield/os/plan.json"),
        ("VIRLUX", Path.home() / "Desktop/Virlux/os/plan.json"),
        ("Noetfield", Path.home() / "Desktop/Noetfield-All-Documents/noetfield/os/plan.json"),
        ("777", Path.home() / "Desktop/The 777 Foundation/os/plan.json"),
    ]
    lanes = []
    for name, p in repos:
        row = {"repo": name, "plan_path": str(p), "exists": p.is_file()}
        if p.is_file():
            data = load_json(p) or {}
            tasks = data.get("tasks") or data.get("queue") or []
            if isinstance(tasks, list) and tasks:
                t0 = tasks[0] if isinstance(tasks[0], dict) else {}
                row["next"] = t0.get("title") or t0.get("text") or str(tasks[0])[:80]
            else:
                row["next"] = data.get("current_focus") or "—"
        lanes.append(row)
    return {
        "daily_card": str(card),
        "daily_card_rel": "founder/ASF_DAILY_CARD.md",
        "daily_card_exists": card.is_file(),
        "lanes": lanes,
    }


def runtime_snapshot() -> dict:
    url = "http://127.0.0.1:8000/health"
    out = {"url": url, "ok": False, "error": None}
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=2) as resp:
            out["ok"] = resp.status == 200
    except Exception as e:
        out["error"] = str(e)
    return {
        "health": out,
        "workers": ["liaison", "chief_of_staff", "analyst", "lead_scout", "operator", "agent_spine"],
        "note": "Telegram Runtime — separate from Cursor",
    }


REPOS_REGISTRY: list[dict] = [
    {"id": "trustfield", "name": "TrustField Technologies", "root_key": "TrustField Technologies",
     "plan_rel": "os/plan.json", "workspace": "TrustField Technologies", "lane": 1,
     "thread": "THREAD-PORTFOLIO", "plane": "DELIVERY", "semantic_key": "trustfield"},
    {"id": "mono", "name": "SinaaiMonoRepo", "root_key": "SinaaiMonoRepo",
     "plan_rel": "os/plan.json", "workspace": "SinaaiMonoRepo", "lane": 2,
     "thread": "THREAD-SUPERBRAIN", "plane": "DESIGN", "semantic_key": "sinaai_mono"},
    {"id": "virlux", "name": "VIRLUX", "root_key": "VIRLUX",
     "plan_rel": "os/plan.json", "workspace": "Virlux", "lane": 3,
     "thread": "THREAD-PORTFOLIO", "plane": "DELIVERY", "semantic_key": "virlux"},
    {"id": "noetfield", "name": "Noetfield", "root_key": "Noetfield-All-Documents",
     "plan_rel": "noetfield/os/plan.json", "workspace": "Noetfield All Documents", "lane": 4,
     "thread": "THREAD-PORTFOLIO", "plane": "DESIGN", "semantic_key": "noetfield"},
    {"id": "seven77", "name": "The 777 Foundation", "root_key": "The 777 Foundation",
     "plan_rel": "os/plan.json", "workspace": "The 777 Foundation", "lane": 5,
     "thread": "THREAD-PORTFOLIO", "plane": "DELIVERY", "semantic_key": "seven77"},
    {"id": "mergepack", "name": "MergePack", "root_key": "mergepack",
     "plan_rel": "PROGRAM_PROGRESS.json", "workspace": None, "lane": "Utility",
     "thread": "THREAD-MERGEPACK", "plane": "L1 Evidence", "semantic_key": None},
    {"id": "wire", "name": "AI Dev Bridge OS", "root_key": "AI Dev Bridge OS",
     "plan_rel": "config/locked_plan.json", "workspace": "AI Dev Bridge OS", "lane": "Wire",
     "thread": "THREAD-WIRE", "plane": "M8 automation", "semantic_key": None},
    {"id": "promptos", "name": "SinaPromptOS", "root_key": "SinaPromptOS",
     "plan_rel": "os/plan.json", "workspace": None, "lane": "Meta",
     "thread": "THREAD-PROMPTOS", "plane": "META", "semantic_key": "sina_prompt_os"},
    {"id": "sourcea", "name": "Source A (SSOT)", "root_key": "SourceA",
     "plan_rel": None, "workspace": None, "lane": "Law",
     "thread": "THREAD-ECOSYSTEM", "plane": "Intelligence", "semantic_key": None},
    {"id": "hq", "name": "SinaaiDataBase HQ", "root_key": "SinaaiDataBase",
     "plan_rel": None, "workspace": "SinaaiDataBase", "lane": "HQ",
     "thread": "THREAD-ECOSYSTEM", "plane": "HQ steward", "semantic_key": None},
]

HIERARCHY: list[dict] = [
    {"level": 0, "id": "ASF", "title": "Founder / final law", "reports_to": None},
    {"level": 1, "id": "ROLE-ARCHITECT", "title": "Permanent Architect", "reports_to": "ASF"},
    {"level": 1, "id": "ROLE-ORCHESTRATOR", "title": "SinaPromptOS Orchestrator", "reports_to": "ASF"},
    {"level": 2, "id": "LANE-1", "title": "TrustField agent", "reports_to": "ROLE-ORCHESTRATOR"},
    {"level": 2, "id": "LANE-2", "title": "Mono agent", "reports_to": "ROLE-ORCHESTRATOR"},
    {"level": 2, "id": "LANE-3", "title": "VIRLUX agent", "reports_to": "ROLE-ORCHESTRATOR"},
    {"level": 2, "id": "LANE-4", "title": "Noetfield agent", "reports_to": "ROLE-ORCHESTRATOR"},
    {"level": 2, "id": "LANE-5", "title": "777 agent", "reports_to": "ROLE-ORCHESTRATOR"},
    {"level": 1, "id": "ROLE-CURSOR-HQ", "title": "HQ steward (cross-repo)", "reports_to": "ASF"},
    {"level": 1, "id": "ROLE-WIRE", "title": "DevBridge wire", "reports_to": "ASF"},
    {"level": 1, "id": "MERGEPACK", "title": "MergePack utility", "reports_to": "ASF"},
    {"level": 1, "id": "RUNTIME", "title": "PAIOS Runtime :8000", "reports_to": "ASF"},
]


def _repo_root(spec: dict) -> Path:
    if spec["root_key"] == "SourceA":
        return SOURCE_A
    return Path.home() / "Desktop" / spec["root_key"]


def _repo_doing_now(plan: dict) -> str | None:
    tasks = plan.get("next_tasks") or []
    if not tasks:
        return plan.get("active_focus")
    first = tasks[0]
    if isinstance(first, dict):
        return (
            first.get("text")
            or first.get("task")
            or first.get("description")
            or first.get("title")
            or plan.get("active_focus")
        )
    return str(first)


def parse_repo_plan(spec: dict) -> dict:
    root = _repo_root(spec)
    plan_path = root / spec["plan_rel"] if spec.get("plan_rel") else None
    out = {
        "plan_path": str(plan_path) if plan_path else None,
        "plan_exists": plan_path.is_file() if plan_path else False,
        "active_focus": None,
        "next_tasks": [],
        "done": [],
        "blocked": [],
        "updated_at": None,
        "last_verify": None,
    }
    if not plan_path or not plan_path.is_file():
        return out
    data = load_json(plan_path) or {}
    out["updated_at"] = data.get("updated_at")
    if spec["id"] == "mergepack":
        out["active_focus"] = data.get("product", "Evidence Factory")
        out["next_tasks"] = [{"text": x} for x in (data.get("next_actions") or [])]
        ms = data.get("milestones") or {}
        out["done"] = [k for k, v in ms.items() if v is True]
        out["blocked"] = [k for k, v in ms.items() if v is False and k.startswith("MP-")]
        return out
    if spec["id"] == "wire":
        wp = data.get("wire_proof") or {}
        out["active_focus"] = data.get("current_phase")
        out["next_tasks"] = [{"text": f"Close g3: {wp.get('g3_tailscale')}"}] if wp.get("g3_tailscale") == "pending" else []
        return out
    out["active_focus"] = data.get("active_focus") or data.get("current_focus")
    nt = data.get("next_tasks") or []
    if isinstance(nt, list):
        out["next_tasks"] = [x if isinstance(x, dict) else {"text": str(x)} for x in nt[:8]]
    out["done"] = (data.get("done") or [])[-6:] if isinstance(data.get("done"), list) else []
    out["blocked"] = data.get("blocked") or []
    out["last_verify"] = data.get("last_verify")
    return out


def repos_registry() -> list[dict]:
    semantic = load_json(SOURCE_A / "SEMANTIC_PROGRESS.json") or {}
    repos_sem = semantic.get("repos") or {}
    global_blk = load_json(SOURCE_A / "GLOBAL_BLOCKERS.json") or {}
    blockers_by_id = {b.get("project_id"): b for b in global_blk.get("blockers") or []}

    rows = []
    for spec in REPOS_REGISTRY:
        root = _repo_root(spec)
        plan = parse_repo_plan(spec)
        sk = spec.get("semantic_key")
        sem = repos_sem.get(sk, {}) if sk else {}
        blk = blockers_by_id.get(sk) or blockers_by_id.get(spec["id"])
        row = {
            **spec,
            "root_path": str(root),
            "root_exists": root.is_dir(),
            **plan,
            "semantic_progress": sem.get("semantic_progress"),
            "semantic_meaning": sem.get("meaning"),
            "evaluator_verdict": (sem.get("signals") or {}).get("evaluator_verdict"),
            "global_blocker": blk,
            "doing_now": _repo_doing_now(plan),
        }
        row["links"] = links_for_repo(spec["id"], row)
        rows.append(row)
    return rows


def _workspace_active_24h(ws: dict) -> bool:
    now = datetime.now(timezone.utc)
    for s in ws.get("sessions") or []:
        iso = s.get("updated_at")
        if not iso:
            continue
        try:
            ts = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            if (now - ts).total_seconds() < 86400:
                return True
        except ValueError:
            pass
    return False


def agents_registry(workspaces: list[dict]) -> list[dict]:
    role_by_lane = {
        "HQ": "ROLE-CURSOR-HQ",
        "Lane 1": "LANE-1", "Lane 2": "LANE-2", "Lane 3": "LANE-3",
        "Lane 4": "LANE-4", "Lane 5": "LANE-5",
        "Wire": "ROLE-WIRE", "Utility": "MERGEPACK", "SKU": "CURSOR-OS-PRO",
    }
    repos = {r["workspace"]: r for r in repos_registry() if r.get("workspace")}
    agents = []
    for ws in workspaces:
        name = ws.get("display_name", "")
        role_id = role_by_lane.get(ws.get("lane_group", ""), "—")
        role = next((r for r in ROLES_DETAIL if r["id"] == role_id), None)
        latest = (ws.get("sessions") or [{}])[0]
        repo = repos.get(name, {})
        not_done = []
        if not ws.get("latest_verify"):
            not_done.append("Last session missing VERIFY block")
        if repo.get("next_tasks"):
            not_done.append(f"Repo next: {len(repo['next_tasks'])} task(s)")
        if repo.get("blocked"):
            not_done.append(f"Repo blocked: {len(repo['blocked'])}")
        done_signals = []
        if ws.get("latest_verify"):
            done_signals.append("VERIFY in latest session")
        if repo.get("done"):
            done_signals.append(f"{len(repo['done'])} items in plan done")
        agent_row = {
            "workspace": name,
            "role_id": role_id,
            "role_title": role["title"] if role else ws.get("lane", "—"),
            "job": role["summary"] if role else ws.get("lane_group"),
            "duties": role.get("duties", []) if role else [],
            "thread": ws.get("thread") or ws.get("latest_thread_hint"),
            "last_active": ws.get("last_active"),
            "active_24h": _workspace_active_24h(ws),
            "doing_now": latest.get("preview", "")[:160],
            "session_count": ws.get("session_count", 0),
            "done_signals": done_signals,
            "not_done": not_done,
            "repo_name": repo.get("name"),
            "repo_next": (repo.get("next_tasks") or [{}])[0].get("text") if repo.get("next_tasks") else None,
            "repo_id": repo.get("id"),
        }
        agent_row["links"] = links_for_agent(name, agent_row)
        agents.append(agent_row)
    agents.sort(key=lambda a: (not a["active_24h"], a.get("last_active") or ""), reverse=True)
    return agents


SOURCEA_NO_ASF_REGISTRY = SOURCE_A / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"
_NO_ASF_SKIP_SNIPPETS = (
    "Founder-only:",
    "Founder:",
    "founder Action",
    "founder/lanes:",
    "Wire lane:",
    "TrustField:",
)


def _sa_plan_agent_runnable(title: str) -> bool:
    t = title or ""
    return not any(s.lower() in t.lower() for s in _NO_ASF_SKIP_SNIPPETS)


def _iter_sa_backlog_picks(plans: list, *, limit: int = 1) -> list[dict]:
    from sourcea_pick_lib import pick_backlog_plans

    return pick_backlog_plans(
        plans,
        tiers=("T0", "T1", "T2", "T3"),
        limit=limit,
        order="phase-first",
    )


def _next_sa_pick() -> dict | None:
    """Live PLAN WITH NO ASF pick — same rules as pick-sourcea-no-asf-plan.py."""
    if not SOURCEA_NO_ASF_REGISTRY.is_file():
        return None
    try:
        data = json.loads(SOURCEA_NO_ASF_REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    rows = _iter_sa_backlog_picks(data.get("plans") or [], limit=1)
    return rows[0] if rows else None


def _sa_queue_row(pl: dict) -> dict:
    rel = pl.get("path") or ""
    abs_path = str(SOURCE_A / "os" / "plan-library" / "sourcea-1000" / rel) if rel else ""
    return {
        "id": pl.get("id"),
        "title": pl.get("title"),
        "tier": pl.get("tier"),
        "path": rel,
        "abs_path": abs_path,
        "verify": pl.get("verify"),
        "agent_prompt": pl.get("agent_prompt"),
    }


def sync_sa_queue_into_payload(payload: dict) -> dict:
    """Refresh sourcea_sa_queue + founder P0 live pick on an existing hub payload (sa-0076 align)."""
    sq = sourcea_sa_queue_payload()
    payload["sourcea_sa_queue"] = sq
    try:
        from worker_drain_lib import healthy_queue_status  # noqa: WPS433

        hq = healthy_queue_status()
        payload["healthy_drain_rail"] = hq
    except Exception:
        payload["healthy_drain_rail"] = {"ok": False}
    try:
        import subprocess

        proc = subprocess.run(
            [
                sys.executable,
                str(SOURCE_A / "scripts" / "healthy-drain-orchestrator-v1.py"),
                "status",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(SOURCE_A),
        )
        payload["healthy_drain_orchestrator"] = (
            json.loads(proc.stdout) if proc.returncode == 0 else {"ok": False}
        )
    except Exception:
        payload["healthy_drain_orchestrator"] = {"ok": False}
    cc = payload.get("command_center") or {}
    founder = cc.get("founder") or {}
    p0 = founder.get("p0") or {}
    live = sq.get("live_pick") or {}
    hq = payload.get("healthy_drain_rail") or {}
    orch = payload.get("healthy_drain_orchestrator") or {}
    orch_brief = orch.get("brief")
    hq_brief = hq.get("brief") if hq.get("ok") else None
    brief = orch_brief or hq_brief
    live_id = str(live.get("id") or "")
    live_title = (live.get("title") or "")[:72] if live.get("id") else None
    try:
        from founder_p0_next_action_v1 import build_founder_p0_next_action  # noqa: WPS433

        p0["next_action"] = build_founder_p0_next_action(
            queue_brief=brief,
            live_pick_id=live_id if live_id.startswith("sa-") else None,
            live_pick_title=live_title,
        )
    except Exception:
        p0["next_action"] = (
            f"FREEZE · Safety guard active · queue {live_id}"
            if live_id.startswith("sa-")
            else "FREEZE · Safety guard active · agent-submit forbidden"
        )
    founder["p0"] = p0
    cc["founder"] = founder
    payload["command_center"] = cc
    return payload


def sourcea_sa_queue_payload(*, up_next_limit: int = 8) -> dict:
    """Hub sa-queue tab — live pick + backlog counts."""
    if not SOURCEA_NO_ASF_REGISTRY.is_file():
        return {"ok": False, "error": "REGISTRY missing", "schema": "sourcea-sa-queue-v1"}
    try:
        data = json.loads(SOURCEA_NO_ASF_REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc), "schema": "sourcea-sa-queue-v1"}
    plans = data.get("plans") or []
    backlog = sum(1 for p in plans if p.get("status") == "backlog")
    try:
        import sys as _sys

        _sys.path.insert(0, str(SOURCE_A / "scripts"))
        from registry_honest_lib_v1 import audit_registry_done  # noqa: WPS433

        audit = audit_registry_done()
        done = audit["honest_done"]
        raw_done = audit["raw_done"]
        unproven = audit["unproven_done"]
    except Exception:
        done = sum(1 for p in plans if p.get("status") == "done")
        raw_done = done
        unproven = 0
    picks = _iter_sa_backlog_picks(plans, limit=up_next_limit)
    fallback = picks[0] if picks else None
    try:
        from queue_sa_pick_lib_v1 import live_pick_aligned  # noqa: WPS433

        live = live_pick_aligned(plans, fallback_pick=fallback)
        if live and picks and live.get("id") != picks[0].get("id"):
            rest = [p for p in picks if p.get("id") != live.get("id")]
            picks = [live] + rest
    except Exception:
        live = fallback
    p0 = founder_automation_p0({"p0": {"id": "STRATEGIC-SLICE"}})
    return {
        "ok": True,
        "schema": "sourcea-sa-queue-v1",
        "counts": {
            "total": len(plans),
            "done": done,
            "honest_done": done,
            "raw_done": raw_done,
            "unproven_done": unproven,
            "backlog": backlog,
        },
        "live_pick": _sa_queue_row(live) if live else None,
        "up_next": [_sa_queue_row(p) for p in picks[1:]],
        "p0": {"id": p0.get("id"), "next_action": p0.get("next_action")},
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def _forge_factory_era_active() -> bool:
    """True when FORGE FACTORY cycle2 is the live execution clock."""
    try:
        era_path = SOURCE_A / "data" / "factory-era-v1.json"
        if era_path.is_file():
            era = json.loads(era_path.read_text(encoding="utf-8"))
            if era.get("current_era") == "forge_factory_cycle2":
                return True
        fn_path = Path.home() / ".sina" / "factory-now-v1.json"
        if fn_path.is_file():
            fn = json.loads(fn_path.read_text(encoding="utf-8"))
            return str(fn.get("mode") or "") == "FORGE_FACTORY"
    except Exception:
        pass
    return False


def founder_automation_p0(bowl: dict) -> dict:
    """Hub founder card — strategic slice + live sa pick; RunReceipt is parallel factory only."""
    pick = _next_sa_pick()
    factory_p0 = bowl.get("factory_parallel") or bowl.get("p0") or {}
    if factory_p0.get("id") == "STRATEGIC-SLICE":
        factory_p0 = bowl.get("runreceipt_parallel") or {}
    pick_id = pick.get("id") if pick else "—"
    pick_title = (pick.get("title") or "See SOURCEA-PRIORITY.md")[:72] if pick else "See SOURCEA-PRIORITY.md"
    brief = None
    try:
        from worker_drain_lib import healthy_queue_status  # noqa: WPS433

        hq = healthy_queue_status()
        if hq.get("ok") and hq.get("brief"):
            brief = hq["brief"]
    except Exception:
        pass
    try:
        from founder_p0_next_action_v1 import build_founder_p0_next_action  # noqa: WPS433

        next_action = build_founder_p0_next_action(
            queue_brief=brief,
            live_pick_id=pick_id if str(pick_id).startswith("sa-") else None,
            live_pick_title=pick_title if pick else None,
        )
    except Exception:
        next_action = f"FREEZE · tap Safety · Live pick: {pick_id} — {pick_title}"
    if _forge_factory_era_active():
        return {
            "id": "FORGE-FACTORY-CYCLE2",
            "thread": "FORGE-FACTORY",
            "title": "FORGE FACTORY cycle2 — Goal 3 active · commercial P0 parallel",
            "status": "active",
            "priority": 1,
            "phase": "forge-factory-cycle2",
            "next_action": next_action,
            "hook": "data/forge-factory-unified-brand-v1.json",
            "runreceipt_parallel": {
                "id": factory_p0.get("id"),
                "thread": factory_p0.get("thread"),
                "title": factory_p0.get("title"),
                "note": "Goal 1 archived · Goal 2 merged · factory parallel when ASF names THREAD-FACTORY",
            },
        }
    return {
        "id": "STRATEGIC-SLICE",
        "thread": "STRATEGIC-SLICE",
        "title": "Execution spine — WTM strategic slice (not RunReceipt north star)",
        "status": "active",
        "priority": 1,
        "phase": "T4 spine",
        "next_action": next_action,
        "hook": "brain-os/system/GOAL_HIERARCHY_LOCKED_v1.md",
        "runreceipt_parallel": {
            "id": factory_p0.get("id"),
            "thread": factory_p0.get("thread"),
            "title": factory_p0.get("title"),
            "note": "Factory parallel only — THREAD-FACTORY when ASF names it",
        },
    }


def _must_do_today_lines(bowl: dict) -> list[str]:
    duties = list((bowl.get("asf_duties") or [])[:6])
    try:
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        form = live_form_payload()
        oq = int(form.get("open_questions_count") or 0)
        if oq > 0:
            return [
                f"Official form — {oq} open PICKs logged · M1 Canvas · INCIDENT-037 block ON",
                "Form agent-submit forbidden · founder supremacy guard active",
            ]
    except Exception:
        pass
    try:
        from founder_p0_next_action_v1 import rt_live_gate_active  # noqa: WPS433

        if rt_live_gate_active():
            from rt_live_gate_v1 import receipt_pass  # noqa: WPS433

            if receipt_pass():
                open_q = 0
                try:
                    open_q = int(live_form_payload().get("open_questions_count") or 0)
                except Exception:
                    pass
                lines = [
                    "ENFORCEMENT W1 film · W3 NF outreach · FR-003 wired",
                    "Phase 3 index-only · 3.07 NO · 9.07 A ship order locked",
                ]
                if open_q:
                    lines.append(
                        f"Official form — {open_q} open PICKs logged · M1 Canvas · INCIDENT-037 block ON"
                    )
                else:
                    lines.append("Form clear · 0 open PICKs · INCIDENT-037 guard ON")
                return lines
            return [
                "RT LIVE gate OPEN · hub repair-only · FR-003 wired",
                "Safety guard active · factory background only",
                "Form FILLED logged · RT LIVE receipt pending",
            ]
    except Exception:
        pass
    return duties


def founder_playbook(bowl: dict, ops: list[dict], progress: dict) -> dict:
    asf_todos = [t for t in (progress.get("todos") or bowl.get("open_todos") or []) if t.get("owner") == "ASF" and t.get("status") == "open"]
    return {
        "p0": founder_automation_p0(
            {
                **bowl,
                "factory_parallel": bowl.get("factory_parallel")
                or next(
                    (p for p in (bowl.get("parallel_plans") or []) if p.get("id") == "P0-RUNRECEIPT"),
                    None,
                ),
            }
        ),
        "must_do_today": _must_do_today_lines(bowl),
        "ops_cards": ops,
        "asf_todos": asf_todos,
        "drift": bowl.get("drift") or [],
        "open_todos_all": bowl.get("open_todos") or [],
    }


PROMPTOS_ROOT = Path.home() / "Desktop/SinaPromptOS"
PROMPTOS_PASTE = PROMPTOS_ROOT / "outputs/ready_to_paste"
DOC_DENY_NAMES = frozenset({"SECRETS_VAULT.md", ".env", ".DS_Store"})
# UI experiments quarantined outside SourceA — never index in hub/rules scan
DOC_SKIP_PARTS = frozenset({
    ".git", "node_modules", "agent-control-panel",
    "sourcea-site-v1",
})


def _doc_category(rel: str) -> str:
    r = rel.lower()
    if r.startswith("founder/") or "daily_card" in r:
        return "daily"
    if r.startswith("sina-bowl/"):
        return "bowl"
    if r.startswith("product/"):
        return "product"
    if "locked" in r or r.startswith("sina_os") or "ssot" in r:
        return "law"
    if "agent" in r or "prompt_os" in r or "architect" in r:
        return "agents"
    return "spec"


def resolve_doc_path(rel: str) -> tuple[Path, str] | None:
    if not rel or ".." in rel:
        return None
    if rel.startswith("promptos:"):
        sub = rel[9:].lstrip("/")
        p = (PROMPTOS_ROOT / sub).resolve()
        root = PROMPTOS_ROOT.resolve()
        if root != p and root not in p.parents:
            return None
        return p, rel
    p = (SOURCE_A / rel).resolve()
    root = SOURCE_A.resolve()
    if root != p and root not in p.parents:
        return None
    if p.name in DOC_DENY_NAMES:
        return None
    return p, rel


def _doc_row(rel: str, title: str | None = None, root: str = "sourcea") -> dict:
    resolved = resolve_doc_path(rel if root == "promptos" else rel)
    if not resolved:
        return {"path": rel, "title": title or rel, "exists": False, "root": root}
    p, key = resolved
    return {
        "path": key,
        "title": title or p.name.replace("_", " ").replace(".md", ""),
        "exists": p.is_file(),
        "updated_at": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
        if p.is_file() else None,
        "size": p.stat().st_size if p.is_file() else 0,
        "category": _doc_category(rel.replace("promptos:", "")),
    }


def all_docs_flat() -> list[dict]:
    rows: list[dict] = []
    if SOURCE_A.is_dir():
        for p in sorted(SOURCE_A.rglob("*")):
            if not p.is_file():
                continue
            if p.suffix.lower() not in (".md", ".txt", ".json", ".yaml", ".yml"):
                continue
            if any(x in p.parts for x in DOC_SKIP_PARTS):
                continue
            if "quarantine" in p.as_posix().lower():
                continue
            rel = p.relative_to(SOURCE_A).as_posix()
            if p.name in DOC_DENY_NAMES:
                continue
            rows.append(_doc_row(rel))
    if PROMPTOS_PASTE.is_dir():
        for p in sorted(PROMPTOS_PASTE.glob("*.txt")):
            rel = f"promptos:outputs/ready_to_paste/{p.name}"
            repo = p.name.replace("ready_to_paste_", "").replace(".txt", "")
            rows.append({
                **_doc_row(rel, f"Agent daily · {repo}", "promptos"),
                "category": "agent_daily",
                "repo_id": repo,
            })
    return rows


def rules_registry(*, slim_for_hub: bool = True) -> dict:
    flat = all_docs_flat()
    if slim_for_hub:
        flat = [
            {"path": r["path"], "title": r["title"], "category": r.get("category"), "exists": r.get("exists")}
            for r in flat
        ]
    groups: dict[str, list] = {
        "law": [], "product": [], "daily": [], "bowl": [], "agent_daily": [], "agents": [], "spec": [],
    }
    for row in flat:
        cat = row.get("category") or "spec"
        groups.setdefault(cat, []).append(row)
    return {"flat": flat, "groups": [
        {"id": "law", "title": "Law & locks", "docs": groups.get("law", [])},
        {"id": "daily", "title": "Daily · ASF", "docs": groups.get("daily", [])},
        {"id": "bowl", "title": "Bowl & brief", "docs": groups.get("bowl", [])},
        {"id": "agent_daily", "title": "Agent daily cards (paste prompts)", "docs": groups.get("agent_daily", [])},
        {"id": "product", "title": "Product factory", "docs": groups.get("product", [])},
        {"id": "agents", "title": "Agents & automation", "docs": groups.get("agents", [])},
        {"id": "spec", "title": "Specs & other", "docs": groups.get("spec", [])},
    ], "total": len(flat)}


def sources_registry(bowl: dict) -> dict:
    tier1 = bowl.get("tier1_links") or []
    extra = [
        {"label": "ASF daily card", "path": "founder/ASF_DAILY_CARD.md"},
        {"label": "Daily bowl", "path": "sina-bowl/DAILY_BOWL.md"},
        {"label": "Bowl state", "path": "sina-bowl/state.json"},
        {"label": "Program progress", "path": "PROGRAM_PROGRESS.json"},
        {"label": "Drift", "path": "sina-bowl/DRIFT.json"},
        {"label": "Document registry", "path": "brain-os/system/SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md"},
        {"label": "Agent governance index", "path": "brain-os/law/AGENT_GOVERNANCE_INDEX_LOCKED_v1.md"},
        {"label": "Private agent workspaces law", "path": "brain-os/law/SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md"},
        {"label": "Sina Command edit lock", "path": "archive/legacy/sina-command/SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md"},
        {"label": "Agents blueprint", "path": "brain-os/law/SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md"},
    ]
    seen = set()
    links = []
    for item in tier1 + extra:
        p = item.get("path", "")
        if p in seen:
            continue
        seen.add(p)
        links.append({**item, "editable": resolve_doc_path(p) is not None})
    return {"tier1": links, "all_docs_count": len(all_docs_flat())}


def daily_hub_payload(bowl: dict) -> dict:
    asf_card = SOURCE_A / "founder/ASF_DAILY_CARD.md"
    bowl_md = SOURCE_A / "sina-bowl/DAILY_BOWL.md"
    founder_docs = []
    founder_dir = SOURCE_A / "founder"
    if founder_dir.is_dir():
        for p in sorted(founder_dir.glob("*.md")):
            founder_docs.append({
                "path": f"founder/{p.name}",
                "title": p.stem.replace("_", " "),
                "exists": True,
            })
    agent_cards = []
    repos = [
        ("trustfield", "TrustField"),
        ("sinaai_mono", "Mono"),
        ("virlux", "VIRLUX"),
        ("noetfield", "Noetfield"),
        ("seven77", "777"),
    ]
    for repo_id, label in repos:
        fname = f"ready_to_paste_{repo_id}.txt"
        p = PROMPTOS_PASTE / fname
        preview = ""
        if p.is_file():
            preview = p.read_text(encoding="utf-8", errors="replace")[:500]
        agent_cards.append({
            "repo_id": repo_id,
            "label": label,
            "path": f"promptos:outputs/ready_to_paste/{fname}",
            "exists": p.is_file(),
            "preview": preview,
            "updated_at": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
            if p.is_file() else None,
        })
    return {
        "asf_daily_card": {
            "path": "founder/ASF_DAILY_CARD.md",
            "exists": asf_card.is_file(),
            "preview": asf_card.read_text(encoding="utf-8", errors="replace")[:800] if asf_card.is_file() else "",
        },
        "daily_bowl": {
            "path": "sina-bowl/DAILY_BOWL.md",
            "exists": bowl_md.is_file(),
            "preview": bowl_md.read_text(encoding="utf-8", errors="replace")[:600] if bowl_md.is_file() else "",
        },
        "asf_duties": bowl.get("asf_duties") or [],
        "roles_glance": bowl.get("roles_glance") or [],
        "founder_docs": founder_docs,
        "agent_cards": agent_cards,
        "dispatch_action_id": "pos-dispatch",
    }


def read_rule(rel: str) -> dict:
    resolved = resolve_doc_path(rel)
    if not resolved:
        return {"ok": False, "error": "path not allowed"}
    p, key = resolved
    if not p.is_file():
        return {"ok": False, "error": "file missing"}
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"ok": False, "error": "binary file"}
    return {"ok": True, "path": key, "content": text}


def write_rule(rel: str, content: str) -> dict:
    resolved = resolve_doc_path(rel)
    if not resolved:
        return {"ok": False, "error": "path not allowed"}
    p, key = resolved
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"ok": True, "path": key, "updated_at": datetime.now(timezone.utc).isoformat()}


# MONO_ROOT (Layer A tree) stays defined at module top — do not reassign here.
MONO_REPO_ROOT = Path.home() / "Desktop/SinaaiMonoRepo"
DESKTOP_ROOT = Path.home() / "Desktop"


def _tcp_alive(port: int, host: str = "127.0.0.1") -> bool:
    import socket
    try:
        with socket.create_connection((host, port), timeout=0.4):
            return True
    except OSError:
        return False


def _ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _http_alive(url: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=1.5, context=_ssl_context()) as resp:
            return resp.status == 200
    except Exception:
        return False


def _url_reachable(url: str, timeout: float = 4.0) -> bool:
    """HEAD/GET for live product links (200–399 = up)."""
    if not url:
        return False
    ctx = _ssl_context()
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "SinaCommand/1.0"})
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return resp.status < 400
        except Exception:
            continue
    return False


MERGEPACK_ROOT = Path.home() / "Desktop/mergepack"
VIRLUX_ROOT = Path.home() / "Desktop/VIRLUX"
TRUSTFIELD_ROOT = Path.home() / "Desktop/TrustField Technologies"
NOETFIELD_ROOT = Path.home() / "Desktop/Noetfield All Documents"
SEVEN77_ROOT = Path.home() / "Desktop/The 777 Foundation"

# Canonical live URLs — do not drop from Command (ASF reminder 2026-06-04)
FORM_TO_PDF_LIVE = "https://frontend-bice-ten-x2gt8cr50b.vercel.app/form-to-pdf"


def live_products_registry() -> list[dict]:
    """Shipped / in-progress products with live URLs + local repo links."""
    mp = load_json(MERGEPACK_PROGRESS) or {}
    mp_urls = mp.get("urls") or {}
    form_url = mp_urls.get("form_to_pdf") or FORM_TO_PDF_LIVE
    ui_base = (mp_urls.get("ui") or "https://frontend-the-777-foundation.vercel.app").rstrip("/")
    api_base = (mp_urls.get("api") or "https://mergepack-api-production.up.railway.app").rstrip("/")

    items = [
        {
            "id": "mergepack-form-pdf",
            "title": "MergePack · Form to PDF",
            "subtitle": "Live — quote → branded PDF (your ship URL)",
            "program_id": "MERGEPACK-L1",
            "thread": "THREAD-MERGEPACK",
            "accent": "green",
            "category": "revenue",
            "open_url": form_url,
            "local_path": str(MERGEPACK_ROOT),
            "doc_path": str(MERGEPACK_ROOT / "START_HERE.md"),
            "next_action": (mp.get("next_actions") or ["Chase KPI trio"])[0],
        },
        {
            "id": "mergepack-site",
            "title": "MergePack · Marketing UI",
            "subtitle": "Home, pricing, FAQ, SEO pages",
            "program_id": "MERGEPACK-L1",
            "thread": "THREAD-MERGEPACK",
            "accent": "green",
            "category": "revenue",
            "open_url": ui_base,
            "local_path": str(MERGEPACK_ROOT / "frontend"),
            "doc_path": str(MERGEPACK_ROOT / "docs/_TOPICS/08-deploy-ready/DEPLOY_READY.md"),
        },
        {
            "id": "mergepack-api",
            "title": "MergePack · API",
            "subtitle": "Railway — KPI, Stripe, evidence ledger",
            "program_id": "MERGEPACK-L1",
            "thread": "THREAD-MERGEPACK",
            "accent": "green",
            "category": "revenue",
            "open_url": f"{api_base}/health",
            "local_path": str(MERGEPACK_ROOT / "backend"),
            "doc_path": str(MERGEPACK_ROOT / "EVIDENCE_FACTORY_LOCKED.md"),
        },
        {
            "id": "virlux-api",
            "title": "VIRLUX · API",
            "subtitle": "Vercel — health, auth, meta",
            "program_id": "PORTFOLIO",
            "thread": "THREAD-PORTFOLIO",
            "accent": "blue",
            "category": "portfolio",
            "open_url": "https://virlux-api.vercel.app/health",
            "local_path": str(VIRLUX_ROOT),
            "doc_path": str(VIRLUX_ROOT / "docs/LIVE-DEPLOY-RUNBOOK.md"),
        },
        {
            "id": "virlux-web",
            "title": "VIRLUX · Marketing",
            "subtitle": "Live pilot marketing site",
            "program_id": "PORTFOLIO",
            "thread": "THREAD-PORTFOLIO",
            "accent": "blue",
            "category": "portfolio",
            "open_url": "https://virlux-web.vercel.app",
            "local_path": str(VIRLUX_ROOT / "apps/web"),
            "doc_path": str(VIRLUX_ROOT / "docs/LIVE-DEPLOY-RUNBOOK.md"),
        },
        {
            "id": "virlux-app",
            "title": "VIRLUX · Dashboard",
            "subtitle": "Live pilot app UI",
            "program_id": "PORTFOLIO",
            "thread": "THREAD-PORTFOLIO",
            "accent": "blue",
            "category": "portfolio",
            "open_url": "https://virlux-app.vercel.app",
            "local_path": str(VIRLUX_ROOT / "apps/app"),
            "doc_path": str(VIRLUX_ROOT / "os/plan.json"),
        },
        {
            "id": "trustfield",
            "title": "TrustField Technologies",
            "subtitle": "Lane 1 — local repo + deploy docs",
            "program_id": "PORTFOLIO",
            "thread": "THREAD-PORTFOLIO",
            "accent": "violet",
            "category": "portfolio",
            "open_url": None,
            "local_path": str(TRUSTFIELD_ROOT),
            "doc_path": str(TRUSTFIELD_ROOT / "docs/DEPLOY_VERCEL_CLOUDFLARE.md"),
        },
        {
            "id": "sinaai-mono",
            "title": "Sinaai PAIOS (MonoRepo)",
            "subtitle": "Layer A · Personal DB · Super Brain",
            "program_id": "SUPERBRAIN-P0",
            "thread": "THREAD-SUPERBRAIN",
            "accent": "violet",
            "category": "platform",
            "open_url": None,
            "local_path": str(MONO_ROOT),
            "doc_path": str(MONO_ROOT / "README.md"),
        },
        {
            "id": "noetfield",
            "title": "Noetfield",
            "subtitle": "Lane 4 — design plane",
            "program_id": "PORTFOLIO",
            "thread": "THREAD-PORTFOLIO",
            "accent": "violet",
            "category": "portfolio",
            "open_url": None,
            "local_path": str(NOETFIELD_ROOT),
            "doc_path": str(NOETFIELD_ROOT / "os/plan.json"),
        },
        {
            "id": "seven77",
            "title": "777 Foundation",
            "subtitle": "Lane 5 — delivery",
            "program_id": "PORTFOLIO",
            "thread": "THREAD-PORTFOLIO",
            "accent": "violet",
            "category": "portfolio",
            "open_url": None,
            "local_path": str(SEVEN77_ROOT),
            "doc_path": str(SEVEN77_ROOT / "os/plan.json"),
        },
        {
            "id": "wire-devbridge",
            "title": "AI Dev Bridge OS (Wire)",
            "subtitle": "M8 automation — phone → Mac",
            "program_id": "M8-WIRE",
            "thread": "THREAD-WIRE",
            "accent": "blue",
            "category": "wire",
            "open_url": None,
            "local_path": str(Path.home() / "Desktop/AI Dev Bridge OS"),
            "doc_path": str(SOURCE_A / "brain-os/law/WIRE_LANE_PROGRESS.md"),
        },
    ]
    for row in items:
        row["live"] = _url_reachable(row["open_url"]) if row.get("open_url") else None
        row["links"] = links_for_product(row["id"], row)
    return items


def mini_apps_catalog() -> list[dict]:
    """Real side apps + engine commands — not Desktop folder shortcuts."""
    hub = "http://127.0.0.1:13020"
    return [
        {
            "id": "sina-command",
            "title": "Sina Command",
            "subtitle": "This hub — control center",
            "type": "hub",
            "accent": "gold",
            "port": 13020,
            "open_url": hub,
            "hub_link": f"{hub}/?tab=command",
            "desktop": "Sina Command.command",
            "launch": None,
        },
        {
            "id": "mac-health-guard",
            "title": "Mac Health Guard",
            "subtitle": "Local scan only · official Apple guides · data stays on Mac",
            "type": "ui",
            "accent": "blue",
            "port": 13024,
            "open_url": "http://127.0.0.1:13024/",
            "hub_link": "http://127.0.0.1:13024/",
            "desktop": "Mac Health Guard.app",
            "launch": None,
        },
        {
            "id": "apple-health",
            "title": "Apple Health",
            "subtitle": "Wellness · sleep · goals · standalone :13025",
            "type": "standalone",
            "accent": "green",
            "port": 13025,
            "open_url": "http://127.0.0.1:13025/",
            "hub_link": "http://127.0.0.1:13025/",
            "desktop": "Apple Health.app",
            "launch": {
                "kind": "nohup",
                "cwd": str(SOURCE_A),
                "argv": ["bash", str(SOURCE_A / "scripts/serve-apple-health.sh")],
                "log": str(Path.home() / ".sina/apple-health-server.log"),
            },
        },
        {
            "id": "sourcea-monitor",
            "title": "SourceA Monitor",
            "subtitle": "Pre-sleep · queue · receipts · Apple Health sensor",
            "type": "ui",
            "accent": "gold",
            "port": 13021,
            "open_url": "http://127.0.0.1:13021/monitor",
            "hub_link": "http://127.0.0.1:13021/",
            "desktop": None,
            "launch": {
                "kind": "nohup",
                "cwd": str(SOURCE_A),
                "argv": ["python3", str(SOURCE_A / "scripts" / "dashboard_server_v1.py")],
                "log": str(Path.home() / ".sina" / "dashboard.log"),
            },
        },
        {
            "id": "chat-unify",
            "title": "Chat Unify",
            "subtitle": "Standalone mini app · :13023 · no hub required",
            "type": "standalone",
            "accent": "violet",
            "port": 13023,
            "open_url": "http://127.0.0.1:13023/",
            "hub_link": "http://127.0.0.1:13023/",
            "desktop": "Chat Unify.app",
            "launch": {
                "kind": "nohup",
                "cwd": str(SOURCE_A),
                "argv": ["bash", str(SOURCE_A / "scripts/serve-chat-unify.sh")],
                "log": str(Path.home() / ".sina/chat-unify-server.log"),
            },
        },
        {
            "id": "n8n-integration",
            "title": "N8N Integration",
            "subtitle": "Automation spine · standalone :13026",
            "type": "standalone",
            "accent": "green",
            "port": 13026,
            "open_url": "http://127.0.0.1:13026/",
            "hub_link": "http://127.0.0.1:13026/",
            "desktop": "N8N Integration.app",
            "launch": {
                "kind": "nohup",
                "cwd": str(SOURCE_A),
                "argv": ["bash", str(SOURCE_A / "scripts/serve-n8n-integration.sh")],
                "log": str(Path.home() / ".sina/n8n-integration-server.log"),
            },
        },
        {
            "id": "promptos-ui",
            "title": "Prompt OS UI",
            "subtitle": "Streamlit app — ecosystem, lanes, feedback",
            "type": "ui",
            "accent": "blue",
            "port": 8765,
            "open_url": "http://127.0.0.1:8765",
            "hub_link": hub,
            "desktop": "Sina Prompt OS.command",
            "launch": {
                "kind": "nohup",
                "cwd": str(PROMPTOS_ROOT),
                "argv": ["bash", str(SOURCE_A / "scripts/founder-start-promptos.sh")],
                "log": str(Path.home() / ".sina/mini-app-promptos-ui.log"),
            },
        },
        {
            "id": "mono-next",
            "title": "Mono Command (Next.js)",
            "subtitle": "PWA-style panel in monorepo",
            "type": "ui",
            "accent": "violet",
            "port": 13022,
            "open_url": "http://127.0.0.1:13022",
            "hub_link": hub,
            "desktop": None,
            "launch": {
                "kind": "nohup",
                "cwd": str(MONO_ROOT / "command-center"),
                "argv": ["npm", "run", "dev"],
                "log": str(Path.home() / ".sina/mini-app-mono-next.log"),
            },
        },
        {
            "id": "promptos-remote",
            "title": "Prompt OS Remote HTTP",
            "subtitle": "iPhone one-click · port 8899",
            "type": "ui",
            "accent": "blue",
            "port": 8899,
            "open_url": "http://127.0.0.1:8899/t/status",
            "hub_link": hub,
            "desktop": None,
            "launch": {
                "kind": "nohup",
                "cwd": str(PROMPTOS_ROOT),
                "argv": ["bash", "scripts/start-remote-ops.sh"],
                "log": str(Path.home() / ".sina/mini-app-remote-ops.log"),
            },
        },
        {
            "id": "sina-dispatch",
            "title": "Sina Dispatch",
            "subtitle": "Engine: refresh 5-repo paste prompts",
            "type": "engine",
            "accent": "blue",
            "port": None,
            "open_url": None,
            "hub_link": f"{hub}/?tab=apps&run=pos-dispatch",
            "desktop": "Sina Dispatch.command",
            "launch": {"kind": "one_click", "action": "dispatch"},
        },
        {
            "id": "sina-execute",
            "title": "Sina Execute All",
            "subtitle": "Engine: full execute cycle",
            "type": "engine",
            "accent": "blue",
            "port": None,
            "open_url": None,
            "hub_link": f"{hub}/?tab=apps&run=pos-execute",
            "desktop": "Sina Execute All.command",
            "launch": {"kind": "one_click", "action": "execute"},
        },
        {
            "id": "sina-decide",
            "title": "Sina Decide",
            "subtitle": "Engine: decision pass",
            "type": "engine",
            "accent": "blue",
            "port": None,
            "open_url": None,
            "hub_link": f"{hub}/?tab=apps&run=pos-decide",
            "desktop": "Sina Decide.command",
            "launch": {"kind": "one_click", "action": "decide"},
        },
        {
            "id": "sina-run",
            "title": "Sina Run Now",
            "subtitle": "Engine: run cycle",
            "type": "engine",
            "accent": "blue",
            "port": None,
            "open_url": None,
            "hub_link": f"{hub}/?tab=apps&run=pos-run",
            "desktop": "Sina Run Now.command",
            "launch": {"kind": "one_click", "action": "run"},
        },
        {
            "id": "sina-status",
            "title": "Sina Status",
            "subtitle": "Engine: status report",
            "type": "engine",
            "accent": "blue",
            "port": None,
            "open_url": None,
            "hub_link": f"{hub}/?tab=apps&run=pos-status",
            "desktop": "Sina Status.command",
            "launch": {"kind": "one_click", "action": "status"},
        },
        {
            "id": "n8n",
            "title": "n8n Workflows",
            "subtitle": "External glue · :5678 · starter Telegram→Runtime test",
            "type": "automation",
            "accent": "green",
            "port": 5678,
            "open_url": "http://127.0.0.1:5678",
            "hub_link": f"{hub}/?tab=apps",
            "desktop": None,
            "launch": {
                "kind": "nohup",
                "cwd": str(SOURCE_A),
                "argv": ["bash", str(SOURCE_A / "scripts/founder-start-n8n.sh")],
                "log": str(Path.home() / ".sina/n8n.log"),
            },
        },
    ]


def mini_apps_registry() -> list[dict]:
    apps = []
    for spec in mini_apps_catalog():
        port = spec.get("port")
        if spec["id"] == "mac-health-guard":
            running = _tcp_alive(spec.get("port") or 13024)
        elif spec["id"] == "apple-health":
            running = _tcp_alive(spec.get("port") or 13025)
        elif spec["id"] == "chat-unify":
            running = _tcp_alive(spec.get("port") or 13023)
        elif spec["id"] == "n8n-integration":
            running = _tcp_alive(spec.get("port") or 13026)
        elif port:
            running = _tcp_alive(port)
        else:
            running = spec["type"] == "hub"
        if spec["id"] == "sina-command":
            running = True
        app_row = {**spec, "running": running}
        app_row["links"] = links_for_app(spec["id"])
        apps.append(app_row)
    return apps


def launch_mini_app(app_id: str) -> dict:
    spec = next((a for a in mini_apps_catalog() if a["id"] == app_id), None)
    if not spec:
        return {"ok": False, "error": f"unknown app: {app_id}"}
    launch = spec.get("launch")
    if not launch:
        if spec.get("open_url"):
            subprocess.run(["open", spec["open_url"]], check=False)
            return {"ok": True, "message": "Opened", "open_url": spec["open_url"]}
        return {"ok": False, "error": "nothing to launch"}

    kind = launch.get("kind")
    if kind == "one_click":
        result = run_branch_action(f"pos-{launch['action']}")
        result["open_url"] = spec.get("hub_link") or "http://127.0.0.1:13020/?tab=apps"
        result["stay_in_hub"] = True
        return result
    if kind == "terminal_ui":
        started = launch_mini_app("promptos-ui")
        return started if started.get("ok") else {
            "ok": False,
            "error": "Prompt OS start failed — use Connected Apps → Start & open",
        }
    if kind == "nohup":
        cwd = Path(launch["cwd"])
        log = Path(launch.get("log", Path.home() / ".sina/mini-app.log"))
        log.parent.mkdir(parents=True, exist_ok=True)
        if spec.get("port") and _tcp_alive(spec["port"]):
            subprocess.run(["open", spec["open_url"]], check=False)
            return {"ok": True, "message": "Already running", "open_url": spec["open_url"]}
        argv = launch["argv"]
        with open(log, "a", encoding="utf-8") as lf:
            subprocess.Popen(
                argv,
                cwd=cwd,
                stdout=lf,
                stderr=lf,
                start_new_session=True,
            )
        return {
            "ok": True,
            "message": f"Starting {spec['title']}…",
            "open_url": spec.get("open_url"),
            "log": str(log),
        }
    return {"ok": False, "error": f"unsupported launch: {kind}"}


def open_live_product(product_id: str) -> dict:
    spec = next((p for p in live_products_registry() if p["id"] == product_id), None)
    if not spec:
        return {"ok": False, "error": f"unknown product: {product_id}"}
    url = spec.get("open_url")
    if url:
        subprocess.run(["open", url], check=False)
        return {"ok": True, "open_url": url, "message": f"Opened {spec['title']}"}
    local = spec.get("local_path")
    if local:
        p = Path(local).expanduser()
        if p.is_dir():
            subprocess.run(["open", str(p)], check=False)
            return {"ok": True, "message": f"Opened folder {spec['title']}"}
    return {"ok": False, "error": "no URL or local path for this product"}


def open_mini_app(app_id: str) -> dict:
    spec = next((a for a in mini_apps_catalog() if a["id"] == app_id), None)
    if not spec:
        prod = next((p for p in live_products_registry() if p["id"] == app_id), None)
        if prod:
            return open_live_product(app_id)
        return {"ok": False, "error": f"unknown app: {app_id}"}
    port = spec.get("port")
    if port and not _tcp_alive(port):
        started = launch_mini_app(app_id)
        if not started.get("ok"):
            return started
    url = spec.get("open_url") or spec.get("hub_link")
    if not url:
        return launch_mini_app(app_id)
    subprocess.run(["open", url], check=False)
    return {"ok": True, "open_url": url, "message": f"Opened {spec['title']}"}


def _integrity_canvas_action_hint() -> str:
    """Live form open count — nerve-routed canvas (gather pack vs M1)."""
    try:
        from form_official_canvas_route_v1 import hub_canvas_target  # noqa: WPS433

        return str(hub_canvas_target().get("hint") or "")
    except Exception:
        return "FORM_OFFICIAL · cite form_official_canvas_route_v1.py --json"


def founder_actions_flat() -> list[dict]:
    """Every founder command — one tap in the app, no Terminal."""
    ingest_repos = [
        ("trustfield", "TrustField"),
        ("sinaai_mono", "Mono"),
        ("virlux", "VIRLUX"),
        ("noetfield", "Noetfield"),
        ("seven77", "777"),
    ]
    rows: list[dict] = [
        {
            "id": "founder-emergency-stop",
            "title": "Emergency stop",
            "icon": "⛔",
            "kind": "emergency_stop",
            "group": "emergency",
            "danger": True,
            "hint": "Stops hub :13020, all auto-paste, remote_ops — force exit",
        },
        {"id": "founder-refresh", "title": "Refresh panel", "icon": "↻", "kind": "refresh", "group": "hub"},
        {
            "id": "founder-open-secret-vault",
            "title": "Open secret vault",
            "icon": "🔑",
            "kind": "shell",
            "group": "hub",
            "cwd": str(Path.home()),
            "argv": ["open", "-e", str(Path.home() / ".sina" / "secrets.env")],
            "hint": "Vault keys · Voyage configured (P05 done) · edit only to rotate · never paste in chat",
        },
        {
            "id": "founder-brain-sync-monitor",
            "title": "Fix Brain sync (monitor ↺)",
            "icon": "🧠",
            "kind": "brain_sync_monitor",
            "group": "hub",
            "hint": "Sync brain snapshot to live Valid YES — fixes Brain PEND on green rows + dual_proof GAP",
        },
        {
            "id": "founder-cursor-research-mode",
            "title": "Chrome research mode (stop Cursor pop)",
            "icon": "🌐",
            "kind": "cursor_research_mode",
            "group": "hub",
            "hint": "Toggle: stops auto-run from forcing Cursor on top while you research in Chrome",
        },
        {
            "id": "founder-enforcement-k1",
            "title": "K1 enforcement kernel",
            "icon": "⛨",
            "kind": "shell",
            "group": "hub",
            "cwd": str(SOURCE_A),
            "argv": ["bash", "scripts/validate-enforcement-kernel-v1.sh", "--quick"],
            "hint": "K1 tamper-on-read + critic boot — PASS/BLOCK on hub read",
        },
        {
            "id": "founder-ecosystem-safety",
            "title": "Ecosystem safety check",
            "icon": "🛡",
            "kind": "ecosystem_safety",
            "group": "hub",
            "hint": "Factory lock · hub :13020 · monitor truth · INBOX sync · lane wiring · P0 bundle",
        },
        {
            "id": "founder-anti-staleness-check",
            "title": "Anti-staleness check",
            "icon": "🧊",
            "kind": "anti_staleness_check",
            "group": "hub",
            "hint": "Full anti-staleness bundle — hub P0 · spawn gate · bowl · brain sync",
        },
        {
            "id": "founder-run-governance-demo",
            "title": "Run governance demo (5-min)",
            "icon": "⚖",
            "kind": "shell",
            "group": "hub",
            "cwd": str(SOURCE_A),
            "argv": ["bash", "scripts/demo-enforcement-5min-v1.sh"],
            "hint": "ENFORCEMENT-6MO — Copilot BLOCK · ALLOW · tamper FAIL · P-001",
        },
        {
            "id": "founder-factory-stop",
            "title": "Factory STOP (FREEZE)",
            "icon": "⏹",
            "kind": "factory_stop",
            "group": "emergency",
            "danger": True,
            "hint": "Write stop receipt · kill flag ON · no drain spawn until bounded ASF resume",
        },
        {
            "id": "founder-ecosystem-fix-all",
            "title": "Fix ecosystem (full repair)",
            "icon": "🔁",
            "kind": "ecosystem_fix_all",
            "group": "hub",
            "hint": "Unstick · deliver · hygiene · fast ladder · safety PASS (~2 min) — then RUN INBOX",
        },
        {
            "id": "founder-sync-agent-skills",
            "title": "Sync agent skills to Cursor",
            "icon": "◎",
            "kind": "shell",
            "group": "hub",
            "argv": ["bash", "scripts/sync-cursor-agent-skills.sh"],
            "cwd": str(SOURCE_A),
            "hint": "Installs agent-skills → ~/.cursor/skills/sina-* + SourceA/.cursor/skills",
        },
        {"id": "founder-restart-hub", "title": "Restart hub", "icon": "⌂", "kind": "restart_hub", "group": "hub"},
        {
            "id": "founder-restart-rebuild-worker",
            "title": "Restart rebuild worker",
            "icon": "⚙",
            "kind": "restart_rebuild_worker",
            "group": "hub",
            "hint": "Restart :13030 queue consumer (~5s) — no Terminal",
        },
        {
            "id": "founder-enqueue-spine-bridge",
            "title": "Enqueue eval spine bridge",
            "icon": "⛓",
            "kind": "enqueue_eval_spine_bridge",
            "group": "hub",
            "hint": "Eval-1b gate + spine-smoke-echo proof — founder confirm",
        },
        {
            "id": "founder-runreceipt-pack",
            "title": "Build RunReceipt pack",
            "icon": "📦",
            "kind": "runreceipt_pack",
            "group": "hub",
        },
        {"id": "founder-rebuild-bowl", "title": "Rebuild daily bowl", "icon": "☀", "kind": "shell", "group": "daily",
         "cwd": str(SOURCE_A), "argv": ["python3", "scripts/build-sina-daily-bowl.py"]},
        {"id": "founder-rebuild-ecosystem-map", "title": "Rebuild ecosystem map", "icon": "◇", "kind": "shell",
         "group": "hub", "cwd": str(SOURCE_A / "scripts"),
         "argv": ["python3", "-c", "from ecosystem_subjects import build_ecosystem; build_ecosystem(refresh=True); print('OK')"]},
        {"id": "pos-dispatch", "title": "Morning dispatch", "icon": "📤", "kind": "one_click", "action": "dispatch", "group": "daily"},
        {"id": "pos-status", "title": "Full status report", "icon": "📊", "kind": "one_click", "action": "status", "group": "daily"},
        {"id": "pos-decide", "title": "Decide next", "icon": "🎯", "kind": "one_click", "action": "decide", "group": "engines"},
        {"id": "pos-run", "title": "Run now", "icon": "▶", "kind": "one_click", "action": "run", "group": "engines"},
        {"id": "pos-execute", "title": "Execute all", "icon": "⚡", "kind": "one_click", "action": "execute", "group": "engines"},
        {"id": "founder-brief-en", "title": "Play brief (English)", "icon": "♪", "kind": "brief", "lang": "en", "group": "audio"},
        {"id": "founder-brief-fa", "title": "Play brief (فارسی)", "icon": "♪", "kind": "brief", "lang": "fa", "group": "audio"},
        {"id": "founder-ai-advisory", "title": "Run AI advisory", "icon": "✦", "kind": "ai_advisory", "group": "coach"},
        {"id": "founder-intelligence-brief", "title": "Intelligence Circle brief", "icon": "◎", "kind": "intelligence_brief", "group": "coach"},
        {"id": "founder-intelligence-keepalive", "title": "Ping live agents", "icon": "⟳", "kind": "intelligence_keepalive", "group": "coach"},
        {"id": "founder-semej-install", "title": "Install SEMEJ browser tools", "icon": "🌐", "kind": "shell",
         "cwd": str(SOURCE_A / "scripts"), "argv": ["bash", "install-semej-deps.sh"], "group": "coach"},
        {"id": "founder-semej-chrome", "title": "Start Chrome for SEMEJ", "icon": "🌐", "kind": "semej_chrome", "group": "coach"},
        {
            "id": "founder-open-m1-canvas",
            "title": "Official founder form",
            "icon": "◆",
            "kind": "open",
            "group": "law",
            "path": str(Path.home()),  # resolved at runtime via form_official_canvas_route_v1
            "hint": "Subject · Question · A/B/C/D — hub /form/",
        },
        {
            "id": "founder-open-integrity-form",
            "title": "Official founder form",
            "icon": "◆",
            "kind": "open",
            "group": "law",
            "path": str(Path.home()),  # resolved at runtime via form_official_canvas_route_v1
            "hint": _integrity_canvas_action_hint(),
        },
        {
            "id": "founder-open-phase3-playbook",
            "title": "Phase 3 playbook",
            "icon": "📋",
            "kind": "open",
            "group": "integrity",
            "path": str(SOURCE_A / "brain-os/law/SOURCEA_SYSTEM_INTEGRITY_100_STEP_PLAYBOOK_LOCKED_v1.md"),
            "hint": "Q-SYS-INTEGRITY-RESUME YES · index-only · 3.07 NO GOV_UNIFY",
        },
        {
            "id": "founder-w1-film-checklist",
            "title": "W1 film checklist",
            "icon": "🎬",
            "kind": "open",
            "group": "enforcement",
            "path": str(
                SOURCE_A / "archive/attachments/2026-06-12/enf-0303-W1-film-take-1-package_LOCKED_v1.md"
            ),
            "hint": "W1 take 1 witness PASS · ASF screen record → package folder",
        },
        {
            "id": "founder-w1-film-witness",
            "title": "Run W1 witness script",
            "icon": "▶",
            "kind": "shell",
            "group": "enforcement",
            "cwd": str(SOURCE_A),
            "argv": ["bash", "scripts/demo-enforcement-5min-v1.sh"],
            "hint": "5-min demo enforcement witness — film prep (executor only)",
        },
        {
            "id": "founder-approve-outbound-batch",
            "title": "Approve outbound batch",
            "icon": "✓",
            "kind": "shell",
            "group": "enforcement",
            "cwd": str(SOURCE_A),
            "argv": ["python3", "scripts/w3_outbound_batch_approve_v1.py", "--approve", "--json"],
            "hint": "9.07 A · W3 NF outreach — one tap before send · not manual email",
        },
        {
            "id": "founder-w3-nf-outreach",
            "title": "Open W3 workflow spec",
            "icon": "📤",
            "kind": "open",
            "group": "enforcement",
            "path": str(SOURCE_A / "archive/attachments/2026-06-12/AGENTIC_W3_OUTREACH_WORKFLOW_SPEC_v1.md"),
            "hint": "AGENTIC_W3_OUTREACH_WORKFLOW_SPEC — queue design · approve via card above",
        },
        {"id": "founder-open-form-pdf", "title": "Open Form to PDF", "icon": "◆", "kind": "url", "url": FORM_TO_PDF_LIVE, "group": "products"},
        {"id": "founder-verify-mp-health", "title": "Verify MergePack /health", "icon": "✓", "kind": "url",
         "url": "https://mergepack-api-production.up.railway.app/health", "group": "products"},
        {
            "id": "founder-mp-ship-vercel",
            "title": "MP-SHIP: Vercel protection settings",
            "icon": "◆",
            "kind": "url",
            "url": "https://vercel.com/dashboard",
            "group": "products",
            "hint": "Project frontend-the-777-foundation → Settings → Deployment Protection → disable Production",
        },
        {
            "id": "founder-audit-mp-ship",
            "title": "Audit MergePack ship (MP-SHIP)",
            "icon": "✓",
            "kind": "shell",
            "group": "products",
            "cwd": str(SOURCE_A / "scripts"),
            "argv": ["python3", "audit_mergepack_ship_v1.py"],
            "hint": "Probes UI/KPI — updates mergepack_ship_status_v1.json",
        },
        {"id": "founder-open-wire-progress", "title": "Wire progress", "icon": "◎", "kind": "open",
         "path": str(SOURCE_A / "brain-os/law/WIRE_LANE_PROGRESS.md"), "group": "law"},
        {
            "id": "founder-wire-preflight",
            "title": "Wire preflight check",
            "icon": "📱",
            "kind": "shell",
            "group": "wire",
            "cwd": str(Path.home() / "Desktop/AI Dev Bridge OS"),
            "argv": ["npm", "run", "wire:preflight"],
            "hint": "Code gates only — G3 Tailscale still needs iPhone proof",
        },
        {
            "id": "founder-open-mergepack-ui",
            "title": "Open MergePack UI",
            "icon": "◆",
            "kind": "url",
            "url": "https://frontend-the-777-foundation.vercel.app",
            "group": "products",
        },
        {
            "id": "founder-trustfield-pilot-track",
            "title": "TrustField pilot (Track)",
            "icon": "◎",
            "kind": "url",
            "url": "http://127.0.0.1:13020/?tab=track",
            "group": "portfolio",
            "hint": "Confirm pilot vault note + P0 attest on Track",
        },
        {"id": "founder-open-global-blockers", "title": "GLOBAL_BLOCKERS", "icon": "⚖", "kind": "open",
         "path": str(SOURCE_A / "sina-bowl/GLOBAL_BLOCKERS.json"), "group": "law"},
        {"id": "founder-open-architect-report", "title": "Architect report", "icon": "⚖", "kind": "open",
         "path": str(SOURCE_A / "sina-bowl/ARCHITECT_REPORT.yaml"), "group": "law"},
        {"id": "founder-start-promptos", "title": "Start Prompt OS UI", "icon": "◉", "kind": "launch_app", "app_id": "promptos-ui", "group": "apps"},
        {
            "id": "founder-open-sourcea-monitor",
            "title": "Open Pre-Sleep Monitor",
            "icon": "⚡",
            "kind": "launch_app",
            "app_id": "sourcea-monitor",
            "group": "engines",
            "hint": "Live queue · sidecars · Apple Health — http://127.0.0.1:13021/monitor",
        },
        {"id": "founder-open-remote-status", "title": "Open remote status", "icon": "⎇", "kind": "url",
         "url": "http://127.0.0.1:8899/t/status", "group": "apps"},
        {
            "id": "founder-goal1-autorun-start",
            "title": "▶ RUN INBOX (Brain routes)",
            "icon": "▶",
            "kind": "goal1_unified_autorun_start",
            "group": "drain",
            "primary": True,
            "hidden": True,
            "disabled": True,
            "max_turns": 1,
            "hint": "LEGACY hidden — Cursor AUTO-RUN does not exist · Worker: run inbox when Brain routes",
        },
        {
            "id": "founder-goal1-autorun-stop",
            "title": "⏹ Factory STOP",
            "icon": "⏹",
            "kind": "goal1_unified_autorun_stop",
            "group": "drain",
            "hint": "FREEZE factory drain · stop receipt · spawn gate ON",
        },
        {
            "id": "founder-start-worker-batch-5",
            "title": "▶ START WORKER BATCH (5)",
            "icon": "▶",
            "kind": "worker_batch_loop",
            "group": "drain",
            "hidden": True,
            "batch_size": 5,
            "max_batches": 6,
            "hint": "LEGACY — hidden; use RUN INBOX when Brain routes",
        },
        {
            "id": "founder-start-worker-batch-10",
            "title": "▶ START WORKER BATCH (10)",
            "icon": "▶",
            "kind": "worker_batch_loop",
            "group": "drain",
            "hidden": True,
            "batch_size": 10,
            "max_batches": 3,
            "hint": "LEGACY — hidden",
        },
        {
            "id": "founder-brain-checkpoint-ack",
            "title": "Brain checkpoint ack",
            "icon": "✓",
            "kind": "broker_brain_checkpoint_ack",
            "group": "drain",
            "hint": "Only when batch paused at checkpoint — then restart WORKER BATCH",
        },
        {
            "id": "founder-execute-turn",
            "title": "EXECUTE 1 TURN (Brain path)",
            "icon": "◎",
            "kind": "brain_execute_turn",
            "group": "drain",
            "hidden": True,
            "hint": "LEGACY — hidden; RUN INBOX when Brain routes",
        },
        {
            "id": "founder-execute-loop-3",
            "title": "⟳ RUN 3 TURNS (semi-auto)",
            "icon": "⟳",
            "kind": "brain_execute_turn",
            "group": "drain",
            "hidden": True,
            "loop": 3,
            "hint": "LEGACY — hidden",
        },
        {
            "id": "founder-stop-goal1-executor",
            "title": "⏹ Stop Goal 1 executor",
            "icon": "⏹",
            "kind": "goal1_unified_autorun_stop",
            "group": "drain",
            "hidden": True,
            "hint": "Alias — use Factory STOP on home",
        },
        {
            "id": "founder-unstick-worker",
            "title": "🔧 Unstick Worker",
            "icon": "🔧",
            "kind": "worker_stuck_recovery",
            "group": "drain",
            "hint": "Kill hung validators, heal stale turn, replay INBOX — then Worker: run inbox once",
        },
        {
            "id": "founder-enforce-honest-registry",
            "title": "🛡 Enforce honest REGISTRY",
            "icon": "🛡",
            "kind": "enforce_registry_honest",
            "group": "drain",
            "hint": "Revert YAML-inflated done rows — monitor shows receipt-backed count only",
        },
        {
            "id": "founder-reconcile-1000-pass",
            "title": "⚡ Reconcile 1000 (validator PASS)",
            "icon": "⚡",
            "kind": "reconcile_1000_machine_pass",
            "group": "drain",
            "limit": 25,
            "hint": "Run backlog verify commands — receipt + done only when machine PASS (batch skipped)",
        },
        {
            "id": "founder-copy-healthy-drain",
            "title": "Deliver healthy drain → Worker INBOX",
            "icon": "📥",
            "kind": "healthy_drain_paste",
            "group": "drain",
            "hint": "Writes .sina-loop/INBOX.md — prompt locally (no clipboard hijack)",
        },
        {
            "id": "founder-start-worker-turn",
            "title": "START Worker turn (same as Execute)",
            "icon": "▶",
            "kind": "brain_execute_turn",
            "group": "drain",
            "hint": "Alias — runs brain_execute_turn_v1.py (Brain+agent+broker)",
        },
        {
            "id": "founder-open-worker-inbox",
            "title": "Open Worker INBOX in editor",
            "icon": "📄",
            "kind": "worker_inbox_open",
            "group": "drain",
            "hint": "View only — does NOT start loop; use START Worker turn",
        },
        {
            "id": "founder-broker-poll",
            "title": "Broker poll (Brain status)",
            "icon": "◎",
            "kind": "broker_brain_poll",
            "group": "drain",
            "hint": "YAML status — Worker report + queue (SourceA Brain reads this)",
        },
        {
            "id": "founder-brain-ack",
            "title": "Brain ack (after turn)",
            "icon": "✓",
            "kind": "broker_brain_ack",
            "group": "drain",
            "hint": "Clear awaiting_brain_ack — usually auto after Execute turn",
        },
        {
            "id": "founder-copy-worker-drain",
            "title": "Deliver Worker drain → INBOX",
            "icon": "📥",
            "kind": "worker_drain_paste",
            "group": "drain",
            "hint": "One sa from live pick — clipboard only",
        },
        {
            "id": "founder-advance-healthy-queue",
            "title": "Advance healthy queue",
            "icon": "→",
            "kind": "healthy_queue_advance",
            "group": "drain",
            "hint": "After Worker STOP — next check/act/verify slot",
        },
        {"id": "founder-queue-deliver", "title": "Send next to Cursor", "icon": "➡", "kind": "prompt_queue",
         "queue_action": "deliver_next", "group": "queue"},
        {"id": "founder-queue-load-dispatch", "title": "Load 5-repo dispatch", "icon": "📋", "kind": "prompt_queue",
         "queue_action": "load_dispatch", "group": "queue"},
        {"id": "founder-queue-clear", "title": "Clear pending queue", "icon": "✕", "kind": "prompt_queue",
         "queue_action": "clear", "group": "queue"},
        {"id": "founder-n8n-start", "title": "Start n8n", "icon": "▶", "kind": "n8n_automation",
         "action": "start", "group": "automation"},
        {"id": "founder-n8n-test-flow", "title": "Run n8n starter test", "icon": "✓", "kind": "n8n_automation",
         "action": "test_flow", "group": "automation"},
        {"id": "founder-n8n-test-extended", "title": "Run extended n8n test", "icon": "✓✓", "kind": "n8n_automation",
         "action": "test_extended", "group": "automation"},
        {"id": "founder-n8n-capture-intel", "title": "Capture intelligence", "icon": "◎", "kind": "n8n_automation",
         "action": "capture_intelligence", "group": "automation"},
        {"id": "founder-n8n-open-brief", "title": "Open intel brief", "icon": "📊", "kind": "open",
         "path": str(Path.home() / ".sina/n8n-intelligence/brief-latest.md"), "group": "automation"},
        {"id": "founder-n8n-open", "title": "Open n8n UI", "icon": "⎇", "kind": "url",
         "url": "http://127.0.0.1:5678", "group": "automation"},
        {"id": "founder-n8n-doc", "title": "Automation & n8n law", "icon": "📜", "kind": "open",
         "path": "brain-os/law/SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md", "group": "automation"},
    ]
    for repo_id, label in ingest_repos:
        rows.append({
            "id": f"founder-ingest-{repo_id}",
            "title": f"Ingest {label} (clipboard)",
            "icon": "📥",
            "kind": "ingest_clipboard",
            "repo": repo_id,
            "group": "ingest",
        })
    return rows


def goal1_auto_run_payload() -> dict:
    """Hub Goal 1 auto-run tab — Brain executor + broker + INBOX SSOT."""
    out: dict = {"ok": True, "schema": "goal1-auto-run-hub-v1"}
    try:
        proc = subprocess.run(
            [sys.executable, str(SOURCE_A / "scripts" / "program-1000-honest-status-v1.py"), "--write"],
            capture_output=True,
            text=True,
            timeout=20,
            cwd=str(SOURCE_A),
        )
        if proc.returncode == 0 and proc.stdout.strip():
            out["program_1000"] = json.loads(proc.stdout)
        else:
            out["program_1000"] = {"ok": False}
    except Exception as exc:
        out["program_1000"] = {"ok": False, "error": str(exc)}
    try:
        from worker_drain_lib import healthy_queue_status  # noqa: WPS433

        out["queue"] = healthy_queue_status()
    except Exception as exc:
        out["queue"] = {"ok": False, "error": str(exc)}
    try:
        from worker_inject_lib import inbox_status  # noqa: WPS433

        out["inbox"] = inbox_status()
    except Exception as exc:
        out["inbox"] = {"ok": False, "pending": False, "error": str(exc)}
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(SOURCE_A / "scripts" / "healthy-drain-orchestrator-v1.py"),
                "status",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(SOURCE_A),
        )
        out["orchestrator"] = json.loads(proc.stdout) if proc.returncode == 0 else {"ok": False}
    except Exception as exc:
        out["orchestrator"] = {"ok": False, "error": str(exc)}
    try:
        proc = subprocess.run(
            [sys.executable, str(SOURCE_A / "scripts" / "goal1_lane_broker.py"), "brain-poll"],
            capture_output=True,
            text=True,
            timeout=20,
            cwd=str(SOURCE_A),
        )
        out["broker_poll"] = proc.stdout[:4000] if proc.returncode == 0 else proc.stderr[:500]
        out["broker_ok"] = proc.returncode == 0
    except Exception as exc:
        out["broker_ok"] = False
        out["broker_poll"] = str(exc)
    def _lock_busy(path: Path) -> dict:
        if not path.is_file():
            return {"busy": False}
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
            pid = row.get("pid")
            if pid:
                try:
                    os.kill(int(pid), 0)
                    return {"busy": True, "pid": pid, "since": row.get("at")}
                except OSError:
                    pass
        except (OSError, json.JSONDecodeError):
            pass
        return {"busy": False}

    brain_lock = _lock_busy(Path.home() / ".sina" / "brain-executor-lock-v1.json")
    batch_lock = _lock_busy(Path.home() / ".sina" / "goal1-worker-batch-lock-v1.json")
    auto_lock = _lock_busy(Path.home() / ".sina" / "goal1-auto-run-lock-v1.json")
    if not auto_lock.get("busy"):
        auto_lock = _lock_busy(Path.home() / ".sina" / "goal1-auto-loop-lock-v1.json")
    factory_lock = _lock_busy(Path.home() / ".sina" / "factory-validation-lock-v1.json")
    auto_running = False
    try:
        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from goal1_auto_run_deliver_v1 import _auto_run_running  # noqa: WPS433

        auto_running = _auto_run_running()
    except Exception:
        pass
    auto_busy = bool(auto_running)
    busy = (
        brain_lock.get("busy")
        or batch_lock.get("busy")
        or auto_lock.get("busy")
        or factory_lock.get("busy")
        or auto_busy
    )
    out["executor"] = {
        "busy": busy,
        "pid": (
            (auto_lock.get("pid") if auto_lock.get("busy") else None)
            or batch_lock.get("pid")
            or brain_lock.get("pid")
            or (auto_running.get("pid") if isinstance(auto_running, dict) else None)
        ),
        "since": (
            auto_lock.get("since")
            or factory_lock.get("since")
            or batch_lock.get("since")
            or brain_lock.get("since")
        ),
        "factory_validation_lock": factory_lock.get("busy"),
        "mode": (
            "unified_autorun"
            if auto_lock.get("busy") or auto_busy
            else ("worker_batch" if batch_lock.get("busy") else ("brain_turn" if brain_lock.get("busy") else "ready"))
        ),
    }
    orch = out.get("orchestrator") or {}
    out["brief"] = orch.get("brief") or (out.get("queue") or {}).get("brief") or "Factory drain — RUN INBOX when Brain routes"
    try:
        bst = json.loads((Path.home() / ".sina" / "goal1-lane-broker-v1.json").read_text(encoding="utf-8"))
        out["broker_batch"] = bst.get("batch") or {}
        out["broker_status"] = bst.get("status")
    except Exception:
        out["broker_batch"] = {}
        out["broker_status"] = "unknown"
    try:
        cp = Path.home() / ".sina" / "goal1-batch-checkpoint-v1.json"
        out["last_checkpoint"] = json.loads(cp.read_text(encoding="utf-8")) if cp.is_file() else None
    except Exception:
        out["last_checkpoint"] = None
    freeze = False
    factory_line = ""
    try:
        from factory_control_v1 import load_factory_now  # noqa: WPS433

        fn = load_factory_now()
        freeze = bool(fn.get("kill_flag")) or str(fn.get("mode")) == "FREEZE"
        factory_line = str(fn.get("line") or "")
        out["factory_state"] = {
            "freeze": freeze,
            "mode": fn.get("mode") or "FREEZE",
            "line": factory_line,
            "stop_receipt_open": bool(fn.get("stop_receipt_open")),
            "queue_sa": fn.get("queue_sa") or "",
        }
    except Exception:
        pass

    try:
        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from goal1_unified_autorun_v1 import is_active, status as unified_status  # noqa: WPS433

        ua = unified_status()
        out["unified_autorun"] = ua
        if freeze:
            out["primary_action_id"] = "founder-ecosystem-safety"
            out["tab_hint"] = (
                f"{factory_line} · tap Safety · Cursor AUTO-RUN rejected"
                if factory_line
                else "FREEZE — tap Safety · bounded resume on ASF order only"
            )
        elif is_active() or ua.get("running"):
            out["primary_action_id"] = "founder-goal1-autorun-stop"
            out["tab_hint"] = ua.get("message") or "Drain active — watch Batch log"
            out["execution_surface"] = "unified_orchestrator"
            out["worker_chat_visible"] = True
            out["visibility_hint"] = (
                "RUN INBOX when Brain routes — one sa per turn. "
                "Watch status line · Batch log for detail."
            )
        else:
            out["primary_action_id"] = "founder-ecosystem-safety"
            out["tab_hint"] = "RUN INBOX when Brain routes · tap Safety · Cursor AUTO-RUN rejected"
    except Exception:
        out["primary_action_id"] = "founder-ecosystem-safety"
        out["tab_hint"] = (
            "FREEZE — tap Safety"
            if freeze
            else "RUN INBOX when Brain routes · tap Safety"
        )
    try:
        ar = Path.home() / ".sina" / "auto-run-worker-batch-v1.json"
        out["autorun"] = json.loads(ar.read_text(encoding="utf-8")) if ar.is_file() else {}
    except Exception:
        out["autorun"] = {}
    batch_log = Path.home() / ".sina" / "goal1-worker-batch-latest.log"
    if batch_log.is_file():
        try:
            out["batch_log_tail"] = batch_log.read_text(encoding="utf-8", errors="replace")[-4000:]
        except OSError:
            out["batch_log_tail"] = ""
    try:
        tp = Path.home() / ".sina" / "goal1-turn-progress-v1.json"
        out["turn_progress"] = json.loads(tp.read_text(encoding="utf-8")) if tp.is_file() else None
        if (
            not out["executor"].get("busy")
            and isinstance(out.get("turn_progress"), dict)
            and out["turn_progress"].get("status") == "RUNNING"
        ):
            out["turn_progress"] = {
                "status": "STOPPED",
                "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "message": "Stale — agent was killed; autorun will respawn next batch",
            }
        elif (
            not out["executor"].get("busy")
            and isinstance(out.get("turn_progress"), dict)
            and out["turn_progress"].get("status") == "STOPPED"
            and out["turn_progress"].get("stop_note") in ("auto_run_prepare", "auto_loop_prepare")
        ):
            out["turn_progress"] = {
                "status": "READY",
                "at": out["turn_progress"].get("at"),
                "message": "Ready — RUN INBOX when Brain routes",
            }
    except Exception:
        out["turn_progress"] = None
    if not out.get("execution_surface"):
        out["execution_surface"] = "headless_agent_cli"
    if "worker_chat_visible" not in out:
        out["worker_chat_visible"] = False
    if not out.get("visibility_hint"):
        out["visibility_hint"] = (
            "Headless agent CLI — Worker chat stays empty. Watch Batch log (AGENT START/DONE) "
            "on this tab; auto-refresh every 25s while executor is busy."
        )
    return out


def goal1_loop_payload() -> dict:
    """Deprecated alias — use goal1_auto_run_payload()."""
    return goal1_auto_run_payload()


def goal1_hub_status_bundle(g1: dict | None = None) -> dict:
    """Hub JSON keys — primary goal1_auto_run; goal1_loop mirror for rollback."""
    row = g1 if g1 is not None else goal1_auto_run_payload()
    return {"goal1_auto_run": row, "goal1_loop": row}


def founder_actions_grouped() -> list[dict]:
    """UI sections for one-click command bar."""
    groups = [
        ("emergency", "Emergency", "One tap — stop hub, auto-paste, and background inject"),
        ("drain", "Factory drain", "RUN INBOX when Brain routes — Brain+Worker+broker PEV"),
        ("hub", "Hub", "Refresh and restart — no typing"),
        ("daily", "Daily rhythm", "Dispatch and status"),
        ("engines", "Engines", "Background automation"),
        ("ingest", "After Cursor chat", "Paste reply in clipboard, then tap"),
        ("coach", "Coach", "AI reads your live snapshot"),
        ("audio", "Audio", "Morning brief on your Mac"),
        ("products", "Live products", "Open shipped URLs"),
        ("wire", "Wire lane", "DevBridge preflight — G3 needs iPhone proof"),
        ("portfolio", "Portfolio", "TrustField pilot and lane attests"),
        ("law", "Law & blockers", "Open the right file"),
        ("apps", "Apps", "Prompt OS and remote status"),
        ("queue", "Next steps", "Live next 10 in the repository — optional direction commentary (auto-paste OFF)"),
        ("automation", "Automation & n8n", "Start n8n · starter test · Runtime glue (optional)"),
    ]
    flat = [a for a in founder_actions_flat() if not a.get("hidden")]
    by_group: dict[str, list] = {}
    for a in flat:
        by_group.setdefault(a.get("group") or "other", []).append(a)
    return [
        {"id": gid, "title": title, "subtitle": sub, "actions": by_group.get(gid, [])}
        for gid, title, sub in groups
        if by_group.get(gid)
    ]


def branches_registry() -> list[dict]:
    """Engine + founder actions for Connected Apps output panel."""
    flat = founder_actions_flat()
    engines = [a for a in flat if a.get("group") == "engines"]
    daily = [a for a in flat if a.get("group") in ("daily", "ingest")]
    return [
        {
            "id": "engines",
            "title": "Prompt OS engines",
            "subtitle": "One tap — results in output panel below",
            "accent": "blue",
            "actions": engines + [a for a in flat if a["id"] == "pos-dispatch"],
        },
        {
            "id": "daily",
            "title": "Daily & ingest",
            "subtitle": "Dispatch prompts · ingest Cursor replies from clipboard",
            "accent": "gold",
            "actions": daily,
        },
    ]


def _branch_action_index() -> dict[str, dict]:
    idx: dict[str, dict] = {}
    for act in founder_actions_flat():
        idx[act["id"]] = act
    return idx


def restart_rebuild_worker() -> dict:
    """Founder one-tap — restart hub rebuild worker sidecar on :13030."""
    script = SOURCE_A / "scripts/serve-hub-rebuild-worker.sh"
    if not script.is_file():
        return {"ok": False, "error": "serve-hub-rebuild-worker.sh missing"}
    log = Path.home() / ".sina/hub-rebuild-worker.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a", encoding="utf-8") as lf:
        proc = subprocess.run(
            ["bash", str(script)],
            cwd=SOURCE_A,
            stdout=lf,
            stderr=lf,
            text=True,
            timeout=30,
            env={**os.environ, "SINA_FORCE_RESTART": "1"},
        )
    if proc.returncode != 0:
        return {"ok": False, "error": "worker restart failed", "exit_code": proc.returncode}
    try:
        import urllib.request

        with urllib.request.urlopen("http://127.0.0.1:13030/health", timeout=5) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        if body.get("ok") and body.get("service") == "hub-rebuild-worker":
            return {"ok": True, "message": "Rebuild worker restarted — :13030 healthy"}
    except Exception as exc:
        return {"ok": False, "error": f"worker health check failed: {exc}"}
    return {"ok": False, "error": "worker health contract mismatch"}


def run_branch_action(action_id: str) -> dict:
    spec = _branch_action_index().get(action_id)
    if not spec:
        return {"ok": False, "error": f"unknown action: {action_id}"}

    kind = spec.get("kind")
    try:
        from execution_spine.spine import run_branch_via_spine, should_use_spine  # noqa: WPS433

        if should_use_spine(spec):
            result = run_branch_via_spine(action_id, spec)
            if result.get("ok") and spec.get("kind") == "ingest_clipboard":
                payload = build_payload(run_refresh_scripts=True)
                write_panel_outputs(payload)
                result["data"] = payload
            return result
        if kind == "refresh":
            payload = build_payload(run_refresh_scripts=True)
            write_panel_outputs(payload)
            return {"ok": True, "message": "Panel refreshed", "built_at": payload.get("built_at")}

        if kind == "open":
            if action_id in ("founder-open-integrity-form", "founder-open-m1-canvas"):
                from form_official_canvas_route_v1 import hub_canvas_target  # noqa: WPS433

                route = hub_canvas_target()
                form_url = str(route.get("form_page_url") or "http://127.0.0.1:13020/form/")
                subprocess.run(["open", form_url], check=False)
                route_hint = str(route.get("open_canvas_hint") or route.get("hint") or "")
                return {
                    "ok": True,
                    "message": f"Opened official founder form — {form_url}",
                    "hint": route_hint,
                    "surface": route.get("surface"),
                    "path": form_url,
                    "view": route.get("view"),
                    "hub_url": route.get("hub_url") or "http://127.0.0.1:13020/",
                    "form_hub_line": route.get("form_hub_line") or "",
                    "output": (
                        f"FORM_OFFICIAL · official form page (founder-readable)\n"
                        f"Hub: {route.get('hub_url') or 'http://127.0.0.1:13020/'}\n"
                        f"Form: {form_url}\n"
                        f"M1 Canvas data mirror · Pending confirmations · INCIDENT-029\n"
                        f"{route_hint}"
                    ),
                }
            target = Path(spec["path"]).expanduser().resolve()
            if not target.exists():
                return {"ok": False, "error": f"not found: {target}"}
            subprocess.run(["open", str(target)], check=False)
            return {"ok": True, "message": f"Opened {target}"}

        if kind == "url":
            subprocess.run(["open", spec["url"]], check=False)
            return {"ok": True, "message": f"Opened {spec['url']}"}

        if kind == "one_click":
            root = PROMPTOS_ROOT
            script = root / "scripts/one-click.sh"
            if not script.is_file():
                return {"ok": False, "error": "SinaPromptOS not found on Desktop"}
            proc = subprocess.run(
                ["bash", str(script), spec["action"]],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=300,
            )
            out = (proc.stdout or "") + (proc.stderr or "")
            return {
                "ok": proc.returncode == 0,
                "stdout": proc.stdout or "",
                "stderr": proc.stderr or "",
                "output": out.strip(),
                "exit_code": proc.returncode,
                "message": "Done" if proc.returncode == 0 else "Engine failed",
            }

        if kind == "brief":
            script = SOURCE_A / "scripts/sina-morning-brief.sh"
            lang = spec.get("lang", "en")
            if not script.is_file():
                return {"ok": False, "error": "brief script missing"}
            proc = subprocess.run(
                ["bash", str(script), lang],
                cwd=SOURCE_A,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return {
                "ok": proc.returncode == 0,
                "message": f"Playing brief ({lang})" if proc.returncode == 0 else "Brief failed",
                "output": ((proc.stdout or "") + (proc.stderr or "")).strip(),
            }

        if kind == "ai_advisory":
            from sina_ai_advisory import run_advisory  # noqa: WPS433

            payload = build_payload(run_refresh_scripts=False)
            result = run_advisory(payload=payload)
            if result.get("ok"):
                write_panel_outputs(build_payload(run_refresh_scripts=False))
            return {
                **result,
                "message": result.get("message") or ("AI advisory updated" if result.get("ok") else "Advisory failed"),
            }

        if kind == "intelligence_brief":
            from intelligence_circle import generate_brief  # noqa: WPS433

            payload = build_payload(run_refresh_scripts=False)
            result = generate_brief(hub_payload=payload)
            if result.get("ok"):
                subprocess.run(["open", result["path"]], check=False)
            return result

        if kind == "intelligence_keepalive":
            from intelligence_circle import ping_live_agents  # noqa: WPS433

            return ping_live_agents()

        if kind == "emergency_stop":
            from emergency_stop import run_emergency_stop  # noqa: WPS433

            result = run_emergency_stop(from_hub=True)
            import signal

            def _exit_hub() -> None:
                time.sleep(0.35)
                os.kill(os.getpid(), signal.SIGTERM)

            threading.Thread(target=_exit_hub, daemon=True).start()
            return result

        if kind == "enqueue_eval_spine_bridge":
            from runtime.graph_executor.spine_bridge import build_spine_bridge  # noqa: WPS433

            bridge = build_spine_bridge()
            if not bridge.get("eval_1b_gate_ok"):
                return {"ok": False, "error": bridge.get("eval_1b_note", "Eval-1b gate closed")}
            proof = bridge.get("eval_proof_bridge") or {}
            if not proof.get("spine_bridge_ready"):
                return {"ok": False, "error": "eval proof bridge not ready", "bridge": bridge}
            from execution_spine.spine import run_branch_via_spine  # noqa: WPS433

            action_id = proof.get("action_id") or "spine-smoke-echo"
            spec = dict(proof.get("enqueue_spec") or {})
            spec.setdefault("kind", "shell")
            spec.setdefault("argv", ["echo", "spine-bridge-ok"])
            spec.setdefault("cwd", str(Path.home()))
            spec.setdefault("timeout", 30)
            result = run_branch_via_spine(action_id, spec)
            try:
                from runtime.event_bus.bus_v1 import publish  # noqa: WPS433

                publish(topic="spine.bridge", payload={"action_id": action_id, "ok": result.get("ok")}, source="founder_action")
            except Exception:
                pass
            return {**result, "bridge": bridge, "message": "Eval spine bridge enqueued"}

        if kind == "runreceipt_pack":
            from runreceipt.pack_v1 import build_pack  # noqa: WPS433

            return build_pack(status="PASS")

        if kind == "restart_hub":
            script = SOURCE_A / "scripts/serve-sina-command.sh"
            if not script.is_file():
                return {"ok": False, "error": "serve script missing"}
            log = Path.home() / ".sina/command-server.log"
            log.parent.mkdir(parents=True, exist_ok=True)
            with open(log, "a", encoding="utf-8") as lf:
                subprocess.Popen(
                    ["bash", str(script)],
                    cwd=SOURCE_A,
                    stdout=lf,
                    stderr=lf,
                    start_new_session=True,
                    env={**os.environ, "SINA_FORCE_RESTART": "1"},
                )
            return {"ok": True, "message": "Hub restarting — wait a few seconds, then Refresh"}

        if kind == "restart_rebuild_worker":
            return restart_rebuild_worker()

        if kind == "launch_app":
            return launch_mini_app(spec.get("app_id", "promptos-ui"))

        if kind == "ingest_clipboard":
            repo = spec.get("repo")
            script = PROMPTOS_ROOT / "scripts/ingest-clipboard.sh"
            if not script.is_file():
                return {"ok": False, "error": "ingest script missing"}
            proc = subprocess.run(
                ["bash", str(script), repo],
                cwd=PROMPTOS_ROOT,
                capture_output=True,
                text=True,
                timeout=120,
            )
            out = ((proc.stdout or "") + (proc.stderr or "")).strip()
            ok = proc.returncode == 0
            payload = None
            if ok:
                payload = build_payload(run_refresh_scripts=True)
                write_panel_outputs(payload)
            return {
                "ok": ok,
                "message": f"Ingested {repo} from clipboard" if ok else f"Ingest failed for {repo}",
                "output": out,
                "data": payload,
            }

        if kind == "shell":
            cwd = Path(spec["cwd"]).expanduser()
            proc = subprocess.run(
                spec["argv"],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return {
                "ok": proc.returncode == 0,
                "output": ((proc.stdout or "") + (proc.stderr or "")).strip(),
                "exit_code": proc.returncode,
            }

        if kind == "terminal_ui":
            return launch_mini_app("promptos-ui")

        if kind == "semej_chrome":
            from semej_browser import open_chrome_debug  # noqa: WPS433

            return open_chrome_debug()

        if kind == "n8n_automation":
            from n8n_automation import handle_n8n_action  # noqa: WPS433

            result = handle_n8n_action(spec.get("action", "status"))
            if spec.get("action") == "start" and result.get("ok") and result.get("open_url") is None:
                result["open_url"] = "http://127.0.0.1:5678"
            return result

        if kind == "prompt_queue":
            body = {"action": spec.get("queue_action", "list")}
            if body["action"] == "deliver_next":
                body["paste"] = False
                body["founder_confirmed"] = True
            if body["action"] == "clear":
                body["only_pending"] = True
            return prompt_queue_handle(body)

        if kind == "healthy_drain_paste":
            from worker_drain_lib import healthy_drain_paste  # noqa: WPS433

            return healthy_drain_paste()

        if kind == "goal1_unified_autorun_start":
            sys.path.insert(0, str(SOURCE_A / "scripts"))
            from goal1_unified_autorun_v1 import start as unified_start  # noqa: WPS433

            max_turns = int(spec.get("max_turns") or 30)
            result = unified_start(max_turns=max_turns)
            payload = build_payload(run_refresh_scripts=False)
            g1 = goal1_auto_run_payload()
            return {
                **result,
                "message": result.get("message") or "Unified auto-run started",
                **goal1_hub_status_bundle(g1),
                "turn_progress": g1.get("turn_progress"),
                "data": payload,
                "background": True,
            }

        if kind == "goal1_unified_autorun_stop":
            sys.path.insert(0, str(SOURCE_A / "scripts"))
            from goal1_unified_autorun_v1 import stop as unified_stop  # noqa: WPS433

            result = unified_stop(note="hub_action")
            payload = build_payload(run_refresh_scripts=False)
            stop_row = result.get("stop") or {}
            g1 = goal1_auto_run_payload()
            return {
                **result,
                "message": result.get("message") or "Auto-run stopped — tap RESUME to continue",
                "paused": True,
                "killed": stop_row.get("killed"),
                "remaining_pids": stop_row.get("remaining_pids"),
                **goal1_hub_status_bundle(g1),
                "data": payload,
            }

        if kind == "worker_batch_loop":
            loop_n = int(spec.get("batch_size") or 5)
            max_b = int(spec.get("max_batches") or 6)
            log_path = Path.home() / ".sina" / "goal1-worker-batch-latest.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            # Hard stop any prior loop before starting (prevents double agent + fake "running").
            subprocess.run(
                [sys.executable, str(SOURCE_A / "scripts" / "stop_goal1_loop_v1.py")],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=30,
            )
            with log_path.open("w", encoding="utf-8") as logfh:
                logfh.write(f"[hub] starting batch size={loop_n} max_batches={max_b}\n")
                proc = subprocess.Popen(
                    [
                        sys.executable,
                        str(SOURCE_A / "scripts" / "goal1_worker_batch_loop_v1.py"),
                        "--batch-size",
                        str(loop_n),
                        "--max-batches",
                        str(max_b),
                    ],
                    cwd=str(SOURCE_A),
                    stdout=logfh,
                    stderr=subprocess.STDOUT,
                )
            return {
                "ok": True,
                "message": f"Worker batch STARTED (pid {proc.pid}) — ~2–3 min per prompt · tail log below",
                "output": f"pid: {proc.pid}\nlog: {log_path}\n\nRefresh Output in ~30s or watch Goal 1 auto-run.",
                "pid": proc.pid,
                "log_path": str(log_path),
                "batch_size": loop_n,
                "background": True,
            }

        if kind == "broker_brain_checkpoint_ack":
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SOURCE_A / "scripts" / "goal1_lane_broker.py"),
                    "brain-checkpoint-ack",
                    "--note",
                    "hub_founder",
                ],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "ok": proc.returncode == 0,
                "message": "Checkpoint cleared — tap START WORKER BATCH to continue",
                "output": proc.stdout or proc.stderr,
            }

        if kind == "brain_execute_turn":
            loop_n = int(spec.get("loop") or 1)
            cmd = [sys.executable, str(SOURCE_A / "scripts" / "brain_execute_turn_v1.py"), "--yaml"]
            if loop_n > 1:
                cmd.extend(["--loop", str(min(loop_n, 5))])
            proc = subprocess.run(
                cmd,
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=3600 if loop_n > 1 else 1900,
            )
            out = (proc.stdout or proc.stderr or "").strip()
            return {
                "ok": proc.returncode == 0,
                "message": "Goal 1 turn complete" if proc.returncode == 0 else "Execute turn failed or busy",
                "output": out[:8000],
                "returncode": proc.returncode,
                "loop": loop_n,
            }

        if kind == "reconcile_1000_machine_pass":
            lim = int(spec.get("limit") or 25)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SOURCE_A / "scripts" / "reconcile-1000-machine-pass-v1.py"),
                    "--limit",
                    str(lim),
                ],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=3600,
            )
            try:
                row = json.loads(proc.stdout) if proc.stdout.strip() else {}
            except json.JSONDecodeError:
                row = {"raw": proc.stdout, "stderr": proc.stderr}
            payload = build_payload(run_refresh_scripts=False)
            brain_sync: dict = {}
            try:
                sys.path.insert(0, str(SOURCE_A / "scripts"))
                from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

                brain_sync = sync_brain_snapshot(mode="light", caller="reconcile_1000")
            except Exception as exc:
                brain_sync = {"ok": False, "error": str(exc)}
            return {
                "ok": row.get("ok", proc.returncode == 0),
                "message": (
                    f"Reconcile 1000: closed {row.get('closed_count', 0)} · "
                    f"honest now {row.get('honest_done_after', '?')}/1000"
                ),
                "output": proc.stdout[:12000] or proc.stderr[:2000],
                "reconcile": row,
                "brain_sync": brain_sync,
                "data": payload,
            }

        if kind == "cursor_research_mode":
            sys.path.insert(0, str(SOURCE_A / "scripts"))
            from cursor_window_preflight_v1 import (  # noqa: WPS433
                cursor_focus_steal_disabled,
                toggle_cursor_focus_steal_disabled,
            )

            row = toggle_cursor_focus_steal_disabled(caller="hub_cursor_research_mode")
            on = cursor_focus_steal_disabled()
            payload = build_payload(run_refresh_scripts=False)
            write_panel_outputs(payload)
            return {
                "ok": True,
                "message": (
                    "Chrome research mode ON — auto-run will not pop Cursor"
                    if on
                    else "Research mode OFF — auto-run may foreground Cursor again"
                ),
                "research_mode": on,
                "cursor_focus_steal": row,
                "data": payload,
            }

        if kind == "brain_sync_monitor":
            sys.path.insert(0, str(SOURCE_A / "scripts"))
            from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

            row = sync_brain_snapshot(mode="light", caller="hub_brain_sync_monitor")
            payload = build_payload(run_refresh_scripts=True)
            write_panel_outputs(payload)
            after = row.get("after") or row
            return {
                "ok": bool(row.get("ok")),
                "message": (
                    f"Brain sync {'OK' if row.get('ok') else 'GAP'} · "
                    f"live {after.get('live_vy')} · snapshot {after.get('brain_vy')} · "
                    f"dual_proof {'OK' if after.get('dual_proof_ok') else 'GAP'} — tap ↺ on monitor"
                ),
                "brain_sync": row,
                "data": payload,
            }

        if kind == "enforce_registry_honest":
            proc = subprocess.run(
                [sys.executable, str(SOURCE_A / "scripts" / "enforce-registry-honest-v1.py"), "--json"],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=60,
            )
            try:
                row = json.loads(proc.stdout) if proc.stdout.strip() else {}
            except json.JSONDecodeError:
                row = {"raw": proc.stdout, "stderr": proc.stderr}
            brain_sync: dict = {}
            try:
                sys.path.insert(0, str(SOURCE_A / "scripts"))
                from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

                brain_sync = sync_brain_snapshot(mode="full", caller="enforce_registry_honest")
            except Exception as exc:
                brain_sync = {"ok": False, "error": str(exc)}
            payload = build_payload(run_refresh_scripts=False)
            after = row.get("after") or row
            honest = after.get("honest_done", "?")
            reverted = row.get("reverted_count", 0)
            return {
                "ok": row.get("ok", proc.returncode == 0) and brain_sync.get("ok", True),
                "message": f"Honest REGISTRY: {honest}/1000 · reverted {reverted} unproven · brain sync",
                "output": proc.stdout[:8000] or proc.stderr[:2000],
                "enforce": row,
                "brain_sync": brain_sync,
                "data": payload,
            }

        if kind == "worker_stuck_recovery":
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SOURCE_A / "scripts" / "worker_stuck_recovery_v1.py"),
                    "--json",
                ],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=60,
            )
            try:
                row = json.loads(proc.stdout) if proc.stdout.strip() else {}
            except json.JSONDecodeError:
                row = {"raw": proc.stdout, "stderr": proc.stderr}
            payload = build_payload(run_refresh_scripts=False)
            killed = (row.get("steps") or {}).get("killed_hung", {}).get("count", 0)
            return {
                "ok": row.get("ok", proc.returncode == 0),
                "message": (
                    f"Worker unstuck · killed {killed} hung process(es) · "
                    f"inbox_sa={row.get('inbox_sa') or '—'} · say run inbox once in Worker chat"
                ),
                "output": proc.stdout[:8000] or proc.stderr[:2000],
                "recovery": row,
                "data": payload,
            }

        if kind == "anti_staleness_check":
            proc = subprocess.run(
                ["bash", str(SOURCE_A / "scripts" / "validate-anti-staleness-bundle-v1.sh")],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=240,
            )
            out = (proc.stdout or "") + (proc.stderr or "")
            tail = ""
            for line in reversed(out.splitlines()):
                if line.startswith(("OK:", "FAIL:", "PASS:")):
                    tail = line
                    break
            ok = proc.returncode == 0
            return {
                "ok": ok,
                "message": f"Anti-staleness {'PASS' if ok else 'FAIL'}" + (f" · {tail}" if tail else ""),
                "output": out[-8000:],
            }

        if kind == "factory_stop":
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SOURCE_A / "scripts" / "stop_goal1_auto_run_v1.py"),
                    "--note",
                    "hub_founder_factory_stop",
                    "--json",
                ],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=60,
            )
            ok = proc.returncode == 0
            return {
                "ok": ok,
                "message": "Factory STOP — FREEZE · kill flag ON · bounded resume on ASF order only",
                "output": (proc.stdout or proc.stderr or "")[-4000:],
            }

        if kind in ("ecosystem_safety", "ecosystem_fix_all"):
            script = (
                "validate-ecosystem-safety-h1-fast-v1.sh"
                if kind == "ecosystem_safety"
                else "fix-ecosystem-all-v1.sh"
            )
            timeout = 45 if kind == "ecosystem_safety" else 600
            proc = subprocess.run(
                ["bash", str(SOURCE_A / "scripts" / script)],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            out = ((proc.stdout or "") + (proc.stderr or "")).strip()
            ok = proc.returncode == 0
            tail = ""
            for line in reversed(out.splitlines()):
                if line.startswith(("OK:", "FAIL:", "PASS:", "sweep:")):
                    tail = line
                    break
            label = "Ecosystem safety" if kind == "ecosystem_safety" else "Ecosystem fix-all"
            return {
                "ok": ok,
                "message": (
                    f"{label} {'PASS' if ok else 'FAIL'}"
                    + (f" · {tail}" if tail else "")
                ),
                "output": out[-8000:],
            }

        if kind == "stop_goal1_executor":
            proc = subprocess.run(
                [sys.executable, str(SOURCE_A / "scripts" / "stop_goal1_loop_v1.py")],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=30,
            )
            try:
                row = json.loads(proc.stdout) if proc.stdout.strip() else {}
            except json.JSONDecodeError:
                row = {"raw": proc.stdout, "stderr": proc.stderr}
            payload = build_payload(run_refresh_scripts=False)
            row["data"] = payload
            return {
                "ok": row.get("ok", proc.returncode == 0),
                "message": row.get("message") or "Goal 1 auto-run stopped",
                "output": proc.stdout[:8000] or proc.stderr[:2000],
                "killed": row.get("killed"),
                "remaining_pids": row.get("remaining_pids"),
                "data": payload,
            }

        if kind == "broker_brain_ack":
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SOURCE_A / "scripts" / "goal1_lane_broker.py"),
                    "brain-ack",
                    "--note",
                    "hub_founder_ack",
                ],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "ok": proc.returncode == 0,
                "message": "Brain ack complete",
                "output": proc.stdout or proc.stderr,
            }

        if kind == "broker_brain_poll":
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SOURCE_A / "scripts" / "goal1_lane_broker.py"),
                    "brain-poll",
                ],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=30,
            )
            brain_sync: dict = {}
            try:
                sys.path.insert(0, str(SOURCE_A / "scripts"))
                from brain_sync_lib_v1 import brain_snapshot_status, sync_brain_snapshot  # noqa: WPS433

                st = brain_snapshot_status()
                if st.get("snapshot_stale"):
                    brain_sync = sync_brain_snapshot(mode="light", caller="broker_brain_poll")
            except Exception as exc:
                brain_sync = {"ok": False, "error": str(exc)}
            msg = "Broker poll — paste output to SourceA Brain chat"
            if brain_sync.get("synced") or brain_sync.get("ok"):
                msg += " · brain snapshot synced"
            return {
                "ok": proc.returncode == 0,
                "message": msg,
                "output": proc.stdout or proc.stderr,
                "brain_sync": brain_sync,
            }

        if kind == "worker_inbox_open":
            from worker_inject_lib import open_inbox_in_editor, inbox_status  # noqa: WPS433

            st = inbox_status()
            opened = open_inbox_in_editor(background=True)
            return {
                "ok": opened.get("ok", False),
                "message": "INBOX tab only — does NOT run agent. Tap START Worker turn to execute.",
                "inbox": st,
                "editor": opened,
            }

        if kind == "worker_drain_paste":
            from worker_drain_lib import worker_drain_paste  # noqa: WPS433

            return worker_drain_paste()

        if kind == "healthy_queue_advance":
            from worker_drain_lib import advance_healthy_queue  # noqa: WPS433

            out = advance_healthy_queue()
            if out.get("brain_sync") is None:
                try:
                    sys.path.insert(0, str(SOURCE_A / "scripts"))
                    from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

                    out["brain_sync"] = sync_brain_snapshot(mode="light", caller="healthy_queue_advance")
                except Exception as exc:
                    out["brain_sync"] = {"ok": False, "error": str(exc)}
            return out

        return {"ok": False, "error": f"unsupported kind: {kind}"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "action timed out"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def run_refresh_pipeline() -> list[dict]:
    """Rebuild live signals — returns human-readable step log for UI.

    Dedupe env on all child jobs (sa-0205):
    - ``SINA_SKIP_NESTED_BOWL`` — ``update-program-progress`` must not call ``build-sina-daily-bowl.sh``
    - ``SINA_SKIP_PANEL_BUILD`` — ``build-sina-daily-bowl`` must not nest panel or master-orders export
    - ``SINA_SKIP_FLEET_SCAN`` — fleet scan runs once at pipeline start; bowl reads registry only
    """
    steps: list[dict] = []
    jobs = [
        ("Program progress", SOURCE_A / "scripts/update-program-progress.py"),
        ("Daily bowl", SOURCE_A / "scripts/build-sina-daily-bowl.py"),
        ("Master orders", SOURCE_A / "scripts/export-master-orders-json.py"),
    ]
    refresh_env = {
        **os.environ,
        "SINA_SKIP_NESTED_BOWL": "1",
        "SINA_SKIP_PANEL_BUILD": "1",
        "SINA_SKIP_FLEET_SCAN": "1",
    }
    fleet_env = {k: v for k, v in refresh_env.items() if k != "SINA_SKIP_FLEET_SCAN"}
    fleet_once = SOURCE_A / "scripts" / "scan-cursor-agent-fleet.py"
    if fleet_once.is_file() and os.environ.get("SINA_SKIP_FLEET_SCAN", "").strip() not in ("1", "true", "yes"):
        try:
            proc = subprocess.run(
                ["python3", str(fleet_once)],
                cwd=SOURCE_A,
                capture_output=True,
                text=True,
                timeout=180,
                env=fleet_env,
            )
            steps.append(
                {
                    "label": "Fleet scan",
                    "ok": proc.returncode == 0,
                    "detail": "registry refreshed once for pipeline",
                }
            )
        except subprocess.TimeoutExpired:
            steps.append({"label": "Fleet scan", "ok": False, "detail": "timeout after 180s"})
    for label, script in jobs:
        if not script.is_file():
            steps.append({"label": label, "ok": False, "detail": "script missing"})
            continue
        try:
            proc = subprocess.run(
                ["python3", str(script)],
                cwd=SOURCE_A,
                capture_output=True,
                text=True,
                timeout=300,
                env=refresh_env,
            )
            tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
            detail = tail[-1][:120] if tail else ("ok" if proc.returncode == 0 else "failed")
            steps.append({"label": label, "ok": proc.returncode == 0, "detail": detail})
        except subprocess.TimeoutExpired:
            steps.append({"label": label, "ok": False, "detail": "timeout after 300s"})
    steps.append({"label": "Panel + KPI scan", "ok": True, "detail": "command-data rebuilt"})
    return steps


def apps_guide_for_ui() -> dict:
    return {
        "title": "Sina apps — plain-English guide",
        "start_here": [
            "Double-click Sina Command on Desktop (gold icon).",
            "Use Command tab for today's picture.",
            "Use Connected Apps to open Prompt OS or run engines.",
            "Press Refresh after real work (dispatch, plan edits, ingest).",
        ],
        "refresh": {
            "summary": "Refresh re-reads your real files — not a cosmetic reload.",
            "steps": [
                "Updates PROGRAM_PROGRESS.json from repo signals",
                "Rebuilds DAILY_BOWL.md and the daily card",
                "Re-scans fleet, blockers, MergePack KPI, todos",
                "Redraws this panel with a new timestamp",
            ],
            "when": [
                "After morning dispatch",
                "After editing GLOBAL_BLOCKERS or a lock file",
                "After ingesting a Cursor reply",
                "When numbers or agent status look stale",
            ],
            "timing": "Usually 5–20 seconds. Wait for the gold toast and 'Synced … (live)'.",
            "if_fails": "Pill shows Offline → tap Restart hub (Command home or Connected Apps), then Refresh.",
        },
        "desktop_apps": [
            {
                "name": "Sina Command",
                "role": "CEO dashboard — all tabs, rules, repos, agents",
                "url": "http://127.0.0.1:13020",
            },
            {
                "name": "Sina Prompt OS",
                "role": "Best Cursor prompt, lanes, prompt library",
                "url": "http://127.0.0.1:8765",
            },
            {
                "name": "Sina Dispatch",
                "role": "Refresh 5-repo paste prompts for Cursor",
                "url": "http://127.0.0.1:13020/?tab=apps&run=pos-dispatch",
            },
            {
                "name": "Sina Decide",
                "role": "Instant preview — what scheduler would do next",
                "url": "http://127.0.0.1:13020/?tab=apps&run=pos-decide",
            },
            {
                "name": "Sina Status",
                "role": "Full health report with clickable links",
                "url": "http://127.0.0.1:8899/t/status",
            },
            {
                "name": "Sina Run / Execute",
                "role": "Background automation — then check Status",
                "url": "http://127.0.0.1:13020/?tab=apps",
            },
            {
                "name": "MergePack · Form to PDF",
                "role": "Live product you asked to keep visible",
                "url": FORM_TO_PDF_LIVE,
            },
            {
                "name": "MergePack API + VIRLUX live",
                "role": "All shipped URLs in Products tab",
                "url": "http://127.0.0.1:13020/?tab=products",
            },
        ],
        "command_tabs": [
            ("Connected Apps", "Launch side apps and engines"),
            ("Command", "Home — tiles, path, recent work (tap for detail)"),
            ("Your notes", "Sticky notes for Cursor — fix / idea / question"),
            ("AI Advisory", "Coach — connections, upgrades, risks, one focus"),
            ("Guide", "Teacher lessons — like tips on a new app"),
            ("Rules", "Read and edit Source A law"),
            ("Daily", "ASF card, bowl, paste files, dispatch"),
            ("Agents", "Who is active; done vs not done"),
            ("Repos", "Every repo: plan, blocked, next"),
            ("Today", "P0, KPI, drift, todos — tap red cards for detail"),
            ("Live products", "Shipped URLs — Form to PDF, VIRLUX, API"),
            ("Program path", "Duolingo-style path — tap each bubble"),
        ],
        "openrouter": {
            "where": "Private vault on this Mac (not shown in the app)",
            "key_line": "OPENROUTER_API_KEY",
            "note": "Apps load your vault locally; they never display or delete the key. Restart Prompt OS from Desktop after you add it.",
        },
        "voyage_embeddings": {
            "where": "~/.sina/secrets.env",
            "key_line": "VOYAGE_API_KEY",
            "status": "live — voyage-4-lite · semantic:true · 629 chunks (P05 done)",
            "note": "Key in vault · re-index complete · next COMM step P03 NVIDIA Inception · rotate key in vault only",
        },
        "mistakes": [
            ("Panel Offline or blank", "Open http://127.0.0.1:13020 via Desktop app, not file://"),
            ("Refresh seems dead", "Wait for toast; server may need Desktop Sina Command"),
            ("Engine only says Started", "Normal — tap Full status report for the result"),
            ("OpenRouter not connected", "Restart Sina Prompt OS.app after vault edit"),
        ],
        "teacher_intro": {
            "title": "Welcome — learn Sina Command like a new app on your phone",
            "body": (
                "When you download any app from the web, you get short tips: “Tap here”, “This is your feed”, "
                "“Settings live here”. This Guide does the same for **your** control room — one lesson per area, "
                "plain language, and a **Try it now** button so you learn by tapping, not by memorizing tables."
            ),
        },
        "teacher_lessons": _teacher_lessons(),
    }


def _teacher_lessons() -> list[dict]:
    return [
        {
            "id": "mandatory-agents",
            "icon": "⛔",
            "open": True,
            "title": "Lesson 0 — Mandatory for Cursor agents (coding the app)",
            "analogy": "Like a safety briefing before touching production: read the incident report first, then the loop laws.",
            "sections": [
                {
                    "heading": "Read before you code",
                    "body": (
                        "Open each locked doc from the red **Mandatory reading** card on Home, Guide, or Rules. "
                        "Start with **Auto-paste incident report** — never re-enable Live agents paste into Cursor without ASF."
                    ),
                    "try_tab": "rules",
                },
                {
                    "heading": "Emergency stop",
                    "body": "If auto-paste or spam returns: executor runs kill-sina-command.sh — founder sees **Restart hub** in app, not Terminal.",
                    "try_tab": "actions",
                },
                {
                    "heading": "Three loops",
                    "body": "Meta (Next steps) = plan only. Factory (Private agents) = rounds in app. Repo = one task per plan.json. See Prompt-fast loop doc.",
                    "try_tab": "guide",
                },
            ],
        },
        {
            "id": "welcome",
            "icon": "👋",
            "open": False,
            "title": "Lesson 1 — First time you open the app",
            "analogy": "Like installing a new app: first you check that it’s really running, then you learn where the main buttons are.",
            "sections": [
                {
                    "heading": "Step 1: Open the right way",
                    "body": "Double-click **Sina Command** on your Desktop (gold compass). A browser tab opens at http://127.0.0.1:13020 — that is correct. Do not double-click index.html in a folder.",
                    "tip": "Top-right pill must say **Live** (green). If it says Offline, the server is not running — double-click Sina Command again.",
                },
                {
                    "heading": "Step 2: Learn the layout",
                    "body": "Left = menu (tabs). Top = page title + gold **Refresh** + **Brief**. Center = the page you chose. Many pages also show a panel on the right when you tap a card — like “more info” on a phone.",
                    "try_tab": "command",
                },
                {
                    "heading": "Step 3: One tap — never Terminal",
                    "body": "Open the **Actions** page from Home (or sidebar). Dispatch, ingest, AI advisory, morning brief, restart hub — each has its own button. **Home** stays clean; heavy controls live on their own pages.",
                    "tip": "Red blocker cards on **Today** also have action buttons — Open Form to PDF, Open GLOBAL_BLOCKERS, etc.",
                    "try_tab": "actions",
                },
            ],
        },
        {
            "id": "command-home",
            "icon": "⌂",
            "title": "Lesson 2 — Command home (your memory board)",
            "analogy": "This is your home screen — like the main dashboard in a fitness app showing today’s workout, streak, and shortcuts.",
            "sections": [
                {
                    "heading": "The four big tiles",
                    "body": "Each tile is a button. **P0** opens the full program page (goals, next action, links). **Agents active** opens who worked in the last 24 hours. **Repos blocked** opens what is stuck. **KPI trio** opens MergePack live metrics.",
                    "tip": "Every tile says “Open →” — if nothing happens, press Refresh first.",
                    "try_tab": "command",
                    "try_page": "program",
                    "try_id": "P0-RUNRECEIPT",
                },
                {
                    "heading": "Try: Agents page",
                    "body": "After you understand the home screen, open the full agents activity list.",
                    "try_page": "agents",
                },
                {
                    "heading": "The path (numbered steps)",
                    "body": "The vertical steps are your real to-do chain. Tap a step to open that **program** with explanation and links — not just a headline.",
                },
                {
                    "heading": "Recent work cards",
                    "body": "Form to PDF, MergePack, VIRLUX, Prompt OS, etc. Tap any card → **full detail page** with connected links (thread, repo, live URL, hub tabs).",
                    "try_tab": "products",
                },
            ],
        },
        {
            "id": "refresh",
            "icon": "↻",
            "title": "Lesson 3 — What Refresh really does",
            "analogy": "Like “pull to refresh” in email — it fetches new truth from your Mac, not fake animation.",
            "sections": [
                {
                    "heading": "When to press it",
                    "body": "After dispatch, after editing a law file, after a Cursor chat ingest, after marking a todo done, or when numbers look old.",
                    "tip": "Wait 5–20 seconds. Toast + “Synced … (live)” means done.",
                },
                {
                    "heading": "What happens inside",
                    "body": "Updates progress files, rebuilds daily bowl, re-reads fleet + KPI + blockers, saves new data for the panel.",
                    "try_tab": "command",
                },
            ],
        },
        {
            "id": "connected-apps",
            "icon": "⎇",
            "title": "Lesson 4 — Connected Apps & Desktop icons",
            "analogy": "Like having Netflix, Spotify, and Settings as icons — each opens a different tool, but one hub lists them all.",
            "sections": [
                {
                    "heading": "Connected Apps tab",
                    "body": "Open Prompt OS UI, run engines (Dispatch, Decide, Status), open Mono. **Form to PDF** is pinned at the top so you never lose the live ship URL.",
                    "try_tab": "apps",
                },
                {
                    "heading": "Desktop .app icons",
                    "body": "Same actions without opening the browser first. Engines that say only “Started…” are background jobs — run **Sina Status** for the full report.",
                    "tip": "First time macOS may block an app — right-click → Open once.",
                },
            ],
        },
        {
            "id": "notes-ai",
            "icon": "✎",
            "title": "Lesson 5 — Your notes & AI Advisory",
            "analogy": "Notes = leaving a sticky note for your future self. AI Advisory = a smart coach reading your whole system once and suggesting upgrades.",
            "sections": [
                {
                    "heading": "Your notes",
                    "body": "Write what to fix or improve — Cursor reads it next time. No screenshots needed. Categories: Update, Fix, Idea, Question.",
                    "try_tab": "notes",
                },
                {
                    "heading": "AI Advisory",
                    "body": "Uses OpenRouter (your private key) on a snapshot of live data. Returns golden connections, upgrade ideas, risks, and one focus for today. Run again after big changes.",
                    "try_tab": "ai-advisory",
                },
            ],
        },
        {
            "id": "daily-today",
            "icon": "☀",
            "title": "Lesson 6 — Daily rhythm (five repos)",
            "analogy": "Like a morning checklist: one card tells five “teams” what to do today in Cursor.",
            "sections": [
                {
                    "heading": "Daily tab",
                    "body": "ASF daily card, bowl text, paste prompts per repo. **Run Dispatch** rebuilds ready-to-paste files for Cursor.",
                    "try_tab": "daily",
                },
                {
                    "heading": "Today tab",
                    "body": "P0 detail, live KPI trio, red blocker cards — tap a card for full explanation.",
                    "try_tab": "today",
                },
                {
                    "heading": "Program path",
                    "body": "Duolingo-style bubbles — tap each program to learn what it means and where to go next.",
                    "try_tab": "plans",
                },
            ],
        },
        {
            "id": "law-repos",
            "icon": "⚖",
            "title": "Lesson 7 — Rules, repos, agents, fleet",
            "analogy": "Rules = the constitution. Repos = each company folder. Agents/Fleet = who actually worked in Cursor.",
            "sections": [
                {
                    "heading": "Rules",
                    "body": "Search and edit Source A law. Saving writes to disk — you are the only law editor.",
                    "try_tab": "rules",
                },
                {
                    "heading": "Repos",
                    "body": "TrustField, Mono, VIRLUX, Noetfield, 777, MergePack — each shows plan, next task, blockers. Tap for detail page.",
                    "try_tab": "repos",
                },
                {
                    "heading": "Agents & Fleet",
                    "body": "Agents = friendly summary per workspace. Fleet = raw transcripts and VERIFY blocks.",
                    "try_tab": "agents",
                },
            ],
        },
        {
            "id": "ecosystem",
            "icon": "◎",
            "title": "Lesson 8 — Ecosystem, products, audio, HQ",
            "analogy": "The “about the company” page — how all layers and live products connect.",
            "sections": [
                {
                    "heading": "Live products",
                    "body": "Every shipped URL (Form to PDF, VIRLUX, MergePack API) with Open live + repo folder.",
                    "try_tab": "products",
                },
                {
                    "heading": "Ecosystem",
                    "body": "Flywheel, L1–L5 layers, KPI — how money and factory logic connect.",
                    "try_tab": "ecosystem",
                },
                {
                    "heading": "Audio",
                    "body": "Morning brief in English or pure Farsi — listen instead of reading.",
                    "try_tab": "audio",
                },
                {
                    "heading": "Personal DB & HQ",
                    "body": "Layer A memory for agents. HQ = duties and team supervision.",
                    "try_tab": "personal-db",
                },
            ],
        },
        {
            "id": "mistakes",
            "icon": "⚠",
            "title": "Lesson 9 — When something feels broken",
            "analogy": "Like FAQ pages in app support — quick fixes before you panic.",
            "sections": [
                {
                    "heading": "Offline / blank panel",
                    "body": "Always open via Desktop **Sina Command**, not a saved HTML file.",
                    "tip": "Check green Live pill.",
                },
                {
                    "heading": "Click does nothing",
                    "body": "Refresh once. If Desktop app was just updated, right-click app → Open once (macOS security).",
                },
                {
                    "heading": "Engine only says Started",
                    "body": "Normal for Dispatch/Run/Execute — open **Sina Status** or Connected Apps output panel.",
                },
            ],
        },
    ]


def mandatory_reads_for_agents() -> dict:
    """Locked docs — unified with hub_essentials READ_CHAIN (no duplicate list)."""
    from hub_essentials_index import mandatory_reads_from_chain  # noqa: WPS433

    return mandatory_reads_from_chain()


def guides_payload() -> dict:
    guide_path = SOURCE_A / "archive/legacy/sina-command/SINA_COMMAND_GUIDE_LOCKED_v1.md"
    apps_path = SOURCE_A / "brain-os/law/SINA_APPS_GUIDE_FOR_SINA_v1.md"
    human = guide_path.read_text(encoding="utf-8") if guide_path.is_file() else ""
    apps_md = apps_path.read_text(encoding="utf-8") if apps_path.is_file() else ""
    return {
        "human_markdown": human,
        "apps_markdown": apps_md,
        "apps": apps_guide_for_ui(),
        "mandatory_reads": mandatory_reads_for_agents(),
        "hierarchy": HIERARCHY,
        "agent_opening_line": "Active thread: THREAD-_____. Role: ROLE-_____. One outcome only.",
        "agent_end_rule": "VERIFY block + update os/plan.json or PROGRAM_PROGRESS",
        "tier1": [
            "SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md",
            "SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md",
            "SINA_PROMPT_FAST_LOOP_LOCKED_v1.md",
            "SINA_AGENT_LOOP_ORDER_v1.md",
            "SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md",
            "AGENT_GOVERNANCE_INDEX_LOCKED_v1.md",
            "sina-bowl/DAILY_BOWL.md",
            "SINA_APPS_GUIDE_FOR_SINA_v1.md",
            "SINA_COMMAND_GUIDE_LOCKED_v1.md",
            "brain-os/law/UNDERSTANDING_ROLES_CURSOR_ECOSYSTEM_v1.md",
            "ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md",
        ],
    }


def recent_subjects_registry(
    bowl: dict,
    progress: dict,
    ops: list[dict],
    mp_prog: dict | None,
) -> list[dict]:
    """Founder home — everything you were last working on (tap → drill in Command tab)."""
    subjects: list[dict] = []
    seen: set[str] = set()

    def add(row: dict) -> None:
        rid = row.get("id")
        if not rid or rid in seen:
            return
        seen.add(rid)
        subjects.append(row)

    for p in live_products_registry():
        if p["id"] == "mergepack-form-pdf":
            add({
                "id": p["id"],
                "title": "Form to PDF",
                "subtitle": "Live MergePack ship — quote → PDF",
                "thread": p.get("thread"),
                "accent": "green",
                "drill_kind": "product",
                "drill_id": p["id"],
                "badge": "live" if p.get("live") else "check",
                "sort": 0,
            })
            break

    try:
        from live_founder_decision_form_v1 import payload as _form_payload  # noqa: WPS433
        from rt_live_gate_v1 import receipt_pass  # noqa: WPS433

        _form = _form_payload()
        if receipt_pass() and int(_form.get("open_questions_count") or 0) == 0:
            add({
                "id": "subject-phase3-resume",
                "title": "Phase 3 integrity resume",
                "subtitle": "SYS-INTEGRITY-100 index-only · 55 answered · 0 open",
                "thread": "THREAD-INTEGRITY-100",
                "accent": "green",
                "drill_kind": "plan",
                "drill_id": "SYS-INTEGRITY-100",
                "badge": "resume",
                "sort": 3,
            })
    except Exception:
        pass

    for o in ops:
        thread = "THREAD-MERGEPACK"
        if o["id"].startswith("WIRE"):
            thread = "THREAD-WIRE"
        elif o["id"] == "B-001":
            thread = "THREAD-ECOSYSTEM"
        elif o["id"] == "PHASE-3-RESUME":
            thread = "THREAD-INTEGRITY-100"
        add({
            "id": f"ops-{o['id']}",
            "title": o["title"],
            "subtitle": (o.get("action") or "")[:96],
            "thread": thread,
            "accent": "red" if o.get("severity") == "critical" else "amber",
            "drill_kind": "ops",
            "drill_id": o["id"],
            "badge": o.get("severity", "ops"),
            "sort": 3 if o["id"] == "PHASE-3-RESUME" else (8 if o["id"] == "MP-SHIP" else 12),
        })

    for i, duty in enumerate((bowl.get("asf_duties") or [])[:4]):
        add({
            "id": f"duty-{i}",
            "title": duty[:72],
            "subtitle": "Must do today (ASF)",
            "thread": "HQ",
            "accent": "gold",
            "drill_kind": "duty",
            "drill_id": duty,
            "badge": "today",
            "sort": 6 + i,
        })

    plan_sort = {
        "MERGEPACK-L1": 18,
        "P0-RUNRECEIPT": 22,
        "PROMPTOS-DAILY": 28,
        "M8-WIRE": 34,
        "SUPERBRAIN-P0": 38,
        "PORTFOLIO": 42,
        "CURSOR-OS-PRO": 48,
        "INVESTOR": 52,
    }
    plans = progress.get("parallel_plans") or bowl.get("parallel_plans") or []
    for p in sorted(plans, key=lambda x: plan_sort.get(x.get("id"), 60)):
        pid = p.get("id")
        if not pid:
            continue
        accent = "green" if "MERGEPACK" in pid else "violet" if "SUPERBRAIN" in pid else "blue"
        add({
            "id": f"plan-{pid}",
            "title": p.get("title") or pid,
            "subtitle": (p.get("next_action") or p.get("phase") or "")[:96],
            "thread": p.get("thread") or pid,
            "accent": accent,
            "drill_kind": "plan",
            "drill_id": pid,
            "badge": p.get("status") or "plan",
            "sort": plan_sort.get(pid, 60),
            "progress_pct": p.get("progress_pct"),
        })

    for p in live_products_registry():
        if p["id"] == "mergepack-form-pdf" or not p.get("open_url"):
            continue
        add({
            "id": p["id"],
            "title": p["title"],
            "subtitle": (p.get("subtitle") or "")[:96],
            "thread": p.get("thread"),
            "accent": p.get("accent", "blue"),
            "drill_kind": "product",
            "drill_id": p["id"],
            "badge": "live" if p.get("live") else "url",
            "sort": 44 if "mergepack" in p["id"] else 46 if "virlux" in p["id"] else 50,
        })

    for app_id, sort_key in (
        ("sina-command", 4),
        ("promptos-ui", 26),
        ("remote-ops", 27),
        ("mono-next", 39),
    ):
        spec = next((a for a in mini_apps_catalog() if a["id"] == app_id), None)
        if not spec:
            continue
        add({
            "id": f"app-{app_id}",
            "title": spec["title"],
            "subtitle": spec.get("subtitle", ""),
            "thread": "THREAD-WIRE" if "remote" in app_id else "PROMPTOS-DAILY",
            "accent": "blue",
            "drill_kind": "app",
            "drill_id": app_id,
            "badge": "running" if spec.get("running") else "stopped",
            "sort": sort_key,
        })

    for r in repos_registry():
        name = r.get("name") or r.get("id")
        if not (r.get("global_blocker") or r.get("blocked") or (r.get("next_tasks"))):
            continue
        nt = (r.get("next_tasks") or [{}])[0]
        sub = nt.get("text") if isinstance(nt, dict) else str(nt)
        add({
            "id": f"repo-{name}",
            "title": name,
            "subtitle": (sub or r.get("active_focus") or "")[:96],
            "thread": r.get("thread"),
            "accent": "violet",
            "drill_kind": "repo",
            "drill_id": r.get("id") or name,
            "badge": "blocked" if r.get("blocked") else "repo",
            "sort": 62,
        })

    p0 = bowl.get("p0") or {}
    if p0.get("id"):
        add({
            "id": f"plan-{p0['id']}",
            "title": p0.get("title") or p0["id"],
            "subtitle": (p0.get("next_action") or "")[:96],
            "thread": p0.get("thread"),
            "accent": "gold",
            "drill_kind": "plan",
            "drill_id": p0["id"],
            "badge": "p0",
            "sort": 20,
            "progress_pct": p0.get("progress_pct"),
        })

    subjects.sort(key=lambda x: (x.get("sort", 99), x.get("title", "")))
    return subjects


def command_center_payload(bowl: dict, fleet: dict, ops: list, progress: dict, kpi: dict) -> dict:
    workspaces = fleet.get("workspaces") or []
    repos = repos_registry()
    agents = agents_registry(workspaces)
    active_agents = [a for a in agents if a["active_24h"]]
    blocked_repos = [r for r in repos if r.get("blocked") or r.get("global_blocker")]
    return {
        "founder": founder_playbook(bowl, ops, progress),
        "repos": repos,
        "agents": agents,
        "summary": {
            "repos_count": len(repos),
            "agents_count": len(agents),
            "active_agents_24h": len(active_agents),
            "blocked_repos": len(blocked_repos),
            "kpi_trio_complete": (kpi.get("data") or {}).get("kpi_trio_complete") if kpi.get("ok") else False,
        },
    }


def drift_hints() -> list[dict]:
    drift = load_json(DRIFT_JSON) or []
    hints = []
    for d in drift if isinstance(drift, list) else []:
        fix = d.get("action", "")
        if "THREAD-MERGEPACK" in fix:
            fix += " → ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md"
        hints.append({**d, "fix_file": "ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md" if "registry" in fix.lower() else None})
    return hints


def kernel_k1_payload() -> dict:
    """K1 enforcement kernel — critic boot + tamper-on-read.

    Hook point: loaders (load_healthy_queue, load_factory_now, load_active_now) —
    NOT build_payload(). See demo/governance/K1_LOADER_HOOK_ARCHITECTURE_v1.md.
    """
    payload: dict = {
        "schema": "kernel-k1-v1",
        "ok": False,
        "verdict": "BLOCK",
        "founder_line": "K1 BLOCK — kernel not evaluated",
    }
    try:
        from critic_boot_v1 import run_boot  # noqa: WPS433

        boot = run_boot(in_gate=True)
        boot_ok = bool(boot.get("ok"))
        payload["critic_boot"] = {
            "verdict": boot.get("verdict"),
            "ok": boot_ok,
            "checks": boot.get("checks"),
            "blockers": boot.get("blockers"),
        }
        payload["sourcea_boot_unified"] = True

        tamper_block: dict = {"ok": False}
        try:
            import subprocess

            proc = subprocess.run(
                ["bash", str(SOURCE_A / "scripts" / "validate-enforcement-kernel-v1.sh"), "--quick"],
                capture_output=True,
                text=True,
                timeout=90,
                cwd=str(SOURCE_A),
            )
            tamper_block = {
                "ok": proc.returncode == 0,
                "exit": proc.returncode,
                "stdout_tail": (proc.stdout or "").strip()[-400:],
            }
            if proc.returncode != 0 and proc.stderr:
                tamper_block["stderr_tail"] = (proc.stderr or "").strip()[-200:]
        except Exception as te:
            tamper_block = {"ok": False, "error": str(te)}

        payload["k1_tamper_validator"] = tamper_block
        payload["ok"] = boot_ok and bool(tamper_block.get("ok"))
        payload["verdict"] = "PASS" if payload["ok"] else "BLOCK"
        if payload["ok"]:
            payload["founder_line"] = "K1 PASS — boot + tamper-on-read"
        else:
            parts: list[str] = []
            if not boot_ok:
                parts.extend((boot.get("blockers") or [])[:2])
            if not tamper_block.get("ok"):
                parts.append("k1_tamper_validator")
            payload["founder_line"] = "K1 BLOCK — " + " · ".join(parts[:3])
    except Exception as e:
        payload["error"] = str(e)
        payload["founder_line"] = f"K1 BLOCK — {e}"
    return payload


def build_payload(*, run_refresh_scripts: bool = False) -> dict:
    refresh_log: list[dict] = []
    if run_refresh_scripts:
        refresh_log = run_refresh_pipeline()

    bowl = load_json(BOWL_STATE) or {}
    fleet_raw = load_json(FLEET) or {}
    # Refresh pipeline already exports MASTER_ORDERS.json — skip duplicate subprocess (H1).
    if not run_refresh_scripts:
        _maybe_export_master_orders(force=False)
    orders = load_json(MASTER_ORDERS) or {}
    progress = load_json(PROGRESS) or {}
    mp_prog = load_json(MERGEPACK_PROGRESS)
    signals = progress.get("signals_auto") or {}
    wire = signals.get("wire") or {}
    kpi_fetch = fetch_mergepack_kpi()

    workspaces = [enrich_fleet_workspace(dict(w)) for w in fleet_raw.get("workspaces") or []]
    fleet = {**fleet_raw, "workspaces": workspaces, "groups": group_fleet(workspaces)}

    audit_path = SOURCE_A / "AGENT_SELF_AUDIT_ASF_REPORT_2026-06-04.md"
    audit = {"exists": audit_path.is_file(), "path": str(audit_path), "updated_at": None}
    if audit_path.is_file():
        audit["updated_at"] = datetime.fromtimestamp(
            audit_path.stat().st_mtime, tz=timezone.utc
        ).isoformat()

    ops_list = ops_blockers(progress, wire, mp_prog)
    ops_enriched = [{**o, "links": links_for_ops(o["id"])} for o in ops_list]
    live_products = live_products_registry()
    repos_rows = repos_registry()
    cc = command_center_payload(bowl, fleet, ops_enriched, progress, kpi_fetch)

    bowl_out = dict(bowl)
    bowl_out["parallel_plans"] = [
        {**p, "links": links_for_plan(p.get("id") or "")}
        for p in (bowl.get("parallel_plans") or [])
    ]
    eco: dict = {"ok": False, "subjects": [], "by_category": []}
    try:
        from ecosystem_subjects import (  # noqa: WPS433
            ecosystem_payload,
            founder_threads_from_ecosystem,
            today_from_ecosystem,
        )

        eco = ecosystem_payload(
            refresh=run_refresh_scripts,
            bowl=bowl,
            ops=ops_enriched,
        )
        ft = founder_threads_from_ecosystem(eco)
        recent = attach_links_to_subjects(
            today_from_ecosystem(eco.get("subjects") or [], bowl=bowl, ops=ops_enriched),
            live_products,
            repos_rows,
        )
        full_work = attach_links_to_subjects(
            ft.get("full") or [],
            live_products,
            repos_rows,
        )
    except Exception as e:
        eco = {"ok": False, "error": str(e), "subjects": [], "by_category": []}
        try:
            from founder_threads import founder_threads_payload, today_subjects_for_home  # noqa: WPS433

            ft = founder_threads_payload(
                bowl=bowl,
                ops=ops_enriched,
                refresh_scan=run_refresh_scripts,
            )
            recent = attach_links_to_subjects(
                today_subjects_for_home(bowl, progress, ops_enriched, mp_prog),
                live_products,
                repos_rows,
            )
            full_work = attach_links_to_subjects(ft.get("full") or [], live_products, repos_rows)
        except Exception as e2:
            ft = {"ok": False, "error": f"{e}; {e2}", "full": [], "today": [], "by_category": []}
            full_work = []
            recent = attach_links_to_subjects(
                recent_subjects_registry(bowl, progress, ops_enriched, mp_prog)[:8],
                live_products,
                repos_rows,
            )

    out = {
        "schema_version": 5,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "refresh_log": refresh_log,
        "source_a_root": str(SOURCE_A),
        "command_center": cc,
        "branches": branches_registry(),
        "founder_actions": founder_actions_grouped(),
        "mini_apps": mini_apps_registry(),
        "live_products": live_products,
        "recent_subjects": recent,
        "ecosystem": eco,
        "founder_threads": ft,
        "full_threads": full_work,
        "thread_index": thread_index_registry(live_products, repos_rows),
        "daily_hub": daily_hub_payload(bowl),
        "sources": sources_registry(bowl),
        "guides": guides_payload(),
        "emergency_stop": {
            "label": "Emergency stop",
            "title": "Stop hub & auto-paste",
            "terminal": "~/Desktop/SourceA/scripts/emergency-stop.sh",
            "action_id": "founder-emergency-stop",
            "api_path": "/api/emergency-stop",
            "icon": "⛔",
        },
        "rules": rules_registry(),
        "bowl": bowl_out,
        "fleet": fleet,
        "signals": {
            "wire": wire,
            "mergepack": signals.get("mergepack") or {},
            "architect_blockers": signals.get("architect_blockers") or [],
        },
        "mergepack_kpi": kpi_fetch,
        "ops_blockers": ops_enriched,
        "drift_hints": drift_hints(),
        "roles_detail": [{**r, "links": links_for_role(r["id"])} for r in ROLES_DETAIL],
        "hq_duties_full": HQ_DUTIES_FULL,
        "master_orders": orders,
        "personal_db": _personal_db_payload(),
        "prompt_os": prompt_os_snapshot(),
        "runtime": runtime_snapshot(),
        "hq_audit": audit,
        "brief_text": bowl.get("brief_text", ""),
        "brief_fa": bowl.get("brief_fa") or _load_brief_fa(),
        "lane_briefs": {},
        "ecosystem_brief": "",
        "universal_brief": {},
        "asf_notes": progress.get("asf_notes", ""),
        "todos_editable": True,
        "founder_notes": list_notes(),
        "ai_advisory": _load_ai_advisory(),
        "prompt_queue": queue_payload(),
        "prompt_direction": direction_payload(),
        "sourcea_sa_queue": sourcea_sa_queue_payload(),
    }
    try:
        from live_prompt_overrides_v1 import payload as live_ongoing_payload  # noqa: WPS433

        out["live_ongoing_prompts"] = live_ongoing_payload().get("live_ongoing_prompts") or {}
    except Exception:
        out["live_ongoing_prompts"] = {"ok": False}
    try:
        from worker_drain_lib import healthy_queue_status  # noqa: WPS433

        out["healthy_drain_rail"] = healthy_queue_status()
    except Exception:
        out["healthy_drain_rail"] = {"ok": False}
    try:
        from worker_inject_lib import inbox_status  # noqa: WPS433

        out["worker_inbox"] = inbox_status()
    except Exception:
        out["worker_inbox"] = {"ok": False, "pending": False}
    try:
        import subprocess

        proc = subprocess.run(
            [
                sys.executable,
                str(SOURCE_A / "scripts" / "healthy-drain-orchestrator-v1.py"),
                "status",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(SOURCE_A),
        )
        out["healthy_drain_orchestrator"] = (
            json.loads(proc.stdout) if proc.returncode == 0 else {"ok": False}
        )
    except Exception:
        out["healthy_drain_orchestrator"] = {"ok": False}
    try:
        g1 = goal1_auto_run_payload()
        out.update(goal1_hub_status_bundle(g1))
    except Exception:
        out.update(goal1_hub_status_bundle({"ok": False}))
    try:
        from hub_home_founder_view_v1 import hub_home_founder_payload  # noqa: WPS433

        out["home_founder_view"] = hub_home_founder_payload(hub_payload=out)
        hfv = out.get("home_founder_view") or {}
        out["worker_drain_next_10"] = hfv.get("worker_drain_next_10") or {}
        out["missed_actions_card"] = hfv.get("missed_actions_card") or {}
    except Exception:
        out["home_founder_view"] = {"ok": False, "schema": "hub-home-founder-v1"}
        out["worker_drain_next_10"] = {}
        out["missed_actions_card"] = {}
    try:
        from strategic_synthesis_hub import strategic_synthesis_payload  # noqa: WPS433

        out["strategic_synthesis"] = strategic_synthesis_payload()
    except Exception:
        out["strategic_synthesis"] = {"ok": False}
    out["agent_loop"] = loop_payload(hub_payload=out)
    try:
        from semej_loop import semej_payload  # noqa: WPS433

        out["semej"] = semej_payload()
    except Exception as e:
        out["semej"] = {"ok": False, "error": str(e), "status": "idle"}
    try:
        from lane_briefs import lane_briefs_registry  # noqa: WPS433

        out["lane_briefs"] = lane_briefs_registry()
    except Exception:
        out["lane_briefs"] = out.get("lane_briefs") or {}

    try:
        from founder_commitments import commitments_payload  # noqa: WPS433

        cc = out.get("command_center") or {}
        out["commitments"] = commitments_payload(
            bowl=bowl,
            progress=progress,
            ops=ops_enriched,
            founder=cc.get("founder"),
            repos=cc.get("repos"),
            founder_notes=list_notes(),
            prompt_queue=out.get("prompt_queue"),
            agent_loop=out.get("agent_loop"),
            semej=out.get("semej"),
            prompt_direction=out.get("prompt_direction"),
            ecosystem=out.get("ecosystem"),
        )
    except Exception as e:
        out["commitments"] = {"ok": False, "error": str(e), "open_count": 0, "items": [], "lanes": []}

    try:
        from command_audit_backlog import audit_backlog_payload, home_priority_cards  # noqa: WPS433

        out["audit_backlog"] = audit_backlog_payload()
        out["recent_subjects"] = attach_links_to_subjects(
            home_priority_cards(out.get("commitments"), out.get("ecosystem")),
            live_products,
            repos_rows,
        )
    except Exception as e:
        out["audit_backlog"] = {"ok": False, "error": str(e), "items": [], "by_category": {}}
        out["recent_subjects"] = out.get("recent_subjects") or []

    try:
        from agent_command_reviews import reviews_payload  # noqa: WPS433

        out["agent_reviews"] = reviews_payload()
    except Exception as e:
        out["agent_reviews"] = {"ok": False, "error": str(e), "items": [], "open_count": 0}

    try:
        from agent_private_workspaces import workspaces_payload  # noqa: WPS433

        out["agent_workspaces"] = workspaces_payload()
    except Exception as e:
        out["agent_workspaces"] = {"ok": False, "error": str(e), "workspaces": []}

    try:
        from agent_incident_system import incident_room_payload  # noqa: WPS433

        out["incident_room"] = incident_room_payload()
    except Exception as e:
        out["incident_room"] = {"ok": False, "error": str(e), "posts": [], "agents": []}

    try:
        from agent_conflict_room import conflict_room_payload  # noqa: WPS433

        out["conflict_room"] = conflict_room_payload()
    except Exception as e:
        out["conflict_room"] = {"ok": False, "error": str(e), "cases": [], "agents": []}

    try:
        from agent_council_room import council_room_payload  # noqa: WPS433

        out["council_room"] = council_room_payload()
    except Exception as e:
        out["council_room"] = {"ok": False, "error": str(e), "agents": [], "channels": []}

    try:
        from agent_scoreboard import scoreboard_payload  # noqa: WPS433

        out["agent_scoreboard"] = scoreboard_payload()
    except Exception as e:
        out["agent_scoreboard"] = {"ok": False, "error": str(e), "rows": []}

    try:
        from agent_essay_discourse import essay_discourse_payload  # noqa: WPS433

        essay = essay_discourse_payload()
        out["essay_discourse"] = essay
        if out.get("council_room"):
            out["council_room"]["essay_discourse"] = essay
            if not out["council_room"].get("topics"):
                out["council_room"]["essay_topics"] = essay.get("topics") or []
    except Exception as e:
        out["essay_discourse"] = {"ok": False, "error": str(e), "topics": []}

    try:
        from founder_request_tracker import requests_payload  # noqa: WPS433

        out["founder_requests"] = requests_payload()
    except Exception as e:
        out["founder_requests"] = {"ok": False, "error": str(e), "open_count": 0, "open_top": []}

    try:
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        out["live_founder_decision_form"] = live_form_payload()
    except Exception as e:
        out["live_founder_decision_form"] = {"ok": False, "error": str(e), "needs_asf_fill": True}

    try:
        from task_orders_guardian import orders_payload  # noqa: WPS433

        out["order_guardian"] = orders_payload(out)
    except Exception as e:
        out["order_guardian"] = {"ok": False, "error": str(e), "actionable_count": 0, "advisory": {}}

    try:
        from founder_agent_use_guide import guide_payload  # noqa: WPS433

        out["founder_agent_guide"] = guide_payload(out)
    except Exception as e:
        out["founder_agent_guide"] = {"ok": False, "error": str(e), "wanted_count": 0, "reminder": {}}

    try:
        from governance_drift_engine import drift_payload  # noqa: WPS433

        out["governance_drift"] = drift_payload()
        gd = out["governance_drift"]
        if gd.get("aggregate_score") is not None:
            hints = list(out.get("drift_hints") or [])
            hints.append(
                {
                    "severity": "high" if gd.get("status") != "ok" else "low",
                    "title": f"Governance drift score {gd.get('aggregate_score')}/100",
                    "fix_file": "scripts/governance_drift_engine.py",
                }
            )
            out["drift_hints"] = hints
    except Exception as e:
        out["governance_drift"] = {"ok": False, "error": str(e)}

    try:
        from agent_governance_unification import unification_payload  # noqa: WPS433

        out["governance_unification"] = unification_payload()
    except Exception as e:
        out["governance_unification"] = {"ok": False, "error": str(e)}

    try:
        from important_docs_index import important_docs_payload  # noqa: WPS433

        out["important_docs"] = important_docs_payload()
    except Exception as e:
        out["important_docs"] = {"ok": False, "error": str(e), "sections": []}

    try:
        from founder_advisor_discussion_v1 import founder_advisor_discussion_payload  # noqa: WPS433

        out["founder_advisor_discussion"] = founder_advisor_discussion_payload()
    except Exception as e:
        out["founder_advisor_discussion"] = {"ok": False, "error": str(e), "pinned": True, "pending_decisions": 4}

    try:
        from hub_essentials_index import hub_essentials_payload  # noqa: WPS433

        out["hub_essentials"] = hub_essentials_payload(hub_port=13020)
    except Exception as e:
        out["hub_essentials"] = {"ok": False, "error": str(e), "pillars": [], "quick_tiles": []}

    try:
        from n8n_automation import automation_payload  # noqa: WPS433

        out["n8n_automation"] = automation_payload()
    except Exception as e:
        out["n8n_automation"] = {"ok": False, "error": str(e)}

    try:
        from roadmaps_goals import roadmaps_goals_payload  # noqa: WPS433

        out["roadmaps_goals"] = roadmaps_goals_payload()
    except Exception as e:
        out["roadmaps_goals"] = {"ok": False, "error": str(e), "parallel_plans": [], "roadmap_docs": []}

    try:
        from system_roadmap import system_roadmap_payload  # noqa: WPS433

        out["system_roadmap"] = system_roadmap_payload()
    except Exception as e:
        out["system_roadmap"] = {"ok": False, "error": str(e)}

    try:
        from knowledge_library_payload import knowledge_library_payload  # noqa: WPS433

        out["knowledge_library"] = knowledge_library_payload()
    except Exception as e:
        out["knowledge_library"] = {"ok": False, "error": str(e)}

    try:
        from meta_reasoning_policy import meta_reasoning_payload  # noqa: WPS433

        out["meta_reasoning_policy"] = meta_reasoning_payload(hub=out)
    except Exception as e:
        out["meta_reasoning_policy"] = {"ok": False, "error": str(e), "layer_count": 0}

    try:
        from agent_skills_registry import agent_skills_payload  # noqa: WPS433

        out["agent_skills"] = agent_skills_payload()
    except Exception as e:
        out["agent_skills"] = {"ok": False, "error": str(e), "skill_count": 0}

    try:
        from agent_research_pipeline import research_pipeline_payload  # noqa: WPS433

        out["agent_research_pipeline"] = research_pipeline_payload()
    except Exception as e:
        out["agent_research_pipeline"] = {"ok": False, "error": str(e), "items": []}

    try:
        from execution_spine.spine import spine_payload  # noqa: WPS433

        out["execution_spine"] = spine_payload()
    except Exception as e:
        out["execution_spine"] = {"ok": False, "error": str(e)}

    try:
        from execution_intelligence.decision_memory.api import decisions_v1_payload  # noqa: WPS433

        out["execution_decisions_v1"] = decisions_v1_payload()
        out["execution_decisions"] = out["execution_decisions_v1"]
    except Exception as e:
        out["execution_decisions"] = {"ok": False, "error": str(e)}

    try:
        from execution_intelligence.context_intelligence.api import (
            context_intelligence_v1_payload,
            execution_context_payload,
        )  # noqa: WPS433

        out["context_intelligence_v1"] = context_intelligence_v1_payload()
        out["execution_context"] = execution_context_payload()
    except Exception as e:
        out["context_intelligence_v1"] = {"ok": False, "error": str(e)}
        out["execution_context"] = {"ok": False, "error": str(e)}

    try:
        from execution_intelligence.pattern_engine.api import patterns_v1_payload  # noqa: WPS433

        out["execution_patterns_v1"] = patterns_v1_payload()
    except Exception as e:
        out["execution_patterns_v1"] = {"ok": False, "error": str(e)}

    try:
        from execution_intelligence.feedback_loop.api import feedback_v1_payload  # noqa: WPS433

        out["execution_feedback_v1"] = feedback_v1_payload()
    except Exception as e:
        out["execution_feedback_v1"] = {"ok": False, "error": str(e)}

    try:
        from execution_intelligence.planner_upgrade.api import planner_upgrade_v1_payload  # noqa: WPS433

        out["planner_upgrade_v1"] = planner_upgrade_v1_payload()
    except Exception as e:
        out["planner_upgrade_v1"] = {"ok": False, "error": str(e)}

    try:
        from execution_intelligence.self_optimization.api import self_optimization_v1_payload  # noqa: WPS433

        out["self_optimization_v1"] = self_optimization_v1_payload()
    except Exception as e:
        out["self_optimization_v1"] = {"ok": False, "error": str(e)}

    try:
        from runtime.tool_graph.api import tool_graph_v1_payload  # noqa: WPS433

        out["tool_graph_v1"] = tool_graph_v1_payload()
    except Exception as e:
        out["tool_graph_v1"] = {"ok": False, "error": str(e)}

    try:
        from runtime.tool_graph_verification.api import tool_graph_verify_v1_payload  # noqa: WPS433

        out["tool_graph_verified_v1"] = tool_graph_verify_v1_payload()
    except Exception as e:
        out["tool_graph_verified_v1"] = {"ok": False, "error": str(e)}

    try:
        from runtime.execution_router.api import execution_router_v1_payload  # noqa: WPS433

        out["execution_router_v1"] = execution_router_v1_payload()
    except Exception as e:
        out["execution_router_v1"] = {"ok": False, "error": str(e)}

    try:
        from execution_intelligence.api import intelligence_payload  # noqa: WPS433

        out["execution_intelligence"] = intelligence_payload()
    except Exception as e:
        out["execution_intelligence"] = {"ok": False, "error": str(e)}

    try:
        from execution_intelligence_v2.api import intelligence_v2_payload  # noqa: WPS433

        out["execution_intelligence_v2"] = intelligence_v2_payload()
    except Exception as e:
        out["execution_intelligence_v2"] = {"ok": False, "error": str(e)}

    try:
        from ecosystem_incidents_index import ecosystem_incidents_payload  # noqa: WPS433

        out["ecosystem_incidents"] = ecosystem_incidents_payload()
    except Exception as e:
        out["ecosystem_incidents"] = {"ok": False, "error": str(e), "sections": []}

    try:
        from intelligence_circle import circle_payload  # noqa: WPS433

        out["intelligence_circle"] = circle_payload(hub_payload=out)
    except Exception as e:
        out["intelligence_circle"] = {"ok": False, "error": str(e), "feed": [], "roster": []}

    try:
        from lane_briefs import build_universal_cursor_brief  # noqa: WPS433

        cc = out.get("command_center") or {}
        founder = cc.get("founder") or {}
        out["universal_brief"] = build_universal_cursor_brief(
            bowl=bowl,
            eco=out.get("ecosystem"),
            p0=founder.get("p0") or bowl.get("p0"),
            ai_advisory=out.get("ai_advisory"),
            prompt_direction=out.get("prompt_direction"),
            ops_blockers=out.get("ops_blockers"),
            founder=founder,
            repos=cc.get("repos"),
            commitments=out.get("commitments"),
        )
        out["ecosystem_brief"] = out["universal_brief"].get("copy_text") or out.get("brief_text", "")
    except Exception:
        out["universal_brief"] = out.get("universal_brief") or {}
        out["ecosystem_brief"] = out.get("ecosystem_brief") or out.get("brief_text", "")

    try:
        from agent_system_unified import system_unified_payload  # noqa: WPS433

        out["system_unified"] = system_unified_payload(hub_payload=out)
        ric = out["system_unified"].get("rules_in_charge") or {}
        if out.get("council_room") and ric.get("ok"):
            try:
                from agent_council_room import _shared_rules_digest_raw  # noqa: WPS433
                from agent_rules_in_charge import enrich_shared_rules_digest  # noqa: WPS433

                out["council_room"]["shared_rules"] = enrich_shared_rules_digest(_shared_rules_digest_raw(), out)
                out["council_room"]["rules_in_charge"] = ric
            except Exception:
                pass
    except Exception as e:
        out["system_unified"] = {"ok": False, "error": str(e), "all_rules": [], "copy_brief": ""}

    try:
        out["kernel_k1"] = kernel_k1_payload()
    except Exception as e:
        out["kernel_k1"] = {"ok": False, "error": str(e), "schema": "kernel-k1-v1", "verdict": "BLOCK"}

    return sync_sa_queue_into_payload(out)


def _load_ai_advisory() -> dict:
    try:
        from sina_ai_advisory import load_cached_advisory  # noqa: WPS433

        return load_cached_advisory()
    except Exception as e:
        return {"ok": False, "error": str(e), "advisory": None}


def _load_brief_fa() -> str:
    p = SOURCE_A / "sina-bowl" / "brief.fa.txt"
    if p.is_file():
        return p.read_text(encoding="utf-8").strip()
    return ""


_HUB_CACHE: dict | None = None
_HUB_CACHE_AT: float = 0.0
_HUB_CACHE_TTL_SEC = 180.0
_HUB_LOCK = threading.Lock()

# Deferred to background fetch — keeps first paint under ~500KB (sa-0016).
SHELL_MAX_BYTES = 500 * 1024
HEAVY_PAYLOAD_KEYS = frozenset(
    {
        "fleet",
        "ecosystem",
        "council_room",
        "agent_loop",
        "system_roadmap",
        "founder_threads",
        "rules",
        "lane_briefs",
        "full_threads",
        "essay_discourse",
        "intelligence_circle",
        "order_guardian",
        "incident_room",
        "conflict_room",
        "agent_scoreboard",
        "knowledge_library",
        "execution_intelligence",
        "execution_intelligence_v2",
        "execution_patterns_v1",
        "agent_research_pipeline",
        "governance_drift",
        "governance_unification",
        "meta_reasoning_policy",
        "agent_skills",
        "execution_spine",
        "semej",
        "prompt_queue",
        "prompt_direction",
        "ai_advisory",
        "founder_notes",
        "important_docs",
        "n8n_automation",
        "thread_index",
        "founder_agent_guide",
        "system_unified",
        "commitments",
        "guides",
        "audit_backlog",
        "roles_detail",
        "hq_duties_full",
        "context_intelligence_v1",
        "execution_decisions",
        "execution_decisions_v1",
        "roadmaps_goals",
        "ecosystem_incidents",
        "universal_brief",
        "ecosystem_brief",
        # sa-0852 — defer from lazy shell; load via tab slice / hub-sync (legacy /legacy/ only)
        "agent_reviews",
        "hub_essentials",
        "live_products",
        # sa-0016 hospital — hub-sync + worker-hub API slices (not first paint)
        "home_founder_view",
        "live_founder_decision_form",
        "bowl",
    }
)


def invalidate_hub_cache() -> None:
    global _HUB_CACHE, _HUB_CACHE_AT
    with _HUB_LOCK:
        _HUB_CACHE = None
        _HUB_CACHE_AT = 0.0


def warm_hub_cache_from_disk() -> None:
    global _HUB_CACHE, _HUB_CACHE_AT
    path = PANEL_DIR / "command-data.json"
    if not path.is_file():
        return
    with _HUB_LOCK:
        if _HUB_CACHE is not None:
            return
        try:
            _HUB_CACHE = json.loads(path.read_text(encoding="utf-8"))
            _HUB_CACHE_AT = time.monotonic()
        except Exception:
            _HUB_CACHE = None
            _HUB_CACHE_AT = 0.0


def get_hub_payload(*, run_refresh_scripts: bool = False, force: bool = False) -> dict:
    global _HUB_CACHE, _HUB_CACHE_AT
    with _HUB_LOCK:
        now = time.monotonic()
        if (
            not force
            and not run_refresh_scripts
            and _HUB_CACHE is not None
            and (now - _HUB_CACHE_AT) < _HUB_CACHE_TTL_SEC
        ):
            return _HUB_CACHE
        payload = build_payload(run_refresh_scripts=run_refresh_scripts)
        _HUB_CACHE = payload
        _HUB_CACHE_AT = now
        return payload


def build_shell_payload(full: dict | None = None) -> dict:
    full = full if full is not None else get_hub_payload()
    return {k: v for k, v in full.items() if k not in HEAVY_PAYLOAD_KEYS}


def command_data_response() -> dict:
    warm_hub_cache_from_disk()
    return get_hub_payload()


def command_data_shell_response() -> dict:
    warm_hub_cache_from_disk()
    return build_shell_payload(get_hub_payload())


def hub_light_refresh(*, write_html: bool = False) -> dict:
    """Fast founder Refresh — disk + live block align, no build_payload (HUB-LITE Phase 0)."""
    global _HUB_CACHE, _HUB_CACHE_AT
    from align_command_data_ui_v1 import _align_p0_pick, _refresh_live_blocks  # noqa: WPS433
    from hub_sync_slim_v1 import bump_shell_generation_id  # noqa: WPS433

    try:
        from governance_projection_g3_v1 import authorize_projection_write  # noqa: WPS433

        authorize_projection_write(["hub", "monitor", "truth_bundle"], reason="hub_light_refresh")
    except Exception:
        pass

    warm_hub_cache_from_disk()
    path = PANEL_DIR / "command-data.json"
    with _HUB_LOCK:
        payload = _HUB_CACHE
    if not payload and path.is_file():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            payload = None
    if not payload:
        payload = get_hub_payload(run_refresh_scripts=False, force=True)
    _refresh_live_blocks(payload)
    try:
        sync_sa_queue_into_payload(payload)
        _apply_factory_freeze_from_lib(payload)
    except Exception:
        pass
    _align_p0_pick(payload)
    payload["built_at"] = datetime.now(timezone.utc).isoformat()
    bump_shell_generation_id()
    write_panel_outputs(payload, json_only=not write_html)
    shell = build_shell_payload(payload)
    with _HUB_LOCK:
        _HUB_CACHE = payload
        _HUB_CACHE_AT = time.monotonic()
    return shell


def hub_after_mutation(*, run_refresh_scripts: bool = False, write_html: bool = False) -> dict:
    invalidate_hub_cache()
    payload = get_hub_payload(run_refresh_scripts=run_refresh_scripts, force=True)
    try:
        sync_sa_queue_into_payload(payload)
        _apply_factory_freeze_from_lib(payload)
    except Exception:
        pass
    write_panel_outputs(payload, json_only=not write_html)
    try:
        proc = subprocess.run(
            ["bash", str(SOURCE_A / "scripts" / "validate-hub-p0-no-autorun-v1.sh")],
            cwd=str(SOURCE_A),
            capture_output=True,
            text=True,
            timeout=90,
        )
        payload["anti_staleness_as01"] = {
            "ok": proc.returncode == 0,
            "stdout": (proc.stdout or proc.stderr or "").strip()[-240:],
        }
    except Exception as exc:
        payload["anti_staleness_as01"] = {"ok": False, "error": str(exc)}
    return payload


def _apply_factory_freeze_from_lib(payload: dict) -> None:
    """Mirror build-sina-command-panel freeze state on refresh path."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_panel",
        SOURCE_A / "scripts" / "build-sina-command-panel.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    mod._apply_factory_freeze_state(payload)


def _write_text_atomic(path: Path, text: str) -> None:
    """Temp file + replace — readers never see partial JSON (sa-0220)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def verify_command_data_atomic() -> tuple[bool, str]:
    """Post-build proof: command-data.json and shell.json parse and align (sa-0220)."""
    out_json = PANEL_DIR / "command-data.json"
    out_shell = PANEL_DIR / "command-data-shell.json"
    if not out_json.is_file() or not out_shell.is_file():
        return False, "command-data.json or command-data-shell.json missing"
    try:
        full = json.loads(out_json.read_text(encoding="utf-8"))
        shell = json.loads(out_shell.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    built = full.get("built_at")
    if not built or built != shell.get("built_at"):
        return False, f"built_at mismatch: {built!r} vs {shell.get('built_at')!r}"
    if full.get("schema_version") != shell.get("schema_version"):
        return False, "schema_version mismatch"
    for key in HEAVY_PAYLOAD_KEYS:
        if key in shell:
            return False, f"heavy key {key} leaked into shell"
    if out_shell.stat().st_size > SHELL_MAX_BYTES:
        return False, f"shell {out_shell.stat().st_size} bytes > {SHELL_MAX_BYTES} (sa-0016)"
    return True, f"built_at={built}"


def heal_command_data_shell_from_disk(*, force: bool = False) -> tuple[bool, str]:
    """Re-strip heavy keys from command-data.json into shell (sa-0016 stale-hub guard)."""
    out_json = PANEL_DIR / "command-data.json"
    out_shell = PANEL_DIR / "command-data-shell.json"
    if not out_json.is_file():
        return False, "command-data.json missing"
    if not force:
        ok, msg = verify_command_data_atomic()
        if ok:
            return True, msg
    try:
        full = json.loads(out_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid command-data.json: {exc}"
    shell_text = json.dumps(build_shell_payload(full), ensure_ascii=False, separators=(",", ":"))
    _write_text_atomic(out_shell, shell_text)
    return verify_command_data_atomic()


def bump_shell_generation_id() -> int:
    from hub_sync_slim_v1 import bump_shell_generation_id as _bump  # noqa: WPS433

    return _bump()


def _patch_founder_guard_copy(payload: dict) -> None:
    """INCIDENT-037 — every hub projection write gets guard-only founder surfaces (no invitation)."""
    cc = payload.get("command_center") or {}
    founder = dict(cc.get("founder") or {})
    bowl = payload.get("daily_bowl") or payload.get("bowl") or {}
    founder["must_do_today"] = _must_do_today_lines(bowl)
    p0 = dict(founder.get("p0") or {})
    sq = payload.get("sourcea_sa_queue") or {}
    live = sq.get("live_pick") or {}
    live_id = str(live.get("id") or "")
    live_title = (live.get("title") or "")[:72] if live.get("id") else None
    try:
        from founder_p0_next_action_v1 import build_founder_p0_next_action  # noqa: WPS433

        p0["next_action"] = build_founder_p0_next_action(
            queue_brief=None,
            live_pick_id=live_id if live_id.startswith("sa-") else None,
            live_pick_title=live_title,
        )
    except Exception:
        pass
    founder["p0"] = p0
    cc["founder"] = founder
    payload["command_center"] = cc


_FOUNDER_INVITE_PATTERNS = (
    r"automatic recommended picks",
    r"open form · submit",
    r"one next tap",
    r"asf must answer",
    r"tap here",
    r"submit when ready",
)


def _assert_founder_guard_copy_clean(payload: dict) -> None:
    """Fail-closed — hub projection must never ship invitation copy (INCIDENT-037)."""
    import re

    founder = ((payload.get("command_center") or {}).get("founder") or {})
    blob = json.dumps(
        [founder.get("must_do_today"), (founder.get("p0") or {}).get("next_action")],
        ensure_ascii=False,
    ).lower()
    for pat in _FOUNDER_INVITE_PATTERNS:
        if re.search(pat, blob, re.I):
            raise RuntimeError(f"founder invitation blocked on hub write: {pat}")


def write_panel_outputs(payload: dict, *, json_only: bool = False) -> None:
    global _HUB_CACHE, _HUB_CACHE_AT
    try:
        from governance_projection_g3_v1 import assert_projection_write_allowed  # noqa: WPS433

        assert_projection_write_allowed(["hub"])
    except Exception as exc:
        import os

        if os.environ.get("SINA_G3_ENFORCE", "1") != "0":
            raise RuntimeError(str(exc)) from exc
    out_json = PANEL_DIR / "command-data.json"
    out_canonical = PANEL_DIR / "command-data-canonical.json"
    out_runtime = PANEL_DIR / "command-data-runtime.json"
    out_shell = PANEL_DIR / "command-data-shell.json"
    shell = PANEL_DIR / "assets" / "shell.html"
    out_html = PANEL_DIR / "index.html"
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    _patch_founder_guard_copy(payload)
    _assert_founder_guard_copy_clean(payload)
    try:
        from hub_projection_canonical_v1 import split_hub_projection  # noqa: WPS433

        canonical_row, runtime_row = split_hub_projection(payload)
        _write_text_atomic(
            out_canonical,
            json.dumps(canonical_row, ensure_ascii=False, separators=(",", ":")),
        )
        _write_text_atomic(
            out_runtime,
            json.dumps(runtime_row, ensure_ascii=False, separators=(",", ":")),
        )
    except Exception:
        pass
    full_text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    shell_row = build_shell_payload(payload)
    try:
        from hub_sync_slim_v1 import read_shell_generation_id  # noqa: WPS433

        shell_row["generation_id"] = read_shell_generation_id() or 1
    except Exception:
        shell_row["generation_id"] = 1
    shell_text = json.dumps(shell_row, ensure_ascii=False, separators=(",", ":"))
    _write_text_atomic(out_json, full_text)
    _write_text_atomic(out_shell, shell_text)
    ok, heal_msg = verify_command_data_atomic()
    if not ok:
        ok, heal_msg = heal_command_data_shell_from_disk(force=True)
        if not ok:
            raise RuntimeError(f"command-data shell verify/heal failed: {heal_msg}")
    with _HUB_LOCK:
        _HUB_CACHE = payload
        _HUB_CACHE_AT = time.monotonic()
    if shell.is_file() and not json_only:
        stamp = (payload.get("built_at") or "").replace(":", "").replace("+", "")[:19] or "0"
        html = shell.read_text(encoding="utf-8").replace(
            "  <!-- COMMAND_DATA_SCRIPT -->",
            '  <script>window.__COMMAND_DATA_LAZY=true;</script>',
        ).replace("__BUILD_STAMP__", stamp)
        _write_text_atomic(out_html, html)


def mark_todo_done(todo_id: str) -> dict:
    data = load_json(PROGRESS)
    if not data:
        return {"ok": False, "error": "PROGRAM_PROGRESS.json missing"}
    found = False
    for t in data.get("todos") or []:
        if t.get("id") == todo_id:
            t["status"] = "done"
            found = True
            break
    if not found:
        return {"ok": False, "error": f"todo {todo_id} not found"}
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["updated_by"] = "sina-command-api"
    PROGRESS.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"ok": True, "id": todo_id}

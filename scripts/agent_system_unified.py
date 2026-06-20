#!/usr/bin/env python3
"""Whole-system unifying brief — all rules visible to every agent via Sina Command."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agent_workspace_registry import AGENT_WORKSPACES
from founder_law import founder_law_payload

SOURCE_A = Path(__file__).resolve().parents[1]
SINA_HOME = Path.home() / ".sina"
FOUNDER_DIRECTIVES_PATH = SINA_HOME / "founder-directives.jsonl"
HUB_URL = "http://127.0.0.1:13020"

AUTHORITY_RULES: list[dict[str, str]] = [
    {"id": "ECOSYSTEM", "path": "SINA_OS_SSOT_LOCKED.md", "title": "Sina OS SSOT", "governs": "Mono structure, ports, phases"},
    {"id": "GOVERNANCE_ENTRY", "path": "SINA_GOVERNANCE_ENTRY_LOCKED_v1.md", "title": "Governance entry", "governs": "Router — pick branch, do not read 49 files"},
    {"id": "NO_TERMINAL", "path": "SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md", "title": "No Terminal (founder)", "governs": "Founder clicks only — executor runs shell or one-tap Actions"},
    {"id": "RULES_LOOP", "path": "AGENT_RULES_IN_CHARGE_LOCKED_v1.md", "title": "Rules in charge", "governs": "Search existing rule — supersession — never parallel duplicate"},
    {"id": "AUTHORITY_INDEX", "path": "SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md", "title": "Authority index", "governs": "Which law wins per topic"},
    {"id": "ALIGNMENT", "path": "SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md", "title": "Source alignment", "governs": "Locked source vs suggestions"},
    {"id": "CRITIC", "path": "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md", "title": "External critic", "governs": "GPT paste = compare only"},
    {"id": "EDIT_LOCK", "path": "SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md", "title": "Edit lock", "governs": "Who may edit SourceA"},
    {"id": "FLEET", "path": "AGENT_GOVERNANCE_INDEX_LOCKED_v1.md", "title": "Agent fleet", "governs": "Eight private agents + forbidden paths"},
    {"id": "UNIFY", "path": "AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md", "title": "Ecosystem unification", "governs": "App as pre-unifying hub"},
    {"id": "MIND_SHARE", "path": "AGENT_MIND_SHARE_LOCKED_v1.md", "title": "Mind Share", "governs": "Cross-agent learning + paradoxes"},
    {"id": "COUNCIL", "path": "AGENT_COUNCIL_ROOM_LOCKED_v1.md", "title": "Council Room", "governs": "Report channels + discourse"},
    {"id": "APP_HUB", "path": "AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md", "title": "App as unifying hub", "governs": "Start every session in Council Room"},
    {"id": "APP_BLUEPRINT", "path": "AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md", "title": "Agent app use blueprint", "governs": "Full E2E roles, tasks, access, APIs — all agents"},
    {"id": "VAULT", "path": "AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md", "title": "Workspace vault", "governs": "Middle layer — deposit all docs + activity in app"},
    {"id": "NO_MP_AGENT", "path": "AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md", "title": "MergePack not an agent", "governs": "MergePack = semi-separate lane — not private agent registry"},
    {"id": "GOV_UNIFY", "path": "GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md", "title": "Governance unification", "governs": "Batch intake merge/archive"},
    {"id": "JUDGMENT", "path": "AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md", "title": "Decision stack", "governs": "Smart judgment hierarchy"},
    {"id": "CONSOLIDATION", "path": "AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md", "title": "Sprint consolidation", "governs": "Preserved conclusions + open decisions + reserved build queue"},
    {"id": "ACE", "path": "AUTO_CONFLICT_ENGINE_V3_LOCKED.md", "title": "ACE v3", "governs": "Conflict planes — never block fleet"},
    {"id": "WTM", "path": "WORLD_TARGET_MODEL_MAP_LOCKED_v5.md", "title": "World Target Model", "governs": "33-step upgrade map"},
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_founder_directives(limit: int = 40) -> list[dict]:
    if not FOUNDER_DIRECTIVES_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in FOUNDER_DIRECTIVES_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    rows.sort(key=lambda r: r.get("at") or "", reverse=True)
    return rows[:limit]


def _append_founder_directive(text: str, *, source: str = "asf") -> dict:
    text = (text or "").strip()
    if len(text) < 8:
        return {"ok": False, "error": "Directive must be at least 8 characters"}
    row = {
        "id": f"DIR-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "text": text[:2000],
        "source": source,
        "visible_to": "all_agents",
    }
    SINA_HOME.mkdir(parents=True, exist_ok=True)
    with FOUNDER_DIRECTIVES_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    try:
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from founder_input_cascade_v1 import cascade_founder_input  # noqa: WPS433

        cascade_founder_input(text, source=f"agent_system_unified:{source}")
    except Exception:
        pass
    return {"ok": True, "directive": row}


def _master_orders_items() -> list[dict]:
    path = SOURCE_A / "sina-bowl" / "MASTER_ORDERS.json"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    out: list[dict] = []
    for sec in data.get("sections") or []:
        for it in sec.get("items") or []:
            if (it.get("status") or "").lower() in ("active", "locked"):
                out.append(
                    {
                        "section": sec.get("title"),
                        "id": it.get("id"),
                        "text": it.get("text"),
                        "status": it.get("status"),
                    }
                )
    return out


def _all_rules_visible() -> list[dict]:
    try:
        from hub_essentials_index import READ_CHAIN  # noqa: WPS433

        chain = list(READ_CHAIN)
    except Exception:
        chain = []
    seen = {r["path"] for r in chain}
    rules: list[dict] = []
    for i, row in enumerate(chain):
        rules.append(
            {
                "tier": "read_chain",
                "order": i + 1,
                "path": row["path"],
                "title": row["title"],
                "why": row.get("why", ""),
                "visible_to": "all_agents",
            }
        )
    for j, row in enumerate(AUTHORITY_RULES):
        if row["path"] in seen:
            continue
        rules.append(
            {
                "tier": "authority",
                "order": len(chain) + j + 1,
                "path": row["path"],
                "title": row["title"],
                "why": row.get("governs", ""),
                "visible_to": "all_agents",
            }
        )
        seen.add(row["path"])
    return rules


def _agent_lane_summary() -> list[dict]:
    return [
        {
            "id": w["id"],
            "label": w["label"],
            "lane": w.get("lane"),
            "repo_root": w.get("repo_root"),
            "governance_focus": w.get("governance_focus", ""),
            "hub_tab": f"workspace-{w['id']}",
            "may_edit_source_a": bool(w.get("may_edit_source_a")),
        }
        for w in AGENT_WORKSPACES
    ]


def _progress_snapshot(hub: dict | None) -> dict:
    hub = hub or {}
    sr = hub.get("system_roadmap") or {}
    ui = sr.get("ui_contract") or {}
    cc = hub.get("command_center") or {}
    p0 = (cc.get("founder") or {}).get("p0") or {}
    return {
        "wtm_step": ui.get("current_strategic_step") or sr.get("current_strategic_step"),
        "do_now": (ui.get("do_now") or {}).get("label"),
        "p0_title": p0.get("title"),
        "p0_next": p0.get("next_action"),
        "payload_version": ui.get("payload_version") or sr.get("version"),
    }


def _conflict_unification(hub: dict | None) -> dict:
    hub = hub or {}
    cr = hub.get("conflict_room") or {}
    council = hub.get("council_room") or {}
    cases = cr.get("cases") or []
    open_cases = [c for c in cases if (c.get("status") or "") not in ("closed", "resolved")]
    return {
        "open_conflicts": len(open_cases),
        "paradox_signals": council.get("paradox_count") or len(council.get("paradoxes") or []),
        "mind_shares": council.get("mind_share_count") or len(council.get("mind_share") or []),
        "resolve_via": [
            {"tab": "conflict-room", "label": "Conflict Room — ACE triage"},
            {"tab": "council-room", "label": "Council Room — paradox + mind share"},
            {"tab": "backlog", "label": "Backlog — agent reports"},
        ],
        "law": "Never block whole fleet — continue lane work after reporting.",
    }


def _strategic_slice_brief_block() -> list[str]:
    try:
        from council_strategic_brief import strategic_brief_payload  # noqa: WPS433

        sb = strategic_brief_payload()
    except Exception:
        return []
    if not sb.get("ok"):
        return []
    lines = [
        "STRATEGIC PRIORITY (FOUNDER VERDICT — LOCKED):",
        f"  {sb.get('verdict_one_line', '')}",
        f"  Doc: {sb.get('doc_path', '')}",
        "  Workstreams:",
    ]
    for ws in sb.get("workstreams") or []:
        lines.append(f"    • {ws.get('title')} ({ws.get('validator', '')})")
    lines.append(f"  NOT NOW: {', '.join(sb.get('deferred') or [])}")
    lines.append(f"  Lanes: {', '.join(sb.get('scope_lanes') or [])}")
    return lines


def _build_copy_brief(
    *,
    rules: list[dict],
    orders: list[dict],
    directives: list[dict],
    lanes: list[dict],
    progress: dict,
    conflict: dict,
    founder: dict,
) -> str:
    fl = founder.get("founder_law_agent") or founder.get("founder_law") or ""
    lines = [
        "═ SOURCEA — WHOLE SYSTEM BRIEF (all agents · paste once) ═",
        f"Worker Hub: {HUB_URL}/  ·  Machine Hub: {HUB_URL}/machines/",
        "",
        "SESSION START (every agent, every chat):",
        "1. `agent_session_gate_run_v1.py --role <role>` — session gate only (no incident compendium).",
        "2. Daily: RUN INBOX in Cursor Worker chat — Worker Hub glance optional.",
        "3. Deposit deliverables to workspace vault logged when shipping.",
        "4. Work in YOUR repo only — never edit ~/Desktop/SourceA (SourceA Worker chat for hub code only).",
        "5. Hub bugs → POST /api/agent-review — Command brand DELETED.",
        "",
        "FOUNDER LAW:",
        fl,
        "",
        f"PROGRESS NOW: P0={progress.get('p0_title') or '—'} · next={progress.get('p0_next') or '—'}",
        f"WTM: {progress.get('do_now') or progress.get('wtm_step') or '—'}",
        f"OPEN CONFLICTS: {conflict.get('open_conflicts', 0)} · PARADOX SIGNALS: {conflict.get('paradox_signals', 0)}",
        "",
        *_strategic_slice_brief_block(),
        "",
        "RULES IN CHARGE NOW (highlighted in hub — same for all 8 agents):",
        "  Apex + session + founder live + current WTM — see Council Room panel",
        "",
        "ALL RULES (full inclusive index — open in hub Doc library):",
    ]
    for r in rules[:32]:
        lines.append(f"  {r.get('order', '')}. {r.get('title')} — {r.get('path')} — {r.get('why', '')[:80]}")
    if len(rules) > 32:
        lines.append(f"  … +{len(rules) - 32} more in Council Room / Essentials read chain")
    lines.append("")
    lines.append("FOUNDER ORDERS (active):")
    for o in orders[:16]:
        lines.append(f"  • [{o.get('section')}] {o.get('text')}")
    if directives:
        lines.append("")
        lines.append("FOUNDER DIRECTIVES (ASF said in chat — unified here):")
        for d in directives[:12]:
            lines.append(f"  • {d.get('text', '')[:200]}")
    lines.append("")
    lines.append("NINE LANES (pick one per chat):")
    for lane in lanes:
        lock = "maintainer" if lane.get("may_edit_source_a") else "SourceA locked"
        lines.append(f"  • {lane.get('label')} ({lane.get('id')}) — {lane.get('governance_focus', '')[:60]} [{lock}]")
    lines.append("")
    lines.append("END BRIEF — app is the unifying place; do not ask ASF to re-paste rules.")
    return "\n".join(lines)


def system_unified_payload(*, hub_payload: dict | None = None) -> dict:
    hub = hub_payload or {}
    founder = founder_law_payload()
    rules = _all_rules_visible()
    orders = _master_orders_items()
    directives = _load_founder_directives()
    lanes = _agent_lane_summary()
    progress = _progress_snapshot(hub)
    conflict = _conflict_unification(hub)
    copy_brief = _build_copy_brief(
        rules=rules,
        orders=orders,
        directives=directives,
        lanes=lanes,
        progress=progress,
        conflict=conflict,
        founder=founder,
    )
    hub_stub = {
        **(hub_payload or {}),
        "system_unified": {
            "founder_orders": orders,
            "founder_directives": directives,
        },
        "essay_discourse": (hub_payload or {}).get("essay_discourse"),
        "conflict_room": (hub_payload or {}).get("conflict_room"),
        "system_roadmap": (hub_payload or {}).get("system_roadmap"),
        "command_center": (hub_payload or {}).get("command_center"),
        "council_room": (hub_payload or {}).get("council_room"),
    }
    try:
        from agent_rules_in_charge import rules_in_charge_payload  # noqa: WPS433

        rules_charge = rules_in_charge_payload(hub_payload=hub_stub, all_rules=rules)
        rules = rules_charge.get("all_rules_indexed") or rules
    except Exception:
        rules_charge = {"ok": False, "in_charge_now": [], "context_groups": []}
    return {
        "ok": True,
        "built_at": _now(),
        "hub_url": HUB_URL,
        "council_url": f"{HUB_URL}/?tab=council-room",
        "agent_hub_url": f"{HUB_URL}/?tab=agent-loop",
        "law_doc": "AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md",
        "tagline": "SourceA disk + Cursor Worker chat — legacy hub archived",
        "founder_law": founder,
        "all_rules": rules,
        "all_rules_count": len(rules),
        "rules_in_charge": rules_charge,
        "in_charge_count": rules_charge.get("in_charge_count", 0),
        "founder_orders": orders,
        "founder_directives": directives,
        "agent_lanes": lanes,
        "progress": progress,
        "conflict_unification": conflict,
        "entry_steps": [
            {"order": 1, "tab": "council-room", "label": "Council Room", "desc": "Whole system + all rules + mind share"},
            {"order": 2, "tab": "agent-loop", "label": "Agent hub", "desc": "Pick your private agent page"},
            {"order": 3, "tab": None, "label": "Workspace vault", "desc": "Deposit docs + log activity (middle layer)"},
            {"order": 4, "tab": "agent-scoreboard", "label": "Scoreboard", "desc": "File session report — auto-checks green"},
            {"order": 5, "tab": None, "label": "Your repo", "desc": "Implement in allowed repo_root only"},
            {"order": 6, "tab": "council-room", "label": "Report back", "desc": "Mind share / conflict / backlog"},
        ],
        "copy_brief": copy_brief,
        "copy_brief_chars": len(copy_brief),
        "directives_path": str(FOUNDER_DIRECTIVES_PATH),
        "strategic_brief": _strategic_brief_payload_safe(),
    }


def _strategic_brief_payload_safe() -> dict:
    try:
        from council_strategic_brief import strategic_brief_payload  # noqa: WPS433

        return strategic_brief_payload()
    except Exception:
        return {"ok": False}


def handle_unified_action(body: dict) -> dict:
    action = (body.get("action") or "").strip().lower()
    if action == "add_directive":
        return _append_founder_directive(body.get("text") or body.get("directive") or "")
    if action in ("list", "brief"):
        return system_unified_payload()
    return {"ok": False, "error": f"unknown action: {action}"}

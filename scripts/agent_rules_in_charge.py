#!/usr/bin/env python3
"""Rules in charge — which laws govern NOW, with context, highlights, full inclusive index."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

LAW_DOC = "AGENT_RULES_IN_CHARGE_LOCKED_v1.md"

# path → static charge metadata (particular per-rule context)
RULE_CHARGE_META: dict[str, dict[str, Any]] = {
    "brain-os/law/SINA_OS_SSOT_LOCKED.md": {
        "charge_level": "apex",
        "context_id": "ecosystem",
        "context_label": "Whole ecosystem",
        "governs_now": "Mono structure, ports, phases — wins all subordinate docs",
    },
    "SINA_GOVERNANCE_ENTRY_LOCKED_v1.md": {
        "charge_level": "apex",
        "context_id": "routing",
        "context_label": "Law routing",
        "governs_now": "Pick one branch — do not read 49 files",
    },
    "SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md": {
        "charge_level": "apex",
        "context_id": "authority",
        "context_label": "Who wins on conflict",
        "governs_now": "LAW PURITY SSOT — law=law 100% · one topic · no dup · no mix · ask if unknown",
    },
    "SINA_COMMAND_DEACTIVATED_INCIDENT_READ_POLICY_LOCKED_v1.md": {
        "charge_level": "apex",
        "context_id": "founder_ui",
        "context_label": "Founder daily ops",
        "governs_now": "PERMANENT — never legacy hub brand in founder text · RUN INBOX · session gate not read-all-incidents",
    },
    "AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "agent_session",
        "context_label": "Every agent session",
        "governs_now": "Start Council Room — one brief for all",
    },
    "AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "agent_session",
        "context_label": "Every agent session",
        "governs_now": "Full E2E roles, tasks, APIs — 7 agents",
    },
    "AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "vault",
        "context_label": "Middle layer / evidence",
        "governs_now": "Deposit all work in app — not chat-only",
    },
    "AGENT_SCOREBOARD_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "scoreboard",
        "context_label": "Session compliance",
        "governs_now": "File report — ASF verify column ✓",
    },
    "AGENT_ESSAY_DISCOURSE_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "essay",
        "context_label": "Essay assignments",
        "governs_now": "Same subject — all agents write — mark best",
    },
    "AGENT_COUNCIL_ROOM_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "council",
        "context_label": "Council Room",
        "governs_now": "Report channels + discourse",
    },
    "brain-os/law/COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "council",
        "context_label": "Strategic slice",
        "governs_now": "Next build = Eval-1 + L0/L1 + ENFORCE map — not new D-module",
    },
    "brain-os/law/STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md": {
        "charge_level": "session",
        "context_id": "wtm",
        "context_label": "Big picture + next steps",
        "governs_now": "Goals, pendings, phase plan 0–5 — Eval-1b before dispatch/L8",
    },
    "AGENT_MIND_SHARE_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "mind_share",
        "context_label": "Cross-agent learning",
        "governs_now": "Insights + paradox compare",
    },
    "AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "agent_session",
        "context_label": "Every agent session",
        "governs_now": "7 agents · never edit SourceA — SinaaiDataBase workspace for hub code only",
    },
    "SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md": {
        "charge_level": "operational",
        "context_id": "edit_lock",
        "context_label": "Editing SourceA / hub",
        "governs_now": "Only SinaaiDataBase workspace + ASF may edit SourceA hub",
    },
    "AGENT_GOVERNANCE_INDEX_LOCKED_v1.md": {
        "charge_level": "operational",
        "context_id": "fleet",
        "context_label": "Agent fleet scope",
        "governs_now": "7 private agents + forbidden paths",
    },
    "AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md": {
        "charge_level": "operational",
        "context_id": "semi_separate",
        "context_label": "Semi-separate lanes",
        "governs_now": "MergePack = products/repos — not private agent",
    },
    "brain-os/law/SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md": {
        "charge_level": "operational",
        "context_id": "semi_separate",
        "context_label": "Semi-separate lanes",
        "governs_now": "Wire · MergePack · Prompt OS boundaries",
    },
    "SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md": {
        "charge_level": "operational",
        "context_id": "safety",
        "context_label": "Safety / inject",
        "governs_now": "Never re-enable Cursor auto-paste",
    },
    "SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md": {
        "charge_level": "operational",
        "context_id": "conflict",
        "context_label": "Law conflicts",
        "governs_now": "ACE triage — continue work",
    },
    "brain-os/law/AUTO_CONFLICT_ENGINE_V3_LOCKED.md": {
        "charge_level": "operational",
        "context_id": "conflict",
        "context_label": "Law conflicts",
        "governs_now": "DESIGN / EXECUTION / DELIVERY planes",
    },
    "SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md": {
        "charge_level": "operational",
        "context_id": "incident",
        "context_label": "Incident learning",
        "governs_now": "Weekly share + certify",
    },
    "brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md": {
        "charge_level": "progress",
        "context_id": "wtm",
        "context_label": "Build order (WTM)",
        "governs_now": "33-step upgrade map — current step governs build",
    },
    "SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md": {
        "charge_level": "operational",
        "context_id": "alignment",
        "context_label": "Suggestions vs locked source",
        "governs_now": "Locked source wins — 12-order procedure",
    },
    "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md": {
        "charge_level": "operational",
        "context_id": "critic",
        "context_label": "External GPT paste",
        "governs_now": "Compare only — never steer build",
    },
    "AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md": {
        "charge_level": "reference",
        "context_id": "judgment",
        "context_label": "Before non-trivial builds",
        "governs_now": "Decision inventory hierarchy",
    },
    "SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "agent_session",
        "context_label": "Every agent session",
        "governs_now": "Hyper-active conduct — disk result, options, golden insight, founder next actions",
    },
    "SOURCEA_SYSTEM_INTEGRITY_100_STEP_PLAYBOOK_LOCKED_v1.md": {
        "charge_level": "task",
        "context_id": "system_integrity",
        "context_label": "Whole-system audit",
        "governs_now": "100-step playbook — LAW/MACHINE/PROJECTION · Founder forks · Canvas tick-check",
    },
    "SOURCEA_COMPLEX_SITUATION_FORK_MACHINE_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "complex_fork",
        "context_label": "Mega chat · Brain · multi-fork",
        "governs_now": "Fork inventory · Effect per option · ASF FORK-MACHINE order · no vague confirm",
    },
    "SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "five_step_apex",
        "context_label": "Every session — apex",
        "governs_now": "SCAN SAY PICK PROVE SHIP — daily autonomous progress machine",
    },
    "SOURCEA_INTEGRITY_STACK_UNIFIED_BLUEPRINT_BATCH_2_LOCKED_v1.md": {
        "charge_level": "reference",
        "context_id": "integrity_batch_2",
        "context_label": "Integrity stack map",
        "governs_now": "Which doc when · hierarchy · one ASF prefix — pointer hub only",
    },
    "SOURCEA_CROSS_DOC_LINKAGE_AND_AUDIT_LOCKED_v1.md": {
        "charge_level": "reference",
        "context_id": "cross_doc_linkage",
        "context_label": "Cross-doc cluster audit",
        "governs_now": "SESSION-INTEGRITY-10 + EXPAND-11 · human vs machine channel — pointer only",
    },
    "SOURCEA_SSOT_FOUNDATION_WRITING_GUIDE_LOCKED_v1.md": {
        "charge_level": "reference",
        "context_id": "ssot_foundation",
        "context_label": "Human SSOT foundation",
        "governs_now": "018 egg · subject→SSOT→blueprint→hatch — before writing new law",
    },
    "SOURCEA_LOST_LINK_RECOVERY_ETHICS_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "lost_link_recovery",
        "context_label": "Lost link recovery",
        "governs_now": "FOUND = complete reward · transcript + disk — @sina-conscious-recovery",
    },
    "SOURCEA_ECOSYSTEM_MASTER_CATALOG_LOCKED_v1.md": {
        "charge_level": "reference",
        "context_id": "master_catalog",
        "context_label": "Ecosystem inventory",
        "governs_now": "T0–T12 threads · counts · live vs paper — one page",
    },
    "SOURCEA_TODAY_SESSION_UNIFIED_CLOSEOUT_RECEIPT_2026-06-11_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "today_closeout",
        "context_label": "2026-06-11 session receipt",
        "governs_now": "Nothing left behind — full wire · proof table · founder next 3",
    },
    "SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md": {
        "charge_level": "reference",
        "context_id": "live_gov_bp",
        "context_label": "Live governance",
        "governs_now": "P0–P7 · truth tree down-only · propagation cascade",
    },
    "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "live_decision_form",
        "context_label": "Live founder decision form",
        "governs_now": "SCAN pending + open questions · evidence-only ANSWERED · CAPS=non-caps",
    },
    "SOURCEA_FOUNDER_MESSAGE_NORMALIZATION_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "founder_msg_norm",
        "context_label": "Founder message normalization",
        "governs_now": "ALL-CAPS = mixed case — parse PICK without case friction",
    },
    "SOURCEA_GOVERNANCE_EVENT_SPINE_SCHEMA_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "gov_event_spine",
        "context_label": "Governance event spine G1+G2",
        "governs_now": "Spine ledger + reference graph — projections materialized only",
    },
    "SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "agent_session",
        "context_label": "Every agent session",
        "governs_now": "Founder clicks only — executor runs shell",
    },
    "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md": {
        "charge_level": "reference",
        "context_id": "wtm",
        "context_label": "GPT/Claude synthesis",
        "governs_now": "Saved critic analysis + live results vs pendings",
    },
    "AGENT_RULES_IN_CHARGE_LOCKED_v1.md": {
        "charge_level": "session",
        "context_id": "rules_loop",
        "context_label": "Rules loop",
        "governs_now": "Check in-charge rules every session — supersession law",
    },
}

# Levels that count as "in charge NOW" (highlighted)
HIGHLIGHT_LEVELS = frozenset({"apex", "session", "founder_live", "progress_active"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _context_snapshot(hub: dict) -> dict:
    cc = hub.get("command_center") or {}
    p0 = (cc.get("founder") or {}).get("p0") or {}
    sr = hub.get("system_roadmap") or {}
    ui = sr.get("ui_contract") or {}
    essay = hub.get("essay_discourse") or {}
    topics = essay.get("topics") or []
    active_essay = topics[0] if topics else {}
    council = hub.get("council_room") or {}
    try:
        from agent_workspace_registry import AGENT_WORKSPACES

        agent_count = len(AGENT_WORKSPACES)
    except Exception:
        agent_count = 7
    return {
        "built_at": _now(),
        "p0_title": p0.get("title"),
        "p0_next": p0.get("next_action"),
        "wtm_step": ui.get("current_strategic_step") or sr.get("current_strategic_step"),
        "wtm_do_now": (ui.get("do_now") or {}).get("label"),
        "council_phase": council.get("phase_label") or "Mind Share",
        "agent_count": agent_count,
        "essay_subject": active_essay.get("title") or active_essay.get("subject_norm"),
        "open_conflicts": (hub.get("conflict_room") or {}).get("open_count"),
        "summary": "Inclusive: all rules in app for all agents · Exclusive: particular in-charge-now highlights",
    }


def _annotate_rule(path: str, base: dict, *, hub: dict, extra_reason: str = "") -> dict:
    meta = RULE_CHARGE_META.get(path, {})
    level = meta.get("charge_level", "reference")
    ctx = hub.get("context_snapshot") or _context_snapshot(hub)

    # WTM map is progress_active when we have a current step
    if path == "brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md" and ctx.get("wtm_step"):
        level = "progress_active"

    # Boost conflict rules when open conflicts
    open_c = ctx.get("open_conflicts") or 0
    if open_c and path in (
        "SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md",
        "brain-os/law/AUTO_CONFLICT_ENGINE_V3_LOCKED.md",
    ):
        level = "progress_active"

    in_charge = level in HIGHLIGHT_LEVELS
    reason = extra_reason or meta.get("governs_now") or base.get("why", "")
    if level == "progress_active" and path.startswith("WORLD"):
        reason = f"Current WTM step: {ctx.get('wtm_do_now') or ctx.get('wtm_step')}"

    return {
        **base,
        "path": path,
        "in_charge_now": in_charge,
        "highlight": in_charge,
        "charge_level": level,
        "context_id": meta.get("context_id", "reference"),
        "context_label": meta.get("context_label", "Reference / read chain"),
        "charge_reason": reason,
    }


def _founder_live_rules(hub: dict) -> list[dict]:
    su = hub.get("system_unified") or {}
    rows: list[dict] = []
    for d in (su.get("founder_directives") or [])[:8]:
        rows.append(
            {
                "tier": "founder_live",
                "path": "__founder_directive__",
                "title": f"Founder directive · {d.get('id', '')}",
                "why": (d.get("text") or "")[:240],
                "visible_to": "all_agents",
                "in_charge_now": True,
                "highlight": True,
                "charge_level": "founder_live",
                "context_id": "founder",
                "context_label": "ASF said in chat",
                "charge_reason": "Live founder directive — visible to all on refresh",
                "directive_id": d.get("id"),
                "at": d.get("at"),
            }
        )
    for o in (su.get("founder_orders") or [])[:6]:
        rows.append(
            {
                "tier": "founder_live",
                "path": "__master_order__",
                "title": f"Founder order · {o.get('id', '')}",
                "why": (o.get("text") or "")[:240],
                "visible_to": "all_agents",
                "in_charge_now": True,
                "highlight": True,
                "charge_level": "founder_live",
                "context_id": "orders",
                "context_label": "MASTER_ORDERS active",
                "charge_reason": f"Active order [{o.get('section', '')}]",
                "order_id": o.get("id"),
            }
        )
    return rows


def rules_in_charge_payload(*, hub_payload: dict | None = None, all_rules: list[dict] | None = None) -> dict:
    hub = dict(hub_payload or {})
    hub["context_snapshot"] = _context_snapshot(hub)

    annotated: list[dict] = []
    if all_rules:
        for r in all_rules:
            annotated.append(_annotate_rule(r.get("path", ""), r, hub=hub))
    else:
        try:
            from agent_system_unified import _all_rules_visible  # noqa: WPS433

            for r in _all_rules_visible():
                annotated.append(_annotate_rule(r.get("path", ""), r, hub=hub))
        except Exception:
            pass

    founder_live = _founder_live_rules(hub)
    in_charge_now = [r for r in annotated if r.get("in_charge_now")]
    in_charge_now = sorted(
        in_charge_now,
        key=lambda x: (
            0 if x.get("charge_level") == "apex" else 1 if x.get("charge_level") == "founder_live" else 2,
            x.get("order", 99),
        ),
    )
    in_charge_now = founder_live + in_charge_now

    # Group by context for relatable structure
    by_context: dict[str, dict] = {}
    for r in annotated + founder_live:
        if not r.get("highlight"):
            continue
        cid = r.get("context_id") or "other"
        if cid not in by_context:
            by_context[cid] = {
                "id": cid,
                "label": r.get("context_label") or cid,
                "rules": [],
            }
        by_context[cid]["rules"].append(r)

    contexts_ordered = [
        "founder",
        "orders",
        "ecosystem",
        "routing",
        "authority",
        "agent_session",
        "vault",
        "scoreboard",
        "essay",
        "council",
        "mind_share",
        "edit_lock",
        "fleet",
        "semi_separate",
        "safety",
        "conflict",
        "incident",
        "wtm",
        "alignment",
        "critic",
    ]
    context_groups = [by_context[c] for c in contexts_ordered if c in by_context]

    reference_rules = [r for r in annotated if not r.get("highlight")]

    return {
        "ok": True,
        "law_doc": LAW_DOC,
        "context_now": hub["context_snapshot"],
        "in_charge_count": len(in_charge_now),
        "highlight_count": len(in_charge_now),
        "total_rules": len(annotated),
        "in_charge_now": in_charge_now[:24],
        "context_groups": context_groups,
        "all_rules_indexed": annotated,
        "reference_rules_count": len(reference_rules),
        "tagline": "Inclusive: all rules in app for all agents · Exclusive: particular laws in charge for this moment",
        "charge_levels": {
            "apex": "Always governs — wins on conflict",
            "founder_live": "ASF orders/directives — live now",
            "session": "In charge every agent session",
            "progress_active": "In charge for current WTM / open conflicts",
            "operational": "In charge when you touch that topic",
            "reference": "Background read chain — open when relevant",
        },
    }


def enrich_shared_rules_digest(chain: list[dict], hub: dict | None = None) -> list[dict]:
    """Council Room shared rules with in_charge flags."""
    hub = hub or {}
    out = []
    for row in chain:
        base = {"path": row["path"], "title": row["title"], "why": row.get("why", ""), "tier": "digest"}
        out.append(_annotate_rule(row["path"], base, hub=hub))
    return sorted(out, key=lambda r: (0 if r.get("highlight") else 1, r.get("path", "")))

#!/usr/bin/env python3
"""Per-lane briefs + universal Cursor session brief (any chat, advisory-aware)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sina_command_lib import PROMPTOS_PASTE, REPOS_REGISTRY, parse_repo_plan, _repo_root

SOURCE_A = Path(__file__).resolve().parents[1]
REPO_NOTICES_DIR = SOURCE_A / "founder" / "repo-agent-notices"
SEMI_LANE_IDS = frozenset({"wire", "cursor_os_pro", "mergepack", "promptos", "noetfield_cloud"})

CURSOR_OS_PRO_SPEC: dict = {
    "id": "cursor_os_pro",
    "name": "Cursor OS Pro",
    "root_key": "Cursor OS Pro",
    "plan_rel": None,
    "workspace": "Cursor OS Pro",
    "thread": "THREAD-CURSOR-OS-PRO",
    "plane": "Commercial SKU",
    "semantic_key": "cursor_os_pro",
}

NOETFIELD_CLOUD_SPEC: dict = {
    "id": "noetfield_cloud",
    "name": "Noetfield (cloud / GitHub ship)",
    "root_key": "Noetfield",
    "plan_rel": "os/plan.json",
    "workspace": "Noetfield",
    "thread": "THREAD-PORTFOLIO",
    "plane": "SHIP",
    "semantic_key": "noetfield_cloud",
}

SUBJECT_TO_LANE: dict[str, str] = {
    "subj-trustfield": "trustfield",
    "subj-mono": "mono",
    "subj-virlux": "virlux",
    "subj-noetfield": "noetfield",
    "subj-777": "seven77",
    "subj-mergepack-repo": "mergepack",
    "subj-wire-repo": "wire",
    "subj-promptos-repo": "promptos",
    "subj-form-pdf": "mergepack",
    "THREAD-WIRE": "wire",
    "THREAD-MERGEPACK": "mergepack",
    "THREAD-PROMPTOS": "promptos",
    "THREAD-PORTFOLIO": "trustfield",
}

TAB_DEFAULT_LANE: dict[str, str] = {
    "products": "mergepack",
    "prompt-os": "promptos",
    "fleet": "hq",
}


def _paste_path(semantic_key: str | None, repo_id: str) -> Path | None:
    if semantic_key:
        p = PROMPTOS_PASTE / f"ready_to_paste_{semantic_key}.txt"
        if p.is_file():
            return p
    for alt in (repo_id, repo_id.replace("-", "_")):
        p = PROMPTOS_PASTE / f"ready_to_paste_{alt}.txt"
        if p.is_file():
            return p
    return None


def _short_label(name: str, repo_id: str) -> str:
    if repo_id == "seven77":
        return "777"
    if repo_id == "wire":
        return "AI Dev Bridge"
    if repo_id == "mono":
        return "Mono"
    return name.split()[0] if name else repo_id


def _repo_notice_excerpt(repo_id: str) -> str:
    if repo_id in SEMI_LANE_IDS:
        path = REPO_NOTICES_DIR / f"SEMI_NOTICE_{repo_id}_v1.md"
    else:
        path = REPO_NOTICES_DIR / f"REPO_NOTICE_{repo_id}_v1.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:12000]


def build_lane_brief(spec: dict) -> dict:
    plan = parse_repo_plan(spec)
    sk = spec.get("semantic_key")
    paste_file = _paste_path(sk, spec["id"])
    paste_text = ""
    if paste_file:
        paste_text = paste_file.read_text(encoding="utf-8", errors="replace")
    notice = _repo_notice_excerpt(spec["id"])
    root = _repo_root(spec)
    next_tasks = plan.get("next_tasks") or []
    task_lines = [t.get("text", str(t)) for t in next_tasks[:6]]
    header = [
        f"LANE BRIEF — {spec['name']}",
        f"Repo: {spec['id']} · Thread: {spec.get('thread', '—')} · Plane: {spec.get('plane', '—')}",
        f"Root: {root}",
        f"Active focus: {plan.get('active_focus') or '—'}",
    ]
    if task_lines:
        header.append("Next tasks (from plan):")
        header.extend(f"  • {t}" for t in task_lines)
    if plan.get("global_blocker"):
        blk = plan["global_blocker"]
        header.append(f"BLOCKER: {blk.get('item', '')} — {blk.get('reason', '')}")
    header.append("")
    blocks: list[str] = []
    if notice:
        label = "SEMI-SEPARATE LANE" if spec["id"] in SEMI_LANE_IDS else "REPO"
        blocks.append(f"══ SYSTEM UPDATE + {label} NOTICE (paste first) ══")
        blocks.append(notice)
        blocks.append("")
    blocks.append("\n".join(header))
    if paste_text:
        blocks.append("--- Cursor paste prompt (ready_to_paste) ---")
        blocks.append(paste_text)
    else:
        blocks.append(
            "(No ready_to_paste file — run: python3 scripts/build_repo_agent_notices.py "
            "then Morning dispatch on Actions/Daily.)"
        )
    full_text = "\n".join(blocks)

    rel = f"promptos:outputs/ready_to_paste/ready_to_paste_{sk or spec['id']}.txt"
    return {
        "repo_id": spec["id"],
        "label": spec["name"],
        "short_label": _short_label(spec["name"], spec["id"]),
        "thread": spec.get("thread"),
        "summary": task_lines[0] if task_lines else (plan.get("active_focus") or ""),
        "paste_path": rel,
        "has_paste": bool(paste_text),
        "paste_text": paste_text,
        "text": full_text,
        "copy_text": paste_text if paste_text else full_text,
    }


def lane_briefs_registry() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for spec in REPOS_REGISTRY:
        if spec["id"] in ("sourcea", "hq"):
            continue
        out[spec["id"]] = build_lane_brief(spec)
    for extra in (CURSOR_OS_PRO_SPEC, NOETFIELD_CLOUD_SPEC):
        if extra["id"] not in out:
            out[extra["id"]] = build_lane_brief(extra)
    return out


def _repo_lane_lines(repos: list[dict] | None) -> list[str]:
    lines: list[str] = []
    skip = {"sourcea", "hq"}
    for r in repos or []:
        rid = r.get("id") or ""
        if rid in skip:
            continue
        nt = r.get("next_tasks") or []
        task = ""
        if nt:
            t0 = nt[0]
            task = t0.get("text", str(t0)) if isinstance(t0, dict) else str(t0)
        task = (task or r.get("active_focus") or "—")[:200]
        blk = r.get("global_blocker")
        flag = " [BLOCKED]" if blk or r.get("blocked") else ""
        lines.append(f"  • {r.get('name', rid)} · {rid}{flag}: {task}")
    return lines


def build_universal_cursor_brief(
    *,
    bowl: dict,
    eco: dict | None = None,
    p0: dict | None = None,
    ai_advisory: dict | None = None,
    prompt_direction: dict | None = None,
    ops_blockers: list | None = None,
    founder: dict | None = None,
    repos: list[dict] | None = None,
    commitments: dict | None = None,
) -> dict:
    """
    Universal paste for ANY Cursor chat — triggers real work or a sharp brief+plan.
    Merges live bowl + plans + ops + AI advisory + confirmed direction when present.
    """
    sources: list[str] = ["bowl", "plans", "ops"]
    p0 = p0 or bowl.get("p0") or (founder or {}).get("p0") or {}
    founder = founder or {}
    lines: list[str] = [
        "CURSOR SESSION BRIEF — Sina OS (universal)",
        "Paste at the start of this chat (planning, Command, or any repo). Read fully before acting.",
        "",
        "══ AGENT CONTRACT ══",
        "1. Line 1 of your reply: state ONE active THREAD id (e.g. THREAD-FACTORY, THREAD-MERGEPACK, THREAD-PORTFOLIO).",
        "2. Line 2: one primary outcome for THIS session only (sub-steps OK if they serve that outcome).",
        "3. Use the live snapshot below — whole ecosystem, not only the last user message.",
        "4. Deliver either: (A) verifiable progress with evidence paths/commands, or (B) a brief + numbered plan if founder asked to plan only.",
        "5. Do not open unrelated repos, rewrite SSOT law, or start parked work unless listed under OPS or advisory.",
        "6. If this chat is repo-specific work, say so and use the lane paste from disk or Worker Hub → Repos.",
        "",
        "══ LAW (quick) ══",
        "• Read SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md + your repo notice (Repos → Copy lane brief).",
        "• Hub Essentials tab = full map (2026-06-04 upgrade). Personal DB = Layer A P0.",
        "• MergePack revenue ≠ M8 Wire automation — separate threads.",
        "• Factory P0 = RunReceipt (PASS/FAIL agent run artifacts).",
        "• Five delivery lanes: trustfield · mono · virlux · noetfield · seven77 — one lane focus per product chat.",
        "• SSOT when unclear: SINA_OS_SSOT_LOCKED.md · ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md",
        "",
    ]

    adv = (ai_advisory or {}).get("advisory") if (ai_advisory or {}).get("ok") else None
    if adv:
        sources.append("ai_advisory")
        lines.extend(["══ AI ADVISOR (latest — use as strategic lens) ══"])
        if adv.get("one_focus_today"):
            lines.append(f"One focus today: {adv['one_focus_today']}")
        for g in (adv.get("golden_connections") or [])[:4]:
            lines.append(
                f"  Link: {g.get('from', '?')} → {g.get('to', '?')}: {g.get('why', '')}"
            )
        lines.append("Upgrade suggestions:")
        for u in (adv.get("upgrade_suggestions") or [])[:6]:
            lines.append(
                f"  • [{u.get('priority', 'P1')}] {u.get('title', '')} — {u.get('action', '')} "
                f"({u.get('thread', '')})"
            )
        for r in (adv.get("risks") or [])[:4]:
            lines.append(f"  Risk: {r}")
        lines.append(
            f"(Advisory generated: {(ai_advisory or {}).get('generated_at', '—')}. "
            "Refresh: legacy /legacy/ AI Advisory or disk brief — RUN INBOX primary.)"
        )
        lines.append("")
    else:
        lines.extend(
            [
                "══ AI ADVISOR ══",
                "Not loaded — run disk brief or legacy AI Advisory, then copy Brief again.",
                "",
            ]
        )

    prop = (prompt_direction or {}).get("proposal")
    pdir_status = (prompt_direction or {}).get("status")
    if prop and pdir_status in ("proposed", "confirmed", "queued"):
        sources.append("prompt_direction")
        lines.extend(["══ PROMPT DIRECTION (from last planning reply) ══"])
        if prop.get("direction_title"):
            lines.append(f"Direction: {prop['direction_title']}")
        if prop.get("big_picture"):
            lines.append(f"Big picture: {prop['big_picture']}")
        if prop.get("connection_to_last_reply"):
            lines.append(f"Continues: {prop['connection_to_last_reply']}")
        lines.append("10-step outline (execute in order when building):")
        for step in (prop.get("prompt_outline") or [])[:10]:
            repo = step.get("repo") or "meta"
            lines.append(
                f"  {step.get('step', '?')}. {step.get('title', '')} [{repo}] — {step.get('intent', '')}"
            )
        lines.append("")

    lines.extend(["══ P0 & PROGRAMS (live) ══"])
    lines.append(
        f"P0: {p0.get('id', '—')} — {p0.get('title', '—')} · thread {p0.get('thread', '—')}"
    )
    if p0.get("next_action"):
        lines.append(f"P0 next action: {p0['next_action']}")
    for plan in (bowl.get("parallel_plans") or [])[:6]:
        lines.append(
            f"  • {plan.get('id')}: {plan.get('title', '')} — {plan.get('next_action', '')[:120]} "
            f"({plan.get('progress_pct', 0)}%)"
        )

    lines.extend(["", "══ MUST DO TODAY ══"])
    for m in (founder.get("must_do_today") or [])[:6]:
        lines.append(f"  • {m}")
    for todo in (bowl.get("open_todos") or [])[:5]:
        lines.append(f"  • [{todo.get('id', 'todo')}] {todo.get('text', todo)}")

    if ops_blockers:
        lines.extend(["", "══ OPS / BLOCKERS ══"])
        for o in ops_blockers[:6]:
            lines.append(f"  • [{o.get('severity', 'ops')}] {o.get('title', '')}: {o.get('action', '')}")

    drift = bowl.get("drift") or []
    if drift:
        lines.extend(["", "══ DRIFT (resolve — founder is law editor) ══"])
        for d in drift[:4]:
            lines.append(f"  • {d.get('message', d) if isinstance(d, dict) else d}")

    if repos:
        lines.extend(["", "══ PORTFOLIO LANES (next task each) ══"])
        lines.extend(_repo_lane_lines(repos))

    if eco:
        lines.append(
            f"\nEcosystem map: {eco.get('subject_count', 0)} subjects · "
            f"{eco.get('doc_links', 0)} doc links · {eco.get('chat_links', 0)} chat links "
            "(Worker Hub ecosystem map or disk index)."
        )

    comm = commitments or {}
    if comm.get("open_count"):
        lines.append(
            f"Track: {comm.get('open_count')} open commitments "
            f"({comm.get('needs_you', 0)} need you) — see `~/.sina/goal-progress-v1.json` or Worker Hub Track."
        )

    lines.extend(
        [
            "",
            "══ YOUR MOVE NOW ══",
            "Pick the highest-leverage thread for THIS chat. Execute one outcome with VERIFY.",
            "End with: THREAD · DONE/PARTIAL/BLOCKED · evidence paths · single next action for founder.",
            "",
            "If founder only wants a brief: output Executive brief (5 bullets) + Plan (numbered, max 8 steps) + which lane paste to use next.",
        ]
    )

    copy_text = "\n".join(lines)
    return {
        "title": "Universal Cursor session brief",
        "copy_text": copy_text,
        "sources": sources,
        "has_advisory": bool(adv),
        "has_direction": bool(prop and pdir_status in ("proposed", "confirmed", "queued")),
        "advisory_at": (ai_advisory or {}).get("generated_at"),
        "direction_status": pdir_status,
        "hint": "Run AI Advisory to refresh focus, then copy Brief again."
        if not adv
        else "Includes AI Advisor. For one repo only: Repos → Copy lane brief.",
    }


def ecosystem_brief_text(**kwargs) -> str:
    """Backward-compatible string — prefer build_universal_cursor_brief()."""
    return build_universal_cursor_brief(**kwargs)["copy_text"]

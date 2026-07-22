#!/usr/bin/env python3
"""
10-round agent loop — legacy archive orchestrator; planner AI is NOT the executing Cursor agent.

Flow (one trigger):
  1. Hub planner (OpenRouter) writes prompt N from last Cursor answer
  2. Hub injects prompt into Cursor chat (paste + Enter)
  3. Cursor agent executes → POST /api/agent-loop response
  4. Repeat until N=10
"""
from __future__ import annotations

import json
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

LOOP_PATH = Path.home() / ".sina" / "agent-loop.json"
DEBUG_LOG_PATH = Path("/Users/sinakazemnezhad/Desktop/SinaaiDataBase/.cursor/debug-9afa14.log")


def _dbg_agent_loop(hypothesis_id: str, location: str, message: str, data: dict | None = None) -> None:
    # #region agent log
    try:
        import time

        DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with DEBUG_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "sessionId": "9afa14",
                        "hypothesisId": hypothesis_id,
                        "location": location,
                        "message": message,
                        "data": data or {},
                        "timestamp": int(time.time() * 1000),
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion


INBOX_PATHS = [
    Path.home() / ".sina" / "cursor-inbox.md",
    Path.home() / "Desktop/SinaaiDataBase/.sina-loop/INBOX.md",
    Path.home() / "Desktop/SourceA/.sina-loop/INBOX.md",
]
SOURCE_A = Path(__file__).resolve().parents[1]
DONE_SCRIPT = SOURCE_A / "scripts/agent-loop-done.sh"

PLANNER_SYSTEM = """You are the Sina OS loop planner (separate from the Cursor agent that executes code).
You only write the NEXT user message that should appear in the founder's Cursor chat.

Output ONLY valid JSON:
{
  "round_title": "short label",
  "prompt_for_cursor": "full message to inject — self-contained task, reference prior answer when round>1",
  "planner_note": "one sentence for the founder UI"
}
Rules:
- prompt_for_cursor must be actionable in the current workspace (files, tests, docs).
- Founder law: NEVER tell the founder to open Terminal or run shell. Executor runs shell; founder uses **RUN INBOX** in Worker chat or legacy archive Actions if ASF enables.
- When telling the founder what to do after a round: Worker chat summary — not legacy loop UI.
- Each round must advance the stated goal; do not repeat prior rounds.
- Round 1 starts from goal only; later rounds must use last_cursor_response."""


def _is_orphan_round(st: dict) -> bool:
    hist = st.get("history") or []
    cur = st.get("round") or 0
    return (
        not st.get("active")
        and st.get("status") == "idle"
        and cur > len(hist)
        and bool(st.get("current_prompt"))
    )


def _resume_orphan_round(st: dict) -> dict:
    """Round was delivered but loop was left idle — restore awaiting_agent so Submit round works."""
    if not _is_orphan_round(st):
        return st
    cur = st.get("round") or 0
    hist_len = len(st.get("history") or [])
    # #region agent log
    _dbg_agent_loop(
        "H1",
        "agent_loop.py:_resume_orphan_round",
        "auto-resume orphan round",
        {"round": cur, "history_len": hist_len, "last_inject_blocked": bool((st.get("last_inject") or {}).get("blocked"))},
    )
    # #endregion
    st["active"] = True
    st["status"] = "awaiting_agent"
    _save(st)
    return st


def _load() -> dict:
    if not LOOP_PATH.is_file():
        return _default_state()
    st = json.loads(LOOP_PATH.read_text(encoding="utf-8"))
    return _resume_orphan_round(st)


def _default_state() -> dict:
    return {
        "active": False,
        "status": "idle",
        "round": 0,
        "max_rounds": 10,
        "goal": "",
        "trigger_source": None,
        "history": [],
        "current_prompt": None,
        "current_title": None,
        "planner_note": None,
        "error": None,
        "awaiting_since": None,
    }


def _save(st: dict) -> None:
    # #region agent log
    hist_len = len(st.get("history") or [])
    cur = st.get("round") or 0
    _dbg_agent_loop(
        "H1",
        "agent_loop.py:_save",
        "persist loop state",
        {
            "active": st.get("active"),
            "status": st.get("status"),
            "round": cur,
            "history_len": hist_len,
            "has_current_prompt": bool(st.get("current_prompt")),
            "orphan_round": bool(
                not st.get("active")
                and st.get("status") == "idle"
                and cur > hist_len
                and st.get("current_prompt")
            ),
        },
    )
    # #endregion
    LOOP_PATH.parent.mkdir(parents=True, exist_ok=True)
    st["updated_at"] = datetime.now(timezone.utc).isoformat()
    LOOP_PATH.write_text(json.dumps(st, indent=2), encoding="utf-8")
    try:
        LOOP_PATH.chmod(0o600)
    except OSError:
        pass


def _parse_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
    return None


def _planner_chat(system: str, user: str) -> tuple[bool, str]:
    import sys

    sys.path.insert(0, str(Path.home() / "Desktop/SinaPromptOS"))
    try:
        from core.openrouter_client import chat_completion  # noqa: WPS433

        def _chat(s: str, u: str) -> tuple[bool, str]:
            return chat_completion(system=s, user=u, temperature=0.4, timeout=120)

        source_scripts = Path.home() / "Desktop" / "SourceA" / "scripts"
        if source_scripts.is_dir():
            sys.path.insert(0, str(source_scripts))
            try:
                import model_dispatch as md  # noqa: WPS433

                if md.current_gate_mode() != "off":
                    repo = str(Path.home() / "Desktop" / "SourceA")
                    out = md.dispatch_chat(
                        system=system,
                        user=user,
                        chat_fn=_chat,
                        task_id="agent-loop-planner",
                        repo_root=repo,
                        source="agent_loop_planner",
                    )
                    if out.get("blocked"):
                        return False, str(out.get("message") or "Model call blocked — packet not gate-eligible")
                    return bool(out.get("ok")), str(out.get("response") or "")
            except Exception:
                pass
        return _chat(system, user)
    except Exception as e:
        return False, str(e)


def _write_inbox(st: dict) -> None:
    r = st.get("round", 0)
    mx = st.get("max_rounds", 10)
    title = st.get("current_title") or f"Round {r}"
    body = st.get("current_prompt") or ""
    content = f"""<!-- SINA_AGENT_LOOP active round={r}/{mx} -->
# Agent loop — round {r} of {mx}

## {title}

{body}

---
**When finished (founder — never Terminal):**

1. **RUN INBOX** in Cursor Worker chat — or legacy archive Private agents page if ASF enables.
2. Paste summary + answer in Worker chat — legacy Submit round is archive only.

Do not ask the founder to run shell. Commands belong in **Actions** one-tap buttons (maintainer adds them) or executor API.

*(Executing Cursor agent may POST `action: response` — founder never runs Terminal.)*
"""
    for p in INBOX_PATHS:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def inject_cursor_chat(message: str, *, force: bool = False) -> dict:
    """Paste into Cursor — disabled unless founder opted in via ~/.sina/auto-prompt-opt-in.json."""
    from auto_prompt_guard import (  # noqa: WPS433
        auto_prompt_blocked,
        block_inject,
        founder_opted_in,
    )

    if "[SINA_LIVE_MAINTAINER]" in (message or "") or "[SINA_ADVISOR]" in (message or ""):
        return block_inject("live_maintainer_inject_forbidden")
    if auto_prompt_blocked() or not founder_opted_in():
        return block_inject("auto_prompt_off")
    if "[GOAL1_HEALTHY_DRAIN]" in (message or "") or "HEALTHY DRAIN — queue" in (message or ""):
        from worker_inject_lib import inject_worker_prompt  # noqa: WPS433

        return inject_worker_prompt(message, source="agent_loop_goal1")

    from clipboard_safe import clipboard_paste_into_cursor  # noqa: WPS433

    # Maintainer loop only — never Goal 1 Worker drain (inbox delivery instead).
    allow = bool(founder_opted_in() and (force or "[SINA_LOOP" in (message or "")))
    return clipboard_paste_into_cursor(message, allow_automation=allow, target="focused")


def _loop_owner_from_config() -> dict:
    """Active workspace for loop ownership (sidebar Private agents page)."""
    try:
        from loop_seeds import _load_loop_config  # noqa: WPS433
        from agent_workspace_registry import get_workspace  # noqa: WPS433

        cfg = _load_loop_config()
        ws_id = cfg.get("active_workspace") or ""
        if not ws_id and cfg.get("active_pack"):
            from agent_private_workspaces import _workspace_id_for_pack  # noqa: WPS433

            ws_id = _workspace_id_for_pack(cfg.get("active_pack")) or ""
        spec = get_workspace(ws_id) if ws_id else None
        return {
            "loop_owner_workspace_id": ws_id or None,
            "loop_owner_label": (spec or {}).get("label") or ws_id or None,
        }
    except Exception:
        return {"loop_owner_workspace_id": None, "loop_owner_label": None}


def loop_payload(*, hub_payload: dict | None = None) -> dict:
    from loop_advisor import advisor_payload  # noqa: WPS433
    from loop_seeds import seeds_payload  # noqa: WPS433

    st = _load()
    owner = _loop_owner_from_config()
    if st.get("loop_owner_workspace_id"):
        owner = {
            "loop_owner_workspace_id": st.get("loop_owner_workspace_id"),
            "loop_owner_label": st.get("loop_owner_label") or st.get("loop_owner_workspace_id"),
        }
    active = st.get("active")
    status = st.get("status", "idle")
    hist = st.get("history") or []
    mx = st.get("max_rounds", 10) or 10
    cur = st.get("round") or 0
    out = {
        "ok": True,
        "active": active,
        "status": status,
        "round": cur,
        "max_rounds": mx,
        "rounds_completed": len(hist),
        "rounds_remaining": max(0, mx - len(hist)) if active else 0,
        "progress_pct": int(100 * len(hist) / mx) if mx else 0,
        "goal": st.get("goal"),
        "current_title": st.get("current_title"),
        "current_prompt_preview": (st.get("current_prompt") or "")[:500],
        "planner_note": st.get("planner_note"),
        "history": st.get("history") or [],
        "error": st.get("error"),
        "awaiting_since": st.get("awaiting_since"),
        "founder_submit": "Private agent page (sidebar) → Submit round — never Terminal",
        "loop_owner_workspace_id": owner.get("loop_owner_workspace_id"),
        "loop_owner_label": owner.get("loop_owner_label"),
        "executor_api": "POST /api/agent-loop action=response (executor only)",
        "roles": {
            "executor": "Cursor agent in chat — builds code only",
            "advisor": "Advisor — pick provider below",
            "planner": "OpenRouter loop planner — reshapes each prompt after executor answers",
        },
    }
    out.update(seeds_payload(hub_payload))
    try:
        from agent_private_workspaces import loop_workspaces_payload  # noqa: WPS433

        out.update(loop_workspaces_payload())
    except Exception:
        out["loop_workspaces"] = []
        out["selected_workspace_id"] = None
    out.update(advisor_payload())
    try:
        from pre_llm.packet_readiness.hub_surface import packet_readiness_hub_payload  # noqa: WPS433

        out["packet_readiness"] = packet_readiness_hub_payload(task_id="agent-loop-readiness")
    except Exception:
        out["packet_readiness"] = {"ok": False, "error": "packet_readiness_unavailable"}
    adv_role = {
        "openrouter": "OpenRouter API — chat on this page",
        "cursor_cloud": "Cursor Cloud Agent (CURSOR_API_KEY) — real Cursor, not coding chat",
        "cursor_ide": "Cursor IDE — message injects into Advisor chat (@sina-advisor)",
    }
    out["roles"]["advisor"] = adv_role.get(out.get("advisor_provider", "openrouter"), adv_role["openrouter"])
    orphan_round = _is_orphan_round(st)
    active = st.get("active")
    status = st.get("status", "idle")
    # #region agent log
    _dbg_agent_loop(
        "H2",
        "agent_loop.py:loop_payload",
        "loop payload snapshot",
        {
            "active": active,
            "status": status,
            "round": cur,
            "rounds_completed": len(hist),
            "orphan_round": orphan_round,
            "awaiting_since": st.get("awaiting_since"),
            "last_inject_blocked": bool((st.get("last_inject") or {}).get("blocked")),
        },
    )
    # #endregion
    if not active and status == "idle":
        out["loop_status_badge"] = "ready"
        out["loop_status_label"] = "Ready — pick a prompt or custom goal, then Start"
        out["status_hint"] = "10 rounds = 10 Cursor tasks. Submit round on this agent's private page after each answer."
    elif active:
        out["loop_status_badge"] = "process"
        if status == "awaiting_agent":
            out["loop_status_label"] = f"Round {cur}/{mx} — Cursor working (then Submit round in app)"
            out["status_hint"] = f"Completed {len(hist)}/{mx}. When Cursor finishes → Submit round → Planner sends round {cur + 1 if cur < mx else mx}."
        else:
            out["loop_status_label"] = out.get("planner_note") or status
            out["status_hint"] = "Planner thinking…"
    elif status == "complete":
        out["loop_status_badge"] = "done"
        out["loop_status_label"] = f"Finished all {mx} rounds"
        out["status_hint"] = "Loop complete. Start again with a new goal if needed."
    else:
        out["loop_status_badge"] = "warn" if st.get("error") else "ready"
        out["loop_status_label"] = st.get("error") or status
    return out


def _plan_next_prompt(st: dict, *, payload: dict | None) -> dict:
    goal = st.get("goal") or ""
    history = st.get("history") or []
    round_n = st.get("round", 1)
    snap = {}
    if payload:
        from sina_ai_advisory import build_snapshot  # noqa: WPS433

        snap = build_snapshot(payload)

    from loop_advisor import advisor_context_text  # noqa: WPS433
    from loop_seeds import seeds_payload  # noqa: WPS433
    from execution_intelligence.planner_influence import planner_context_block  # noqa: WPS433

    seed_info = seeds_payload(payload) if payload else {}
    user = json.dumps(
        {
            "goal": goal,
            "round": round_n,
            "max_rounds": st.get("max_rounds", 10),
            "history": history[-6:],
            "command_snapshot": snap,
            "advisor_conversation": advisor_context_text(),
            "seed_suggestions": seed_info.get("seed_suggestions") or [],
            **planner_context_block(),
        },
        indent=2,
        ensure_ascii=False,
    )[:16000]

    ok, raw = _planner_chat(PLANNER_SYSTEM, user)
    if not ok:
        return {"ok": False, "error": raw}
    parsed = _parse_json(raw)
    if not parsed or not parsed.get("prompt_for_cursor"):
        return {"ok": False, "error": "Planner returned invalid JSON", "_raw": raw[:1500]}
    return {"ok": True, "plan": parsed}


def _registry_forbidden_lines() -> list[str]:
    try:
        from loop_seeds import _load_loop_config  # noqa: WPS433
        from agent_workspace_registry import get_workspace  # noqa: WPS433

        cfg = _load_loop_config()
        ws_id = cfg.get("active_workspace")
        if not ws_id and cfg.get("active_pack"):
            from agent_private_workspaces import _workspace_id_for_pack  # noqa: WPS433

            ws_id = _workspace_id_for_pack(cfg.get("active_pack"))
        spec = get_workspace(ws_id or "") if ws_id else None
        if not spec:
            return []
        return [f"Do NOT edit (registry): {p}" for p in (spec.get("forbidden_roots") or [])]
    except Exception:
        return []


def _workspace_lock_banner() -> str:
    try:
        from loop_seeds import _load_loop_config  # noqa: WPS433

        cfg = _load_loop_config()
    except Exception:
        cfg = {}
    reg_lines = _registry_forbidden_lines()
    if not cfg.get("workspace_rule") and not reg_lines:
        return ""
    lines = ["--- WORKSPACE LOCK (founder) ---"]
    if cfg.get("workspace_rule"):
        lines.append(cfg["workspace_rule"])
    if cfg.get("workspace_primary"):
        lines.append(f"Open Cursor folder ONLY: {cfg['workspace_primary']}")
    if cfg.get("workspace_forbidden"):
        lines.append(f"Do NOT edit (pack): {cfg['workspace_forbidden']}")
    lines.extend(reg_lines)
    if cfg.get("cursor_workspace"):
        lines.append(f"Expected Cursor workspace id: {cfg['cursor_workspace']}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def _rules_loop_banner() -> str:
    try:
        from agent_rules_loop_orchestrator import rules_loop_banner  # noqa: WPS433

        return rules_loop_banner(phase="loop_round", max_lines=9)
    except Exception:
        return (
            "<!-- RULES_IN_CHARGE_LOOP -->\n"
            "Read AGENT_RULES_IN_CHARGE_LOCKED_v1.md + Council Room rules in charge before acting.\n---\n\n"
        )


def _deliver_round(st: dict) -> dict:
    prompt = st.get("current_prompt") or ""
    r = st.get("round", 1)
    mx = st.get("max_rounds", 10)
    lock = _workspace_lock_banner()
    rules_banner = _rules_loop_banner()
    owner = _loop_owner_from_config()
    owner_name = owner.get("loop_owner_label") or "Private agents"
    inject_body = (
        f"[SINA_LOOP {r}/{mx}] Legacy loop task (archive) — execute fully. "
        f"Founder: RUN INBOX in Worker chat — never Terminal. "
        f"Executor: POST action=response when done.\n\n"
        f"{rules_banner}{lock}{prompt}"
    )
    inj = inject_cursor_chat(inject_body)
    if inj.get("blocked"):
        inj = {
            **inj,
            "message": "Round saved on disk + INBOX — RUN INBOX in Worker chat (legacy loop archive).",
        }
    st["status"] = "awaiting_agent"
    st["awaiting_since"] = datetime.now(timezone.utc).isoformat()
    st["last_inject"] = inj
    _write_inbox(st)
    _save(st)
    return inj


def start_loop(
    *,
    goal: str,
    trigger_source: str = "app",
    max_rounds: int = 10,
    payload: dict | None = None,
    workspace_id: str | None = None,
) -> dict:
    from gate_receipt_lib import loop_gate_block  # noqa: WPS433

    blocked = loop_gate_block(max_age_hours=8.0)
    if blocked:
        return blocked

    goal = (goal or "").strip()
    if not goal:
        return {"ok": False, "error": "goal required"}

    owner = _loop_owner_from_config()
    cfg_ws = owner.get("loop_owner_workspace_id")
    if workspace_id and cfg_ws and workspace_id != cfg_ws:
        return {
            "ok": False,
            "error": f"Wrong agent page — open Private agents → {owner.get('loop_owner_label') or cfg_ws} or Stop loop first",
        }

    prev = _load()
    if prev.get("active"):
        prev_owner = prev.get("loop_owner_workspace_id") or cfg_ws
        if workspace_id and prev_owner and workspace_id != prev_owner:
            from agent_workspace_registry import get_workspace  # noqa: WPS433

            spec = get_workspace(prev_owner) or {}
            return {
                "ok": False,
                "error": f"Loop already running for {spec.get('label', prev_owner)} — open that page or Stop loop",
            }

    lock = _workspace_lock_banner()
    if lock and "WORKSPACE LOCK" not in goal:
        goal = goal + "\n\n" + lock.strip()

    from sina_ai_advisory import _load_vault_key  # noqa: WPS433

    if not _load_vault_key():
        return {"ok": False, "error": "OpenRouter required for planner AI (not the executing agent)"}

    st = _default_state()
    st["active"] = True
    st["status"] = "planning"
    st["round"] = 1
    st["max_rounds"] = min(10, max(1, int(max_rounds)))
    st["goal"] = goal[:8000]
    st["trigger_source"] = trigger_source
    st["history"] = []
    st["error"] = None
    st["loop_owner_workspace_id"] = cfg_ws or workspace_id
    st["loop_owner_label"] = owner.get("loop_owner_label")
    _save(st)

    plan = _plan_next_prompt(st, payload=payload)
    if not plan.get("ok"):
        st["status"] = "error"
        st["error"] = plan.get("error")
        st["active"] = False
        _save(st)
        return plan

    p = plan["plan"]
    st["current_title"] = p.get("round_title", f"Round {st['round']}")
    st["current_prompt"] = p.get("prompt_for_cursor", "")
    st["planner_note"] = p.get("planner_note", "")
    _save(st)

    inj = _deliver_round(st)
    from agent_governance_events import log_governance_event  # noqa: WPS433

    log_governance_event(
        "loop_started",
        workspace_id=st.get("loop_owner_workspace_id"),
        detail=goal[:500],
        extra={"max_rounds": st["max_rounds"], "round": 1},
    )
    return {
        "ok": True,
        "message": f"Loop started — round 1/{st['max_rounds']} sent to Cursor",
        "round": 1,
        "inject": inj,
        "planner_note": st["planner_note"],
    }


def submit_response(*, summary: str, response: str, payload: dict | None = None) -> dict:
    from gate_receipt_lib import loop_gate_block  # noqa: WPS433

    blocked = loop_gate_block(max_age_hours=8.0)
    if blocked:
        return blocked

    st = _load()
    if not st.get("active") or st.get("status") != "awaiting_agent":
        return {"ok": False, "error": "Loop not waiting for agent response"}

    summary = (summary or "").strip()[:500]
    response = (response or "").strip()[:80000]
    if not response:
        return {"ok": False, "error": "response text required"}

    r = st.get("round", 1)
    st.setdefault("history", []).append(
        {
            "round": r,
            "title": st.get("current_title"),
            "prompt": (st.get("current_prompt") or "")[:2000],
            "summary": summary,
            "response": response[:12000],
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    owner_ws = st.get("loop_owner_workspace_id")
    try:
        from agent_workspace_vault import auto_deposit_loop_round  # noqa: WPS433

        auto_deposit_loop_round(
            owner_ws or "",
            round_num=r,
            title=st.get("current_title") or f"Round {r}",
            summary=summary,
            response=response,
        )
    except Exception:
        pass

    mx = st.get("max_rounds", 10)
    if r >= mx:
        st["active"] = False
        st["status"] = "complete"
        st["current_prompt"] = None
        _save(st)
        from agent_governance_events import log_governance_event  # noqa: WPS433

        log_governance_event(
            "loop_complete",
            workspace_id=st.get("loop_owner_workspace_id"),
            detail=summary,
            extra={"rounds": mx},
        )
        return {"ok": True, "message": f"Loop complete — {mx} rounds finished", "complete": True}

    st["round"] = r + 1
    st["status"] = "planning"
    _save(st)

    plan = _plan_next_prompt(st, payload=payload)
    if not plan.get("ok"):
        st["status"] = "error"
        st["error"] = plan.get("error")
        _save(st)
        return plan

    p = plan["plan"]
    st["current_title"] = p.get("round_title", f"Round {st['round']}")
    st["current_prompt"] = p.get("prompt_for_cursor", "")
    st["planner_note"] = p.get("planner_note", "")
    _save(st)

    inj = _deliver_round(st)
    from agent_governance_events import log_governance_event  # noqa: WPS433

    log_governance_event(
        "loop_round_submitted",
        workspace_id=st.get("loop_owner_workspace_id"),
        detail=summary,
        extra={"round": r, "next_round": st["round"]},
    )
    return {
        "ok": True,
        "message": f"Round {r} saved — sent round {st['round']}/{mx} to Cursor",
        "round": st["round"],
        "inject": inj,
        "planner_note": st["planner_note"],
        "complete": False,
    }


def cancel_loop() -> dict:
    st = _load()
    was = st.get("round", 0)
    mx = st.get("max_rounds", 10)
    done = len(st.get("history") or [])
    st["active"] = False
    st["status"] = "idle"
    st["error"] = None
    st["current_prompt"] = None
    st["current_title"] = None
    st["planner_note"] = "Stopped by founder"
    owner_ws = st.get("loop_owner_workspace_id")
    st.pop("loop_owner_workspace_id", None)
    st.pop("loop_owner_label", None)
    _save(st)
    from agent_governance_events import log_governance_event  # noqa: WPS433

    log_governance_event(
        "loop_stopped",
        workspace_id=owner_ws,
        detail=f"completed {done}/{mx}",
    )
    for p in INBOX_PATHS:
        if p.is_file():
            p.write_text("<!-- SINA_AGENT_LOOP inactive — stopped -->\n", encoding="utf-8")
    return {
        "ok": True,
        "message": f"Loop stopped — completed {done}/{mx} rounds (was on round {was})",
        "rounds_completed": done,
    }


def handle_action(body: dict, *, payload: dict | None = None) -> dict:
    action = (body.get("action") or "status").strip().lower()
    if action == "status":
        return loop_payload(hub_payload=payload)
    if action == "set_seeds":
        from loop_seeds import set_seed_suggestions  # noqa: WPS433

        return set_seed_suggestions(body.get("suggestions") or [], author_note=body.get("author_note", ""))
    if action == "select_workspace":
        from agent_private_workspaces import select_loop_workspace  # noqa: WPS433

        return select_loop_workspace(
            body.get("workspace_id") or body.get("id") or "",
            sync_ui_file=body.get("sync_ui", True),
        )
    if action in ("activate_devbridge_pack", "activate_pack"):
        from loop_seeds import activate_devbridge_seed_pack, activate_seed_pack  # noqa: WPS433

        pack_id = body.get("pack") or body.get("id") or "ai_dev_bridge_os"
        if action == "activate_devbridge_pack":
            return activate_devbridge_seed_pack(sync_ui_file=body.get("sync_ui", True))
        return activate_seed_pack(pack_id, sync_ui_file=body.get("sync_ui", True))
    if action == "start":
        return start_loop(
            goal=body.get("goal", ""),
            trigger_source=body.get("trigger_source", "app"),
            max_rounds=body.get("max_rounds", 10),
            payload=payload,
            workspace_id=(body.get("workspace_id") or body.get("id") or "").strip() or None,
        )
    if action == "response":
        return submit_response(
            summary=body.get("summary", ""),
            response=body.get("response", ""),
            payload=payload,
        )
    if action == "cancel":
        return cancel_loop()
    if action == "reinject":
        st = _load()
        if not st.get("active") or not st.get("current_prompt"):
            return {"ok": False, "error": "nothing to inject"}
        inj = _deliver_round(st)
        return {"ok": True, "inject": inj}
    return {"ok": False, "error": f"unknown action: {action}"}

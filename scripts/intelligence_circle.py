#!/usr/bin/env python3
"""
Live agents layer — online API / cloud / bridge agents that talk to Sina Command in real time.

NOT repo Cursor chats. NOT private-agent workspace logs.

Comms log (hub ↔ live agents only): ~/.sina/live-agent-comms.jsonl
Brief: ~/.sina/intelligence-circle-brief-latest.md
Config: ~/.sina/intelligence-circle-config.json
"""
from __future__ import annotations

import json
import ssl
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import certifi

SOURCE_A = Path(__file__).resolve().parents[1]
COMMS_PATH = Path.home() / ".sina" / "live-agent-comms.jsonl"
BRIEF_PATH = Path.home() / ".sina" / "intelligence-circle-brief-latest.md"
CONFIG_PATH = Path.home() / ".sina" / "intelligence-circle-config.json"
MAINTAINER_INBOX = Path.home() / ".sina" / "live-agent-maintainer-inbox.md"
MAINTAINER_OUTBOX = Path.home() / ".sina" / "live-agent-maintainer-outbox.md"
MAINTAINER_SESSION = Path.home() / ".sina" / "live-agent-maintainer-session.json"

# Isolated chat sessions per live agent (never share loop advisor-chat.json)
SESSION_FILES: dict[str, Path] = {
    "openrouter": Path.home() / ".sina" / "live-agent-session-openrouter.json",
    "cursor_maintainer": MAINTAINER_SESSION,
    "cursor_cloud": Path.home() / ".sina" / "live-agent-session-cursor-cloud.json",
}

DEFAULT_ENABLED_AGENTS: dict[str, bool] = {
    "openrouter": False,
    "cursor_cloud": False,
    "cursor_maintainer": True,
    "semej": False,
}

DEFAULT_SELECTED_LIVE_AGENT = "cursor_maintainer"

LIVE_OPENROUTER_SYSTEM = """You are the Sina Command Live Advisor (OpenRouter) — founder ASF's coach.

Write plain English for a phone screen. No markdown asterisks, no "Lead —" labels, no template headers.

Format:
- First line: direct answer in one short sentence.
- Blank line, then short sections with a simple title on its own line (e.g. "This week").
- Use bullet lines starting with "- " (one idea per line).
- End with one clear next step on its own line.

Max ~12 lines unless asked for more. No Terminal — point to Live agents, Private agents, Actions tabs."""

TOPICS = {
    "bugs": "Bugs & regressions",
    "roadmap": "Roadmap & P0",
    "ui": "UI / Sina Command",
    "business": "Business & GTM",
    "artifact": "Report / spec",
    "general": "General",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_config() -> dict:
    if not CONFIG_PATH.is_file():
        return {
            "auto_ping": False,
            "ping_interval_sec": 120,
            "auto_keepalive": False,
            "keepalive_interval_sec": 0,
            "selected_live_agent": DEFAULT_SELECTED_LIVE_AGENT,
            "last_ping_at": None,
            "enabled_agents": dict(DEFAULT_ENABLED_AGENTS),
            "chat_cleared_at": {},
            "maintainer_auto_inject_cursor": False,
        }
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if "enabled_agents" not in cfg:
        cfg["enabled_agents"] = dict(DEFAULT_ENABLED_AGENTS)
    if "chat_cleared_at" not in cfg:
        cfg["chat_cleared_at"] = {}
    if "maintainer_auto_inject_cursor" not in cfg:
        cfg["maintainer_auto_inject_cursor"] = False
    return cfg


def _maintainer_should_inject_cursor(cfg: dict, *, explicit: bool | None = None) -> bool:
    """Always False — Live agents must never auto-dispatch into Cursor (founder law)."""
    _ = (cfg, explicit)
    return False


def disable_live_agent_automation() -> None:
    """Emergency stop — no keepalive, no Cursor inject flags."""
    cfg = _load_config()
    cfg["auto_keepalive"] = False
    cfg["maintainer_auto_inject_cursor"] = False
    cfg["auto_ping"] = False
    _save_config(cfg)


def _preferred_live_agent(cfg: dict | None = None) -> str:
    """Founder default: maintainer when on; else first enabled chat agent."""
    cfg = cfg or _load_config()
    sel = cfg.get("selected_live_agent") or DEFAULT_SELECTED_LIVE_AGENT
    if sel == "cursor_ide":
        sel = "cursor_maintainer"
    if _is_agent_enabled(sel, cfg):
        return sel
    if _is_agent_enabled(DEFAULT_SELECTED_LIVE_AGENT, cfg):
        return DEFAULT_SELECTED_LIVE_AGENT
    for aid, on in _enabled_agents(cfg).items():
        if on and aid in SESSION_FILES:
            return aid
    return DEFAULT_SELECTED_LIVE_AGENT


def _chat_cleared_at(cfg: dict, agent_id: str) -> str | None:
    return (cfg.get("chat_cleared_at") or {}).get(agent_id)


def _after_cleared(at: str | None, cleared: str | None) -> bool:
    """True if row timestamp is strictly after clear marker."""
    if not cleared:
        return True
    return bool(at) and at > cleared


def _newest_agent_timestamp(agent_id: str) -> str | None:
    newest: str | None = None
    for row in read_comms(agent_id=agent_id, limit=500):
        at = row.get("at") or ""
        if at and (newest is None or at > newest):
            newest = at
    for msg in (_load_agent_session(agent_id).get("messages") or []):
        at = msg.get("at") or ""
        if at and (newest is None or at > newest):
            newest = at
    return newest


def _clear_marker_after(agent_id: str) -> str:
    """ISO timestamp strictly after all existing rows (avoids same-µs clear leaks)."""
    marker = datetime.now(timezone.utc)
    newest = _newest_agent_timestamp(agent_id)
    if newest:
        try:
            ts = datetime.fromisoformat(newest.replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= marker:
                marker = ts + timedelta(microseconds=1)
        except ValueError:
            pass
    return marker.isoformat()


def clear_agent_chat(agent_id: str) -> dict:
    """Founder clear — hide old comms + session; new messages start fresh."""
    if agent_id == "cursor_ide":
        agent_id = "cursor_maintainer"
    cfg = _load_config()
    cfg.setdefault("chat_cleared_at", {})[agent_id] = _clear_marker_after(agent_id)
    _save_config(cfg)
    _clear_agent_session(agent_id)
    if agent_id == "cursor_maintainer" and MAINTAINER_OUTBOX.is_file():
        try:
            MAINTAINER_OUTBOX.unlink()
        except OSError:
            pass
    return {"ok": True, "agent_id": agent_id, "cleared_at": cfg["chat_cleared_at"][agent_id]}


def _enabled_agents(cfg: dict | None = None) -> dict[str, bool]:
    cfg = cfg or _load_config()
    out = dict(DEFAULT_ENABLED_AGENTS)
    out.update(cfg.get("enabled_agents") or {})
    return out


def _is_agent_enabled(agent_id: str, cfg: dict | None = None) -> bool:
    return bool(_enabled_agents(cfg).get(agent_id, False))


def _set_agent_enabled(agent_id: str, enabled: bool) -> dict:
    if agent_id not in DEFAULT_ENABLED_AGENTS and agent_id != "cursor_ide":
        return {"ok": False, "error": f"unknown agent: {agent_id}"}
    if agent_id == "cursor_ide":
        agent_id = "cursor_maintainer"
    cfg = _load_config()
    cfg.setdefault("enabled_agents", dict(DEFAULT_ENABLED_AGENTS))
    cfg["enabled_agents"][agent_id] = bool(enabled)
    if not enabled and cfg.get("selected_live_agent") == agent_id:
        for aid, on in _enabled_agents(cfg).items():
            if on:
                cfg["selected_live_agent"] = aid
                break
    _save_config(cfg)
    return {"ok": True, "agent_id": agent_id, "enabled": bool(enabled)}


def _load_agent_session(agent_id: str) -> dict:
    path = SESSION_FILES.get(agent_id)
    if not path or not path.is_file():
        return {"messages": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"messages": []}


def _save_agent_session(agent_id: str, data: dict) -> None:
    path = SESSION_FILES.get(agent_id)
    if not path:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    data["messages"] = (data.get("messages") or [])[-40:]
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _append_agent_session(agent_id: str, role: str, content: str, *, topic: str = "general") -> list:
    data = _load_agent_session(agent_id)
    msgs = data.get("messages") or []
    msgs.append({
        "role": role,
        "content": content,
        "at": _now(),
        "topic": topic,
        "agent_id": agent_id,
    })
    data["messages"] = msgs
    _save_agent_session(agent_id, data)
    return data["messages"]


def _clear_agent_session(agent_id: str) -> None:
    _save_agent_session(agent_id, {"messages": []})


def _chat_thread(agent_id: str) -> list[dict]:
    """Chat box — session + comms after last founder clear only."""
    cfg = _load_config()
    cleared = _chat_cleared_at(cfg, agent_id)
    session_msgs = _load_agent_session(agent_id).get("messages") or []
    comms = read_comms(agent_id=agent_id, limit=100)
    merged: dict[str, dict] = {}
    for m in session_msgs:
        if not _after_cleared(m.get("at"), cleared):
            continue
        content = (m.get("content") or "").strip()
        if not content:
            continue
        key = f"{m.get('role')}|{content[:240]}|{(m.get('at') or '')[:19]}"
        merged[key] = {**m, "agent_id": agent_id, "content": content}
    for c in comms:
        direction = c.get("direction") or ""
        if direction == "system":
            continue
        if not _after_cleared(c.get("at"), cleared):
            continue
        content = (c.get("content") or "").strip()
        if not content:
            continue
        role = "user" if direction == "hub_to_agent" else "assistant"
        key = f"{role}|{content[:240]}|{(c.get('at') or '')[:19]}"
        if key not in merged:
            merged[key] = {
                "role": role,
                "content": content,
                "at": c.get("at") or _now(),
                "topic": c.get("topic") or "general",
                "agent_id": agent_id,
            }
    out = sorted(merged.values(), key=lambda x: x.get("at") or "")
    return out[-40:]


def _comms_for_ui(agent_id: str, *, limit: int = 30) -> list[dict]:
    cfg = _load_config()
    cleared = _chat_cleared_at(cfg, agent_id)
    rows = read_comms(agent_id=agent_id, limit=limit * 3 if cleared else limit)
    if cleared:
        rows = [r for r in rows if _after_cleared(r.get("at"), cleared)]
    return rows[-limit:]


def _rebuild_session_from_comms(agent_id: str) -> None:
    """Keep session file aligned with comms so chat + replies stay in sync."""
    thread = _chat_thread(agent_id)
    _save_agent_session(agent_id, {"messages": thread})


def _build_live_response(
    hub_payload: dict | None,
    agent_id: str,
    **extra: Any,
) -> dict:
    """Payload for Live agents UI — one agent's chat only, never mixed."""
    cfg = _load_config()
    if agent_id == "cursor_ide":
        agent_id = "cursor_maintainer"
    agents = _live_agent_rows(hub_payload)
    msgs = _chat_thread(agent_id)
    from loop_advisor import provider_status  # noqa: WPS433

    st = provider_status()
    return {
        "ok": True,
        "built_at": _now(),
        "scope": "live_agents_only",
        "scope_note": "Each agent has its own chat. Turn agents off in the list if you only want one.",
        "selected_live_agent": agent_id,
        "chat_agent_id": agent_id,
        "chat_messages": msgs,
        "enabled_agents": _enabled_agents(cfg),
        "live_agents": agents,
        "comms": _comms_for_ui(agent_id),
        "openrouter_ready": st.get("openrouter_ready"),
        **extra,
    }


def _save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    cfg["updated_at"] = _now()
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def append_comms(
    *,
    agent_id: str,
    direction: str,
    content: str,
    topic: str = "general",
    extra: dict | None = None,
) -> dict:
    """Hub ↔ live agent only (never repo chat)."""
    row = {
        "at": _now(),
        "agent_id": agent_id,
        "direction": direction,
        "topic": topic if topic in TOPICS else "general",
        "content": (content or "")[:8000],
    }
    if extra:
        row.update(extra)
    COMMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with COMMS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def _format_founder_reply(text: str) -> str:
    """Plain, readable text in Live agents chat (no glued markdown)."""
    import re

    t = (text or "").strip()
    if not t:
        return t
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"^\*+Lead\*+\s*[—–-]\s*", "", t, flags=re.I | re.MULTILINE)
    t = re.sub(r"\*+", "", t)
    t = re.sub(r"(?<=[.!?])\s*(\d+\.\s)", r"\n\n\1", t)
    t = re.sub(r"([^\n])\s*(\d+\.\s)", r"\1\n\n\2", t)
    t = re.sub(r"([^\n])\s*-\s+\*\*", r"\1\n\n- ", t)
    t = re.sub(r"([^\n])\s*-\s+([A-Z])", r"\1\n\n- \2", t)
    t = re.sub(r"(This week|Portfolio|Already shipped|Your one move)[^\n]*\*\*", r"\1", t, flags=re.I)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _format_live_reply(text: str) -> str:
    return _format_founder_reply(text)


def send_to_openrouter(
    text: str,
    *,
    topic: str = "general",
    hub_payload: dict | None = None,
) -> dict:
    """OpenRouter only — isolated session, never touches maintainer or advisor-chat.json."""
    from loop_advisor import _chat_openrouter  # noqa: WPS433

    _append_agent_session("openrouter", "user", text, topic=topic)
    append_comms(agent_id="openrouter", direction="hub_to_agent", content=text, topic=topic)

    hist = _load_agent_session("openrouter").get("messages") or []
    llm_msgs = [{"role": m["role"], "content": m["content"]} for m in hist if m["role"] in ("user", "assistant")]
    if hub_payload:
        ctx = _minimal_hub_context(hub_payload, topic)
        if llm_msgs and llm_msgs[-1]["role"] == "user":
            llm_msgs[-1]["content"] = f"[Hub snapshot]\n{ctx}\n\n[Founder]\n{llm_msgs[-1]['content']}"
    ok, reply = _chat_openrouter(llm_msgs, system=LIVE_OPENROUTER_SYSTEM)
    if not ok:
        return _build_live_response(hub_payload, "openrouter", ok=False, error=reply)
    reply = _format_live_reply(reply)
    _append_agent_session("openrouter", "assistant", reply, topic=topic)
    append_comms(agent_id="openrouter", direction="agent_to_hub", content=reply, topic=topic)
    _rebuild_session_from_comms("openrouter")
    return _build_live_response(
        hub_payload,
        "openrouter",
        reply=reply,
        message="OpenRouter replied (separate from Cursor maintainer chat)",
    )


def send_to_cursor_maintainer(
    text: str,
    *,
    topic: str = "general",
    hub_payload: dict | None = None,
    inject_cursor: bool | None = None,
) -> dict:
    """Founder → maintainer: app chat + inbox file only (never paste into Cursor)."""
    _ = inject_cursor
    ctx = _minimal_hub_context(hub_payload, topic)
    MAINTAINER_INBOX.parent.mkdir(parents=True, exist_ok=True)
    MAINTAINER_INBOX.write_text(
        f"""# Live agent — SinaaiDataBase maintainer chat

**Topic:** {TOPICS.get(topic, topic)}
**From:** Worker Hub live agents (legacy) or Cursor Worker chat

{ctx}

---

## Founder message

{text}

---

**App only** — does not paste into Cursor. Maintainer reads this file only when founder opens that chat.

**Reply to app:** `~/Desktop/SourceA/scripts/live-agent-cursor-reply.sh "Your full reply"`

Or API: `POST /api/intelligence-circle` `{{"action":"agent_reply","reply":"…"}}`
""",
        encoding="utf-8",
    )
    if MAINTAINER_OUTBOX.is_file():
        try:
            MAINTAINER_OUTBOX.unlink()
        except OSError:
            pass

    # Never paste into Cursor from Live agents — app chat + inbox file only (stops [SINA_LIVE_MAINTAINER] spam).
    inject: dict = {"ok": False, "skipped": True, "reason": "live_agents_never_inject_cursor"}

    _append_agent_session("cursor_maintainer", "user", text, topic=topic)
    append_comms(agent_id="cursor_maintainer", direction="hub_to_agent", content=text, topic=topic)
    _rebuild_session_from_comms("cursor_maintainer")
    msg = "Saved in Live agents — does not paste into Cursor (open this chat yourself if you want a reply here)."
    return _build_live_response(
        hub_payload,
        "cursor_maintainer",
        pending_maintainer=False,
        inject_skipped=True,
        message=msg,
    )


def poll_cursor_maintainer(*, hub_payload: dict | None = None) -> dict:
    if not MAINTAINER_OUTBOX.is_file() or MAINTAINER_OUTBOX.stat().st_size < 3:
        return _build_live_response(
            hub_payload,
            "cursor_maintainer",
            ok=False,
            error="no maintainer reply yet",
        )
    reply = MAINTAINER_OUTBOX.read_text(encoding="utf-8").strip()
    try:
        MAINTAINER_OUTBOX.unlink()
    except OSError:
        pass
    return agent_reply_to_maintainer(reply, hub_payload=hub_payload)


def agent_reply_to_maintainer(reply: str, *, topic: str = "general", hub_payload: dict | None = None) -> dict:
    text = _format_founder_reply((reply or "").strip())
    if not text:
        return {"ok": False, "error": "reply required"}
    _append_agent_session("cursor_maintainer", "assistant", text, topic=topic)
    append_comms(agent_id="cursor_maintainer", direction="agent_to_hub", content=text, topic=topic)
    _rebuild_session_from_comms("cursor_maintainer")
    return _build_live_response(
        hub_payload,
        "cursor_maintainer",
        reply=text,
        message="Reply delivered to Live agents tab",
    )


def clear_maintainer_session() -> dict:
    return clear_agent_chat("cursor_maintainer")


def read_comms(*, agent_id: str | None = None, limit: int = 30) -> list[dict]:
    if not COMMS_PATH.is_file():
        return []
    rows = []
    for line in COMMS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if agent_id:
        rows = [r for r in rows if r.get("agent_id") == agent_id]
    return rows[-limit:]


def _ping_openrouter() -> dict:
    from loop_advisor import _load_vault_keys  # noqa: WPS433

    key = _load_vault_keys().get("OPENROUTER_API_KEY") or ""
    if not key:
        return {"online": False, "detail": "No vault key"}
    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            method="GET",
        )
        ctx = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            ok = resp.status == 200
        return {"online": ok, "detail": "API reachable" if ok else f"HTTP {resp.status}"}
    except Exception as e:
        return {"online": False, "detail": str(e)[:120]}


def _live_agent_rows(hub_payload: dict | None) -> list[dict]:
    from loop_advisor import provider_status  # noqa: WPS433

    st = provider_status()
    cfg = _load_config()
    enabled = _enabled_agents(cfg)
    rows = []

    or_ping = _ping_openrouter() if st.get("openrouter_ready") else {"online": False, "detail": "Vault key missing"}
    or_on = enabled.get("openrouter", True)
    rows.append(
        {
            "id": "openrouter",
            "label": "OpenRouter API",
            "kind": "api_ai",
            "plane": "cloud_api",
            "online": or_ping.get("online", False) if or_on else False,
            "configured": bool(st.get("openrouter_ready")),
            "enabled": or_on,
            "detail": "Off — turn on to use" if not or_on else or_ping.get("detail", ""),
            "selected": cfg.get("selected_live_agent") == "openrouter",
            "can_chat": or_on and bool(st.get("openrouter_ready")),
        }
    )

    cc_ready = st.get("cursor_cloud_ready")
    cc_on = enabled.get("cursor_cloud", False)
    rows.append(
        {
            "id": "cursor_cloud",
            "label": "Cursor Cloud Agent",
            "kind": "cursor_cloud",
            "plane": "cloud_api",
            "online": False,
            "configured": bool(cc_ready),
            "enabled": cc_on,
            "detail": "Off — turn on to use" if not cc_on else ("CURSOR_API_KEY + cursor-sdk" if not cc_ready else "Ready to prompt"),
            "selected": cfg.get("selected_live_agent") == "cursor_cloud",
            "can_chat": cc_on and bool(cc_ready),
        }
    )

    maint_pending = MAINTAINER_OUTBOX.is_file() and MAINTAINER_OUTBOX.stat().st_size > 3
    cm_on = enabled.get("cursor_maintainer", True)
    rows.append(
        {
            "id": "cursor_maintainer",
            "label": "Cursor — SinaaiDataBase (this chat)",
            "kind": "cursor_local",
            "plane": "local_cursor",
            "online": cm_on,
            "configured": True,
            "enabled": cm_on,
            "detail": "Off — turn on to use" if not cm_on else ("Reply ready" if maint_pending else "Direct — maintainer agent in Cursor"),
            "selected": cfg.get("selected_live_agent") in ("cursor_maintainer", "cursor_ide"),
            "can_chat": cm_on,
            "recommended": True,
        }
    )

    try:
        from semej_loop import semej_payload  # noqa: WPS433

        s = semej_payload()
        active = (s.get("status") or "").lower() in ("running", "active", "awaiting")
        sj_on = enabled.get("semej", False)
        rows.append(
            {
                "id": "semej",
                "label": "SEMEJ (Chrome AIs)",
                "kind": "browser_chain",
                "plane": "local_browser",
                "online": active and sj_on,
                "configured": True,
                "enabled": sj_on,
                "detail": "Off — turn on to use" if not sj_on else (s.get("status_hint") or s.get("status") or "idle"),
                "selected": cfg.get("selected_live_agent") == "semej",
                "can_chat": sj_on and active,
                "tab": "semej",
            }
        )
    except Exception:
        pass

    return rows


def ping_live_agents() -> dict:
    """Heartbeat enabled live agents — does not read repo chats."""
    cfg = _load_config()
    agents = _live_agent_rows(None)
    results = []
    for a in agents:
        aid = a["id"]
        if not a.get("enabled", True):
            results.append({"id": aid, "online": False, "detail": "disabled"})
            continue
        if aid == "openrouter" and a.get("configured"):
            ping = _ping_openrouter()
            a["online"] = ping["online"]
            a["detail"] = ping["detail"]
            results.append({"id": aid, **ping})
            if ping["online"]:
                append_comms(agent_id=aid, direction="system", content=f"ping ok — {ping['detail']}", topic="general")
        elif aid == "cursor_cloud" and a.get("configured"):
            try:
                from loop_advisor import keepalive_cursor_cloud  # noqa: WPS433

                r = keepalive_cursor_cloud()
                results.append({"id": aid, "online": r.get("ok"), "detail": r.get("message", "")[:120]})
                if r.get("ok"):
                    append_comms(agent_id=aid, direction="agent_to_hub", content=r.get("message", "")[:500], topic="general")
            except Exception as e:
                results.append({"id": aid, "online": False, "detail": str(e)[:120]})
        else:
            results.append({"id": aid, "online": a.get("online"), "detail": a.get("detail", "")})

    cfg["last_ping_at"] = _now()
    cfg["last_ping_results"] = results
    _save_config(cfg)
    online_n = sum(1 for r in results if r.get("online"))
    by_id = {r["id"]: r for r in results}
    agents = _live_agent_rows(None)
    for a in agents:
        if a["id"] in by_id:
            a["online"] = by_id[a["id"]].get("online", False)
            if by_id[a["id"]].get("detail"):
                a["detail"] = by_id[a["id"]]["detail"]
    return {
        "ok": True,
        "at": cfg["last_ping_at"],
        "online_count": online_n,
        "total": len(results),
        "results": results,
        "live_agents": agents,
        "message": f"{online_n} live agent(s) online",
    }


def _minimal_hub_context(hub_payload: dict | None, topic: str) -> str:
    """Small snapshot for live agent — not repo chat history."""
    parts = [f"[Sina Command · live agent · topic: {TOPICS.get(topic, topic)}]"]
    if hub_payload:
        bowl = hub_payload.get("bowl") or {}
        p0 = bowl.get("p0") or {}
        if p0.get("id"):
            parts.append(f"P0: {p0.get('id')} — {p0.get('next_action', '')[:180]}")
        reviews = hub_payload.get("agent_reviews") or {}
        if reviews.get("open_count"):
            parts.append(f"Open Command reports: {reviews.get('open_count')}")
    return "\n".join(parts)


def _resolve_send_agent(
    agent_id: str | None,
    cfg: dict,
    agents: dict[str, dict],
) -> tuple[str, str | None]:
    """Pick agent for send; fall back to maintainer so founder messages are not lost."""
    aid = agent_id or cfg.get("selected_live_agent") or "cursor_maintainer"
    if aid == "cursor_ide":
        aid = "cursor_maintainer"
    spec = agents.get(aid)
    if spec and spec.get("can_chat") and _is_agent_enabled(aid, cfg):
        return aid, None
    if _is_agent_enabled("cursor_maintainer", cfg) and agents.get("cursor_maintainer", {}).get("can_chat"):
        note = None
        if aid != "cursor_maintainer":
            note = (
                f"{agents.get(aid, {}).get('label', aid)} was selected but not reachable — "
                "message sent to **Cursor — SinaaiDataBase (this chat)** instead."
            )
        return "cursor_maintainer", note
    return aid, None


def _dbg_intel(hypothesis_id: str, location: str, message: str, data: dict | None = None) -> None:
    # #region agent log
    try:
        import time

        p = Path("/Users/sinakazemnezhad/Desktop/SinaaiDataBase/.cursor/debug-9afa14.log")
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
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


def talk_to_live_agent(
    message: str,
    *,
    agent_id: str | None = None,
    topic: str = "general",
    hub_payload: dict | None = None,
    inject_cursor: bool | None = None,
) -> dict:
    # #region agent log
    import time as _time

    _chat_t0 = _time.time()
    _dbg_intel(
        "H4",
        "intelligence_circle.py:talk_to_live_agent:entry",
        "chat request",
        {"agent_id": agent_id, "topic": topic, "msg_len": len((message or "").strip())},
    )
    # #endregion
    text = (message or "").strip()
    if not text:
        return {"ok": False, "error": "message required"}
    cfg = _load_config()
    topic = topic if topic in TOPICS else "general"
    agents = {a["id"]: a for a in _live_agent_rows(hub_payload)}
    aid, reroute_note = _resolve_send_agent(agent_id, cfg, agents)

    if not _is_agent_enabled(aid, cfg):
        return {
            "ok": False,
            "error": f"{aid} is off — turn on **Cursor — SinaaiDataBase** in Live agents",
            **_build_live_response(hub_payload, aid),
        }

    spec = agents.get(aid)
    if not spec or not spec.get("can_chat"):
        return {
            "ok": False,
            "error": "No live agent ready — turn on **Cursor — SinaaiDataBase** and select it",
            **_build_live_response(hub_payload, "cursor_maintainer"),
        }

    cfg["selected_live_agent"] = aid
    _save_config(cfg)

    if aid == "semej":
        return {
            "ok": False,
            "error": "SEMEJ uses the SEMEJ tab — Chrome chain, not this chat box",
            "redirect_tab": "semej",
            **_build_live_response(hub_payload, aid),
        }

    if aid == "openrouter":
        out = send_to_openrouter(text, topic=topic, hub_payload=hub_payload)
        out["topic"] = topic
        return out

    if aid in ("cursor_maintainer", "cursor_ide"):
        out = send_to_cursor_maintainer(
            text, topic=topic, hub_payload=hub_payload, inject_cursor=inject_cursor
        )
        out["topic"] = topic
        if reroute_note:
            out["message"] = reroute_note
            out["rerouted_from"] = agent_id or cfg.get("selected_live_agent")
        # #region agent log
        _dbg_intel(
            "H4",
            "intelligence_circle.py:talk_to_live_agent:exit",
            "maintainer chat done",
            {"ms": int((_time.time() - _chat_t0) * 1000), "ok": out.get("ok")},
        )
        # #endregion
        return out

    if aid == "cursor_cloud":
        from loop_advisor import advisor_chat, set_provider  # noqa: WPS433

        set_provider("cursor_cloud")
        ctx = _minimal_hub_context(hub_payload, topic)
        full = f"{ctx}\n\nFounder (via Sina Command Live agents · Cursor Cloud):\n{text}"
        _append_agent_session("cursor_cloud", "user", text, topic=topic)
        result = advisor_chat(full, payload=hub_payload)
        if result.get("ok") and result.get("reply"):
            _append_agent_session("cursor_cloud", "assistant", result["reply"], topic=topic)
            append_comms(agent_id=aid, direction="agent_to_hub", content=result["reply"], topic=topic)
        base = _build_live_response(hub_payload, "cursor_cloud", topic=topic)
        if not result.get("ok"):
            base["ok"] = False
            base["error"] = result.get("error", "Cursor Cloud failed")
        else:
            base["reply"] = result.get("reply")
        return base

    return {"ok": False, "error": f"unsupported agent: {aid}"}


def generate_brief(*, hub_payload: dict | None = None) -> dict:
    payload = hub_payload or {}
    agents = _live_agent_rows(payload)
    lines = [
        "# Live agents brief",
        f"**Generated:** {_now()}",
        "",
        "## Connected agents (API / cloud / bridge)",
    ]
    for a in agents:
        lines.append(f"- **{a['label']}** — {'online' if a.get('online') else 'offline'} · {a.get('detail', '')}")
    lines.extend(["", "## Hub ↔ agent comms (recent)"])
    for c in read_comms(limit=20):
        lines.append(
            f"- {c.get('at', '')[:19]} **{c.get('agent_id')}** {c.get('direction')}: {c.get('content', '')[:160]}"
        )
    lines.append("\n*Repo work stays in Private agents pages — not mixed here.*")
    text = "\n".join(lines)
    BRIEF_PATH.write_text(text, encoding="utf-8")
    return {"ok": True, "path": str(BRIEF_PATH), "preview": text[:2500], "message": "Live agents brief saved"}


def circle_payload(*, hub_payload: dict | None = None) -> dict:
    cfg = _load_config()
    agents = {a["id"]: a for a in _live_agent_rows(hub_payload)}
    sel = _preferred_live_agent(cfg)
    spec = agents.get(sel)
    if not spec or not spec.get("can_chat") or not _is_agent_enabled(sel, cfg):
        sel, _ = _resolve_send_agent(None, cfg, agents)
    if cfg.get("selected_live_agent") != sel:
        cfg["selected_live_agent"] = sel
        _save_config(cfg)
    agents = _live_agent_rows(hub_payload)
    online = [a for a in agents if a.get("online") and a.get("enabled", True)]
    base = _build_live_response(hub_payload, sel)
    base.update(
        {
            "topics": TOPICS,
            "online_count": len(online),
            "comms_path": str(COMMS_PATH),
            "brief_path": str(BRIEF_PATH),
            "brief_exists": BRIEF_PATH.is_file(),
            "config": {k: v for k, v in cfg.items() if k != "enabled_agents"},
            "tagline": f"{len(online)} live agent(s) on — each has its own chat; turn others off if you want one only.",
            "private_agents_link": "sidebar Private agents",
            "maintainer_auto_inject_cursor": bool(cfg.get("maintainer_auto_inject_cursor")),
        }
    )
    return base


def handle_circle_action(body: dict, *, hub_payload: dict | None = None) -> dict:
    action = (body.get("action") or "status").strip().lower()
    if action == "status":
        # #region agent log
        import time as _time

        _st0 = _time.time()
        _dbg_intel("H1", "intelligence_circle.py:handle_circle_action:status", "status request", {"action": action})
        out = circle_payload(hub_payload=hub_payload)
        _dbg_intel(
            "H1",
            "intelligence_circle.py:handle_circle_action:status:done",
            "status done",
            {"ms": int((_time.time() - _st0) * 1000), "agents": len(out.get("live_agents") or [])},
        )
        return out
        # #endregion
    if action in ("chat", "talk"):
        inject_opt = body["inject_cursor"] if "inject_cursor" in body else None
        return talk_to_live_agent(
            body.get("message", ""),
            agent_id=body.get("agent_id") or body.get("live_agent"),
            topic=body.get("topic", "general"),
            hub_payload=hub_payload,
            inject_cursor=inject_opt,
        )
    if action == "set_maintainer_auto_inject":
        cfg = _load_config()
        cfg["maintainer_auto_inject_cursor"] = bool(body.get("enabled"))
        _save_config(cfg)
        out = circle_payload(hub_payload=hub_payload)
        out["maintainer_auto_inject_cursor"] = cfg["maintainer_auto_inject_cursor"]
        out["message"] = (
            "Live agent sends will also paste into Cursor"
            if cfg["maintainer_auto_inject_cursor"]
            else "Live agent sends stay in the app only (no Cursor paste)"
        )
        return out
    if action in ("ping", "keepalive"):
        out = ping_live_agents()
        base = circle_payload(hub_payload=hub_payload)
        base.update({k: v for k, v in out.items() if k not in base})
        return base
    if action == "brief":
        return generate_brief(hub_payload=hub_payload)
    if action in ("set_agent_enabled", "toggle_agent"):
        aid = body.get("agent_id") or body.get("live_agent") or ""
        enabled = body.get("enabled")
        if enabled is None:
            cfg = _load_config()
            enabled = not _is_agent_enabled(aid, cfg)
        r = _set_agent_enabled(aid, bool(enabled))
        return {**r, **circle_payload(hub_payload=hub_payload)}
    if action == "select_agent":
        cfg = _load_config()
        aid = body.get("agent_id") or body.get("live_agent") or _preferred_live_agent(cfg)
        if aid == "cursor_ide":
            aid = "cursor_maintainer"
        if not _is_agent_enabled(aid, cfg):
            return {"ok": False, "error": f"{aid} is off — turn it on first", **circle_payload(hub_payload=hub_payload)}
        cfg["selected_live_agent"] = aid
        _save_config(cfg)
        return circle_payload(hub_payload=hub_payload)
    if action == "set_provider":
        aid = body.get("provider", "openrouter")
        r = _set_agent_enabled(aid, True)
        cfg = _load_config()
        cfg["selected_live_agent"] = aid
        _save_config(cfg)
        return {**r, **circle_payload(hub_payload=hub_payload)}
    if action in ("clear_session", "clear_advisor", "clear_maintainer"):
        aid = body.get("agent_id") or body.get("live_agent")
        cfg = _load_config()
        if not aid:
            aid = _preferred_live_agent(cfg)
        if aid == "cursor_ide":
            aid = "cursor_maintainer"
        clear_agent_chat(aid)
        return {
            "ok": True,
            "cleared_agent": aid,
            "message": "Chat cleared — stays empty after Refresh until you send again",
        }
    if action in ("poll_ide", "poll_maintainer"):
        return poll_cursor_maintainer(hub_payload=hub_payload)
    if action == "agent_reply":
        MAINTAINER_OUTBOX.parent.mkdir(parents=True, exist_ok=True)
        MAINTAINER_OUTBOX.write_text((body.get("reply") or "").strip(), encoding="utf-8")
        return poll_cursor_maintainer(hub_payload=hub_payload)
    return {"ok": False, "error": f"unknown action: {action}"}

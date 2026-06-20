#!/usr/bin/env python3
"""Advisor AI — separate from executing Cursor agent. Multiple backends."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

CHAT_PATH = Path.home() / ".sina" / "advisor-chat.json"
CONFIG_PATH = Path.home() / ".sina" / "advisor-config.json"
IDE_INBOX = Path.home() / ".sina" / "advisor-cursor-inbox.md"
IDE_OUTBOX = Path.home() / ".sina" / "advisor-cursor-outbox.md"
SOURCE_A = Path(__file__).resolve().parents[1]
MAX_MESSAGES = 40

ADVISOR_SYSTEM = """You are the Sina OS Advisor — a strategic coach for founder ASF.
You are NOT the Cursor agent that writes code. You advise before and during the 10-round agent loop.

You know:
- Sina Command hub, P0 RunReceipt, MergePack, five-repo dispatch, THREAD boundaries
- Executing agent works in Cursor; you only plan and discuss
- Founder triggers a loop: Advisor (you) reshapes prompts after each executing-agent answer

Be concise, warm, practical. Suggest direction and clarify goals.
Never ask founder to use Terminal. Point to Private agents page, Actions, Today.
If asked to run code, say the executing Cursor agent will do that after loop starts."""

PROVIDERS = {
    "openrouter": "OpenRouter API (Gemini/etc.)",
    "cursor_cloud": "Cursor Cloud Agent (CURSOR_API_KEY + SDK)",
    "cursor_ide": "Cursor IDE — inject into Advisor chat in Cursor",
}


def _load_vault_keys() -> dict:
    keys = {"OPENROUTER_API_KEY": "", "CURSOR_API_KEY": ""}
    for vault in (Path.home() / ".sina/secrets.env", Path.home() / "Desktop/SinaPromptOS/secrets.env"):
        if not vault.is_file():
            continue
        for line in vault.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            for name in keys:
                if line.startswith(f"{name}="):
                    keys[name] = line.split("=", 1)[1].strip().strip('"').strip("'")
    return keys


def _load_config() -> dict:
    if not CONFIG_PATH.is_file():
        return {
            "provider": "openrouter",
            "cursor_agent_id": None,
            "cursor_cloud_last_ping": None,
            "cursor_cloud_last_ok": None,
        }
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def _provider_is_ready(provider: str, st: dict) -> bool:
    if provider == "openrouter":
        return bool(st.get("openrouter_ready"))
    if provider == "cursor_cloud":
        return bool(st.get("cursor_cloud_ready"))
    if provider == "cursor_ide":
        return bool(st.get("cursor_ide_ready", True))
    return False


def _ensure_working_provider(cfg: dict, st: dict) -> str:
    """If saved provider is offline, use OpenRouter when vault has a key (founder already configured)."""
    current = cfg.get("provider", "openrouter")
    if _provider_is_ready(current, st):
        return current
    if st.get("openrouter_ready"):
        if current != "openrouter":
            cfg["provider"] = "openrouter"
            cfg["provider_fallback_from"] = current
            _save_config(cfg)
        return "openrouter"
    if st.get("cursor_ide_ready"):
        return "cursor_ide"
    return current


def _load_chat() -> dict:
    if not CHAT_PATH.is_file():
        return {"messages": [], "updated_at": None}
    return json.loads(CHAT_PATH.read_text(encoding="utf-8"))


def _save_chat(data: dict) -> None:
    CHAT_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    CHAT_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def provider_status() -> dict:
    keys = _load_vault_keys()
    cfg = _load_config()
    sdk = _cursor_sdk_available()
    st = {
        "providers": PROVIDERS,
        "openrouter_ready": bool(keys["OPENROUTER_API_KEY"]),
        "openrouter_vault": "~/.sina/secrets.env",
        "cursor_cloud_ready": bool(keys["CURSOR_API_KEY"]) and sdk,
        "cursor_cloud_sdk": sdk,
        "cursor_ide_ready": True,
        "cursor_agent_id": cfg.get("cursor_agent_id"),
        "ide_outbox_pending": IDE_OUTBOX.is_file() and IDE_OUTBOX.stat().st_size > 20,
    }
    st["current"] = _ensure_working_provider(cfg, st)
    if cfg.get("provider_fallback_from") and st["current"] == "openrouter":
        st["fallback_note"] = (
            f"Using OpenRouter (vault key found). "
            f"{cfg['provider_fallback_from']} was selected but is not configured."
        )
    return st


def advisor_ready() -> bool:
    st = provider_status()
    p = st["current"]
    if p == "openrouter":
        return st["openrouter_ready"]
    if p == "cursor_cloud":
        return st["cursor_cloud_ready"]
    return True  # cursor_ide always available


def advisor_payload() -> dict:
    st = provider_status()
    p = st["current"]
    labels = {
        "openrouter": "OpenRouter API",
        "cursor_cloud": "Cursor Cloud Agent",
        "cursor_ide": "Cursor IDE bridge",
    }
    ready = advisor_ready()
    hint = PROVIDERS.get(p, p)
    if not ready:
        if p == "openrouter":
            hint = "OpenRouter key not loaded — check ~/.sina/secrets.env and Restart hub"
        elif p == "cursor_cloud":
            hint = "Cursor Cloud optional — tap OpenRouter (vault already has your key)"
        else:
            hint = PROVIDERS.get(p, p)
    label = f"Advisor: {labels.get(p, p)}" + (" · Online" if ready else f" · {hint}")
    if st.get("fallback_note") and ready:
        label = f"Advisor: {labels.get(p, p)} · Online (vault)"
    return {
        "advisor_ready": ready,
        "advisor_provider": p,
        "advisor_label": label,
        "advisor_messages": (_load_chat().get("messages") or [])[-20:],
        "advisor_providers": st,
        "openrouter_ready": st.get("openrouter_ready"),
    }


def _cursor_sdk_available() -> bool:
    try:
        import cursor_sdk  # noqa: F401

        return True
    except ImportError:
        return False


def _chat_openrouter(messages: list[dict], *, system: str | None = None) -> tuple[bool, str]:
    import ssl
    import certifi
    import urllib.request
    import os

    keys = _load_vault_keys()
    key = keys["OPENROUTER_API_KEY"]
    if not key:
        return False, "OPENROUTER_API_KEY missing in ~/.sina/secrets.env"

    body = json.dumps(
        {
            "model": os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
            "messages": [{"role": "system", "content": system or ADVISOR_SYSTEM}] + messages[-16:],
            "temperature": 0.5,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://local.sina-command",
            "X-Title": "SinaAdvisor",
        },
        method="POST",
    )
    ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        data = json.loads(resp.read().decode())
    return True, data["choices"][0]["message"]["content"].strip()


def _chat_cursor_cloud(user_turn: str, history: list[dict]) -> tuple[bool, str]:
    keys = _load_vault_keys()
    api_key = keys["CURSOR_API_KEY"]
    if not api_key:
        return False, "CURSOR_API_KEY missing — Cursor Dashboard → Integrations → User API Keys"

    if not _cursor_sdk_available():
        return False, "Install: pip3 install cursor-sdk  (then restart Sina Command server)"

    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions  # noqa: WPS433

    transcript = "\n".join(
        f"{'Founder' if m['role']=='user' else 'Advisor'}: {m.get('content','')}"
        for m in history[-10:]
        if m["role"] in ("user", "assistant")
    )
    prompt = (
        f"{ADVISOR_SYSTEM}\n\n---\nConversation so far:\n{transcript}\n\n"
        f"Founder now says:\n{user_turn}\n\nReply as Advisor only (no code edits)."
    )

    try:
        result = Agent.prompt(
            prompt,
            AgentOptions(
                api_key=api_key,
                model="composer-2.5",
                local=LocalAgentOptions(cwd=str(SOURCE_A)),
            ),
        )
        text = (getattr(result, "result", None) or "").strip()
        agent_id = getattr(result, "agent_id", None) or getattr(result, "id", None)
        if agent_id:
            cfg = _load_config()
            cfg["cursor_agent_id"] = str(agent_id)
            cfg["cursor_cloud_last_ping"] = datetime.now(timezone.utc).isoformat()
            cfg["cursor_cloud_last_ok"] = True
            _save_config(cfg)
        if not text:
            text = "Cursor agent finished — open Cursor if you need the full thread."
        return True, text
    except Exception as e:
        cfg = _load_config()
        cfg["cursor_cloud_last_ping"] = datetime.now(timezone.utc).isoformat()
        cfg["cursor_cloud_last_ok"] = False
        _save_config(cfg)
        return False, str(e)


def keepalive_cursor_cloud() -> dict:
    """Light ping to keep Cursor Cloud advisor path warm (when SDK + key present)."""
    st = provider_status()
    if not st.get("cursor_cloud_ready"):
        return {"ok": False, "message": "cursor_cloud not ready"}
    cfg = _load_config()
    ping_prompt = (
        "Intelligence Circle keepalive — reply with one short line: online and ready to advise ASF "
        "(bugs, roadmap, UI, business). No code edits."
    )
    ok, reply = _chat_cursor_cloud(ping_prompt, [])
    cfg = _load_config()
    cfg["cursor_cloud_last_ping"] = datetime.now(timezone.utc).isoformat()
    cfg["cursor_cloud_last_ok"] = ok
    _save_config(cfg)
    return {
        "ok": ok,
        "message": reply[:200] if ok else reply,
        "cursor_agent_id": cfg.get("cursor_agent_id"),
    }


def _chat_cursor_ide(user_message: str) -> dict:
    """Save inbox only — never auto-paste into Cursor."""
    IDE_INBOX.parent.mkdir(parents=True, exist_ok=True)
    IDE_INBOX.write_text(
        f"""# Sina Advisor — reply needed

Founder message from Sina Command app:

{user_message}

---
**You are the Advisor** (not the executor). Reply in this chat.

**Founder never uses Terminal.** After you reply, run (advisor agent only):

```bash
~/Desktop/SourceA/scripts/advisor-cursor-reply.sh "Your reply here"
```

The Sina Command app polls and shows your answer automatically.
""",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "reply": "Saved in app — open ~/.sina/advisor-cursor-inbox.md in Cursor yourself if needed (no auto-paste).",
        "pending_ide": False,
        "inject_skipped": True,
    }


def _append_messages(user: str, reply: str, *, provider: str) -> list:
    data = _load_chat()
    msgs = data.get("messages") or []
    msgs.append({
        "role": "user",
        "content": user,
        "at": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
    })
    msgs.append({
        "role": "assistant",
        "content": reply,
        "at": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
    })
    data["messages"] = msgs[-MAX_MESSAGES:]
    _save_chat(data)
    return data["messages"]


def advisor_chat(user_message: str, *, payload: dict | None = None) -> dict:
    text = (user_message or "").strip()
    if not text:
        return {"ok": False, "error": "message required"}

    cfg = _load_config()
    provider = cfg.get("provider", "openrouter")
    if not advisor_ready():
        return {"ok": False, "error": advisor_payload()["advisor_label"]}

    data = _load_chat()
    msgs = data.get("messages") or []

    context = ""
    if payload and provider == "openrouter":
        from sina_ai_advisory import build_snapshot  # noqa: WPS433

        snap = build_snapshot(payload)
        context = f"\n\nLive snapshot:\n{json.dumps(snap, ensure_ascii=False)[:6000]}"
        text = text + context

    if provider == "cursor_ide":
        result = _chat_cursor_ide(text)
        if result.get("ok"):
            data = _load_chat()
            msgs = data.get("messages") or []
            msgs.append({
                "role": "user",
                "content": user_message,
                "at": datetime.now(timezone.utc).isoformat(),
                "provider": provider,
            })
            data["messages"] = msgs[-MAX_MESSAGES:]
            _save_chat(data)
        return result

    llm_msgs = [{"role": m["role"], "content": m["content"]} for m in msgs if m["role"] in ("user", "assistant")]
    llm_msgs.append({"role": "user", "content": text})

    if provider == "cursor_cloud":
        ok, reply = _chat_cursor_cloud(text, msgs)
    else:
        ok, reply = _chat_openrouter(llm_msgs)

    if not ok:
        return {"ok": False, "error": reply}

    messages = _append_messages(user_message, reply, provider=provider)
    return {"ok": True, "reply": reply, "messages": messages, "provider": provider}


def founder_reply_from_cursor(reply: str) -> dict:
    """Cursor Advisor chat posts answer back to app."""
    text = (reply or "").strip()
    if not text:
        return {"ok": False, "error": "reply required"}
    data = _load_chat()
    msgs = data.get("messages") or []
    if not msgs or msgs[-1].get("role") != "user":
        msgs.append({
            "role": "user",
            "content": "(via Cursor IDE)",
            "at": datetime.now(timezone.utc).isoformat(),
        })
    msgs.append({
        "role": "assistant",
        "content": text,
        "at": datetime.now(timezone.utc).isoformat(),
        "provider": "cursor_ide",
    })
    data["messages"] = msgs[-MAX_MESSAGES:]
    _save_chat(data)
    if IDE_OUTBOX.is_file():
        IDE_OUTBOX.unlink()
    return {"ok": True, "reply": text, "messages": data["messages"]}


def set_provider(provider: str) -> dict:
    if provider not in PROVIDERS:
        return {"ok": False, "error": f"unknown provider: {provider}"}
    st = provider_status()
    if provider == "openrouter" and not st.get("openrouter_ready"):
        return {"ok": False, "error": "OpenRouter key not found in ~/.sina/secrets.env"}
    if provider == "cursor_cloud" and not st.get("cursor_cloud_ready"):
        return {
            "ok": False,
            "error": "Cursor Cloud needs CURSOR_API_KEY + cursor-sdk — use OpenRouter (vault key already set)",
        }
    cfg = _load_config()
    cfg["provider"] = provider
    cfg.pop("provider_fallback_from", None)
    if provider != "cursor_cloud":
        cfg["cursor_agent_id"] = None
    _save_config(cfg)
    msg = f"Advisor set to {PROVIDERS[provider]}"
    if provider == "openrouter" and st.get("openrouter_ready"):
        msg = "Advisor set to OpenRouter — using your vault key"
    return {"ok": True, "provider": provider, "message": msg}


def advisor_clear() -> dict:
    _save_chat({"messages": []})
    cfg = _load_config()
    cfg["cursor_agent_id"] = None
    _save_config(cfg)
    return {"ok": True, "message": "Advisor chat cleared"}


def advisor_context_text() -> str:
    data = _load_chat()
    msgs = data.get("messages") or []
    if not msgs:
        return ""
    lines = []
    for m in msgs[-8:]:
        role = "Founder" if m["role"] == "user" else "Advisor"
        prov = m.get("provider", "")
        lines.append(f"{role}{f'({prov})' if prov else ''}: {m.get('content', '')[:500]}")
    return "\n".join(lines)


def handle_advisor_action(body: dict, *, payload: dict | None = None) -> dict:
    action = (body.get("action") or "status").strip().lower()
    if action == "status":
        return {"ok": True, **advisor_payload()}
    if action == "chat":
        return advisor_chat(body.get("message", ""), payload=payload)
    if action == "clear":
        return advisor_clear()
    if action == "set_provider":
        return set_provider(body.get("provider", "openrouter"))
    if action == "founder_reply":
        return founder_reply_from_cursor(body.get("reply", ""))
    if action == "poll_ide":
        if IDE_OUTBOX.is_file():
            text = IDE_OUTBOX.read_text(encoding="utf-8").strip()
            return founder_reply_from_cursor(text)
        data = _load_chat()
        msgs = data.get("messages") or []
        if len(msgs) >= 2 and msgs[-1].get("role") == "assistant" and msgs[-1].get("provider") == "cursor_ide":
            last_user = next((m for m in reversed(msgs[:-1]) if m.get("role") == "user"), None)
            if last_user and last_user.get("provider") == "cursor_ide":
                return {"ok": True, "reply": msgs[-1]["content"], "messages": msgs}
        return {"ok": False, "error": "no IDE reply yet"}
    return {"ok": False, "error": f"unknown action: {action}"}

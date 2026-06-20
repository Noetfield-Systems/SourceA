#!/usr/bin/env python3
"""
SEMEJ — multi-AI Chrome loop: idea → chain of signed-in chatbots → artifact.

Like agent-loop but targets Gemini, ChatGPT, Perplexity, Grok, etc. in Chrome.
Self-healing: retry, simplified prompt, manual inject, skip provider.
"""
from __future__ import annotations

import json
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from semej_browser import SemejBrowser, chrome_debug_alive, open_chrome_debug, playwright_installed
from semej_providers import chain_ids, load_config, providers_payload, save_config

LOOP_PATH = Path.home() / ".sina" / "semej-loop.json"
ARTIFACT_DIR = Path.home() / ".sina" / "semej-artifacts"
SOURCE_A = Path(__file__).resolve().parents[1]

BRIDGE_SYSTEM = """You are SEMEJ bridge planner — you write the NEXT prompt for the next AI chatbot in a chain.
The founder's idea becomes an artifact through multiple AIs (Gemini, ChatGPT, Perplexity, Grok, etc.).

Output ONLY valid JSON:
{
  "round_title": "short label",
  "prompt_for_ai": "full message to paste into the next chatbot",
  "bridge_note": "one sentence for founder UI",
  "artifact_delta": "what this step adds toward the final artifact (markdown fragment)"
}
Rules:
- Reference the previous AI's answer when moving to the next provider.
- Ask the next AI to analyze, challenge, extend, or format — do not repeat the same ask.
- Keep prompts self-contained (include key context from prior answer).
- Never ask the human to use Terminal."""

HEAL_SYSTEM = """SEMEJ browser step failed. Suggest recovery as JSON only:
{"action":"retry|manual|skip|abort","simplified_prompt":"optional shorter prompt","note":"founder-facing one line"}"""


_worker_lock = threading.Lock()
_worker_running = False


def _load() -> dict:
    if not LOOP_PATH.is_file():
        return _default_state()
    return json.loads(LOOP_PATH.read_text(encoding="utf-8"))


def _default_state() -> dict:
    return {
        "active": False,
        "status": "idle",
        "round": 0,
        "max_rounds": 10,
        "idea": "",
        "chain": [],
        "chain_index": 0,
        "history": [],
        "current_provider": None,
        "current_prompt": None,
        "current_title": None,
        "bridge_note": None,
        "last_response": None,
        "last_response_from": None,
        "artifact_parts": [],
        "error": None,
        "heal_count": 0,
        "awaiting_since": None,
        "needs_manual": False,
    }


def _save(st: dict) -> None:
    LOOP_PATH.parent.mkdir(parents=True, exist_ok=True)
    st["updated_at"] = datetime.now(timezone.utc).isoformat()
    LOOP_PATH.write_text(json.dumps(st, indent=2), encoding="utf-8")


def _parse_json(text: str) -> dict | None:
    text = (text or "").strip()
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


def _openrouter_chat(system: str, user: str) -> tuple[bool, str]:
    import ssl
    import certifi
    import urllib.request
    import os

    key = ""
    for vault in (Path.home() / ".sina/secrets.env", Path.home() / "Desktop/SinaPromptOS/secrets.env"):
        if vault.is_file():
            for line in vault.read_text(encoding="utf-8").splitlines():
                if line.startswith("OPENROUTER_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        return False, "OPENROUTER_API_KEY missing"
    body = json.dumps(
        {
            "model": os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
        }
    ).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://local.sina-command",
            "X-Title": "SEMEJ",
        },
        method="POST",
    )
    ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        data = json.loads(resp.read().decode())
    return True, data["choices"][0]["message"]["content"].strip()


def _bridge_plan(st: dict, *, first: bool = False) -> tuple[bool, dict | str]:
    chain = st.get("chain") or []
    idx = st.get("chain_index", 0)
    prov = chain[idx] if idx < len(chain) else "done"
    hist = st.get("history") or []
    user = json.dumps(
        {
            "idea": st.get("idea"),
            "round": st.get("round"),
            "max_rounds": st.get("max_rounds"),
            "next_provider": prov,
            "first_in_chain": first,
            "last_response_from": st.get("last_response_from"),
            "last_response": (st.get("last_response") or "")[:8000],
            "history_titles": [h.get("title") for h in hist[-6:]],
            "artifact_so_far": "\n\n".join(st.get("artifact_parts") or [])[:6000],
        },
        ensure_ascii=False,
    )
    ok, raw = _openrouter_chat(BRIDGE_SYSTEM, user)
    if not ok:
        return False, raw
    parsed = _parse_json(raw)
    if not parsed or not parsed.get("prompt_for_ai"):
        return False, "bridge planner returned invalid JSON"
    return True, parsed


def _heal_plan(st: dict, err: str) -> dict:
    user = json.dumps({"error": err, "provider": st.get("current_provider"), "round": st.get("round")})
    ok, raw = _openrouter_chat(HEAL_SYSTEM, user)
    if ok:
        p = _parse_json(raw)
        if p:
            return p
    return {"action": "manual", "note": err}


def _save_artifact(st: dict) -> Path | None:
    parts = st.get("artifact_parts") or []
    if not parts and not st.get("last_response"):
        return None
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", (st.get("idea") or "artifact")[:40].lower()).strip("-") or "artifact"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = ARTIFACT_DIR / f"{slug}-{ts}.md"
    body = f"# SEMEJ artifact\n\n**Idea:** {st.get('idea')}\n\n**Rounds:** {st.get('round')}/{st.get('max_rounds')}\n\n"
    body += "\n\n---\n\n".join(parts)
    if st.get("last_response") and not parts:
        body += f"\n\n## Final\n\n{st['last_response']}"
    path.write_text(body, encoding="utf-8")
    st["artifact_path"] = str(path)
    _save(st)
    return path


def _dispatch_to_provider(st: dict) -> None:
    """Background: open provider tab, send prompt, try auto-capture."""
    global _worker_running
    prov_id = st.get("current_provider")
    prompt = st.get("current_prompt") or ""
    browser = SemejBrowser()
    try:
        ok, msg = browser.send_prompt(prov_id, prompt)
        if not ok:
            heal = _heal_plan(st, msg)
            st = _load()
            st["error"] = msg
            st["status"] = "heal"
            st["heal_suggestion"] = heal
            if heal.get("action") == "retry" and st.get("heal_count", 0) < 2:
                st["heal_count"] = st.get("heal_count", 0) + 1
                st["current_prompt"] = heal.get("simplified_prompt") or prompt
                st["status"] = "sending"
                _save(st)
                _dispatch_to_provider(st)
                return
            st["needs_manual"] = heal.get("action") in ("manual", "retry")
            st["status"] = "awaiting_manual" if st["needs_manual"] else "error"
            _save(st)
            return
        st = _load()
        st["status"] = "awaiting_response"
        st["awaiting_since"] = datetime.now(timezone.utc).isoformat()
        st["needs_manual"] = False
        _save(st)

        cfg = load_config()
        deadline = cfg.get("wait_response_sec", 90)
        polls = max(1, deadline // cfg.get("poll_interval_sec", 4))
        for _ in range(polls):
            st = _load()
            if st.get("status") != "awaiting_response":
                return
            ok2, text = browser.extract_response(prov_id)
            if ok2 and len(text) > 50:
                _on_provider_response(text, auto=True)
                return
            import time

            time.sleep(cfg.get("poll_interval_sec", 4))

        st = _load()
        st["status"] = "awaiting_manual"
        st["needs_manual"] = True
        st["bridge_note"] = "Copy answer from Chrome → Inject answer in Sina Command"
        _save(st)
    finally:
        browser.close()
        with _worker_lock:
            _worker_running = False


def _start_worker(st: dict) -> None:
    global _worker_running
    with _worker_lock:
        if _worker_running:
            return
        _worker_running = True
    t = threading.Thread(target=_dispatch_to_provider, args=(st,), daemon=True)
    t.start()


def _step_chain_index(st: dict) -> dict:
    """After a provider answers, move to next AI in chain or next round."""
    chain = st.get("chain") or []
    if not chain:
        return st
    idx = st.get("chain_index", 0)
    if idx + 1 >= len(chain):
        st["chain_index"] = 0
        st["round"] = int(st.get("round") or 1) + 1
    else:
        st["chain_index"] = idx + 1
    return st


def _on_provider_response(text: str, *, auto: bool = False) -> dict:
    st = _load()
    if not st.get("active"):
        return {"ok": False, "error": "no active loop"}
    prov = st.get("current_provider")
    st["last_response"] = text
    st["last_response_from"] = prov
    st["needs_manual"] = False
    st["status"] = "bridging"
    part = st.get("bridge_note") or f"Answer from {prov}"
    st.setdefault("history", []).append(
        {
            "round": st.get("round"),
            "provider": prov,
            "title": st.get("current_title") or prov,
            "summary": text[:500],
            "auto_captured": auto,
        }
    )
    if st.get("artifact_delta"):
        st.setdefault("artifact_parts", []).append(f"## {prov} (R{st.get('round')})\n\n{text[:4000]}")
    _save(st)

    st = _step_chain_index(st)
    if int(st.get("round") or 1) > int(st.get("max_rounds") or 10):
        st["status"] = "done"
        st["active"] = False
        path = _save_artifact(st)
        return {"ok": True, "message": "SEMEJ loop complete", "artifact_path": str(path) if path else None}
    ok, planned = _bridge_plan(st)
    if not ok:
        st["status"] = "error"
        st["error"] = str(planned)
        _save(st)
        return {"ok": False, "error": planned}

    st["current_title"] = planned.get("round_title")
    st["current_prompt"] = planned.get("prompt_for_ai")
    st["bridge_note"] = planned.get("bridge_note")
    delta = planned.get("artifact_delta")
    if delta:
        st.setdefault("artifact_parts", []).append(f"### Bridge note R{st.get('round')}\n\n{delta}")
    chain = st.get("chain") or []
    idx = st.get("chain_index", 0)
    st["current_provider"] = chain[idx % len(chain)]
    st["status"] = "sending"
    _save(st)
    _start_worker(st)
    return {"ok": True, "message": f"Bridging → {st['current_provider']}", "bridge_note": st.get("bridge_note")}


def semej_payload() -> dict:
    st = _load()
    cfg = providers_payload()
    port = cfg.get("chrome_debug_port", 9222)
    return {
        "ok": True,
        "active": st.get("active"),
        "status": st.get("status", "idle"),
        "round": st.get("round"),
        "max_rounds": st.get("max_rounds", 10),
        "idea": st.get("idea"),
        "chain": st.get("chain") or cfg.get("chain_default"),
        "chain_index": st.get("chain_index"),
        "current_provider": st.get("current_provider"),
        "current_prompt_preview": (st.get("current_prompt") or "")[:600],
        "bridge_note": st.get("bridge_note"),
        "history": st.get("history") or [],
        "error": st.get("error"),
        "needs_manual": st.get("needs_manual"),
        "heal_suggestion": st.get("heal_suggestion"),
        "artifact_path": st.get("artifact_path"),
        "providers": cfg.get("providers"),
        "chain_default": cfg.get("chain_default"),
        "chrome_ready": chrome_debug_alive(port),
        "playwright_ready": playwright_installed(),
        "chrome_debug_port": port,
        "roles": {
            "semej": "SEMEJ — opens Chrome, chains signed-in AI chats",
            "bridge": "OpenRouter bridge — rewrites prompt per next AI",
            "heal": "Self-heal — retry / manual inject / skip",
        },
        "inject_script": str(SOURCE_A / "scripts/semej-inject-answer.sh"),
        "chrome_script": str(SOURCE_A / "scripts/semej-start-chrome.sh"),
    }


def handle_semej_action(body: dict) -> dict:
    action = (body.get("action") or "status").strip().lower()

    if action == "status":
        return {"ok": True, **semej_payload()}

    if action == "open_chrome":
        return open_chrome_debug()

    if action == "set_chain":
        chain = body.get("chain") or body.get("providers")
        if not chain:
            return {"ok": False, "error": "chain list required"}
        cfg = load_config()
        cfg["chain_default"] = chain_ids(list(chain))
        save_config(cfg)
        return {"ok": True, "chain": cfg["chain_default"]}

    if action == "cancel":
        st = _default_state()
        _save(st)
        return {"ok": True, "message": "SEMEJ loop cancelled"}

    if action == "response":
        text = (body.get("response") or body.get("answer") or "").strip()
        if not text:
            return {"ok": False, "error": "response text required"}
        return _on_provider_response(text, auto=body.get("auto", False))

    if action == "skip_provider":
        st = _load()
        st = _step_chain_index(st)
        st["last_response"] = st.get("last_response") or "(skipped)"
        _save(st)
        ok, planned = _bridge_plan(st)
        if not ok:
            return {"ok": False, "error": planned}
        st["current_prompt"] = planned.get("prompt_for_ai")
        st["current_title"] = planned.get("round_title")
        st["bridge_note"] = planned.get("bridge_note")
        chain = st.get("chain") or []
        st["current_provider"] = chain[st.get("chain_index", 0) % len(chain)]
        st["status"] = "sending"
        _save(st)
        _start_worker(st)
        return {"ok": True, "message": "Skipped to next provider"}

    if action == "start":
        idea = (body.get("idea") or body.get("goal") or "").strip()
        if not idea:
            return {"ok": False, "error": "idea required"}
        if not playwright_installed():
            return {
                "ok": False,
                "error": "Install SEMEJ deps first (Actions → Install SEMEJ browser tools)",
            }
        port = load_config().get("chrome_debug_port", 9222)
        if not chrome_debug_alive(port):
            opened = open_chrome_debug()
            if not opened.get("ok"):
                return opened
        chain = chain_ids(body.get("chain"))
        max_rounds = int(body.get("max_rounds") or 10)
        ok, planned = _bridge_plan(
            {
                "idea": idea,
                "round": 1,
                "max_rounds": max_rounds,
                "chain": chain,
                "chain_index": 0,
                "history": [],
                "artifact_parts": [],
            },
            first=True,
        )
        if not ok:
            return {"ok": False, "error": planned}
        st = {
            "active": True,
            "status": "sending",
            "round": 1,
            "max_rounds": max_rounds,
            "idea": idea,
            "chain": chain,
            "chain_index": 0,
            "history": [],
            "current_provider": chain[0],
            "current_title": planned.get("round_title"),
            "current_prompt": planned.get("prompt_for_ai"),
            "bridge_note": planned.get("bridge_note"),
            "artifact_parts": [],
            "artifact_delta": planned.get("artifact_delta"),
            "heal_count": 0,
            "run_id": str(uuid.uuid4())[:8],
        }
        if planned.get("artifact_delta"):
            st["artifact_parts"].append(f"## Start\n\n{planned['artifact_delta']}")
        _save(st)
        _start_worker(st)
        out = semej_payload()
        out["message"] = f"SEMEJ started → {chain[0]} in Chrome"
        return {"ok": True, **out}

    if action == "capture_now":
        st = _load()
        prov = st.get("current_provider")
        if not prov:
            return {"ok": False, "error": "no current provider"}
        browser = SemejBrowser()
        try:
            browser.connect()
            ok, text = browser.extract_response(prov)
            if ok:
                return _on_provider_response(text, auto=True)
            return {"ok": False, "error": text}
        finally:
            browser.close()

    return {"ok": False, "error": f"unknown action: {action}"}

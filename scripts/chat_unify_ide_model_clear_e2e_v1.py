#!/usr/bin/env python3
"""Chat Unify IDE — model lock + clear chat E2E (API + optional Playwright).

Receipt: ~/.sina/chat-unify-ide-model-clear-e2e-receipt-v1.json
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RECEIPT = Path.home() / ".sina" / "chat-unify-ide-model-clear-e2e-receipt-v1.json"
BASE = "http://127.0.0.1:13023"
API = f"{BASE}/api/chat-unify-ide/v1"


def _post(body: dict, token: str = "") -> dict:
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Forge-Token"] = token
    req = urllib.request.Request(API, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def _health() -> dict:
    with urllib.request.urlopen(f"{BASE}/health", timeout=4) as r:
        return json.loads(r.read().decode())


def static_checks() -> list[dict]:
    html = urllib.request.urlopen(f"{BASE}/terminal/index.html", timeout=8).read().decode()
    js = urllib.request.urlopen(f"{BASE}/terminal/terminal.js", timeout=8).read().decode()
    rows = [
        {"check": "no_smart_route_model_override", "ok": "route.model_id) model = route.model_id" not in js},
        {"check": "embed_early_api_route", "ok": 'qsBoot.get("embed") === "1"' in js and "CU_IDE_API" in js},
        {"check": "api_waits_engine_route", "ok": "await engineRouteReady" in js},
        {"check": "clear_button_wired", "ok": 'id="btn-clear-chat"' in html and "clearChatThread" in js},
        {"check": "gemini_flash_lite_hidden", "ok": "gemini-3.1-flash-lite" in js and "HIDDEN_DEFAULT_MODELS" in js},
    ]
    return rows


def api_checks(token: str) -> list[dict]:
    rows: list[dict] = []
    try:
        clear = _post({"action": "chat_thread_clear"}, token)
        rows.append({"check": "clear_thread_api", "ok": bool(clear.get("ok")), "detail": str(clear)[:120]})
    except Exception as exc:
        rows.append({"check": "clear_thread_api", "ok": False, "detail": str(exc)[:160]})
    try:
        thread = _post({"action": "chat_thread"}, token)
        turns = thread.get("turns") or []
        rows.append({"check": "thread_empty_after_clear", "ok": thread.get("ok") and len(turns) == 0, "count": len(turns)})
    except Exception as exc:
        rows.append({"check": "thread_empty_after_clear", "ok": False, "detail": str(exc)[:160]})
    try:
        turn = _post(
            {
                "action": "chat_turn",
                "text": "Reply with exactly: OPENAI_OK",
                "full_llm": True,
                "fast": False,
                "model": "gpt-4o",
            },
            token,
        )
        model_used = str((turn.get("llm") or {}).get("model") or "")
        rows.append(
            {
                "check": "openai_model_respected",
                "ok": turn.get("ok") and "gemini" not in model_used.lower() and "flash-lite" not in model_used.lower(),
                "model": model_used[:80],
            }
        )
    except Exception as exc:
        rows.append({"check": "openai_model_respected", "ok": False, "detail": str(exc)[:160]})
    return rows


def main() -> int:
    rows: list[dict] = []
    try:
        health = _health()
        rows.append({"check": "health_chat_unify", "ok": health.get("service") == "chat-unify", "detail": health.get("service")})
    except Exception as exc:
        rows.append({"check": "health_chat_unify", "ok": False, "detail": str(exc)[:160]})
        receipt = {"ok": False, "at": datetime.now(timezone.utc).isoformat(), "rows": rows}
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt, indent=2))
        return 1

    token = str(health.get("forge_local_token") or "")
    rows.extend(static_checks())
    rows.extend(api_checks(token))
    ok = all(r.get("ok") for r in rows)
    receipt = {"ok": ok, "at": datetime.now(timezone.utc).isoformat(), "base": BASE, "rows": rows}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"ok": ok, "receipt": str(RECEIPT), "failed": [r for r in rows if not r.get("ok")]}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Chat Unify — full E2E: shell + IDE + model lock + clear + engine.

Receipt: ~/.sina/chat-unify-full-e2e-receipt-v1.json
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "http://127.0.0.1:13023"
IDE_API = f"{BASE}/api/chat-unify-ide/v1"
ENGINE_API = f"{BASE}/api/chat-unify-engine/v1"
RECEIPT = Path.home() / ".sina" / "chat-unify-full-e2e-receipt-v1.json"
EXPECTED_UI = "4.9.9"
EXPECTED_TERMINAL_UI = "4.9.9-cu-combined"
MACHINE_TABS = (
    "forge-ide",
    "home",
    "start",
    "forge",
    "connect",
    "founder",
    "ord",
    "form",
    "api",
    "hubpro",
    "proofpack",
    "vocab",
)


def _get(path: str, timeout: float = 8) -> str:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def _post(url: str, body: dict, token: str = "", timeout: float = 90) -> dict:
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Forge-Token"] = token
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _row(check: str, ok: bool, **extra) -> dict:
    return {"check": check, "ok": bool(ok), **extra}


def shell_checks() -> list[dict]:
    rows: list[dict] = []
    try:
        html = _get("/")
        rows.append(_row("shell_health", True))
        ver = re.search(r'chat-unify-ui-version"\s+content="([^"]+)"', html)
        rows.append(_row("shell_version_meta", ver and ver.group(1) == EXPECTED_UI, detail=ver.group(1) if ver else ""))
        rows.append(_row("shell_forge_ide_tab", 'id="tab-forge-ide"' in html and 'data-tab="forge-ide"' in html))
        rows.append(_row("shell_all_machine_tabs", all(f'data-tab="{t}"' in html for t in MACHINE_TABS)))
        rows.append(
            _row(
                "shell_ide_iframe",
                'id="forge-ide-frame"' in html and "embed=1" in html and "guide-collapse" in html,
            )
        )
        rows.append(_row("shell_combined_css", "forge-connect.css" in html))
        css = _get("/forge-connect.css")
        rows.append(_row("shell_forge_ide_css", "ft-forge-ide-frame" in css))
    except Exception as exc:
        rows.append(_row("shell_health", False, detail=str(exc)[:160]))
    return rows


def terminal_checks() -> list[dict]:
    rows: list[dict] = []
    try:
        html = _get("/terminal/index.html?embed=1")
        js = _get("/terminal/terminal.js")
        css = _get("/terminal/terminal-desktop.css")
        models = json.loads(_get("/terminal/data/forge-terminal-models-public-v1.json"))
        rows.append(_row("terminal_ui_version", EXPECTED_TERMINAL_UI in js))
        rows.append(_row("terminal_editor_window", 'id="forge-editor-window"' in html))
        rows.append(_row("terminal_clear_btn", 'id="btn-clear-chat"' in html and "clearChatThread" in js))
        rows.append(_row("terminal_model_select", 'id="model-select"' in html))
        rows.append(_row("terminal_model_guide_toggle", 'id="btn-toggle-model-guide"' in html and "initModelGuideCollapse" in js))
        rows.append(_row("terminal_living_chat", "living_chat" in js))
        rows.append(_row("terminal_health_ping", "pingServerHealth" in js))
        rows.append(_row("terminal_fetch_timeout", "fetchJsonWithTimeout" in js))
        rows.append(_row("terminal_offline_banner", "showCuServerOfflineBanner" in js))
        rows.append(_row("terminal_embed_api_boot", 'qsBoot.get("embed") === "1"' in js and "CU_IDE_API" in js))
        rows.append(_row("terminal_engine_route_await", "await engineRouteReady" in js))
        rows.append(_row("terminal_no_route_model_swap", "route.model_id) model = route.model_id" not in js))
        rows.append(_row("terminal_lock_on_send", "lockUserModel(model)" in js))
        rows.append(_row("terminal_clear_suppress_reload", "suppressThreadReload" in js))
        rows.append(_row("terminal_combined_css", "forge-cu-combined" in css))
        rows.append(_row("terminal_no_gemini_flash_lite_catalog", "gemini-3.1-flash-lite" not in json.dumps(models)))
        openai_ids = [m.get("id") for m in models.get("models") or [] if m.get("group") == "OpenAI"]
        rows.append(_row("terminal_openai_models", "gpt-4o" in openai_ids))
    except Exception as exc:
        rows.append(_row("terminal_bundle", False, detail=str(exc)[:160]))
    return rows


def ide_api_checks(token: str) -> list[dict]:
    rows: list[dict] = []
    try:
        st = _post(IDE_API, {"action": "status"}, token, timeout=15)
        rows.append(_row("ide_status", st.get("ok"), detail=str(st.get("motor") or "")[:80]))
        models = st.get("models") or []
        rows.append(_row("ide_models_payload", bool(models), count=len(models)))
        rows.append(_row("ide_default_gpt4o", st.get("default_model") == "gpt-4o", detail=st.get("default_model")))
    except Exception as exc:
        rows.append(_row("ide_status", False, detail=str(exc)[:160]))

    try:
        _post(IDE_API, {"action": "chat_thread_clear"}, token)
        thread = _post(IDE_API, {"action": "chat_thread"}, token)
        rows.append(_row("ide_clear_empty", thread.get("ok") and len(thread.get("turns") or []) == 0))
    except Exception as exc:
        rows.append(_row("ide_clear_empty", False, detail=str(exc)[:160]))

    try:
        turn_hi = _post(
            IDE_API,
            {
                "action": "chat_turn",
                "text": "hi",
                "full_llm": True,
                "fast": True,
                "living_chat": True,
                "model": "deepseek-v4",
            },
            token,
            timeout=60,
        )
        hi_text = str(turn_hi.get("display_response") or turn_hi.get("response") or "")
        rows.append(
            _row(
                "ide_living_chat_hi",
                turn_hi.get("ok") and len(hi_text.strip()) > 0,
                detail=hi_text[:80],
            )
        )
    except Exception as exc:
        rows.append(_row("ide_living_chat_hi", False, detail=str(exc)[:160]))

    try:
        turn = _post(
            IDE_API,
            {
                "action": "chat_turn",
                "text": "E2E ping — reply one word: OK",
                "full_llm": True,
                "fast": True,
                "living_chat": True,
                "model": "gpt-4o",
            },
            token,
            timeout=90,
        )
        model_used = str((turn.get("llm") or {}).get("model") or "")
        rows.append(
            _row(
                "ide_openai_send",
                turn.get("ok") and "gemini" not in model_used.lower() and "flash-lite" not in model_used.lower(),
                model=model_used[:80],
            )
        )
        after = _post(IDE_API, {"action": "chat_thread"}, token)
        n = len(after.get("turns") or [])
        rows.append(_row("ide_thread_has_messages", after.get("ok") and n >= 2, count=n))
        _post(IDE_API, {"action": "chat_thread_clear"}, token)
        cleared = _post(IDE_API, {"action": "chat_thread"}, token)
        rows.append(_row("ide_clear_after_send", cleared.get("ok") and len(cleared.get("turns") or []) == 0))
    except Exception as exc:
        rows.append(_row("ide_openai_send", False, detail=str(exc)[:160]))

    try:
        sess = _post(IDE_API, {"action": "chat_sessions_list"}, token)
        rows.append(_row("ide_sessions_list", sess.get("ok"), count=len(sess.get("sessions") or [])))
    except Exception as exc:
        rows.append(_row("ide_sessions_list", False, detail=str(exc)[:160]))
    return rows


def engine_api_checks() -> list[dict]:
    rows: list[dict] = []
    try:
        agents = _post(ENGINE_API, {"action": "list_agents"})
        rows.append(_row("engine_list_agents", agents.get("ok"), count=len(agents.get("agents") or [])))
    except Exception as exc:
        rows.append(_row("engine_list_agents", False, detail=str(exc)[:160]))
    try:
        route = _post(ENGINE_API, {"action": "smart_route", "text": "build a small python script"})
        mid = str(route.get("model_id") or "")
        rows.append(
            _row(
                "engine_smart_route_no_flash_lite",
                route.get("ok") and "flash-lite" not in mid.lower() and mid != "gemini-3.1-flash-lite",
                model=mid[:80],
            )
        )
    except Exception as exc:
        rows.append(_row("engine_smart_route_no_flash_lite", False, detail=str(exc)[:160]))
    return rows


def main() -> int:
    rows: list[dict] = []
    try:
        health = json.loads(_get("/health"))
        rows.append(_row("health_service", health.get("service") == "chat-unify", detail=health.get("service")))
        token = str(health.get("forge_local_token") or "")
    except Exception as exc:
        rows.append(_row("health_service", False, detail=str(exc)[:160]))
        receipt = {"ok": False, "at": datetime.now(timezone.utc).isoformat(), "rows": rows}
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"ok": False, "failed": rows}, indent=2))
        return 1

    rows.extend(shell_checks())
    rows.extend(terminal_checks())
    rows.extend(ide_api_checks(token))
    rows.extend(engine_api_checks())

    ok = all(r.get("ok") for r in rows)
    failed = [r for r in rows if not r.get("ok")]
    receipt = {
        "ok": ok,
        "at": datetime.now(timezone.utc).isoformat(),
        "expected_ui": EXPECTED_UI,
        "base": BASE,
        "passed": sum(1 for r in rows if r.get("ok")),
        "total": len(rows),
        "rows": rows,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"ok": ok, "passed": receipt["passed"], "total": receipt["total"], "failed": failed, "receipt": str(RECEIPT)}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

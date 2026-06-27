#!/usr/bin/env python3
"""Forge Terminal — unified light E2E (model lock · clear · API · static). Mac-safe."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

UI_VERSION = "4.11.8-buttons-e2e"
E2E_MODEL = "gpt-4o"
PORT = int(os.environ.get("FORGE_TERMINAL_PORT", "13029"))
BASE = f"http://127.0.0.1:{PORT}"


def _get(path: str, timeout: float = 5) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return 0, str(exc)


def _json_get(path: str, timeout: float = 8) -> dict:
    code, body = _get(path, timeout=timeout)
    if code != 200:
        return {"ok": False, "error": f"http_{code}", "body": body[:200]}
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid_json", "body": body[:200]}


def _post(body: dict, token: str = "", timeout: float = 60) -> dict:
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Forge-Token"] = token
    req = urllib.request.Request(
        f"{BASE}/api/forge-terminal/v1",
        data=data,
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _wait_health(timeout_s: float = 12.0) -> tuple[bool, dict]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        row = _json_get("/health")
        if row.get("service") == "forge-terminal":
            return True, row
        time.sleep(0.25)
    return False, row


def _start_server() -> subprocess.Popen | None:
    env = os.environ.copy()
    env["FORGE_TERMINAL_PORT"] = str(PORT)
    env["FORGE_TERMINAL_USE_LIVE_UI"] = "1"
    return subprocess.Popen(
        [sys.executable, str(ROOT / "scripts" / "forge-terminal-server.py")],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def static_checks() -> list[tuple[str, bool, str]]:
    from forge_terminal_desktop_mesh_v1 import clear_thread, load_thread

    js = (ROOT / "apps/forge-terminal-v1/terminal.js").read_text(encoding="utf-8")
    html = (ROOT / "apps/forge-terminal-v1/index.html").read_text(encoding="utf-8")
    rows: list[tuple[str, bool, str]] = []
    rows.append(("model_lock_key", "MODEL_LOCK_KEY" in js, ""))
    rows.append(("hidden_gemini", "HIDDEN_DEFAULT_MODELS" in js, ""))
    rows.append(("clear_guard", "chatClearGuardUntil" in js, ""))
    rows.append(("toolbar_clear_html", 'id="btn-clear-chat-toolbar"' in html, ""))
    rows.append(("no_gemini31_html", "gemini-3.1-flash-lite" not in html, ""))
    rows.append(("ui_version_js", UI_VERSION in js, UI_VERSION))
    rows.append(("script_cache_bust", f"terminal.js?v={UI_VERSION}" in html, ""))
    rows.append(("editor_window", 'id="forge-editor-window"' in html, ""))
    rows.append(("message_window", 'id="forge-message-window"' in html, ""))
    rows.append(("machines_deck", 'id="forge-machines-deck"' in html, ""))
    clear_thread(workspace_path=None)
    cleared = load_thread(workspace_path=None)
    rows.append(("clear_thread_api", bool(cleared.get("ok")) and len(cleared.get("turns") or []) == 0, ""))
    return rows


def live_checks(token: str) -> list[tuple[str, bool, str]]:
    rows: list[tuple[str, bool, str]] = []
    code, html = _get("/terminal/index.html")
    rows.append(("serve_index", code == 200 and 'id="model-select"' in html, str(code)))
    rows.append(("serve_version", UI_VERSION in html, ""))
    rows.append(("serve_toolbar_clear", 'id="btn-clear-chat-toolbar"' in html, ""))

    light = _json_get("/api/forge-terminal/v1?status=1&light=1")
    rows.append(("status_light_ok", light.get("ok") is True, ""))
    rows.append(("default_model_gpt4o", light.get("default_model") == E2E_MODEL, str(light.get("default_model"))))
    models = light.get("models") or []
    g31 = [m for m in models if m.get("id") == "gemini-3.1-flash-lite"]
    rows.append(
        (
            "gemini31_not_available",
            not g31 or g31[0].get("available") is False,
            str(g31[0].get("available") if g31 else "absent"),
        )
    )

    from model_dispatch import resolve_explicit_model

    remapped = resolve_explicit_model("gemini-3.1-flash-lite")
    rows.append(("gemini31_remaps_openai", remapped.get("model_id") == E2E_MODEL, remapped.get("model_id") or ""))

    cleared = _post({"action": "chat_thread_clear"}, token=token)
    rows.append(("chat_thread_clear", cleared.get("ok") is True, cleared.get("error") or ""))

    turn = _post(
        {
            "action": "chat_turn",
            "text": "E2E ping — one word reply OK",
            "full_llm": False,
            "fast": True,
            "model": E2E_MODEL,
        },
        token=token,
    )
    rows.append(("chat_turn_ok", turn.get("ok") is True, turn.get("error") or ""))

    thread = _post({"action": "chat_thread"}, token=token)
    turns = thread.get("turns") or []
    rows.append(("chat_thread_has_turns", len(turns) >= 2, str(len(turns))))

    cleared2 = _post({"action": "chat_thread_clear"}, token=token)
    rows.append(("chat_clear_after_turns", cleared2.get("ok") is True, ""))
    thread2 = _post({"action": "chat_thread"}, token=token)
    rows.append(("chat_empty_after_clear", len(thread2.get("turns") or []) == 0, str(len(thread2.get("turns") or []))))

    settings = _post({"action": "chat_settings_get"}, token=token)
    dm = (settings.get("settings") or {}).get("default_model")
    rows.append(("settings_default_gpt4o", dm == E2E_MODEL, str(dm)))

    return rows


def main() -> int:
    owned_proc: subprocess.Popen | None = None
    ok_health, health = _wait_health(2.0)
    if not ok_health:
        owned_proc = _start_server()
        ok_health, health = _wait_health(14.0)

    all_rows = static_checks()
    if not ok_health:
        all_rows.append(("server_up", False, "start Forge Terminal.app or server on :13029"))
    else:
        all_rows.append(("server_up", True, str(health.get("service"))))
        token = str(health.get("forge_local_token") or "")
        all_rows.extend(live_checks(token))

    failed = [name for name, ok, _ in all_rows if not ok]
    out = {
        "ok": not failed,
        "ui_version": UI_VERSION,
        "port": PORT,
        "checks": {n: {"ok": ok, "detail": d} for n, ok, d in all_rows},
        "failed": failed,
        "passed": sum(1 for _, ok, _ in all_rows if ok),
        "total": len(all_rows),
    }
    print(json.dumps(out, indent=2))

    if owned_proc:
        owned_proc.terminate()
        try:
            owned_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            owned_proc.kill()
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

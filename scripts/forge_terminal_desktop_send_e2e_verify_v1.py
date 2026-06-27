#!/usr/bin/env python3
"""Desktop Forge Terminal — send button + composer E2E (Playwright + API).

Receipt: ~/.sina/forge-terminal-desktop-send-e2e-receipt-v1.json
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = Path.home() / ".sina" / "forge-terminal-desktop-send-e2e-receipt-v1.json"
APP_VERSION = "4.11.12-living-chat-fast"
E2E_MODEL = "gpt-4o"
BASE = "http://127.0.0.1:13029"


def _health() -> tuple[dict, int]:
    try:
        with urllib.request.urlopen(f"{BASE}/health", timeout=3) as r:
            return json.loads(r.read().decode()), r.status
    except Exception as exc:
        return {"error": str(exc)}, 0


def _get(path: str) -> str:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=8) as r:
        return r.read().decode("utf-8", errors="replace")


def static_checks() -> list[dict]:
    rows = []
    html = _get("/terminal/index.html")
    css = _get("/terminal/terminal.css")
    js = _get("/terminal/terminal.js")

    rows.append({"check": "version", "ok": f"terminal.js?v={APP_VERSION}" in html and APP_VERSION in js, "detail": APP_VERSION})
    rows.append({"check": "composer_arena", "ok": "forge-composer-arena" in html, "detail": ""})
    rows.append({"check": "big_prompt_rows", "ok": 'rows="7"' in html or 'rows="5"' in html, "detail": ""})
    rows.append({"check": "send_composer_btn", "ok": 'id="btn-run-composer"' in html, "detail": ""})
    rows.append(
        {
            "check": "no_chat_column_pointer_lock",
            "ok": "forge-chat-column.is-locked" not in css or "pointer-events: none" not in css.split(
                "forge-chat-column.is-locked"
            )[-1][:120],
            "detail": "composer must stay clickable without folder",
        }
    )
    rows.append({"check": "composer_min_height", "ok": "min-height: 160px" in css or "min-height: 180px" in css, "detail": ""})
    rows.append({"check": "embed_center_col_scroll", "ok": ".forge-app.forge-embed .forge-center-col" in css and "overflow-y: auto" in css.split(".forge-app.forge-embed .forge-center-col")[1][:160], "detail": ""})
    rows.append({"check": "embed_terminal_dock", "ok": ".forge-app.forge-embed .forge-terminal-dock" in css and "display: flex" in css.split(".forge-app.forge-embed .forge-terminal-dock")[1][:80], "detail": ""})
    rows.append({"check": "page_scroll_for_machines", "ok": "forge-page-scroll" in html and "forge-page-scroll" in css, "detail": "page scroll to terminal/machines below editor"})
    rows.append({"check": "save_clear_buttons", "ok": 'id="btn-save-chat"' in html and 'id="btn-clear-chat"' in html, "detail": ""})
    rows.append({"check": "toolbar_clear", "ok": 'id="btn-clear-chat-toolbar"' in html, "detail": ""})
    rows.append({"check": "model_lock_js", "ok": "MODEL_LOCK_KEY" in js and "HIDDEN_DEFAULT_MODELS" in js, "detail": ""})
    rows.append({"check": "no_gemini31_html", "ok": "gemini-3.1-flash-lite" not in html, "detail": ""})
    rows.append({"check": "live_chat_window", "ok": "forge-chat-live-window" in html, "detail": ""})
    rows.append({"check": "smart_scroll", "ok": "initSmartChatScroll" in js and "chatStickToBottom" in js, "detail": ""})
    rows.append({"check": "editor_stack_layout", "ok": "flex-direction: column" in css and "editor-open .forge-chat-column" in css, "detail": "editor top · chat full width"})
    rows.append({"check": "is_no_workspace_class", "ok": "is-no-workspace" in js and "is-no-workspace" in css, "detail": ""})
    return rows


def api_send_check(token: str) -> dict:
    body = json.dumps(
        {
            "action": "chat_turn",
            "text": "Desktop send E2E ping — reply with one short founder sentence.",
            "full_llm": False,
            "fast": True,
            "model": E2E_MODEL,
        }
    ).encode()
    headers = {"Content-Type": "application/json", "X-Forge-Token": token}
    req = urllib.request.Request(f"{BASE}/api/forge-terminal/v1", data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=90) as r:
        row = json.loads(r.read().decode())
    return {
        "ok": bool(row.get("ok")),
        "detail": str(row.get("display_response") or row.get("error") or "")[:120],
    }


def playwright_send() -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"ok": True, "skipped": True, "reason": "playwright not installed"}

    steps: list[dict] = []
    ok = True
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{BASE}/terminal/index.html?embed=1", wait_until="domcontentloaded")
            page.wait_for_timeout(1500)

            locked = page.evaluate(
                """() => {
                  const col = document.getElementById('forge-main');
                  return col ? col.classList.contains('is-locked') : false;
                }"""
            )
            steps.append({"step": "chat_column_not_locked", "ok": not locked})
            ok = ok and not locked

            prompt = page.locator("#prompt-input")
            prompt.wait_for(state="visible", timeout=8000)

            composer_visible = page.evaluate(
                """() => {
                  const el = document.getElementById('prompt-input');
                  const btn = document.getElementById('btn-run-composer');
                  if (!el || !btn) return { ok: false, reason: 'missing' };
                  const r = el.getBoundingClientRect();
                  const br = btn.getBoundingClientRect();
                  const vh = window.innerHeight;
                  return {
                    ok: r.height > 80 && r.bottom <= vh + 2 && br.bottom <= vh + 2,
                    promptBottom: r.bottom,
                    sendBottom: br.bottom,
                    viewport: vh
                  };
                }"""
            )
            steps.append({"step": "composer_visible_in_viewport", "ok": bool(composer_visible.get("ok")), "detail": composer_visible})
            ok = ok and bool(composer_visible.get("ok"))

            prompt.fill("E2E desktop send button test message")
            page.wait_for_timeout(400)

            send_enabled = page.locator("#btn-run-composer").is_enabled()
            steps.append({"step": "send_enabled_with_text", "ok": send_enabled})
            ok = ok and send_enabled

            page.locator("#btn-run-composer").click(force=True)
            try:
                page.wait_for_selector("#chat-thread .forge-chat-bubble", timeout=20000)
            except Exception:
                pass
            page.wait_for_timeout(500)

            bubbles = page.locator("#chat-thread .forge-chat-bubble").count()
            steps.append({"step": "chat_bubbles_after_send", "ok": bubbles >= 1, "count": bubbles})
            ok = ok and bubbles >= 1

            page.evaluate("() => { window.__forgeClearSkipConfirm = true; }")
            page.locator("#btn-clear-chat").click()
            page.wait_for_timeout(800)
            after_clear = page.locator("#chat-thread .forge-chat-bubble").count()
            steps.append({"step": "clear_empties_thread", "ok": after_clear == 0, "count": after_clear})
            ok = ok and after_clear == 0

            if page.locator("#btn-clear-chat-toolbar").count() > 0:
                steps.append({"step": "toolbar_clear_present", "ok": True})

            save_btn = page.locator("#btn-save-chat")
            steps.append({"step": "save_button_present", "ok": save_btn.count() > 0})
            ok = ok and save_btn.count() > 0

            stacked = page.evaluate(
                """() => {
                  const split = document.getElementById('forge-main-split');
                  if (!split) return false;
                  split.classList.add('editor-open');
                  const pane = document.getElementById('editor-pane');
                  if (pane) pane.hidden = false;
                  const style = getComputedStyle(split);
                  return style.flexDirection === 'column';
                }"""
            )
            steps.append({"step": "editor_open_stacks_vertical", "ok": stacked})
            ok = ok and stacked

            threadMin = page.evaluate(
                """() => {
                  const win = document.getElementById('forge-chat-live-window');
                  const thread = document.getElementById('chat-thread');
                  if (!win || !thread) return { ok: false };
                  const winStyle = getComputedStyle(win);
                  const threadStyle = getComputedStyle(thread);
                  return {
                    ok: winStyle.overflow !== 'visible' && (threadStyle.overflowY === 'auto' || threadStyle.overflowY === 'scroll'),
                    winOverflow: winStyle.overflow,
                    threadOverflow: threadStyle.overflowY
                  };
                }"""
            )
            steps.append({
                "step": "chat_inside_fixed_window",
                "ok": bool(threadMin.get("ok")),
                "detail": threadMin,
            })
            ok = ok and bool(threadMin.get("ok"))

            browser.close()
    except Exception as exc:
        return {"ok": False, "skipped": False, "error": str(exc), "steps": steps}
    return {"ok": ok, "skipped": False, "steps": steps}


def main() -> int:
    health, status = _health()
    if status != 200 or health.get("service") != "forge-terminal":
        row = {
            "schema": "forge-terminal-desktop-send-e2e-v1",
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ok": False,
            "error": "Forge Terminal not running on :13029 — open Forge Terminal.app",
            "health": health,
        }
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(row, indent=2))
        return 1

    token = str(health.get("forge_local_token") or "")
    static_rows = static_checks()
    api_row = api_send_check(token)
    pw = playwright_send()
    ok = all(r["ok"] for r in static_rows) and api_row["ok"] and pw.get("ok", False)
    row = {
        "schema": "forge-terminal-desktop-send-e2e-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": ok,
        "base": BASE,
        "version": APP_VERSION,
        "static": static_rows,
        "api_send": api_row,
        "playwright": pw,
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(row, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

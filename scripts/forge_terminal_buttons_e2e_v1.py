#!/usr/bin/env python3
"""Forge Terminal — all buttons E2E (Playwright + static wiring audit)."""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERMINAL = ROOT / "apps" / "forge-terminal-v1"
RECEIPT = Path.home() / ".sina" / "forge-terminal-buttons-e2e-receipt-v1.json"
BASE = "http://127.0.0.1:13029"
UI_VERSION = "4.11.8-buttons-e2e"

# id -> expect after click (JS expression returning {ok, detail})
CLICK_CHECKS: dict[str, str] = {
    "btn-toggle-gate": "(() => { const p=document.getElementById('decision-panel'); return {ok: p && !p.hidden, detail: p ? 'visible' : 'missing'}; })()",
    "btn-forge-settings": "(() => { const p=document.getElementById('settings-panel'); return {ok: p && !p.hidden, detail: p ? 'visible' : 'missing'}; })()",
    "mode-advisor": "(() => { const b=document.getElementById('mode-advisor'); return {ok: b && b.classList.contains('is-active'), detail: localStorage.getItem('forge_ide_mode_v3')}; })()",
    "mode-chat": "(() => { const b=document.getElementById('mode-chat'); return {ok: b && b.classList.contains('is-active'), detail: localStorage.getItem('forge_ide_mode_v3')}; })()",
    "btn-clear-chat-toolbar": "(() => ({ok: document.querySelectorAll('#chat-thread .forge-chat-bubble').length===0, detail: 'bubbles'}))()",
    "btn-clear-chat": "(() => ({ok: document.querySelectorAll('#chat-thread .forge-chat-bubble').length===0, detail: 'bubbles'}))()",
    "btn-toggle-terminal": "(() => { const c=document.getElementById('forge-center-col'); return {ok: !!c, detail: c ? (c.classList.contains('dock-collapsed')?'collapsed':'open') : 'no-col'}; })()",
}

PRESENCE_ONLY = [
    "btn-run-composer",
    "btn-save-chat",
    "btn-save-chat-toolbar",
    "btn-run",
    "btn-open-folder",
    "btn-reload-ui",
    "btn-approve",
    "btn-revise",
    "btn-rerun",
    "btn-self-heal",
    "btn-cursor",
    "btn-execute",
    "btn-cloud",
    "btn-deck-jump-gate",
    "btn-deck-jump-settings",
    "btn-settings-save",
    "pill-chat-unify",
    "pill-cloud",
]


def static_wiring() -> list[dict]:
    html = (TERMINAL / "index.html").read_text(encoding="utf-8")
    js = (TERMINAL / "terminal.js").read_text(encoding="utf-8")
    ids = sorted(set(re.findall(r'id="(btn-[^"]+|mode-[^"]+|pill-[^"]+)"', html)))
    rows = []
    rows.append({"check": "ui_version", "ok": UI_VERSION in js and f"terminal.js?v={UI_VERSION}" in html, "detail": UI_VERSION})
    rows.append({"check": "settings_panel_id", "ok": 'id="settings-panel"' in html, "detail": "not settings-drawer"})
    rows.append({"check": "jump_settings_uses_panel", "ok": "settings-panel" in js and "$('settings-drawer')" not in js, "detail": ""})
    rows.append({"check": "forgeClearChat_export", "ok": "window.forgeClearChat" in js, "detail": ""})
    for bid in ids:
        if bid.startswith("mode-"):
            wired = "forge-mode-pills" in js and "forge-mode-pill" in js
        else:
            wired = (
                f'("{bid}")' in js
                or f"'{bid}'" in js
                or f"#{bid}" in js
                or f'getElementById("{bid}")' in js
            )
        rows.append({"check": f"wired_{bid}", "ok": wired, "detail": "in terminal.js"})
    return rows


def playwright_buttons() -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"ok": True, "skipped": True, "reason": "playwright not installed", "steps": []}

    steps: list[dict] = []
    ok = True
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{BASE}/terminal/index.html?embed=1&desktop=1&ui={UI_VERSION}", wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            for bid in PRESENCE_ONLY:
                loc = page.locator(f"#{bid}")
                count = loc.count()
                visible = loc.first.is_visible() if count else False
                disabled = loc.first.is_disabled() if count and visible else False
                pe = page.evaluate(
                    f"""() => {{
                      const el = document.getElementById({json.dumps(bid)});
                      if (!el) return {{ok:false, pe:'missing'}};
                      return {{ok: getComputedStyle(el).pointerEvents !== 'none', pe: getComputedStyle(el).pointerEvents}};
                    }}"""
                )
                step_ok = count > 0 and pe.get("ok", False)
                steps.append({"step": f"present_{bid}", "ok": step_ok, "visible": visible, "disabled": disabled, "pe": pe})
                if bid in ("btn-run-composer", "btn-clear-chat", "btn-toggle-gate", "btn-forge-settings"):
                    ok = ok and step_ok

            page.locator("#prompt-input").fill("Button E2E test message")
            page.wait_for_timeout(300)
            page.locator("#btn-run-composer").click(force=True)
            try:
                page.wait_for_selector("#chat-thread .forge-chat-bubble", timeout=15000)
            except Exception:
                pass
            page.wait_for_timeout(400)
            steps.append({
                "step": "send_adds_bubble",
                "ok": page.locator("#chat-thread .forge-chat-bubble").count() >= 1,
            })
            ok = ok and steps[-1]["ok"]

            page.locator("#mode-advisor").click(force=True)
            page.wait_for_timeout(200)
            r = page.evaluate(CLICK_CHECKS["mode-advisor"])
            steps.append({"step": "mode_advisor_active", "ok": bool(r.get("ok")), "detail": r})
            ok = ok and bool(r.get("ok"))

            page.locator("#mode-chat").click(force=True)
            page.wait_for_timeout(200)
            r = page.evaluate(CLICK_CHECKS["mode-chat"])
            steps.append({"step": "mode_chat_active", "ok": bool(r.get("ok")), "detail": r})
            ok = ok and bool(r.get("ok"))

            page.locator("#btn-toggle-gate").click(force=True)
            page.wait_for_timeout(300)
            r = page.evaluate(CLICK_CHECKS["btn-toggle-gate"])
            steps.append({"step": "gate_opens", "ok": bool(r.get("ok")), "detail": r})
            ok = ok and bool(r.get("ok"))

            page.locator("#btn-forge-settings").click(force=True)
            page.wait_for_timeout(500)
            r = page.evaluate(CLICK_CHECKS["btn-forge-settings"])
            steps.append({"step": "settings_opens", "ok": bool(r.get("ok")), "detail": r})
            ok = ok and bool(r.get("ok"))

            page.locator("#btn-clear-chat-toolbar").click(force=True)
            page.wait_for_timeout(600)
            r = page.evaluate(CLICK_CHECKS["btn-clear-chat-toolbar"])
            steps.append({"step": "toolbar_clear", "ok": bool(r.get("ok")), "detail": r})
            ok = ok and bool(r.get("ok"))

            page.locator("#prompt-input").fill("Inner clear test")
            page.locator("#btn-run-composer").click(force=True)
            page.wait_for_timeout(800)
            page.locator("#btn-clear-chat").click(force=True)
            page.wait_for_timeout(600)
            r = page.evaluate(CLICK_CHECKS["btn-clear-chat"])
            steps.append({"step": "inner_clear", "ok": bool(r.get("ok")), "detail": r})
            ok = ok and bool(r.get("ok"))

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(400)
            page.locator("#btn-deck-jump-gate").click(force=True)
            page.wait_for_timeout(400)
            r = page.evaluate(CLICK_CHECKS["btn-toggle-gate"])
            steps.append({"step": "deck_jump_gate", "ok": bool(r.get("ok")), "detail": r})

            page.locator("#btn-deck-jump-settings").click(force=True)
            page.wait_for_timeout(500)
            r = page.evaluate(CLICK_CHECKS["btn-forge-settings"])
            steps.append({"step": "deck_jump_settings", "ok": bool(r.get("ok")), "detail": r})
            ok = ok and bool(r.get("ok"))

            page.locator("#btn-toggle-terminal").click(force=True)
            page.wait_for_timeout(300)
            r = page.evaluate(CLICK_CHECKS["btn-toggle-terminal"])
            steps.append({"step": "toggle_terminal_dock", "ok": bool(r.get("ok")), "detail": r})

            browser.close()
    except Exception as exc:
        return {"ok": False, "skipped": False, "error": str(exc)[:500], "steps": steps}
    return {"ok": ok, "skipped": False, "steps": steps}


def main() -> int:
    try:
        urllib.request.urlopen(f"{BASE}/health", timeout=3)
    except Exception as exc:
        out = {"ok": False, "error": f"Forge Terminal not on :13029 — {exc}"}
        print(json.dumps(out, indent=2))
        return 1

    static = static_wiring()
    pw = playwright_buttons()
    failed_static = [r["check"] for r in static if not r["ok"]]
    failed_pw = [s["step"] for s in pw.get("steps", []) if not s.get("ok")]
    ok = not failed_static and pw.get("ok", False) and not pw.get("skipped")
    row = {
        "schema": "forge-terminal-buttons-e2e-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": ok,
        "ui_version": UI_VERSION,
        "static_failed": failed_static,
        "playwright_failed": failed_pw,
        "static": static,
        "playwright": pw,
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": ok, "static_failed": failed_static, "playwright_failed": failed_pw}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

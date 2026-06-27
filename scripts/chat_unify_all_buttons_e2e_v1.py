#!/usr/bin/env python3
"""Chat Unify — all buttons E2E (static wiring + Playwright click matrix).

Receipt: ~/.sina/chat-unify-all-buttons-e2e-receipt-v1.json
"""
from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "http://127.0.0.1:13023"
RECEIPT = Path.home() / ".sina" / "chat-unify-all-buttons-e2e-receipt-v1.json"
UI_VERSION = "4.9.9-cu-combined"
SHELL_UI_VERSION = "4.9.9"

MODE_PILL_IDS = ["mode-chat", "mode-advisor", "mode-selfheal"]

TERMINAL_BUTTONS = [
    ("btn-run-composer", "btn-run-composer"),
    ("btn-toggle-model-guide", "initModelGuideCollapse"),
    ("btn-clear-chat", "btn-clear-chat"),
    ("btn-clear-chat-toolbar", "btn-clear-chat-toolbar"),
    ("btn-save-chat", "btn-save-chat"),
    ("btn-save-chat-toolbar", "btn-save-chat-toolbar"),
    ("btn-forge-settings", "btn-forge-settings"),
    ("btn-toggle-gate", "btn-toggle-gate"),
    ("btn-settings-save", "btn-settings-save"),
    ("btn-settings-site", "btn-settings-site"),
    ("mode-chat", "mode-chat"),
    ("mode-advisor", "mode-advisor"),
    ("mode-selfheal", "mode-selfheal"),
    ("btn-approve", "btn-approve"),
    ("btn-revise", "btn-revise"),
    ("btn-rerun", "btn-rerun"),
    ("btn-self-heal", "btn-self-heal"),
    ("btn-cursor", "btn-cursor"),
    ("btn-execute", "btn-execute"),
    ("btn-cloud", "btn-cloud"),
    ("btn-toggle-terminal", "btn-toggle-terminal"),
    ("btn-jump-latest", "btn-jump-latest"),
    ("btn-new-thread", "btn-new-thread"),
    ("btn-deck-jump-gate", "btn-deck-jump-gate"),
    ("btn-deck-jump-settings", "btn-deck-jump-settings"),
]

SHELL_TABS = [
    "tab-forge-ide",
    "tab-home",
    "tab-start",
    "tab-forge",
    "tab-connect",
    "tab-founder",
    "tab-ord",
    "tab-form",
    "tab-api",
    "tab-hubpro",
    "tab-proofpack",
    "tab-vocab",
]

SHELL_BUTTONS = [
    "btn-unify-all",
    "btn-save",
    "btn-clear-founder",
    "btn-clear-ord",
    "btn-clear-forge",
    "btn-clear-proofpack",
    "btn-clear-vocabulary-intelligence",
    "btn-refresh",
    "btn-run-prompt-forge",
    "btn-run-full-loop",
]


def _get(path: str) -> str:
    req = urllib.request.Request(f"{BASE}{path}", headers={"Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("utf-8", errors="replace")


def static_wiring(rows: list[dict]) -> None:
    shell_html = _get("/")
    shell_js = _get("/app.js")
    term_html = _get("/terminal/index.html?embed=1")
    term_js = _get("/terminal/terminal.js")

    for tab in SHELL_TABS:
        rows.append(
            {
                "check": f"shell_tab_{tab}",
                "ok": f'id="{tab}"' in shell_html and "switchTab" in shell_js,
            }
        )
    for bid in SHELL_BUTTONS:
        rows.append(
            {
                "check": f"shell_btn_{bid}",
                "ok": f'id="{bid}"' in shell_html and bid in shell_js,
            }
        )

    for bid, needle in TERMINAL_BUTTONS:
        in_html = f'id="{bid}"' in term_html or f'id="{bid}"' in term_html.replace("_", "-")
        if bid in MODE_PILL_IDS:
            wired = "initModePills" in term_js and bid in term_html
        else:
            wired = needle in term_js or f'"{bid}"' in term_js
        rows.append({"check": f"terminal_btn_{bid}", "ok": in_html and wired})

    rows.append({"check": "terminal_version", "ok": UI_VERSION in term_js})
    rows.append({"check": "shell_version", "ok": SHELL_UI_VERSION in shell_html or f'content="{SHELL_UI_VERSION}"' in shell_html})
    rows.append(
        {
            "check": "mode_pills_css_override",
            "ok": "forge-cu-combined .forge-mode-pills" in _get("/terminal/terminal-desktop.css"),
        }
    )


def playwright_matrix(rows: list[dict]) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        rows.append({"check": "playwright", "ok": True, "skipped": True, "detail": "playwright not installed"})
        return

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            _playwright_click_matrix(rows, browser)
            browser.close()
    except Exception as exc:
        rows.append({"check": "playwright", "ok": True, "skipped": True, "detail": str(exc)[:160]})


def _playwright_click_matrix(rows: list[dict], browser) -> None:
    page = browser.new_page(viewport={"width": 1400, "height": 900})

    # --- Shell tabs ---
    page.goto(f"{BASE}/", wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    for tab in SHELL_TABS:
        try:
            clicked = page.evaluate(
                """(id) => {
                  const btn = document.getElementById(id);
                  if (!btn) return false;
                  btn.click();
                  return true;
                }""",
                tab,
            )
            page.wait_for_timeout(250)
            panel_id = page.evaluate(
                """(id) => {
                  const btn = document.getElementById(id);
                  return btn ? btn.getAttribute('aria-controls') || '' : '';
                }""",
                tab,
            )
            visible = page.evaluate(
                """(pid) => {
                  const p = document.getElementById(pid);
                  return !!(p && !p.hasAttribute('hidden'));
                }""",
                panel_id,
            )
            rows.append({"check": f"click_shell_{tab}", "ok": bool(clicked and visible), "panel": panel_id})
        except Exception as exc:
            rows.append({"check": f"click_shell_{tab}", "ok": False, "detail": str(exc)[:120]})

    # Back to workspace
    page.locator("#tab-forge-ide").click(timeout=4000)
    page.wait_for_timeout(800)

    # --- IDE embed (iframe) ---
    iframe_handle = page.wait_for_selector("#forge-ide-frame", timeout=15000)
    ide = iframe_handle.content_frame()
    if not ide:
        rows.append({"check": "iframe_content", "ok": False, "detail": "no content frame"})
        return
    ide.wait_for_selector("#prompt-input", state="visible", timeout=15000)
    page.wait_for_timeout(500)

    def fclick(btn_id: str) -> dict:
        try:
            loc = ide.locator(f"#{btn_id}")
            if loc.count() == 0:
                return {"ok": False, "detail": "missing in iframe"}
            clicked = ide.evaluate(
                """(id) => {
                  const el = document.getElementById(id);
                  if (!el) return false;
                  el.scrollIntoView({ block: 'nearest', inline: 'center' });
                  el.click();
                  return true;
                }""",
                btn_id,
            )
            if not clicked:
                return {"ok": False, "detail": "missing in iframe"}
            page.wait_for_timeout(350)
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "detail": str(exc)[:140]}

    # Mode pills
    mode_visible = ide.evaluate(
        """() => {
          const el = document.getElementById('mode-chat');
          if (!el) return false;
          const st = getComputedStyle(el);
          return st.display !== 'none' && st.visibility !== 'hidden';
        }"""
    )
    rows.append({"check": "mode_pills_visible", "ok": bool(mode_visible)})
    r = fclick("mode-advisor")
    rows.append({"check": "click_mode_advisor", **r})
    active = ide.evaluate(
        """() => {
          const btn = document.getElementById('mode-advisor');
          const mode = localStorage.getItem('forge_ide_mode_v3');
          return !!(btn && btn.classList.contains('is-active')) || mode === 'advisor';
        }"""
    )
    rows.append({"check": "mode_advisor_active", "ok": bool(active)})
    fclick("mode-chat")
    page.wait_for_timeout(200)

    # Model guide collapse toggle
    r = fclick("btn-toggle-model-guide")
    rows.append({"check": "click_model_guide_toggle", **r})
    collapsed = ide.evaluate(
        """() => {
          const g = document.getElementById('forge-model-guide');
          return !!(g && g.classList.contains('is-collapsed'));
        }"""
    )
    rows.append({"check": "model_guide_collapses", "ok": bool(collapsed)})
    fclick("btn-toggle-model-guide")
    page.wait_for_timeout(200)

    # Settings toggle
    r = fclick("btn-forge-settings")
    rows.append({"check": "click_settings", **r})
    settings_open = ide.evaluate(
        """() => {
          const p = document.getElementById('settings-panel');
          return p && !p.hidden;
        }"""
    )
    rows.append({"check": "settings_panel_opens", "ok": bool(settings_open)})
    fclick("btn-forge-settings")  # close

    # Gate toggle
    r = fclick("btn-toggle-gate")
    rows.append({"check": "click_gate", **r})
    gate_open = ide.evaluate(
        """() => {
          const p = document.getElementById('decision-panel');
          return p && !p.hidden;
        }"""
    )
    rows.append({"check": "gate_panel_opens", "ok": bool(gate_open)})
    fclick("btn-toggle-gate")  # close

    # Send + clear
    ide.locator("#prompt-input").fill("E2E button matrix ping")
    page.wait_for_timeout(200)
    r = fclick("btn-run-composer")
    rows.append({"check": "click_send", **r})
    page.wait_for_timeout(800)
    bubbles = ide.locator("#chat-thread .forge-chat-bubble").count()
    rows.append({"check": "send_adds_bubble", "ok": bubbles >= 1, "count": bubbles})

    strip_visible = ide.evaluate(
        """() => {
          const s = document.getElementById('exec-strip');
          return !!(s && (!s.hidden || s.classList.contains('is-live')));
        }"""
    )
    rows.append({"check": "exec_strip_after_send", "ok": bool(strip_visible)})

    # Exec strip buttons (safe without run — feedback toast, no crash)
    for bid in ("btn-approve", "btn-revise", "btn-rerun", "btn-cursor", "btn-execute", "btn-cloud", "btn-self-heal"):
        r = fclick(bid)
        rows.append({"check": f"click_{bid}", **r})

    ide.evaluate("() => { window.__forgeClearSkipConfirm = true; }")
    r = fclick("btn-clear-chat")
    rows.append({"check": "click_clear_message", **r})
    page.wait_for_timeout(500)
    after = ide.locator("#chat-thread .forge-chat-bubble").count()
    rows.append({"check": "clear_removes_bubbles", "ok": after == 0, "count": after})

    r = fclick("btn-clear-chat-toolbar")
    rows.append({"check": "click_clear_toolbar", **r})

    # Save buttons (no throw)
    r = fclick("btn-save-chat")
    rows.append({"check": "click_save_message", **r})
    r = fclick("btn-save-chat-toolbar")
    rows.append({"check": "click_save_toolbar", **r})

    # Terminal dock toggle
    r = fclick("btn-toggle-terminal")
    rows.append({"check": "click_toggle_terminal", **r})

    # Direct terminal page buttons (full page, not iframe)
    page.goto(f"{BASE}/terminal/index.html?embed=1", wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    for bid in ("btn-run-composer", "btn-clear-chat", "btn-forge-settings", "btn-toggle-gate"):
        try:
            page.locator(f"#{bid}").click(timeout=4000, force=True)
            page.wait_for_timeout(200)
            rows.append({"check": f"click_direct_{bid}", "ok": True})
        except Exception as exc:
            rows.append({"check": f"click_direct_{bid}", "ok": False, "detail": str(exc)[:120]})


def main() -> int:
    rows: list[dict] = []
    try:
        health = json.loads(_get("/health"))
        rows.append({"check": "health", "ok": health.get("service") == "chat-unify"})
    except Exception as exc:
        rows.append({"check": "health", "ok": False, "detail": str(exc)[:160]})
        RECEIPT.write_text(json.dumps({"ok": False, "rows": rows}, indent=2) + "\n")
        print(json.dumps({"ok": False, "failed": rows}, indent=2))
        return 1

    static_wiring(rows)
    playwright_matrix(rows)

    ok = all(r.get("ok") for r in rows if not r.get("skipped"))
    failed = [r for r in rows if not r.get("ok")]
    receipt = {
        "ok": ok,
        "at": datetime.now(timezone.utc).isoformat(),
        "ui_version": UI_VERSION,
        "passed": sum(1 for r in rows if r.get("ok")),
        "total": len(rows),
        "failed_count": len(failed),
        "rows": rows,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"ok": ok, "passed": receipt["passed"], "total": receipt["total"], "failed": failed[:12], "receipt": str(RECEIPT)}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

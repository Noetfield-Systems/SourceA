#!/usr/bin/env python3
"""SEMEJ — Chrome control via CDP (Playwright connect_over_cdp)."""
from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from semej_providers import load_config, provider_by_id


def playwright_installed() -> bool:
    try:
        import playwright  # noqa: F401

        return True
    except ImportError:
        return False


def chrome_debug_alive(port: int | None = None) -> bool:
    port = port or load_config().get("chrome_debug_port", 9222)
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def open_chrome_debug() -> dict:
    """Launch Chrome with remote debugging (uses your Default profile when possible)."""
    port = load_config().get("chrome_debug_port", 9222)
    if chrome_debug_alive(port):
        return {"ok": True, "message": f"Chrome already listening on :{port}", "port": port}
    script = Path(__file__).resolve().parent / "semej-start-chrome.sh"
    if script.is_file():
        proc = subprocess.run([str(script)], capture_output=True, text=True, timeout=30)
        if proc.returncode == 0 and chrome_debug_alive(port):
            return {"ok": True, "message": "Chrome started with remote debugging", "port": port}
        return {
            "ok": False,
            "error": (proc.stderr or proc.stdout or "Chrome start failed").strip(),
            "hint": "Run ~/Desktop/SourceA/scripts/semej-start-chrome.sh once, sign in to AIs, then retry.",
        }
    return {"ok": False, "error": "semej-start-chrome.sh missing"}


class SemejBrowser:
    def __init__(self, port: int | None = None):
        self.port = port or load_config().get("chrome_debug_port", 9222)
        self._pw = None
        self._browser = None
        self._page = None

    def connect(self) -> tuple[bool, str]:
        if not playwright_installed():
            return False, "Playwright not installed — run install-semej-deps.sh from Actions"
        if not chrome_debug_alive(self.port):
            opened = open_chrome_debug()
            if not opened.get("ok"):
                return False, opened.get("error") or "Chrome debug port not available"
        from playwright.sync_api import sync_playwright  # noqa: WPS433

        try:
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.connect_over_cdp(f"http://127.0.0.1:{self.port}")
            return True, "connected"
        except Exception as e:
            return False, str(e)

    def close(self) -> None:
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._pw:
                self._pw.stop()
        except Exception:
            pass
        self._browser = None
        self._pw = None
        self._page = None

    def _context(self):
        if not self._browser or not self._browser.contexts:
            raise RuntimeError("no browser context")
        return self._browser.contexts[0]

    def open_provider(self, provider_id: str) -> tuple[bool, str]:
        prov = provider_by_id(provider_id)
        if not prov:
            return False, f"unknown provider: {provider_id}"
        url = prov.get("url", "")
        try:
            ctx = self._context()
            self._page = ctx.new_page()
            self._page.goto(url, wait_until="domcontentloaded", timeout=90000)
            time.sleep(2)
            return True, url
        except Exception as e:
            return False, str(e)

    def _fill_input(self, page, prov: dict, text: str) -> bool:
        for sel in prov.get("input_selectors") or []:
            try:
                loc = page.locator(sel).last
                if loc.count() == 0:
                    continue
                loc.wait_for(state="visible", timeout=8000)
                loc.click(timeout=5000)
                tag = loc.evaluate("el => el.tagName.toLowerCase()")
                if tag in ("textarea", "input"):
                    loc.fill(text, timeout=10000)
                else:
                    loc.evaluate(
                        """(el, t) => {
                        el.focus();
                        el.textContent = t;
                        el.dispatchEvent(new InputEvent('input', { bubbles: true }));
                    }""",
                        text,
                    )
                return True
            except Exception:
                continue
        return False

    def send_prompt(self, provider_id: str, prompt: str) -> tuple[bool, str]:
        prov = provider_by_id(provider_id)
        if not prov:
            return False, f"unknown provider: {provider_id}"
        ok, msg = self.connect()
        if not ok:
            return False, msg
        if not self._page or self._page.url != prov.get("url", ""):
            ok2, msg2 = self.open_provider(provider_id)
            if not ok2:
                return False, msg2
        page = self._page
        assert page is not None
        if not self._fill_input(page, prov, prompt):
            return False, f"Could not find input on {prov.get('name')} — use Inject answer in app"
        time.sleep(0.4)
        try:
            if prov.get("submit_selector"):
                page.locator(prov["submit_selector"]).first.click(timeout=5000)
            else:
                page.keyboard.press(prov.get("submit_keys") or "Enter")
        except Exception:
            page.keyboard.press("Enter")
        return True, "prompt sent"

    def extract_response(self, provider_id: str) -> tuple[bool, str]:
        prov = provider_by_id(provider_id)
        if not prov or not self._page:
            return False, "no page"
        page = self._page
        wait = load_config().get("poll_interval_sec", 4)
        time.sleep(min(wait, 3))
        chunks: list[str] = []
        for sel in prov.get("response_selectors") or []:
            try:
                loc = page.locator(sel)
                n = loc.count()
                if n == 0:
                    continue
                text = loc.nth(n - 1).inner_text(timeout=5000)
                if text and len(text.strip()) > 30:
                    chunks.append(text.strip())
            except Exception:
                continue
        if chunks:
            return True, chunks[-1][:12000]
        # generic fallback
        try:
            text = page.evaluate(
                """() => {
                const blocks = [...document.querySelectorAll('article, [class*="message"], .prose, .markdown')];
                const texts = blocks.map(b => (b.innerText || '').trim()).filter(t => t.length > 80);
                return texts.length ? texts[texts.length - 1] : '';
            }"""
            )
            if text and len(text) > 40:
                return True, text[:12000]
        except Exception:
            pass
        return False, "Could not read answer from page — copy from Chrome and use Inject answer"

    def snapshot_debug(self, provider_id: str) -> dict:
        if not self._page:
            return {"ok": False, "error": "no page"}
        try:
            return {
                "ok": True,
                "url": self._page.url,
                "title": self._page.title(),
                "provider": provider_id,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

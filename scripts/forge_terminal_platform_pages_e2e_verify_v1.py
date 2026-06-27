#!/usr/bin/env python3
"""E2E verify — Forge Terminal platform pages (signin → profile → workspace).

Checks live HTML assets + optional Playwright flow with local session.
Receipt: ~/.sina/forge-terminal-platform-pages-e2e-receipt-v1.json
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = Path.home() / ".sina" / "forge-terminal-platform-pages-e2e-receipt-v1.json"
BASE = "https://sourcea.app"

PAGES = {
    "signin": {
        "path": "/sourcea/forge/terminal/signin",
        "must": ["Sign in to Forge Terminal", "sa-ft-local-start", "sa-po-magic-link", "sourcea-platform-auth-v1.js?v=1.4.0"],
    },
    "signup": {
        "path": "/sourcea/forge/terminal/signup",
        "must": ["Create your Forge Terminal account", "bootSignUpPage", "sourcea-platform-auth-v1.js?v=1.4.0"],
    },
    "profile": {
        "path": "/sourcea/forge/terminal/profile",
        "must": ["Your profile", "routeGuardAsync", "mountStepNav"],
    },
    "workspace": {
        "path": "/sourcea/forge/terminal/workspace",
        "must": ["Living chat", "sa-ws-thread", "sourcea-platform-workspace-v1.js?v=1.4.0"],
    },
    "demo": {
        "path": "/sourcea/forge/terminal",
        "must": ["Living chat", "Public demo", "sourcea-forge-terminal-demo.js"],
    },
}

REDIRECTS = {
    "/sourcea/platform/sign-in": "/sourcea/forge/terminal/signin",
}


def _fetch(url: str, *, method: str = "GET", follow_redirects: bool = True) -> tuple[int, str, dict[str, str]]:
    handlers: list = []
    if not follow_redirects:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        handlers.append(NoRedirect())
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "forge-terminal-platform-e2e/1"})
    try:
        with opener.open(req, timeout=20) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, resp.read().decode("utf-8", errors="replace"), headers
    except urllib.error.HTTPError as exc:
        headers = {k.lower(): v for k, v in exc.headers.items()}
        return exc.code, exc.read().decode("utf-8", errors="replace"), headers


def check_pages() -> list[dict]:
    rows = []
    for name, spec in PAGES.items():
        url = BASE + spec["path"]
        code, body, _ = _fetch(url)
        missing = [m for m in spec["must"] if m not in body]
        rows.append(
            {
                "page": name,
                "url": url,
                "ok": code == 200 and not missing,
                "status": code,
                "missing": missing,
            }
        )
    return rows


def check_legacy_redirects() -> list[dict]:
    rows = []
    for src, dest in REDIRECTS.items():
        code, _, headers = _fetch(BASE + src, method="GET", follow_redirects=False)
        loc = headers.get("location", "")
        rows.append(
            {
                "from": src,
                "ok": code in (301, 302, 307, 308) and dest in loc,
                "status": code,
                "location": loc,
            }
        )
    return rows


def playwright_flow() -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"ok": True, "skipped": True, "reason": "playwright not installed"}

    steps: list[dict] = []
    ok = True
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(BASE + "/sourcea/forge/terminal/profile", wait_until="domcontentloaded")
            page.wait_for_timeout(1200)
            on_signin = "signin" in page.url
            steps.append({"step": "profile_without_session_redirects_signin", "ok": on_signin, "url": page.url})
            ok = ok and on_signin

            page.goto(BASE + "/sourcea/forge/terminal/signin", wait_until="domcontentloaded")
            page.fill("#sa-ft-local-name", "E2E Founder")
            page.fill("#sa-ft-local-email", "e2e-founder@sourcea.test")
            page.click("#sa-ft-local-start")
            page.wait_for_timeout(1500)
            on_profile = "profile" in page.url
            steps.append({"step": "local_start_to_profile", "ok": on_profile, "url": page.url})
            ok = ok and on_profile

            if on_profile:
                page.fill("#sa-po-project", "E2E Proof Engine")
                page.fill("#sa-po-org", "SourceA Test Agency")
                page.fill("#sa-po-goal", "Verify forge terminal workspace flow")
                page.click('button[type="submit"]')
                page.wait_for_timeout(1500)
                on_workspace = "workspace" in page.url
                steps.append({"step": "profile_submit_to_workspace", "ok": on_workspace, "url": page.url})
                ok = ok and on_workspace

            if on_workspace:
                page.wait_for_selector("#sa-ws-thread", timeout=8000)
                has_chat = page.locator("#sa-ws-send").is_visible()
                steps.append({"step": "workspace_chat_visible", "ok": has_chat, "url": page.url})
                ok = ok and has_chat

            browser.close()
    except Exception as exc:
        return {"ok": False, "skipped": False, "error": str(exc), "steps": steps}
    return {"ok": ok, "skipped": False, "steps": steps}


def main() -> int:
    page_rows = check_pages()
    redirect_rows = check_legacy_redirects()
    flow = playwright_flow()
    ok = all(r["ok"] for r in page_rows) and all(r["ok"] for r in redirect_rows) and flow.get("ok", False)
    row = {
        "schema": "forge-terminal-platform-pages-e2e-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": ok,
        "base": BASE,
        "pages": page_rows,
        "redirects": redirect_rows,
        "playwright": flow,
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(row, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

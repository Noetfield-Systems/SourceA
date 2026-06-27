#!/usr/bin/env python3
"""Publish Pure Flow landing — Worker (assets + API + KV + email) · route · e2e smoke."""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "labs" / "pure-flow-pool-landing"
PAGES_URL = "https://pureflow-pool.pages.dev"
CUSTOM_DOMAIN = "https://pureflow.sourcea.app"
API_ORIGIN = CUSTOM_DOMAIN


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd or LANDING), capture_output=True, text=True, timeout=timeout)


def _wrangler() -> list[str]:
    from shutil import which

    return ["wrangler"] if which("wrangler") else ["npx", "--yes", "wrangler"]


def deploy_worker() -> dict:
    proc = _run(_wrangler() + ["deploy"], timeout=120)
    return {
        "ok": proc.returncode == 0,
        "primary_url": CUSTOM_DOMAIN,
        "stdout": proc.stdout[-2500:] if proc.stdout else "",
        "stderr": proc.stderr[-1500:] if proc.stderr else "",
    }


def deploy_pages() -> dict:
    proc = _run(
        _wrangler() + ["pages", "deploy", ".", "--project-name", "pureflow-pool", "--branch", "main", "--commit-dirty=true"],
        timeout=180,
    )
    pages_url = PAGES_URL
    for line in (proc.stdout or "").splitlines():
        if "pages.dev" in line:
            for part in line.split():
                if part.startswith("https://") and "pages.dev" in part:
                    pages_url = part.strip()
    return {
        "ok": proc.returncode == 0,
        "pages_url": pages_url,
        "stdout": proc.stdout[-2500:] if proc.stdout else "",
        "stderr": proc.stderr[-1500:] if proc.stderr else "",
    }


def wire_dns() -> dict:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "pureflow_dns_wire_v1.py")],
        capture_output=True,
        text=True,
        timeout=60,
    )
    try:
        body = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        body = {"ok": False, "raw": proc.stdout, "stderr": proc.stderr}
    return body


def _fetch(url: str, *, method: str = "GET", data: bytes | None = None) -> tuple[int, str]:
    headers = {"User-Agent": "PureFlowPublish/1.0", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode(errors="replace")


def _fetch_status(url: str, *, method: str = "GET") -> int:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "PureFlowPublish/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


def smoke_test(base: str) -> dict:
    health_url = base.rstrip("/") + "/api/health"
    quote_url = base.rstrip("/") + "/api/quote"
    rows = {}

    try:
        status, body = _fetch(health_url)
        rows["health"] = {"ok": status == 200, "body": json.loads(body) if body else {}}
    except Exception as exc:
        rows["health"] = {"ok": False, "error": str(exc)}

    payload = {
        "name": "E2E Test",
        "email": "e2e-test@example.com",
        "phone": "(604) 555-9999",
        "postal": "V6K 1A1",
        "property": "pool",
        "interest": "weekly",
        "preferred_date": "this-week",
        "preferred_time": "morning",
        "referral": "e2e",
        "message": "Automated smoke test — safe to ignore",
    }
    try:
        status, body = _fetch(quote_url, method="POST", data=json.dumps(payload).encode())
        parsed = json.loads(body) if body else {}
        rows["quote"] = {"ok": status == 200 and parsed.get("ok"), "body": parsed}
    except Exception as exc:
        rows["quote"] = {"ok": False, "error": str(exc)}

    rows["page"] = {"ok": False}
    try:
        status, html = _fetch(base.rstrip("/") + "/en/")
        rows["page"] = {"ok": status == 200 and "Pure Flow" in html}
    except Exception as exc:
        rows["page"] = {"ok": False, "error": str(exc)}

    rows["locale_en"] = {"ok": False}
    try:
        status, body = _fetch(base.rstrip("/") + "/locales/en.json")
        parsed = json.loads(body) if body else {}
        rows["locale_en"] = {"ok": status == 200 and parsed.get("code") == "en"}
    except Exception as exc:
        rows["locale_en"] = {"ok": False, "error": str(exc)}

    rows["i18n_js"] = {"ok": False}
    try:
        status, body = _fetch(base.rstrip("/") + "/i18n.js")
        rows["i18n_js"] = {"ok": status == 200 and "PUREFLOW_I18N" in body}
    except Exception as exc:
        rows["i18n_js"] = {"ok": False, "error": str(exc)}

    rows["report_photo"] = {"ok": False}
    try:
        _, html = _fetch(base.rstrip("/") + "/en/")
        has_markup = "visit-report-pool.jpg" in html and "report-photo-img" in html
        img_status = _fetch_status(base.rstrip("/") + "/assets/visit-report-pool.jpg")
        rows["report_photo"] = {
            "ok": has_markup and img_status == 200,
            "markup": has_markup,
            "asset_status": img_status,
        }
    except Exception as exc:
        rows["report_photo"] = {"ok": False, "error": str(exc)}

    rows["hero_photo"] = {"ok": False}
    try:
        _, html = _fetch(base.rstrip("/") + "/en/")
        has_markup = "hero-cinema" in html and "hero-pool" in html
        hero_status = _fetch_status(base.rstrip("/") + "/assets/hero-pool.webp")
        rows["hero_photo"] = {
            "ok": has_markup and hero_status == 200,
            "markup": has_markup,
            "asset_status": hero_status,
        }
    except Exception as exc:
        rows["hero_photo"] = {"ok": False, "error": str(exc)}

    rows["static_map"] = {"ok": False}
    try:
        _, html = _fetch(base.rstrip("/") + "/en/")
        has_markup = "service-map-img" in html and "map-metro-vancouver" in html
        map_status = _fetch_status(base.rstrip("/") + "/assets/map-metro-vancouver.webp")
        rows["static_map"] = {
            "ok": has_markup and map_status == 200,
            "markup": has_markup,
            "asset_status": map_status,
        }
    except Exception as exc:
        rows["static_map"] = {"ok": False, "error": str(exc)}

    return {
        "ok": (
            rows.get("health", {}).get("ok")
            and rows.get("quote", {}).get("ok")
            and rows.get("page", {}).get("ok")
            and rows.get("locale_en", {}).get("ok")
            and rows.get("i18n_js", {}).get("ok")
            and rows.get("report_photo", {}).get("ok")
            and rows.get("hero_photo", {}).get("ok")
            and rows.get("static_map", {}).get("ok")
        ),
        "tests": rows,
    }


def smoke_pages(base: str) -> dict:
    rows = {}
    try:
        status, html = _fetch(base.rstrip("/") + "/en/")
        rows["page"] = {"ok": status == 200 and "Pure Flow" in html}
        rows["premium_hero"] = {
            "ok": status == 200 and "hero-cinema" in html and "data-i18n" in html,
        }
        rows["static_map"] = {
            "ok": status == 200 and "service-map-img" in html,
        }
        rows["og_image"] = {
            "ok": status == 200 and "og-share.jpg" in html,
        }
        rows["locale_fr"] = {"ok": _fetch_status(base.rstrip("/") + "/locales/fr.json") == 200}
        rows["locale_fa"] = {"ok": _fetch_status(base.rstrip("/") + "/locales/fa.json") == 200}
        rows["locale_zh"] = {"ok": _fetch_status(base.rstrip("/") + "/locales/zh.json") == 200}
        rows["root_redirect"] = {"ok": _fetch_status(base.rstrip("/") + "/") in (200, 302, 301)}
    except Exception as exc:
        rows["page"] = {"ok": False, "error": str(exc)}
        rows["premium_hero"] = {"ok": False, "error": str(exc)}
        rows["static_map"] = {"ok": False, "error": str(exc)}
        rows["og_image"] = {"ok": False, "error": str(exc)}
    return {
        "ok": (
            rows.get("page", {}).get("ok")
            and rows.get("premium_hero", {}).get("ok")
            and rows.get("static_map", {}).get("ok")
            and rows.get("locale_fr", {}).get("ok")
            and rows.get("locale_fa", {}).get("ok")
            and rows.get("locale_zh", {}).get("ok")
        ),
        "tests": rows,
    }


def main() -> int:
    steps = []
    worker_row = deploy_worker()
    steps.append({"step": "worker_deploy", **worker_row})
    pages_row = deploy_pages()
    steps.append({"step": "pages_deploy", **pages_row})

    if not worker_row.get("ok") or not pages_row.get("ok"):
        print(json.dumps({"ok": False, "steps": steps}, indent=2))
        return 1

    smoke_rows = []
    row = smoke_test(CUSTOM_DOMAIN)
    row["base"] = CUSTOM_DOMAIN
    smoke_rows.append(row)
    pages_smoke = smoke_pages(PAGES_URL)
    pages_smoke["base"] = PAGES_URL
    smoke_rows.append(pages_smoke)
    steps.append({"step": "smoke", "results": smoke_rows})

    ok = worker_row.get("ok") and pages_row.get("ok") and any(r.get("ok") for r in smoke_rows)

    out = {
        "ok": ok,
        "primary_url": PAGES_URL,
        "client_url": PAGES_URL,
        "api_url": API_ORIGIN,
        "custom_domain": CUSTOM_DOMAIN,
        "live_urls": [PAGES_URL, CUSTOM_DOMAIN],
        "steps": steps,
    }
    receipt = Path.home() / ".sina" / "pureflow-landing-publish-receipt-v1.json"
    receipt.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify sourcea-boot /eval wiring across all public subpages (ORD URL-check)."""
from __future__ import annotations

import json
import re
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://sourcea.app"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "sourcea-boot-wiring-e2e-receipt-v1.json"

PAGES = [
    "/",
    "/eval",
    "/platform",
    "/start",
    "/sourcea/48h-mvp",
    "/sourcea/",
    "/sourcea/proof",
    "/sourcea/proof/live",
    "/sourcea/platform",
    "/sourcea/pricing",
    "/sourcea/loops/",
    "/sourcea/forge/",
    "/sourcea/factories/try-factory-demo",
    "/sourcea/status",
    "/sourcea/security",
    "/sourcea/compare",
    "/sourcea/scenario",
    "/sourcea/loops/outreach",
    "/sourcea/loops/session-gate",
    "/sourcea/data/trust-signals.json",
    "/sourcea/data/boot-proof.json",
    "/operating-brain-install",
    "/ai-value-governance",
    "/enterprise-ai-control-plane",
]

REDIRECTS = [
    ("/sourcea-boot", "/eval", 301),
]


def fetch(url: str, *, follow: bool = True) -> dict:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "SourceA-boot-wire-e2e/1"})
    if not follow:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ctx))
        try:
            with opener.open(req, timeout=25) as resp:
                return {"status": resp.status, "body": resp.read(120_000).decode("utf-8", errors="replace"), "location": resp.headers.get("Location", "")}
        except urllib.error.HTTPError as e:
            return {"status": e.code, "body": "", "location": e.headers.get("Location", "") if e.headers else ""}
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
            return {"status": resp.status, "body": resp.read(120_000).decode("utf-8", errors="replace"), "location": resp.headers.get("Location", "")}
    except urllib.error.HTTPError as e:
        body = e.read(80_000).decode("utf-8", errors="replace") if e.fp else ""
        return {"status": e.code, "body": body, "location": e.headers.get("Location", "") if e.headers else ""}


CONTRACT_PAGES = {
    "/operating-brain-install",
    "/ai-value-governance",
    "/enterprise-ai-control-plane",
}


def has_boot_wire(body: str, path: str) -> bool:
    if path in CONTRACT_PAGES:
        return "Book an" in body or "mailto:contract@sourcea.app" in body
    if path.endswith(".json"):
        if "trust-signals" in path:
            return "kazemnezhadsina144-dot/sourcea-boot" in body
        if "boot-proof" in path:
            return "sourcea-boot-proof" in body
        return True
    patterns = [r"sourcea-boot", r'href="/eval"', r"github.com/kazemnezhadsina144-dot/sourcea-boot"]
    return any(re.search(p, body, re.I) for p in patterns)


def run() -> dict:
    checks = []
    for path in PAGES:
        url = BASE + path
        r = fetch(url)
        ok = r["status"] == 200 and has_boot_wire(r.get("body", ""), path)
        checks.append({"path": path, "url": url, "status": r["status"], "ok": ok})
    for src, dest, code in REDIRECTS:
        url = BASE + src
        r = fetch(url, follow=False)
        ok = r["status"] == code and dest in r.get("location", "")
        checks.append({"path": f"{src} → {dest}", "url": url, "status": r["status"], "location": r.get("location", ""), "ok": ok})
    gh = fetch("https://api.github.com/repos/kazemnezhadsina144-dot/sourcea-boot")
    return {
        "ok": all(c["ok"] for c in checks),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "github_repo": {"status": gh["status"], "public": gh["status"] == 200, "note": "404 = repo private or not published yet; site still links honestly"},
        "checks": checks,
        "local_package": str(Path(__file__).resolve().parents[1] / "packages" / "sourcea-boot"),
    }


def main() -> int:
    out = run()
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

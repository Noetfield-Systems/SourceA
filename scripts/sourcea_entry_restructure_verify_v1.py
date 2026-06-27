#!/usr/bin/env python3
"""Verify sourcea.app entry restructure — URL-checkable receipt (ORD)."""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://sourcea.app"
CHECKS = [
    {"id": "founder_home", "url": f"{BASE}/", "must_contain": ["AI that proves", "Run a free proof"]},
    {"id": "mvp_canonical", "url": f"{BASE}/start", "must_contain": ["48 hours", "sa-mvp-intake-form"]},
    {"id": "mvp_merged_what_you_get", "url": f"{BASE}/start", "must_contain": ["proof pack", "What you get"]},
    {"id": "mvp_hub_preserved", "url": f"{BASE}/sourcea/48h-mvp", "must_contain": ["agentic stack", "48-hour MVP hub"]},
    {"id": "mvp_retired_301", "url": f"{BASE}/mvp", "expect_status": (301, 302), "follow": False},
    {"id": "kernel", "url": f"{BASE}/sourcea/", "must_contain": ["on proof"]},
    {"id": "platform", "url": f"{BASE}/platform", "must_contain": ["Sign in"]},
    {"id": "sandbox", "url": f"{BASE}/sourcea/factories/try-factory-demo", "must_contain": []},
    {"id": "proof_live", "url": f"{BASE}/sourcea/proof/live", "must_contain": []},
    {"id": "pricing", "url": f"{BASE}/sourcea/pricing", "must_contain": []},
]


def fetch(url: str, *, follow: bool = True) -> dict:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "SourceA-entry-verify/1"})
    if not follow:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ctx))
        try:
            with opener.open(req, timeout=25) as resp:
                body = resp.read(120_000).decode("utf-8", errors="replace")
                return {"status": resp.status, "location": resp.headers.get("Location", ""), "body": body}
        except urllib.error.HTTPError as e:
            loc = e.headers.get("Location", "") if e.headers else ""
            return {"status": e.code, "location": loc, "body": ""}
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
            body = resp.read(120_000).decode("utf-8", errors="replace")
            return {"status": resp.status, "location": resp.headers.get("Location", ""), "body": body}
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location", "") if e.headers else ""
        body = e.read(80_000).decode("utf-8", errors="replace") if e.fp else ""
        return {"status": e.code, "location": loc, "body": body}


def run() -> dict:
    rows = []
    for c in CHECKS:
        row = {"id": c["id"], "url": c["url"], "ok": False}
        r = fetch(c["url"], follow=c.get("follow", True))
        row["status"] = r["status"]
        row["location"] = r.get("location", "")
        if c.get("expect_status"):
            lo, hi = c["expect_status"]
            row["ok"] = lo <= r["status"] <= hi
            if row["location"]:
                row["ok"] = row["ok"] and "/start" in row["location"]
        else:
            row["ok"] = r["status"] == 200
            for needle in c.get("must_contain", []):
                if needle.lower() not in r.get("body", "").lower():
                    row["ok"] = False
                    row["missing"] = needle
                    break
        rows.append(row)
    ok = all(x["ok"] for x in rows)
    return {
        "ok": ok,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "base": BASE,
        "decisions": {
            "canonical_mvp": "/start → /sourcea/start",
            "retired_mvp": "/mvp → 301 /start",
            "preserved_former_root": "/sourcea/48h-mvp (alias /48h-mvp)",
            "new_root": "/ founder-home.html — GTM headline: AI that proves its work",
        },
        "checks": rows,
    }


def main() -> int:
    out = run()
    receipt = Path.home() / ".sina" / "sourcea-entry-restructure-receipt-v1.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

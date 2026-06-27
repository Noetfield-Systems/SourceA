#!/usr/bin/env python3
"""Agent Run platform E2E — desktop sync + cloud URL verify (ORD-checkable)."""
from __future__ import annotations

import json
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "agent-run-platform-e2e-receipt-v1.json"
AGENTRUN = Path.home() / "Desktop/agentrun-app"
CLOUD = "https://sourcea.app"


def _fetch(url: str, *, follow: bool = True) -> dict:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "SourceA-agent-run-e2e/1"})
    if not follow:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ctx))
        try:
            with opener.open(req, timeout=25) as resp:
                body = resp.read(150_000).decode("utf-8", errors="replace")
                return {"status": resp.status, "body": body, "location": resp.headers.get("Location", "")}
        except urllib.error.HTTPError as e:
            loc = e.headers.get("Location", "") if e.headers else ""
            return {"status": e.code, "body": "", "location": loc}
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
            body = resp.read(150_000).decode("utf-8", errors="replace")
            return {"status": resp.status, "body": body, "location": resp.headers.get("Location", "")}
    except urllib.error.HTTPError as e:
        body = e.read(100_000).decode("utf-8", errors="replace") if e.fp else ""
        return {"status": e.code, "body": body, "location": e.headers.get("Location", "") if e.headers else ""}


def sync_desktop() -> dict:
    script = ROOT / "scripts/deploy_sourcea_desktop_landing_v1.py"
    if not script.is_file():
        return {"ok": False, "error": "deploy script missing"}
    if not AGENTRUN.is_dir():
        return {"ok": False, "error": f"agentrun-app missing: {AGENTRUN}"}
    proc = subprocess.run(
        [sys.executable, str(script), "--json"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    try:
        row = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        row = {"raw": proc.stdout[:500], "stderr": proc.stderr[:500]}
    platform_portal = AGENTRUN / "sourcea" / "platform-portal.html"
    loops_hub = AGENTRUN / "sourcea" / "loops" / "index.html"
    return {
        "ok": proc.returncode == 0 and platform_portal.is_file() and loops_hub.is_file(),
        "exit_code": proc.returncode,
        "platform_portal_on_disk": str(platform_portal),
        "loops_hub_on_disk": str(loops_hub),
        "deploy": row,
    }


def verify_cloud() -> list[dict]:
    checks = [
        ("platform_hub", f"{CLOUD}/platform", ["Agent Run", "sa-loops-catalog", "Sign in"]),
        ("agent_run_alias", f"{CLOUD}/agent-run", [], "redirect"),
        ("loops_catalog_json", f"{CLOUD}/sourcea/data/loops-catalog.json", ["outreach"]),
        ("loops_hub", f"{CLOUD}/sourcea/loops/", ["Factory loops", "sa-loops-catalog"]),
        ("factory_live_json", f"{CLOUD}/sourcea/data/factory-live.json", []),
        ("live_console_js", f"{CLOUD}/sourcea/sourcea-live-console.js", ["sa-biz-command"]),
        ("loops_hub_js", f"{CLOUD}/sourcea/sourcea-loops-hub.js", ["loops-catalog"]),
    ]
    rows = []
    for item in checks:
        cid, url = item[0], item[1]
        needles = item[2] if len(item) > 2 else []
        mode = item[3] if len(item) > 3 else "content"
        r = _fetch(url, follow=(mode != "redirect"))
        ok = r["status"] == 200
        if mode == "redirect":
            ok = r["status"] in (301, 302) and "/platform" in r.get("location", "")
        else:
            for n in needles:
                if n.lower() not in r.get("body", "").lower():
                    ok = False
                    break
        rows.append({"id": cid, "url": url, "status": r["status"], "ok": ok, "location": r.get("location", "")})
    return rows


def main() -> int:
    desktop = sync_desktop()
    cloud = verify_cloud()
    ok = desktop.get("ok") and all(c["ok"] for c in cloud)
    out = {
        "ok": ok,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "desktop_sync": desktop,
        "cloud_checks": cloud,
        "urls": {
            "cloud_platform": f"{CLOUD}/platform",
            "cloud_loops": f"{CLOUD}/sourcea/loops/",
            "desktop_sourcea": str(AGENTRUN / "sourcea"),
        },
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

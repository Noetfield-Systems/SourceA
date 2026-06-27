#!/usr/bin/env python3
"""Print (and optionally apply) Cloudflare DNS for sourcea.app → Vercel source-a.

Law: docs/SOURCEA_APP_DNS_VERCEL_LOCKED_v1.md
Apply requires CF API token with Zone.DNS Edit on sourcea.app.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONE_NAME = "sourcea.app"
VERCEL_A = "76.76.21.21"
RECORDS = (
    {"type": "A", "name": ZONE_NAME, "content": VERCEL_A, "proxied": False},
    {"type": "A", "name": f"www.{ZONE_NAME}", "content": VERCEL_A, "proxied": False},
)


def _cf_token() -> str | None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from sourcea_cf_pages_token_v1 import load_sourcea_cf_config  # noqa: WPS433

    cfg = load_sourcea_cf_config()
    return str(cfg["api_token"]) if cfg.get("ok") else None


def _api(token: str, method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return {"success": False, "status": exc.code, "body": exc.read().decode()[:400]}


def main() -> int:
    ap = argparse.ArgumentParser(description="sourcea.app DNS → Vercel")
    ap.add_argument("--apply", action="store_true", help="Create DNS records via CF API")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = {
        "schema": "sourcea-app-dns-vercel-v1",
        "zone": ZONE_NAME,
        "records": RECORDS,
        "vercel_project": "source-a",
        "manual_doc": "docs/SOURCEA_APP_DNS_VERCEL_LOCKED_v1.md",
    }

    if args.apply:
        tok = _cf_token()
        if not tok:
            print("FAIL: need ~/.sina/cf-pages-token-v1.json with Zone.DNS Edit", file=sys.stderr)
            return 1
        zones = _api(tok, "GET", f"/zones?name={ZONE_NAME}")
        zid = (zones.get("result") or [{}])[0].get("id")
        if not zid:
            row["apply"] = {"ok": False, "error": "zone_not_found"}
        else:
            created = []
            for rec in RECORDS:
                out = _api(tok, "POST", f"/zones/{zid}/dns_records", {**rec, "ttl": 1})
                created.append({"name": rec["name"], "ok": bool(out.get("success")), "errors": out.get("errors")})
            row["apply"] = {"ok": all(c["ok"] for c in created), "created": created}

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print("Add in Cloudflare DNS for sourcea.app:")
        for r in RECORDS:
            short = "@" if r["name"] == ZONE_NAME else "www"
            print(f"  A  {short:4}  {r['content']}  (DNS only / grey cloud)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

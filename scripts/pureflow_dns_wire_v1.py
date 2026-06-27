#!/usr/bin/env python3
"""Wire DNS for pureflow.sourcea.app → Cloudflare Worker (proxied AAAA 100::)."""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ZONE = "sourcea.app"
HOST = "pureflow"
ACCOUNT_ID = "0d0b967b77e2e5535455d39ff3dae72c"


def _oauth_token() -> str | None:
    cfg = Path.home() / ".wrangler" / "config" / "default.toml"
    if not cfg.is_file():
        return None
    text = cfg.read_text()
    m = re.search(r'oauth_token\s*=\s*"([^"]+)"', text)
    return m.group(1) if m else None


def _api(token: str, path: str, *, method: str = "GET", data: dict | None = None) -> dict:
    url = f"https://api.cloudflare.com/client/v4{path}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        try:
            return json.loads(exc.read().decode())
        except Exception:
            return {"success": False, "errors": [{"message": str(exc)}]}


def main() -> int:
    token = _oauth_token()
    if not token:
        print(json.dumps({"ok": False, "error": "no_wrangler_oauth"}))
        return 1

    zones = _api(token, f"/zones?name={ZONE}")
    if not zones.get("success") or not zones.get("result"):
        print(json.dumps({"ok": False, "error": "zone_not_found", "zone": ZONE}))
        return 1
    zone_id = zones["result"][0]["id"]

    existing = _api(token, f"/zones/{zone_id}/dns_records?name={HOST}.{ZONE}")
    for rec in existing.get("result") or []:
        if rec.get("type") in ("AAAA", "A", "CNAME") and rec.get("name") == f"{HOST}.{ZONE}":
            print(
                json.dumps(
                    {
                        "ok": True,
                        "action": "exists",
                        "record": rec.get("type"),
                        "name": f"{HOST}.{ZONE}",
                        "id": rec.get("id"),
                    }
                )
            )
            return 0

    created = _api(
        token,
        f"/zones/{zone_id}/dns_records",
        method="POST",
        data={
            "type": "AAAA",
            "name": HOST,
            "content": "100::",
            "proxied": True,
            "comment": "Pure Flow pool landing — Worker route",
        },
    )
    ok = bool(created.get("success"))
    print(
        json.dumps(
            {
                "ok": ok,
                "action": "created",
                "name": f"{HOST}.{ZONE}",
                "errors": [e.get("message") for e in created.get("errors") or []],
                "result": created.get("result"),
            },
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

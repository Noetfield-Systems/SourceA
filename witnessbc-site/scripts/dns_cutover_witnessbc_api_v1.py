#!/usr/bin/env python3
"""Automate witnessbc.com DNS cutover: Vercel → Cloudflare Pages (witnessbc-commercial).

Uses founder wrangler OAuth (witness.bc@gmail.com) — not SourceA/TrustField secrets.env token.
Receipt: ~/.sina/witnessbc-dns-cutover-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ACCOUNT_ID = "2c70de9e879a9b41055642ad47205d71"
PROJECT = "witnessbc-commercial"
PAGES_TARGET = "witnessbc-commercial.pages.dev"
ZONE_NAME = "witnessbc.com"
WRANGLER_CFG = Path.home() / "Library/Preferences/.wrangler/config/default.toml"
RECEIPT = Path.home() / ".sina/witnessbc-dns-cutover-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_oauth() -> str:
    if not WRANGLER_CFG.is_file():
        raise SystemExit(f"FAIL: missing wrangler config {WRANGLER_CFG} — run: wrangler login")
    text = WRANGLER_CFG.read_text(encoding="utf-8")
    m = re.search(r'^oauth_token = "(.+)"', text, re.M)
    if not m:
        raise SystemExit("FAIL: oauth_token missing in wrangler config — run: wrangler login")
    return m.group(1)


def _api(token: str, path: str, method: str = "GET", data: dict | None = None) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode())
        except Exception:
            payload = {"success": False, "errors": [{"message": str(exc)}]}
        payload["_http_status"] = exc.code
        return payload


def _zone_id(token: str) -> str:
    res = _api(token, f"/zones?name={ZONE_NAME}")
    if not res.get("success") or not res.get("result"):
        msgs = [e.get("message", "") for e in res.get("errors", [])]
        raise SystemExit(f"FAIL: cannot read zone {ZONE_NAME}: {msgs or res}")
    return str(res["result"][0]["id"])


def _list_dns(token: str, zid: str) -> list[dict]:
    res = _api(token, f"/zones/{zid}/dns_records?per_page=100")
    if not res.get("success"):
        raise SystemExit(f"FAIL: dns list: {res.get('errors')}")
    return list(res.get("result") or [])


def _upsert_cname(token: str, zid: str, name: str, content: str, proxied: bool, apply: bool) -> dict:
    records = _list_dns(token, zid)
    existing = [r for r in records if r.get("name") == name and r.get("type") in ("CNAME", "A", "AAAA")]
    payload = {
        "type": "CNAME",
        "name": name,
        "content": content,
        "ttl": 1,
        "proxied": proxied,
    }
    action = {"name": name, "target": content, "proxied": proxied, "applied": False}
    if not apply:
        action["dry_run"] = True
        return action
    if existing:
        rid = existing[0]["id"]
        res = _api(token, f"/zones/{zid}/dns_records/{rid}", "PATCH", payload)
        action["method"] = "PATCH"
        action["record_id"] = rid
    else:
        res = _api(token, f"/zones/{zid}/dns_records", "POST", payload)
        action["method"] = "POST"
    action["success"] = bool(res.get("success"))
    action["applied"] = action["success"]
    if not action["success"]:
        action["errors"] = [e.get("message") for e in res.get("errors", [])]
        action["http"] = res.get("_http_status")
    return action


def _attach_pages_domains(token: str, apply: bool) -> list[dict]:
    out: list[dict] = []
    for dom in (f"www.{ZONE_NAME}", ZONE_NAME):
        row = {"domain": dom, "applied": False}
        if not apply:
            row["dry_run"] = True
            out.append(row)
            continue
        res = _api(token, f"/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT}/domains", "POST", {"name": dom})
        row["success"] = bool(res.get("success"))
        row["applied"] = row["success"]
        if not row["success"]:
            row["errors"] = [e.get("message") for e in res.get("errors", [])]
            if any("already exists" in (e or "").lower() for e in row.get("errors", [])):
                row["success"] = True
                row["applied"] = True
                row["note"] = "already_attached"
        out.append(row)
    return out


def run(apply: bool) -> dict:
    token = _load_oauth()
    verify = _api(token, "/user/tokens/verify")
    status = (verify.get("result") or {}).get("status")
    if status != "active":
        msgs = [e.get("message") for e in verify.get("errors", []) if e.get("message")]
        raise SystemExit(
            "FAIL: wrangler oauth token not active — run: wrangler login"
            + (f" ({msgs[0]})" if msgs else "")
        )

    zid = _zone_id(token)
    before = [
        {"type": r.get("type"), "name": r.get("name"), "content": r.get("content"), "proxied": r.get("proxied")}
        for r in _list_dns(token, zid)
        if r.get("name") in (ZONE_NAME, f"www.{ZONE_NAME}")
    ]

    pages_domains = _attach_pages_domains(token, apply)
    dns_actions = [
        _upsert_cname(token, zid, f"www.{ZONE_NAME}", PAGES_TARGET, True, apply),
        _upsert_cname(token, zid, ZONE_NAME, PAGES_TARGET, True, apply),
    ]

    receipt = {
        "schema": "witnessbc-dns-cutover-receipt-v1",
        "at": _now(),
        "ok": all(a.get("success", a.get("dry_run")) for a in pages_domains)
        and all(a.get("success", a.get("dry_run")) for a in dns_actions),
        "apply": apply,
        "account_id": ACCOUNT_ID,
        "project": PROJECT,
        "pages_target": PAGES_TARGET,
        "zone_id": zid,
        "before": before,
        "pages_domains": pages_domains,
        "dns_actions": dns_actions,
        "verify_cmds": [
            f"curl -sSI https://www.{ZONE_NAME}/ | grep -i server",
            f"curl -sL https://www.{ZONE_NAME}/ | grep brand-disambiguation",
        ],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="WitnessBC DNS cutover API")
    ap.add_argument("--apply", action="store_true", help="Apply DNS + Pages domain attach")
    ap.add_argument("--dry-run", action="store_true", help="Plan only (default)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    apply = bool(args.apply) and not args.dry_run
    row = run(apply)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row.get('ok')} apply={apply} receipt={RECEIPT}")
        for a in row.get("dns_actions", []):
            print(f"  dns {a.get('name')} → {a.get('target')} success={a.get('success', a.get('dry_run'))}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())

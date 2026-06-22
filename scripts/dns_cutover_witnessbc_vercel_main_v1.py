#!/usr/bin/env python3
"""Cut over witnessbc.com DNS from old Vercel → main the-777-foundation project.

Uses WITNESSBC_CF_API_TOKEN + WITNESSBC_CF_ZONE_ID from ~/.sina/secrets.env
(or CF token with access to witnessbc.com zone).

Receipt: ~/.sina/witnessbc-vercel-main-dns-cutover-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ZONE_NAME = "witnessbc.com"
DEFAULT_ZONE_ID = "fbaba5b3d756fa9c2d6e5e6368df4414"  # witnessbc.com · witness.bc CF account
WWW_CNAME = "14c1ee71176829d5.vercel-dns-017.com"
APEX_A = "216.198.79.1"
TXT_RECORDS = [
    "vc-domain-verify=www.witnessbc.com,1c973c91295554fc3767",
    "vc-domain-verify=witnessbc.com,daf6300b053924e9be6c",
]
RECEIPT = Path.home() / ".sina/witnessbc-vercel-main-dns-cutover-receipt-v1.json"
SSOT = Path(__file__).resolve().parents[1] / "data/witnessbc-vercel-main-dns-cutover-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _wrangler_oauth_token() -> str | None:
    """Fresh OAuth bearer from `wrangler auth token` (witness.bc login on Mac)."""
    try:
        proc = subprocess.run(
            ["npx", "--yes", "wrangler", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    lines = [
        ln.strip()
        for ln in (proc.stdout or "").splitlines()
        if ln.strip() and not ln.startswith("npm") and not ln.startswith("⛅") and not ln.startswith("─")
    ]
    for ln in reversed(lines):
        if len(ln) > 50 and " " not in ln:
            return ln
    return None


def _load_secrets() -> dict[str, str]:
    env: dict[str, str] = {}
    for path in (Path.home() / ".sina/secrets.env",):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _api(token: str, path: str, method: str = "GET", data: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
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


def _resolve_token(env: dict[str, str]) -> tuple[str, str]:
    if env.get("WITNESSBC_CF_API_TOKEN") or env.get("CF_WITNESSBC_API_TOKEN"):
        return (
            env.get("WITNESSBC_CF_API_TOKEN") or env.get("CF_WITNESSBC_API_TOKEN") or "",
            "secrets",
        )
    oauth = _wrangler_oauth_token()
    if oauth:
        return oauth, "wrangler_oauth"
    raise SystemExit(
        "FAIL: set WITNESSBC_CF_API_TOKEN in ~/.sina/secrets.env or run: npx wrangler login (witness.bc)"
    )


def _zone_id(token: str, env: dict[str, str]) -> str:
    zid = env.get("WITNESSBC_CF_ZONE_ID") or env.get("CF_WITNESSBC_ZONE_ID") or DEFAULT_ZONE_ID
    if zid:
        return zid
    res = _api(token, f"/zones?name={ZONE_NAME}")
    if res.get("success") and res.get("result"):
        return str(res["result"][0]["id"])
    raise SystemExit(f"FAIL: cannot resolve zone {ZONE_NAME}: {res.get('errors')}")


def _list_dns(token: str, zid: str) -> list[dict]:
    res = _api(token, f"/zones/{zid}/dns_records?per_page=100")
    if not res.get("success"):
        raise SystemExit(f"FAIL: dns list: {res.get('errors')}")
    return list(res.get("result") or [])


def _detach_worker_custom_domain(hostname: str = "www.witnessbc.com") -> dict:
    """Remove Workers Custom Domain that blocks manual CNAME (uses wrangler OAuth)."""
    oauth = _wrangler_oauth_token()
    if not oauth:
        return {"skipped": True, "reason": "no_wrangler_oauth"}
    account = "2c70de9e879a9b41055642ad47205d71"
    res = _api(oauth, f"/accounts/{account}/workers/domains")
    if not res.get("success"):
        return {"ok": False, "errors": res.get("errors")}
    removed: list[str] = []
    for row in res.get("result") or []:
        if row.get("hostname") != hostname:
            continue
        did = str(row.get("id") or "")
        del_res = _api(oauth, f"/accounts/{account}/workers/domains/{did}", "DELETE")
        removed.append(did)
        if not del_res.get("success") and del_res.get("_http_status") not in (404,):
            return {"ok": False, "removed": removed, "errors": del_res.get("errors")}
    return {"ok": True, "removed": removed}


def _upsert(token: str, zid: str, *, rtype: str, name: str, content: str, proxied: bool | None, apply: bool) -> dict:
    fq = name if name.endswith(ZONE_NAME) else (ZONE_NAME if name in ("@", ZONE_NAME) else f"{name}.{ZONE_NAME}")
    if name == "@":
        fq = ZONE_NAME
    records = _list_dns(token, zid)
    existing = [
        r
        for r in records
        if r.get("name") in (fq, name, f"{name}.{ZONE_NAME}", ZONE_NAME)
        and r.get("type") == rtype
        and (rtype != "TXT" or r.get("content", "").strip('"') == content)
    ]
    payload: dict = {"type": rtype, "name": name if name != fq else fq, "content": content, "ttl": 1}
    if proxied is not None and rtype in ("CNAME", "A", "AAAA"):
        payload["proxied"] = proxied
    action = {"type": rtype, "name": name, "content": content, "applied": False}
    if not apply:
        action["dry_run"] = True
        return action
    if existing:
        rid = existing[0]["id"]
        res = _api(token, f"/zones/{zid}/dns_records/{rid}", "PATCH", payload)
        action["method"] = "PATCH"
    else:
        res = _api(token, f"/zones/{zid}/dns_records", "POST", payload)
        action["method"] = "POST"
    action["success"] = bool(res.get("success"))
    action["applied"] = action["success"]
    if not action["success"]:
        action["errors"] = [e.get("message") for e in res.get("errors", [])]
    return action


def run(apply: bool) -> dict:
    env = _load_secrets()
    token, token_source = _resolve_token(env)
    zid = _zone_id(token, env)
    worker_detach = _detach_worker_custom_domain() if apply else {"dry_run": True}
    before = [
        {"type": r.get("type"), "name": r.get("name"), "content": r.get("content")}
        for r in _list_dns(token, zid)
        if r.get("name") in (ZONE_NAME, f"www.{ZONE_NAME}") or r.get("name", "").startswith("_vercel")
    ]
    actions = [
        _upsert(token, zid, rtype="CNAME", name="www", content=WWW_CNAME, proxied=False, apply=apply),
        _upsert(token, zid, rtype="A", name="@", content=APEX_A, proxied=False, apply=apply),
    ]
    for txt in TXT_RECORDS:
        actions.append(_upsert(token, zid, rtype="TXT", name="_vercel", content=txt, proxied=None, apply=apply))
    receipt = {
        "schema": "witnessbc-vercel-main-dns-cutover-receipt-v1",
        "at": _now(),
        "ok": all(a.get("success", a.get("dry_run")) for a in actions),
        "apply": apply,
        "token_source": token_source,
        "zone_id": zid,
        "www_cname": WWW_CNAME,
        "worker_detach": worker_detach,
        "before": before,
        "actions": actions,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run(apply=bool(args.apply))
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row['ok']} apply={args.apply} receipt={RECEIPT}")
        for a in row["actions"]:
            print(f"  {a.get('type')} {a.get('name')} -> {a.get('content')[:50]} success={a.get('success', a.get('dry_run'))}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

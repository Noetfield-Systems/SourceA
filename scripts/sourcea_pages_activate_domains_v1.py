#!/usr/bin/env python3
"""Activate sourcea.app + www on Cloudflare Pages project sourcea-com.

Uses wrangler OAuth refresh (client_id 54d11594-…) — wrangler v4 removed
`pages project domain add`. Does not print tokens.

Receipt: ~/.sina/sourcea-pages-domains-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "sourcea-pages-domains-receipt-v1.json"
WRANGLER_CFG = Path.home() / "Library/Preferences/.wrangler/config/default.toml"

ACCOUNT_ID = "0d0b967b77e2e5535455d39ff3dae72c"
PROJECT = "sourcea-com"
CLIENT_ID = "54d11594-84e4-41aa-b438-e81b8fa78ee7"
TOKEN_URL = "https://dash.cloudflare.com/oauth2/token"

DOMAINS_BY_PROJECT: dict[str, tuple[str, ...]] = {
    "sourcea-com": ("sourcea.app", "www.sourcea.app"),
    "sourcea-landing": ("sourcea.com", "www.sourcea.com"),
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_wrangler_oauth() -> dict[str, str]:
    if not WRANGLER_CFG.is_file():
        raise SystemExit(f"FAIL: wrangler not logged in — run: wrangler login ({WRANGLER_CFG})")
    text = WRANGLER_CFG.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for key in ("oauth_token", "refresh_token", "expiration_time"):
        m = re.search(rf'^{key} = "(.+)"', text, re.M)
        if m:
            out[key] = m.group(1)
    if not out.get("refresh_token"):
        raise SystemExit("FAIL: wrangler refresh_token missing — run: wrangler login")
    return out


def _write_wrangler_oauth(oauth_token: str, expiration_time: str, refresh_token: str | None) -> None:
    text = WRANGLER_CFG.read_text(encoding="utf-8")
    text = re.sub(r'^oauth_token = ".*"', f'oauth_token = "{oauth_token}"', text, flags=re.M)
    text = re.sub(r'^expiration_time = ".*"', f'expiration_time = "{expiration_time}"', text, flags=re.M)
    if refresh_token:
        text = re.sub(r'^refresh_token = ".*"', f'refresh_token = "{refresh_token}"', text, flags=re.M)
    WRANGLER_CFG.write_text(text, encoding="utf-8")


def _refresh_access_token(refresh_token: str) -> dict:
    data = (
        f"grant_type=refresh_token&refresh_token={urllib.parse.quote(refresh_token, safe='')}"
        f"&client_id={CLIENT_ID}"
    )
    proc = subprocess.run(
        [
            "curl",
            "-sS",
            "-X",
            "POST",
            TOKEN_URL,
            "-H",
            "Content-Type: application/x-www-form-urlencoded",
            "-H",
            "User-Agent: wrangler/4.103.0",
            "--data",
            data,
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"FAIL: oauth refresh curl — {(proc.stderr or proc.stdout)[-300:]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: oauth refresh invalid JSON — {proc.stdout[:200]}") from exc


def _get_access_token() -> str:
    stored = _read_wrangler_oauth()
    exp = stored.get("expiration_time", "")
    if stored.get("oauth_token") and exp:
        try:
            if datetime.fromisoformat(exp.replace("Z", "+00:00")) > datetime.now(timezone.utc):
                return stored["oauth_token"]
        except ValueError:
            pass
    tok = _refresh_access_token(stored["refresh_token"])
    if "access_token" not in tok:
        raise SystemExit(f"FAIL: oauth refresh — {tok.get('error') or tok}")
    expiry = datetime.now(timezone.utc).timestamp() + float(tok.get("expires_in", 3600))
    expiration_time = datetime.fromtimestamp(expiry, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    _write_wrangler_oauth(tok["access_token"], expiration_time, tok.get("refresh_token"))
    return str(tok["access_token"])


def _cf_api(token: str, path: str, *, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
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


def activate(*, project: str = PROJECT, domains: tuple[str, ...] | None = None) -> dict:
    doms = domains or DOMAINS_BY_PROJECT.get(project, ())
    token = _get_access_token()
    steps: list[dict] = [{"step": "oauth_refresh", "ok": True}]

    listed = _cf_api(token, f"/accounts/{ACCOUNT_ID}/pages/projects/{project}/domains")
    existing = {d.get("name"): d for d in (listed.get("result") or [])}
    steps.append(
        {
            "step": "list_domains",
            "ok": bool(listed.get("success")),
            "existing": list(existing.keys()),
        }
    )

    rows: list[dict] = []
    for dom in doms:
        if dom in existing:
            rows.append({"domain": dom, "ok": True, "note": "already_attached", "status": existing[dom].get("status")})
            continue
        res = _cf_api(
            token,
            f"/accounts/{ACCOUNT_ID}/pages/projects/{project}/domains",
            method="POST",
            body={"name": dom},
        )
        ok = bool(res.get("success"))
        errs = [str(e.get("message") or e) for e in res.get("errors") or []]
        if not ok and any("already" in e.lower() for e in errs):
            ok = True
        rows.append(
            {
                "domain": dom,
                "ok": ok,
                "status": (res.get("result") or {}).get("status"),
                "note": errs[0] if errs and not ok else "added",
            }
        )
        steps.append({"step": f"add_{dom}", "ok": ok, "errors": errs if not ok else []})

    # Re-list for final status
    final = _cf_api(token, f"/accounts/{ACCOUNT_ID}/pages/projects/{project}/domains")
    final_rows = [
        {"domain": d.get("name"), "status": d.get("status"), "verification": d.get("verification_data")}
        for d in (final.get("result") or [])
    ]
    steps.append({"step": "final_domains", "rows": final_rows})

    ok = all(r.get("ok") for r in rows) and bool(final.get("success"))
    row = {
        "ok": ok,
        "schema": "sourcea-pages-domains-v1",
        "at": _now(),
        "project": project,
        "account_id": ACCOUNT_ID,
        "domains": rows,
        "final_domains": final_rows,
        "steps": steps,
        "founder_line": (
            f"Pages domains {'OK' if ok else 'PARTIAL'} · {project} · "
            + ", ".join(d["domain"] for d in rows if d.get("ok"))
        ),
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Activate sourcea.app on Cloudflare Pages")
    ap.add_argument("--project", default=PROJECT)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = activate(project=args.project)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or row.get("error") or "FAIL")
        for d in row.get("domains") or []:
            print(f"  {d.get('domain')}: {'OK' if d.get('ok') else 'FAIL'} — {d.get('note')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

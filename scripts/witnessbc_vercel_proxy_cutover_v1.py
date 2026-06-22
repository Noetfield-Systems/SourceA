#!/usr/bin/env python3
"""Agentic www cutover via Cloudflare Worker Custom Domain (auto DNS — no manual CNAME).

Uses wrangler OAuth (witness.bc) + Workers Domains API to create www DNS and proxy to main Vercel.

Receipt: ~/.sina/witnessbc-vercel-proxy-cutover-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ACCOUNT_ID = "2c70de9e879a9b41055642ad47205d71"
HOSTNAME = "www.witnessbc.com"
WORKER = "witnessbc-vercel-proxy"
PROXY_DIR = Path(__file__).resolve().parents[1] / "infra/witnessbc-vercel-proxy"
RECEIPT = Path.home() / ".sina/witnessbc-vercel-proxy-cutover-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _wrangler_token() -> str:
    proc = subprocess.run(
        ["npx", "--yes", "wrangler", "auth", "token"],
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
        cwd=str(PROXY_DIR),
    )
    lines = [
        ln.strip()
        for ln in (proc.stdout or "").splitlines()
        if ln.strip() and not ln.startswith("npm") and not ln.startswith("⛅") and not ln.startswith("─")
    ]
    for ln in reversed(lines):
        if len(ln) > 50 and " " not in ln:
            return ln
    raise SystemExit("FAIL: wrangler auth token")


def _api(token: str, path: str, method: str = "GET", data: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode())
        except Exception:
            payload = {"success": False, "errors": [{"message": str(exc)}]}
        payload["_http_status"] = exc.code
        return payload


def _deploy_worker() -> dict:
    proc = subprocess.run(
        ["npx", "--yes", "wrangler", "deploy"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        cwd=str(PROXY_DIR),
    )
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-1200:],
        "stderr_tail": (proc.stderr or "")[-800:],
    }


def _attach_domain(token: str) -> dict:
    existing = _api(token, f"/accounts/{ACCOUNT_ID}/workers/domains")
    for row in existing.get("result") or []:
        if row.get("hostname") == HOSTNAME:
            return {"ok": True, "already": True, "result": row}
    payload = {"hostname": HOSTNAME, "service": WORKER, "environment": "production"}
    res = _api(token, f"/accounts/{ACCOUNT_ID}/workers/domains", "PUT", payload)
    return {
        "ok": bool(res.get("success")),
        "method": "PUT",
        "result": res.get("result"),
        "errors": [e.get("message") for e in res.get("errors", [])],
        "_http_status": res.get("_http_status"),
    }


def _verify() -> dict:
    out: dict[str, str] = {}
    for key, url, needle in (
        ("www", f"https://{HOSTNAME}/", "Witness AI"),
        ("observe", f"https://{HOSTNAME}/observe/", "observe and narrate"),
    ):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                body = resp.read(400_000).decode("utf-8", errors="replace")
            out[key] = "PASS" if needle in body else "FAIL"
        except Exception as exc:
            out[key] = f"ERR:{type(exc).__name__}"
    return out


def run(apply: bool) -> dict:
    token = _wrangler_token()
    row: dict = {
        "schema": "witnessbc-vercel-proxy-cutover-receipt-v1",
        "at": _now(),
        "apply": apply,
        "hostname": HOSTNAME,
        "worker": WORKER,
        "ok": False,
    }
    if not apply:
        row["dry_run"] = True
        row["ok"] = True
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    row["deploy"] = _deploy_worker()
    if not row["deploy"].get("ok"):
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    row["domain"] = _attach_domain(token)
    row["verify"] = _verify()
    row["ok"] = bool(row["domain"].get("ok")) and row["verify"].get("www") == "PASS"
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run(apply=bool(args.apply))
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row.get('ok')} receipt={RECEIPT}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

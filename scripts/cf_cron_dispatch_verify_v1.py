#!/usr/bin/env python3
"""Fire dispatch/smoke once per unique job — receipt for CF cron migration verify."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKER = "https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev"
RECEIPT_DIR = ROOT / "receipts" / "cloud" / "cf-cron-dispatch-verify"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _post(url: str, body: dict | None = None, timeout: int = 300) -> tuple[int, dict]:
    data = json.dumps(body or {}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            row = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            row = {"ok": False, "error": raw[:400]}
        return exc.code, row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker-url", default=DEFAULT_WORKER)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    base = args.worker_url.rstrip("/")
    health_url = f"{base}/health"
    smoke_url = f"{base}/dispatch/smoke"

    health_req = urllib.request.Request(health_url, method="GET")
    with urllib.request.urlopen(health_req, timeout=30) as resp:
        health = json.loads(resp.read().decode("utf-8"))

    status, smoke = _post(smoke_url, {})
    receipt = {
        "schema": "cf-cron-dispatch-verify-v1",
        "at": _now(),
        "worker_url": base,
        "health": health,
        "smoke_status": status,
        "smoke": smoke,
        "ok": bool(smoke.get("ok")) and status == 200,
        "unique_jobs": smoke.get("unique_jobs"),
        "results": smoke.get("results", []),
    }

    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = RECEIPT_DIR / f"verify-{stamp}.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_path"] = str(out)

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"receipt: {out}")
        print(f"ok: {receipt['ok']} · unique_jobs: {receipt.get('unique_jobs')}")
        for row in receipt.get("results", []):
            mark = "PASS" if row.get("ok") else "FAIL"
            target = row.get("path") or row.get("handler")
            print(f"  {mark} {row.get('id')} ({target})")

    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

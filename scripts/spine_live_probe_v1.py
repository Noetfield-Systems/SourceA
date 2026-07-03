#!/usr/bin/env python3
"""Spine + GHA live probe — machine-only is-it-live (LP-OUTSIDE-AUDIT)."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "proof" / "spine-live-probe-latest-v1.json"
PY = sys.executable


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _supabase_cfg() -> dict[str, str]:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    spine = Path.home() / ".sourcea-secrets" / "portfolio-spine.env"
    if spine.is_file():
        for line in spine.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k == "SUPABASE_URL" and not url:
                url = v
            if k == "SUPABASE_SERVICE_ROLE_KEY" and not key:
                key = v
    return {"url": url.rstrip("/"), "key": key}


def _truth_log_latest() -> dict[str, Any]:
    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "skipped": True, "reason": "no supabase cfg"}
    q = urllib.parse.urlencode(
        {
            "select": "created_at,event_type,conclusion,payload",
            "event_type": "eq.EXTERNAL_VERIFY_PASS",
            "order": "created_at.desc",
            "limit": "1",
        }
    )
    url = f"{cfg['url']}/rest/v1/truth_log?{q}"
    req = urllib.request.Request(
        url,
        headers={"apikey": cfg["key"], "Authorization": f"Bearer {cfg['key']}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            rows = json.loads(resp.read().decode())
        if rows:
            return {"ok": True, "latest": rows[0]}
        return {"ok": False, "reason": "no EXTERNAL_VERIFY_PASS rows"}
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "reason": str(exc)[:120]}


def _gha_runs() -> dict[str, Any]:
    try:
        out = subprocess.check_output(
            [PY, str(ROOT / "scripts" / "read_action_runs_v1.py"), "--workflow", "external-verify.yml", "--json"],
            text=True,
            cwd=str(ROOT),
            stderr=subprocess.DEVNULL,
        )
        return {"ok": True, "data": json.loads(out) if out.strip().startswith("{") else {"raw": out[:200]}}
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return {"ok": False, "skipped": True, "reason": "read_action_runs unavailable"}


def _head_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
    except subprocess.CalledProcessError:
        return ""


def probe() -> dict[str, Any]:
    truth = _truth_log_latest()
    gha = _gha_runs()
    head = _head_sha()
    ok = truth.get("ok") or gha.get("ok") or bool(head)
    doc = {
        "schema": "spine-live-probe-v1",
        "at": _now(),
        "ok": ok,
        "head_sha": head,
        "truth_log": truth,
        "gha_external_verify": gha,
        "report_line": (
            "spine_probe PASS · truth_log or GHA reachable"
            if ok
            else "spine_probe FAIL · no live signal"
        ),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    mirror = Path.home() / ".sina" / "spine-live-probe-latest-v1.json"
    mirror.parent.mkdir(parents=True, exist_ok=True)
    mirror.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = probe()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

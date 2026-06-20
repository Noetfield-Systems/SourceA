#!/usr/bin/env python3
"""Mac Health cloud glance — read-only Railway health + last dispatch receipt (Mac never runs jobs)."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
CONFIG_PATH = ROOT / "data" / "fbe_cloud_worker_config_v1.json"
LAST_DISPATCH = SINA / "cloud-dispatch-last-receipt-v1.json"
RECEIPT_PATH = SINA / "mac-health-cloud-glance-v1.json"
HUB_URL = "http://127.0.0.1:13020/"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _worker_url() -> str:
    cfg = _read_json(CONFIG_PATH)
    return str(cfg.get("worker_url") or "").strip().rstrip("/")


def _probe_railway(url: str, *, timeout: float = 5.0) -> dict[str, Any]:
    if not url:
        return {"ok": False, "error": "worker_url_missing"}
    target = f"{url}/health"
    try:
        with urllib.request.urlopen(target, timeout=timeout) as resp:
            raw = resp.read(2048).decode("utf-8", errors="replace")
            body = json.loads(raw) if raw.strip() else {}
            return {
                "ok": bool(body.get("ok")),
                "status": resp.status,
                "service": body.get("service"),
                "url": url,
            }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": "http_error", "url": url}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:160], "url": url}


def _last_dispatch() -> dict[str, Any]:
    row = _read_json(LAST_DISPATCH)
    if not row:
        alt = ROOT / "receipts" / "cloud-dispatch"
        if alt.is_dir():
            files = sorted(alt.glob("cloud-dispatch-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if files:
                row = _read_json(files[0])
    if not row:
        return {}
    show = (row.get("for_founder") or {}).get("show_this") or ""
    return {
        "plan_id": row.get("plan_id"),
        "receipt_id": row.get("receipt_id"),
        "ok": row.get("ok"),
        "at": row.get("at"),
        "show_this": show,
        "": row.get(""),
    }


def _founder_line(*, railway: dict[str, Any], dispatch: dict[str, Any]) -> str:
    rail = "Railway OK" if railway.get("ok") else "Railway unreachable"
    if dispatch.get("plan_id"):
        job = "PASS" if dispatch.get("ok") else "FAIL"
        return f"Cloud · {rail} · last job {dispatch.get('plan_id')} {job}"
    return f"Cloud · {rail} · no dispatch receipt yet"


def probe(*, write_receipt: bool = True) -> dict[str, Any]:
    url = _worker_url()
    railway = _probe_railway(url)
    dispatch = _last_dispatch()
    founder_line = _founder_line(railway=railway, dispatch=dispatch)
    row: dict[str, Any] = {
        "schema": "mac-health-cloud-glance-v1",
        "ok": bool(railway.get("ok")),
        "at": _now(),
        "execution_plane": "read_only_mac_glance",
        "railway_ok": bool(railway.get("ok")),
        "railway": railway,
        "last_plan_id": dispatch.get("plan_id"),
        "last_dispatch_ok": dispatch.get("ok"),
        "last_show_this": dispatch.get("show_this"),
        "last_dispatch_at": dispatch.get("at"),
        "last_receipt_id": dispatch.get("receipt_id"),
        "hub_url": HUB_URL,
        "founder_line": founder_line,
        "for_founder": {"show_this": founder_line},
    }
    if write_receipt:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = probe(write_receipt=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or row)
    return 0 if row.get("railway_ok") or row.get("last_plan_id") else 1


if __name__ == "__main__":
    raise SystemExit(main())

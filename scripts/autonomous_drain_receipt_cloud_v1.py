#!/usr/bin/env python3
"""Autonomous drain cycle receipts — cloud persist + optional Supabase + Mac mirror."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
MAC_CYCLE_DIR = SINA / "autonomous-drain-cycle-receipts"
LOG_NAME = "autonomous-drain-cycle-log-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_headless() -> bool:
    if str(os.environ.get("FBE_MODE", "")).lower() == "headless":
        return True
    if os.environ.get("FBE_HOME", "").strip() == "/app":
        return True
    return Path("/app/receipts").is_dir()


def cloud_cycle_dir() -> Path:
    if _is_headless():
        return Path("/app/receipts/cloud/autonomous-drain-cycles")
    return ROOT / "receipts" / "cloud" / "autonomous-drain-cycles"


def cloud_log_path() -> Path:
    return cloud_cycle_dir().parent / LOG_NAME


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _supabase_cfg() -> dict[str, str]:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    table = os.environ.get("AUTONOMOUS_DRAIN_SUPABASE_TABLE", "autonomous_drain_cycles").strip()
    return {"url": url, "key": key, "table": table or "autonomous_drain_cycles"}


def persist_cycle_receipt(doc: dict[str, Any]) -> dict[str, Any]:
    """Write per-cycle file + append log + optional Supabase upsert."""
    at = str(doc.get("at") or _now())
    safe_at = at.replace(":", "").replace("-", "")
    cycle_dir = cloud_cycle_dir()
    cycle_dir.mkdir(parents=True, exist_ok=True)
    path = cycle_dir / f"cycle-{safe_at}-v1.json"
    _write(path, doc)

    log_path = cloud_log_path()
    log = _read(log_path)
    cycles = list(log.get("cycles") or [])
    cycles.append(
        {
            "at": at,
            "path": str(path),
            "verdict": (doc.get("decision") or {}).get("verdict"),
            "trigger_source": doc.get("trigger_source"),
            "plan_id": (doc.get("belt") or {}).get("SHIP", {}).get("plan_id"),
            "prove_ok": (doc.get("belt") or {}).get("PROVE", {}).get("ok"),
            "ship_ok": (doc.get("belt") or {}).get("SHIP", {}).get("ok"),
        }
    )
    log_row = {
        "schema": "autonomous-drain-cycle-log-v1",
        "at": _now(),
        "cycles": cycles[-50:],
        "count": len(cycles),
    }
    _write(log_path, log_row)

    sb = _supabase_cfg()
    sb_result: dict[str, Any] = {"ok": False, "skipped": True}
    if sb["url"] and sb["key"]:
        sb_result = _supabase_upsert(doc, cfg=sb)

    return {
        "ok": True,
        "path": str(path),
        "log_path": str(log_path),
        "supabase": sb_result,
    }


def _supabase_upsert(doc: dict[str, Any], *, cfg: dict[str, str]) -> dict[str, Any]:
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}"
    row = {
        "cycle_at": doc.get("at"),
        "trigger_source": doc.get("trigger_source"),
        "verdict": (doc.get("decision") or {}).get("verdict"),
        "queue_head": doc.get("queue_head"),
        "prove_ok": (doc.get("belt") or {}).get("PROVE", {}).get("ok"),
        "ship_ok": (doc.get("belt") or {}).get("SHIP", {}).get("ok"),
        "plan_id": (doc.get("belt") or {}).get("SHIP", {}).get("plan_id"),
        "receipt": doc,
    }
    payload = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Prefer": "return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"ok": 200 <= resp.status < 300, "status": resp.status}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": exc.read().decode("utf-8", errors="replace")[:200]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def load_last_cycles(*, limit: int = 10) -> list[dict[str, Any]]:
    cycle_dir = cloud_cycle_dir()
    if not cycle_dir.is_dir():
        return []
    paths = sorted(cycle_dir.glob("cycle-*.json"))[-limit:]
    out: list[dict[str, Any]] = []
    for p in paths:
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return out


def observer_payload(*, limit: int = 10) -> dict[str, Any]:
    from fbe.lib.cloud_drain_queue_v1 import read_head  # noqa: WPS433

    head = read_head()
    cycles = load_last_cycles(limit=limit)
    ramp_path = cloud_cycle_dir().parent / "autonomous-drain-ramp-state-v1.json"
    ramp = _read(ramp_path) if ramp_path.is_file() else _read(SINA / "autonomous-drain-ramp-state-v1.json")
    return {
        "schema": "autonomous-drain-observer-v1",
        "at": _now(),
        "ok": True,
        "queue_head": head.get("cloud_drain_head"),
        "last_completed": head.get("cloud_drain_last_completed"),
        "ramp": ramp,
        "cycles": [
            {
                "at": c.get("at"),
                "trigger_source": c.get("trigger_source"),
                "verdict": (c.get("decision") or {}).get("verdict"),
                "prove": (c.get("belt") or {}).get("PROVE"),
                "ship": (c.get("belt") or {}).get("SHIP"),
            }
            for c in cycles
        ],
    }


def mirror_cycles_to_mac(*, limit: int = 20) -> dict[str, Any]:
    """Pull cloud cycle files into ~/.sina when Mac is online."""
    MAC_CYCLE_DIR.mkdir(parents=True, exist_ok=True)
    mirrored = 0
    for doc in load_last_cycles(limit=limit):
        at = str(doc.get("at") or _now())
        safe_at = at.replace(":", "").replace("-", "")
        dest = MAC_CYCLE_DIR / f"cycle-{safe_at}-v1.json"
        _write(dest, doc)
        mirrored += 1
    return {"ok": True, "mirrored": mirrored, "mac_dir": str(MAC_CYCLE_DIR)}


def observer_html(*, limit: int = 10) -> str:
    payload = observer_payload(limit=limit)
    rows = []
    for c in payload.get("cycles") or []:
        prove = c.get("prove") or {}
        ship = c.get("ship") or {}
        rows.append(
            f"<tr><td>{c.get('at','')}</td><td>{c.get('trigger_source','')}</td>"
            f"<td>{payload.get('queue_head','')}</td>"
            f"<td class=\"{'pass' if prove.get('ok') else 'fail'}\">{'PASS' if prove.get('ok') else 'FAIL'}</td>"
            f"<td class=\"{'pass' if ship.get('ok') else 'fail'}\">{'PASS' if ship.get('ok') else 'FAIL'}</td>"
            f"<td class=\"{'pass' if c.get('verdict')=='approved' else 'halt'}\">{c.get('verdict','')}</td></tr>"
        )
    body_rows = "\n".join(rows) or "<tr><td colspan=6>No cycles yet</td></tr>"
    ramp = payload.get("ramp") or {}
    return f"""<!DOCTYPE html>
<html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>SourceA · Autonomous Drain</title>
<style>
body{{font-family:system-ui;background:#0b1220;color:#e8eef8;margin:0;padding:16px}}
.card{{max-width:720px;margin:0 auto;background:#141e33;border:1px solid #243352;border-radius:12px;padding:20px}}
h1{{font-size:1.2rem;margin:0 0 8px}} .muted{{color:#8fa3bf;font-size:.85rem}}
table{{width:100%;border-collapse:collapse;margin-top:16px;font-size:.8rem}}
th,td{{padding:8px;border-bottom:1px solid #243352;text-align:left}}
.pass{{color:#3dd68c}} .fail,.halt{{color:#f87171}}
</style></head><body><main class=card>
<h1>Autonomous drain observer</h1>
<p class=muted>head {payload.get('queue_head','—')} · ramp {ramp.get('consecutive_green',0)}/10 · {payload.get('at')}</p>
<table><thead><tr><th>At</th><th>Trigger</th><th>Queue</th><th>PROVE</th><th>SHIP</th><th>Verdict</th></tr></thead>
<tbody>{body_rows}</tbody></table>
</main></body></html>"""

#!/usr/bin/env python3
"""Hub ecosystem slice — Mac Health grade · pressure · M111 · cloud factories (M111 wave 1)."""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "hub-ecosystem-slice-v1.json"
LIVE_PULSE = SINA / "mac-health" / "live-pulse-v1.json"
H1_BOOT = SINA / "worker-hub-boot-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _fetch_json(url: str, *, timeout: float = 3.0) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {}


def _mac_health_grade() -> dict[str, Any]:
    live = _read(LIVE_PULSE)
    if not live.get("ok"):
        live = _fetch_json("http://127.0.0.1:13024/api/mac-health/live", timeout=2.0)
    health = _fetch_json("http://127.0.0.1:13024/health", timeout=2.0)
    grade = live.get("grade") or live.get("body_mood") or "unknown"
    score = live.get("score")
    status = live.get("live_status") or "OFFLINE"
    prevention = live.get("prevention") if isinstance(live.get("prevention"), dict) else {}
    return {
        "live": status == "LIVE",
        "live_status": status,
        "health_grade": grade,
        "score": score,
        "health": prevention.get("health"),
        "modes": prevention.get("modes") or [],
        "ui_mode": (health.get("ui_contract") or {}).get("ui_mode"),
        "relieve_url": "http://127.0.0.1:13024/",
        "relieve_action": "POST /api/mac-health {\"action\":\"cpu_cool_down\"}",
    }


def _pressure_row() -> dict[str, Any]:
    try:
        from ecosystem_pressure_v1 import write_snapshot  # noqa: WPS433

        return write_snapshot()
    except Exception:
        return _read(SINA / "ecosystem-pressure-v1.json")


def _cloud_factory_heartbeat() -> dict[str, Any]:
    fem = _read(ROOT / "data" / "founder-execution-model-v1.json")
    ids = (fem.get("cloud_role") or {}).get("main_cloud_factories") or []
    receipt = _read(SINA / "cloud-factories-online-only-receipt-v1.json")
    fbe_url = receipt.get("fbe_public_url")
    rows: list[dict[str, Any]] = []
    for fid in ids:
        row: dict[str, Any] = {"id": fid, "online": None, "note": "cloud receipt pending"}
        if fid == "fbe_railway" and fbe_url:
            row["online"] = str(fbe_url).startswith("https://")
            row["url"] = fbe_url[:80]
        rows.append(row)
    return {
        "ok": bool(receipt.get("ok")),
        "line": receipt.get("cloud_factories_online_line"),
        "passed": receipt.get("passed"),
        "total": receipt.get("total"),
        "factories": rows,
    }


def _mandatory_next(hub_boot: dict | None = None) -> dict[str, Any]:
    boot = hub_boot or _read(H1_BOOT)
    m111 = _read(SINA / "ecosystem-111-pulse-receipt-v1.json")
    surfaces = _read(SINA / "agent-live-surfaces-v1.json")
    head = m111.get("head_id") or surfaces.get("ecosystem_mac_health_111_head")
    line = m111.get("line") or surfaces.get("ecosystem_mac_health_111_line")
    p0 = boot.get("p0_next_action") or boot.get("p0_title") or ""
    if head and line:
        return {"source": "m111", "id": head, "line": line, "action": f"WORK {head}"}
    if p0:
        return {"source": "hub_p0", "line": str(p0)[:160]}
    return {"source": "none", "line": "Hub glance — pick on FORM or relieve Mac pressure"}


def hub_slice(*, write_receipt: bool = True, hub_boot: dict | None = None) -> dict[str, Any]:
    health = _mac_health_grade()
    pressure = _pressure_row()
    cloud = _cloud_factory_heartbeat()
    m111 = _read(SINA / "ecosystem-111-pulse-receipt-v1.json")
    mandatory = _mandatory_next(hub_boot)

    row = {
        "schema": "hub-ecosystem-slice-v1",
        "at": _now(),
        "ok": True,
        "health_grade": health.get("health_grade"),
        "health_live_status": health.get("live_status"),
        "health_score": health.get("score"),
        "health_strip": {
            "grade": health.get("health_grade"),
            "score": health.get("score"),
            "live_status": health.get("live_status"),
            "relieve_url": health.get("relieve_url"),
            "modes": health.get("modes"),
        },
        "pressure_badge": pressure.get("badge"),
        "pressure": pressure,
        "cloud_factory_heartbeat": cloud,
        "m111_line": m111.get("line"),
        "m111_head": m111.get("head_id"),
        "m111_progress": m111.get("progress"),
        "mandatory_next": mandatory,
        "form_primary": True,
        "form_note": "Human fork on FORM_OFFICIAL — not chat A/B/C",
        "routing_panel_optional": True,
        "routing_panel_url": "http://127.0.0.1:8780/",
        "mac_health_url": "http://127.0.0.1:13024/",
        "founder_glance_law": "Hub home · Mac Health strip · pressure badge · cloud heartbeat",
    }

    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        badge = SINA / "hub-health-badge-v1.json"
        badge.write_text(
            json.dumps(
                {
                    "schema": "hub-health-badge-v1",
                    "at": row["at"],
                    "health_grade": row["health_grade"],
                    "pressure_badge": row["pressure_badge"],
                    "relieve_url": health.get("relieve_url"),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return row


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = hub_slice()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("health_grade"), row.get("pressure_badge"), row.get("m111_line"))

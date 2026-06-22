#!/usr/bin/env python3
"""Forge v0.2 status + implement index — cloud volume aggregate (Architecture A)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FORGE_DIR = "receipts/forge_v0.2"
INDEX_REL = f"{FORGE_DIR}/implement_index.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _top_20_ids(*, root: Path) -> list[str]:
    top_doc = _read_json(root / FORGE_DIR / "forge_v0.2_top.json")
    rows = top_doc.get("top_20") or top_doc.get("top_20_ranked") or []
    return [str(r.get("id") or "") for r in rows if r.get("id")]


def _scan_implement_receipts(*, root: Path) -> list[dict[str, Any]]:
    impl_dir = root / "receipts" / "cloud-implement"
    out: list[dict[str, Any]] = []
    if not impl_dir.is_dir():
        return out
    for path in impl_dir.glob("*.json"):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if row.get("status") != "PASS" or row.get("implement_mode") != "real":
            continue
        out.append(
            {
                "plan_id": str(row.get("plan_id") or path.stem),
                "workstream": row.get("workstream"),
                "competitor": row.get("competitor"),
                "preview_url": row.get("preview_url"),
                "at": row.get("at"),
                "implement_mode": row.get("implement_mode"),
                "status": row.get("status"),
            }
        )
    out.sort(key=lambda r: str(r.get("at") or ""), reverse=True)
    return out


def write_implement_index(*, root: Path | None = None) -> dict[str, Any]:
    """Rewrite implement_index.json from cloud-implement PASS receipts."""
    base = root or ROOT
    entries = _scan_implement_receipts(root=base)
    doc = {
        "schema": "forge-v02-implement-index-v1",
        "at": _now(),
        "architecture": "A",
        "count": len(entries),
        "entries": entries,
    }
    _write_json(base / INDEX_REL, doc)
    return doc


def build_forge_v02_status(*, root: Path | None = None) -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from forge_v02_implement_v1 import already_implemented_ids, is_real_shippable_plan  # noqa: WPS433

    base = root or ROOT
    top_ids = _top_20_ids(root=base)
    done = already_implemented_ids(root=base)
    top_real = [pid for pid in top_ids if pid in done]
    pending = [pid for pid in top_ids if pid not in done and is_real_shippable_plan(pid, root=base)]
    entries = _scan_implement_receipts(root=base)
    health = _read_json(base / FORGE_DIR / "data_health.json")
    overlay = _read_json(base / FORGE_DIR / "scoring_overlay.json")
    run_doc = _read_json(base / FORGE_DIR / "forge_v0.2_run.json")
    funnel = run_doc.get("funnel") if isinstance(run_doc.get("funnel"), dict) else {}
    cloud_remaining = int(funnel.get("cloudShippableRemaining") or 0)
    mac_excluded = int(funnel.get("macControlExcluded") or len(run_doc.get("dropped_mac_control_ids") or []))
    last_at = entries[0].get("at") if entries else None
    top_pass = len(top_real)
    ship_total = len(top_ids)
    overlay_count = len(overlay.get("already_implemented_plan_ids") or done)
    cloud_queue_complete = cloud_remaining == 0 and len(pending) == 0
    if cloud_queue_complete:
        telemetry = f"Forge cloud queue complete · {overlay_count} total shipped · {mac_excluded} mac observe-only excluded"
    else:
        telemetry = (
            f"Forge drain: {top_pass}/{ship_total or 20} cloud top real PASS · "
            f"{cloud_remaining} cloud pending · {overlay_count} total shipped"
        )
    return {
        "ok": True,
        "schema": "forge-v02-status-v1",
        "at": _now(),
        "architecture": "A",
        "top_20_total": ship_total,
        "top_20_real_pass": top_pass,
        "top_20_pending": pending,
        "cloud_shippable_remaining": cloud_remaining,
        "mac_control_excluded": mac_excluded,
        "cloud_queue_complete": cloud_queue_complete,
        "overlay_count": overlay_count,
        "total_real_shipped": len(entries),
        "fetch_source": health.get("fetch_source"),
        "data_health_at": health.get("at"),
        "last_implement_at": last_at,
        "telemetry_line": telemetry,
        "for_founder": {"show_this": telemetry},
        "urls": {
            "implement_index": "/receipts/forge_v0.2/implement_index.json",
            "forge_top": "/receipts/forge_v0.2/forge_v0.2_top.json",
            "data_health": "/receipts/forge_v0.2/data_health.json",
            "mac_control_queue": "/receipts/forge_v0.2/forge_v0.2_run.json",
        },
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-index", action="store_true")
    args = ap.parse_args()
    if args.write_index:
        row = write_implement_index()
    else:
        row = build_forge_v02_status()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("telemetry_line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

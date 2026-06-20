#!/usr/bin/env python3
"""FBE Mono bridge — secondary RESULT mirror (SourceA side only)."""
from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "fbe-mono-bridge-receipt-v1.json"
INBOX = ROOT / "cloud" / "sync-inbox" / "fbe_bay_events.jsonl"
MAP_PATH = ROOT / "data" / "fbe_cloud_workspace_map_v1.json"
FARM_URL = "https://sinaai-cloud-farm-production.up.railway.app"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _farm_ping(farm: str) -> str:
    try:
        with urllib.request.urlopen(f"{farm.rstrip('/')}/health", timeout=5) as resp:
            return "reachable" if resp.status == 200 else "unhealthy"
    except Exception:
        return "unreachable"


def mirror_bay(*, bay_slug: str, template_id: str = "web-product-factory-v1") -> dict:
    m = _read_json(MAP_PATH)
    farm = (m.get("mono_mirror") or {}).get("farm_url") or FARM_URL
    result = {
        "schema": "fbe-mono-result-v1",
        "at": _now(),
        "bay_slug": bay_slug,
        "template_id": template_id,
        "line": "refinery",
        "wave": "W2",
        "deliveryMode": "prove_only",
    }
    INBOX.parent.mkdir(parents=True, exist_ok=True)
    with INBOX.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, separators=(",", ":")) + "\n")

    farm_status = _farm_ping(farm)
    row = {
        "schema": "fbe-mono-bridge-receipt-v1",
        "ok": True,
        "at": _now(),
        "bay_slug": bay_slug,
        "template_id": template_id,
        "inbox": str(INBOX.relative_to(ROOT)),
        "farm_url": farm,
        "farm_status": farm_status,
        "note": "Secondary mirror — primary FBE runner owns execution",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def mirror_full_job(
    *,
    bay_slug: str,
    template_id: str = "web-product-factory-v1",
    tier_achieved: str | None = None,
) -> dict:
    m = _read_json(MAP_PATH)
    farm = (m.get("mono_mirror") or {}).get("farm_url") or FARM_URL
    fed = _read_json(ROOT / "receipts" / "federated-run-v1.json")
    assembly = (fed.get("lines") or {}).get("assembly") or {}
    result = {
        "schema": "fbe-mono-result-v1",
        "at": _now(),
        "event": "full_job_complete",
        "bay_slug": bay_slug,
        "template_id": template_id,
        "line": "full_job",
        "wave": "W3",
        "deliveryMode": "prove_only",
        "tier_achieved": tier_achieved,
        "lines": {"assembly": assembly},
    }
    INBOX.parent.mkdir(parents=True, exist_ok=True)
    with INBOX.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, separators=(",", ":")) + "\n")

    farm_status = _farm_ping(farm)
    row = {
        "schema": "fbe-mono-bridge-receipt-v1",
        "ok": True,
        "at": _now(),
        "bay_slug": bay_slug,
        "template_id": template_id,
        "event": "full_job_complete",
        "inbox": str(INBOX.relative_to(ROOT)),
        "farm_url": farm,
        "farm_status": farm_status,
        "tier_achieved": tier_achieved,
        "note": "W3 full job RESULT mirror",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="sample-bay")
    ap.add_argument("--template-id", default="web-product-factory-v1")
    ap.add_argument("--full-job", action="store_true")
    ap.add_argument("--tier-achieved", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.full_job:
        row = mirror_full_job(
            bay_slug=args.bay,
            template_id=args.template_id,
            tier_achieved=args.tier_achieved or None,
        )
    else:
        row = mirror_bay(bay_slug=args.bay, template_id=args.template_id)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

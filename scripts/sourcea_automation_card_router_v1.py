#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "sourcea-automation-catalog-v1.json"
RECEIPT_DIR = ROOT / "receipts" / "cloud" / "kaizen"


CARD_SOURCES: dict[str, dict[str, Any]] = {
    "daily-issue-triage": {
        "focus": "issue intake and owner routing",
        "sources": [
            "data/agent-filing-registry-v1.json",
            "data/agent-filing-registry-unification-batch-v1.json",
        ],
    },
    "manual-integrator-arbitration": {
        "focus": "integrator ownership and arbitration",
        "sources": [
            "data/worker-cost-tier-queue-v1.json",
            "data/noetfield-copilot-runtime-v1.json",
        ],
    },
    "hourly-integrator-sync-audit": {
        "focus": "integrator coordination audit",
        "sources": [
            "data/worker-cost-tier-queue-v1.json",
            "data/noetfield-copilot-runtime-v1.json",
            "data/integration-leverage-registry-v1.json",
        ],
    },
    "manual-bug-triage-root-cause": {
        "focus": "bug triage and root cause",
        "sources": [
            "data/cloud-auto-runtime-blocker-registry-v1.json",
            "data/trigger-registry-v1.json",
            "data/witnessbc-proof-lab-v1.json",
        ],
    },
    "manual-implementation-plan": {
        "focus": "implementation planning from current live SSOTs",
        "sources": [
            "data/sourcea-living-brain-autorun-master-plan-v1.json",
            "data/sourcea-brain-registry-inventory-v1.json",
        ],
    },
    "weekly-workflow-effectiveness": {
        "focus": "workflow portfolio effectiveness",
        "sources": [
            "data/sourcea-automation-catalog-v1.json",
            ".github/workflows/sourcea-automation-surface-health.yml",
            "data/trigger-registry-v1.json",
        ],
    },
    "manual-commercial-unblock": {
        "focus": "commercial unblock and release readiness",
        "sources": [
            "data/sourcea-governance-ssot-registry-v1.json",
            "data/sourcea-brain-registry-inventory-v1.json",
        ],
    },
}


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def catalog_entry(catalog: dict[str, Any], card_id: str) -> dict[str, Any]:
    for item in catalog.get("catalog", []):
        if item.get("id") == card_id:
            return item
    raise SystemExit(f"unknown automation card: {card_id}")


def write_receipt(card_id: str, payload: dict[str, Any]) -> Path:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPT_DIR / f"kaizen-automation-card-{card_id}-latest-v1.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    catalog = load_catalog()
    entry = catalog_entry(catalog, args.card)
    card_meta = CARD_SOURCES.get(args.card)
    if not card_meta:
        raise SystemExit(f"no router mapping for automation card: {args.card}")

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = {
        "schema": "sourcea-automation-card-router-v1",
        "card_id": args.card,
        "title": entry.get("title"),
        "cadence": entry.get("cadence"),
        "kind": entry.get("kind"),
        "status": entry.get("status"),
        "focus": card_meta["focus"],
        "sources": card_meta["sources"],
        "workflow_hint": entry.get("workflow_hint"),
        "target": entry.get("sourcea_target"),
        "checked_at": now,
        "ok": True,
    }

    if args.write_receipt:
        receipt_path = write_receipt(args.card, payload)
        payload["receipt_path"] = str(receipt_path.relative_to(ROOT))

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{args.card}: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

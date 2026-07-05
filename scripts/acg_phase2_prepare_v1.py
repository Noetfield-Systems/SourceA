#!/usr/bin/env python3
"""Prepare Phase 2 audit instance artifacts from ACG templates (pre-reply staging)."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECEIPTS = ROOT / "receipts" / "acg"
INSTANCES = ROOT / "data" / "acg-intake-instances"

PHASE2_TEMPLATES = [
    "agentic-cost-governance-tool-inventory-v1.json",
    "agentic-cost-governance-api-inventory-v1.json",
    "agentic-cost-governance-spend-surface-map-v1.json",
    "agentic-cost-governance-leakage-checklist-v1.json",
    "agentic-cost-governance-escalation-risk-v1.json",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_instance(audit_id: str) -> dict[str, Any] | None:
    path = INSTANCES / f"{audit_id}-v1.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_prepare(args: argparse.Namespace) -> dict[str, Any]:
    audit_id = args.audit_id.strip()
    inst = _load_instance(audit_id)
    if not inst:
        return {"ok": False, "error": "instance_not_found", "audit_id": audit_id}

    client = inst.get("client") or {}
    client_name = client.get("name") or "[Company name]"
    out_dir = RECEIPTS / audit_id / "phase2"
    out_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    for name in PHASE2_TEMPLATES:
        src = DATA / name
        if not src.is_file():
            return {"ok": False, "error": "template_missing", "path": str(src)}
        doc = copy.deepcopy(json.loads(src.read_text(encoding="utf-8")))
        doc["template"] = False
        doc["audit_id"] = audit_id
        doc["client_name"] = client_name
        doc["prepared_at"] = _now()
        doc["phase"] = "audit_in_progress"
        doc["status"] = "awaiting_client_reply"
        out_name = name.replace("-v1.json", f"-{audit_id}-instance-v1.json")
        out_path = out_dir / out_name
        out_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        written.append(str(out_path.relative_to(ROOT)))

    manifest = {
        "schema": "acg-phase2-prepare-v1",
        "version": "1.0.0",
        "at": _now(),
        "audit_id": audit_id,
        "client_name": client_name,
        "artifacts": written,
        "next_on_reply": [
            f"python3 scripts/agentic_cost_governance_intake_v1.py receipt --audit-id {audit_id} --json",
            "Populate phase2 instance JSON with client-supplied inventory data",
            "python3 scripts/sourcea_revenue_engine_crm_v1.py touch --id RE-ACG-001 --stage audit_discovery_scheduled --json",
        ],
    }
    manifest_path = out_dir / "manifest-v1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "audit_id": audit_id,
        "phase2_dir": str(out_dir.relative_to(ROOT)),
        "artifact_count": len(written),
        "manifest": str(manifest_path.relative_to(ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="ACG Phase 2 audit instance prepare v1")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare", help="Copy templates to receipts/acg/<audit_id>/phase2/")
    p.add_argument("--audit-id", required=True)
    p.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = cmd_prepare(args)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())

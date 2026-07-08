#!/usr/bin/env python3
"""Agentic Cost Governance intake — audit_id generation and receipt storage."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "data" / "agentic-cost-governance-intake-v1.json"
SINA = Path.home() / ".sina"
RECEIPTS_ACG = ROOT / "receipts" / "acg"
INSTANCES = ROOT / "data" / "acg-intake-instances"

PHASES = {
    "intake_received": {"order": 1, "label": "Phase 1: Intake"},
    "audit_in_progress": {"order": 2, "label": "Phase 2: Audit"},
    "policy_design": {"order": 3, "label": "Phase 3: Firewall policy"},
    "pilot_active": {"order": 4, "label": "Phase 4: 30-day pilot"},
    "final_report": {"order": 5, "label": "Phase 5: Final report"},
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def _load_template() -> dict[str, Any]:
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def _mirror_path(audit_id: str) -> Path:
    return SINA / f"acg-intake-{audit_id}-v1.json"


def _repo_receipt_path(audit_id: str) -> Path:
    return RECEIPTS_ACG / audit_id / "intake-v1.json"


def _instance_path(audit_id: str) -> Path:
    return INSTANCES / f"{audit_id}-v1.json"


def _next_audit_id() -> str:
    INSTANCES.mkdir(parents=True, exist_ok=True)
    prefix = f"ACG-{_today()}-"
    existing = sorted(INSTANCES.glob(f"{prefix}*.json"))
    if not existing:
        return f"{prefix}001"
    last = existing[-1].stem.split("-")[-1]
    try:
        n = int(last) + 1
    except ValueError:
        n = 1
    return f"{prefix}{n:03d}"


def _write_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def cmd_init(_: argparse.Namespace) -> dict[str, Any]:
    if not TEMPLATE.is_file():
        return {"ok": False, "error": "template_missing", "path": str(TEMPLATE)}
    INSTANCES.mkdir(parents=True, exist_ok=True)
    RECEIPTS_ACG.mkdir(parents=True, exist_ok=True)
    return {"ok": True, "template": str(TEMPLATE), "instances_dir": str(INSTANCES)}


def cmd_create(args: argparse.Namespace) -> dict[str, Any]:
    doc = copy.deepcopy(_load_template())
    doc["template"] = False
    audit_id = args.audit_id.strip() if args.audit_id else _next_audit_id()
    doc["audit_id"] = audit_id
    doc["created_at"] = _now()
    doc["audit_status"] = "intake_received"
    doc["client"]["name"] = args.name.strip()
    if args.industry:
        doc["client"]["industry"] = args.industry.strip()
    if args.team_size:
        doc["client"]["team_size"] = args.team_size.strip()
    if args.contact:
        doc["client"]["contact_email"] = args.contact.strip()
    if args.location:
        doc["client"]["location"] = args.location.strip()
    if args.notes:
        doc["notes"] = args.notes.strip()
    _write_json(_instance_path(audit_id), doc)
    return {"ok": True, "audit_id": audit_id, "path": str(_instance_path(audit_id)), "phase": "intake_received"}


def cmd_receipt(args: argparse.Namespace) -> dict[str, Any]:
    audit_id = args.audit_id.strip()
    inst = _instance_path(audit_id)
    if not inst.is_file():
        return {"ok": False, "error": "instance_not_found", "audit_id": audit_id, "hint": "run create first"}
    doc = json.loads(inst.read_text(encoding="utf-8"))
    doc["receipt_at"] = _now()
    doc["audit_status"] = doc.get("audit_status") or "intake_received"
    repo_path = _repo_receipt_path(audit_id)
    mirror_path = _mirror_path(audit_id)
    _write_json(repo_path, doc)
    _write_json(mirror_path, doc)
    _write_json(inst, doc)
    return {
        "ok": True,
        "audit_id": audit_id,
        "repo_receipt": str(repo_path),
        "mirror_receipt": str(mirror_path),
        "phase": doc.get("audit_status"),
    }


def cmd_status(args: argparse.Namespace) -> dict[str, Any]:
    audit_id = args.audit_id.strip()
    for path in (_instance_path(audit_id), _mirror_path(audit_id), _repo_receipt_path(audit_id)):
        if path.is_file():
            doc = json.loads(path.read_text(encoding="utf-8"))
            status = doc.get("audit_status") or "intake_received"
            phase = PHASES.get(status, {"order": 0, "label": status})
            return {
                "ok": True,
                "audit_id": audit_id,
                "audit_status": status,
                "phase": phase["label"],
                "phase_order": phase["order"],
                "path": str(path),
                "client_name": (doc.get("client") or {}).get("name"),
            }
    return {"ok": False, "error": "not_found", "audit_id": audit_id}


def main() -> int:
    parser = argparse.ArgumentParser(description="Agentic Cost Governance intake v1")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Verify template and create dirs")
    p_init.add_argument("--json", action="store_true")

    p_create = sub.add_parser("create", help="Create intake instance")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--contact", default="")
    p_create.add_argument("--industry", default="")
    p_create.add_argument("--team-size", default="")
    p_create.add_argument("--location", default="")
    p_create.add_argument("--audit-id", default="")
    p_create.add_argument("--notes", default="")
    p_create.add_argument("--json", action="store_true")

    p_receipt = sub.add_parser("receipt", help="Write intake receipt to disk")
    p_receipt.add_argument("--audit-id", required=True)
    p_receipt.add_argument("--json", action="store_true")

    p_status = sub.add_parser("status", help="Return workflow phase for audit_id")
    p_status.add_argument("--audit-id", required=True)
    p_status.add_argument("--json", action="store_true")

    args = parser.parse_args()
    handlers = {
        "init": cmd_init,
        "create": cmd_create,
        "receipt": cmd_receipt,
        "status": cmd_status,
    }
    result = handlers[args.cmd](args)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())

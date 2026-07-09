#!/usr/bin/env python3
"""ACG founder personalize — one command to fill prospect instance + intake + CRM."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INSTANCE_MD = ROOT / "docs/commercial/ACG_FIRST_PROSPECT_INSTANCE_v1.md"
INTAKE = ROOT / "data/acg-intake-instances/ACG-20260705-001-v1.json"
CRM = Path.home() / ".sina/sourcea-revenue-engine-crm-v1.json"
AUDIT_ID = "ACG-20260705-001"
CRM_ID = "RE-ACG-001"

REPLACEMENTS = {
    "FOUNDER_FILL_COMPANY": "company",
    "FOUNDER_FILL_NAME": "name",
    "FOUNDER_FILL_TITLE": "title",
    "FOUNDER_FILL_EMAIL": "email",
    "FOUNDER_FILL_TEAM_SIZE": "team_size",
}


def _apply_md(text: str, values: dict[str, str]) -> str:
    out = text
    for placeholder, key in REPLACEMENTS.items():
        out = out.replace(placeholder, values[key])
    return out


def cmd_apply(args: argparse.Namespace) -> dict[str, Any]:
    values = {
        "company": args.company.strip(),
        "name": args.name.strip(),
        "title": args.title.strip(),
        "email": args.email.strip(),
        "team_size": args.team_size.strip(),
    }
    if any(not v for v in values.values()):
        return {"ok": False, "error": "all_fields_required"}

    md = INSTANCE_MD.read_text(encoding="utf-8")
    INSTANCE_MD.write_text(_apply_md(md, values), encoding="utf-8")

    intake = json.loads(INTAKE.read_text(encoding="utf-8"))
    intake["client"]["name"] = values["company"]
    intake["client"]["contact_email"] = values["email"]
    intake["client"]["team_size"] = values["team_size"]
    if args.industry:
        intake["client"]["industry"] = args.industry.strip()
    INTAKE.write_text(json.dumps(intake, indent=2) + "\n", encoding="utf-8")

    crm = json.loads(CRM.read_text(encoding="utf-8"))
    for p in crm.get("prospects") or []:
        if p.get("id") == CRM_ID:
            p["name"] = values["name"]
            p["company"] = values["company"]
            p["audit_id"] = AUDIT_ID
            break
    CRM.write_text(json.dumps(crm, indent=2) + "\n", encoding="utf-8")

    remaining = re.findall(r"FOUNDER_FILL_\w+", INSTANCE_MD.read_text(encoding="utf-8"))
    return {
        "ok": len(remaining) == 0,
        "audit_id": AUDIT_ID,
        "crm_id": CRM_ID,
        "instance_path": str(INSTANCE_MD),
        "intake_path": str(INTAKE),
        "placeholders_remaining": remaining,
        "next": "Sign ACG_FOUNDER_REVIEW_GATE_v1.md then run acg_founder_send_readiness_v1.py check",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="ACG founder personalize v1")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("apply", help="Fill prospect instance, intake JSON, and CRM row")
    p.add_argument("--company", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--email", required=True)
    p.add_argument("--team-size", required=True)
    p.add_argument("--industry", default="SaaS")
    p.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = cmd_apply(args)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())

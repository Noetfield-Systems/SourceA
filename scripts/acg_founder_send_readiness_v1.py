#!/usr/bin/env python3
"""ACG founder send readiness — validate personalization + gate before outbound."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INSTANCE = ROOT / "docs/commercial/ACG_FIRST_PROSPECT_INSTANCE_v1.md"
GATE = ROOT / "docs/commercial/ACG_FOUNDER_REVIEW_GATE_v1.md"
CRM = Path.home() / ".sina/sourcea-revenue-engine-crm-v1.json"
INTAKE_DIR = ROOT / "data/acg-intake-instances"
PLACEHOLDER = re.compile(r"FOUNDER_FILL_|^\[Company name\]|^\[First name\]", re.I)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def cmd_check(_: argparse.Namespace) -> dict[str, Any]:
    issues: list[str] = []
    instance = _read(INSTANCE)
    gate = _read(GATE)

    if PLACEHOLDER.search(instance):
        issues.append("instance_has_placeholders: replace FOUNDER_FILL_* in ACG_FIRST_PROSPECT_INSTANCE_v1.md")

    if re.search(r"Send authorized\s*\|\s*YES\s*/\s*NO", gate):
        issues.append("review_gate_unsigned: set Send authorized YES in ACG_FOUNDER_REVIEW_GATE_v1.md")
    elif not re.search(r"Send authorized:\s*YES\b", gate, re.I):
        issues.append("review_gate_unsigned: set Send authorized YES in ACG_FOUNDER_REVIEW_GATE_v1.md")

    if not CRM.is_file():
        issues.append("crm_missing: run sourcea_revenue_engine_crm_v1.py init")
    else:
        crm = json.loads(CRM.read_text(encoding="utf-8"))
        acg = [p for p in crm.get("prospects") or [] if p.get("id") == "RE-ACG-001"]
        if not acg:
            issues.append("crm_re_acg_001_missing")
        elif acg[0].get("stage") == "lead":
            issues.append("outreach_pending: CRM at lead — send email then touch outreach_sent")

    intakes = list(INTAKE_DIR.glob("ACG-*-v1.json")) if INTAKE_DIR.is_dir() else []
    if not intakes:
        issues.append("intake_instance_missing")

    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "send_ready": len(issues) == 0,
        "instance_path": str(INSTANCE),
        "gate_path": str(GATE),
        "intake_count": len(intakes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="ACG founder send readiness v1")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check", help="Validate founder send prerequisites")
    p.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = cmd_check(args)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate system_anatomy block in reports/locked-definitions-v1.json (NOETFIELD P2)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFINITIONS_PATH = ROOT / "reports" / "locked-definitions-v1.json"

REQUIRED_TERM_IDS = frozenset(
    {
        "BRAIN",
        "SPINE",
        "NERVES",
        "GATES",
        "MACHINES",
        "MISSION",
        "WORKFLOW",
        "CYCLE",
        "RECEIPT",
        "VERIFIED",
    }
)


def validate_anatomy(path: Path | None = None) -> dict[str, Any]:
    target = path or DEFINITIONS_PATH
    if not target.is_file():
        return {
            "ok": False,
            "path": str(target),
            "errors": ["definitions_file_missing"],
            "report_line": "anatomy_lint_fail · definitions file missing",
        }

    doc = json.loads(target.read_text(encoding="utf-8"))
    anatomy = doc.get("system_anatomy")
    errors: list[str] = []
    if not isinstance(anatomy, dict):
        errors.append("system_anatomy_block_missing")
        return {
            "ok": False,
            "path": str(target.relative_to(ROOT)),
            "errors": errors,
            "report_line": "anatomy_lint_fail · system_anatomy block missing",
        }

    terms = anatomy.get("terms")
    if not isinstance(terms, list) or not terms:
        errors.append("system_anatomy_terms_missing")
    else:
        seen: set[str] = set()
        for idx, row in enumerate(terms):
            if not isinstance(row, dict):
                errors.append(f"term_{idx}_not_object")
                continue
            term_id = str(row.get("id") or row.get("term") or "").upper()
            if not term_id:
                errors.append(f"term_{idx}_missing_id")
                continue
            if term_id in seen:
                errors.append(f"duplicate_term:{term_id}")
            seen.add(term_id)
            if not str(row.get("definition") or "").strip():
                errors.append(f"{term_id}_missing_definition")
            if not str(row.get("lives_where") or "").strip():
                errors.append(f"{term_id}_missing_lives_where")

        missing = sorted(REQUIRED_TERM_IDS - seen)
        if missing:
            errors.append(f"missing_required_terms:{','.join(missing)}")

    ok = not errors
    return {
        "schema": "locked-definitions-anatomy-lint-v1",
        "ok": ok,
        "path": str(target.relative_to(ROOT)),
        "required_term_count": len(REQUIRED_TERM_IDS),
        "errors": errors,
        "report_line": (
            "anatomy_lint_pass · all 10 terms locked"
            if ok
            else f"anatomy_lint_fail · {len(errors)} error(s)"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint system_anatomy in locked-definitions-v1.json")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--path", type=Path, default=DEFINITIONS_PATH)
    args = parser.parse_args()
    row = validate_anatomy(args.path)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())

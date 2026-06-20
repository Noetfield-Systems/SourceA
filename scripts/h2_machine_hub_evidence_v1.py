#!/usr/bin/env python3
"""Append SOURCEA-PRIORITY evidence row after H2 weekly machine bundle SHIP pass (sa-0824)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
PRIORITY = SOURCE_A / "brain-os" / "plan-registry" / "SOURCEA-PRIORITY.md"
BUNDLE_RECEIPT = Path.home() / ".sina/h2-machine-weekly-bundle-receipt-v1.json"
CROSSREF = "archive/attachments/2026-06-15/sa-0824-h2-weekly-ship-evidence-row_LOCKED_v1.md"
SA_MARKER = "sa-0824"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def weekly_bundle_ok() -> dict:
    if not BUNDLE_RECEIPT.is_file():
        return {"ok": False, "error": "missing_bundle_receipt"}
    try:
        row = json.loads(BUNDLE_RECEIPT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
    if row.get("schema") != "h2-machine-weekly-bundle-v1":
        return {"ok": False, "error": "bad_schema", "schema": row.get("schema")}
    if not row.get("ok"):
        return {"ok": False, "error": "bundle_not_ok", "at": row.get("at")}
    return {"ok": True, "at": row.get("at"), "reason": row.get("reason"), "cadence": row.get("cadence")}


def append_priority_h2_weekly_ship_evidence(*, dry_run: bool = False) -> dict:
    """Idempotent PRIORITY evidence row after weekly H2 machine hub SHIP pass."""
    bundle = weekly_bundle_ok()
    if not bundle.get("ok"):
        return {"ok": False, "appended": False, "reason": "bundle_not_ok", "bundle": bundle}

    if not PRIORITY.is_file():
        return {"ok": False, "error": "missing_priority", "bundle": bundle}

    text = PRIORITY.read_text(encoding="utf-8")
    row_marker = f"{SA_MARKER} Append H2 machine hub evidence row after weekly SHIP pass"
    if row_marker in text:
        return {"ok": True, "appended": False, "reason": "already_present", "bundle": bundle}

    at = str(bundle.get("at") or _now())[:10]
    row = (
        f"| {at} | {SA_MARKER} Append H2 machine hub evidence row after weekly SHIP pass | "
        f"{CROSSREF} · h2-machine-weekly-bundle-receipt ok · "
        f"validate-h2-weekly-ship-evidence-row-v1 PASS · bundle_at={bundle.get('at')} |\n"
    )
    if dry_run:
        return {"ok": True, "appended": False, "dry_run": True, "row": row.strip(), "bundle": bundle}

    anchor = "## Evidence log"
    if anchor in text:
        text = text.replace(anchor, anchor + "\n" + row, 1)
    else:
        text = text.rstrip() + "\n\n## Evidence log\n" + row
    PRIORITY.write_text(text, encoding="utf-8")
    return {"ok": True, "appended": True, "reason": "weekly_ship_pass", "bundle": bundle, "row": row.strip()}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="H2 weekly SHIP evidence row append")
    p.add_argument("--json", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    row = append_priority_h2_weekly_ship_evidence(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"H2-WEEKLY-EVIDENCE: appended={row.get('appended')} reason={row.get('reason')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Per-app UI upgrade ledger — read, validate, append upgrade entries.

Law: brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md
Index: data/ui-upgrade-ledgers-index-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "ui-upgrade-ledgers-index-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def load_index() -> dict:
    if not INDEX.is_file():
        raise SystemExit(f"FAIL: index missing — {INDEX}")
    return _read(INDEX)


def resolve_surface(surface_id: str) -> dict | None:
    for row in load_index().get("ledgers") or []:
        if row.get("surface_id") == surface_id:
            return row
    return None


def load_ledger(surface_id: str) -> dict:
    row = resolve_surface(surface_id)
    if not row:
        raise SystemExit(f"FAIL: unknown surface — {surface_id}")
    path = ROOT / row["ledger_json"]
    if not path.is_file():
        raise SystemExit(f"FAIL: ledger JSON missing — {path}")
    ledger = _read(path)
    if ledger.get("schema") != "ui-upgrade-ledger-v1":
        raise SystemExit(f"FAIL: bad schema — {ledger.get('schema')}")
    ledger["_paths"] = {
        "ledger_json": str(path),
        "ledger_md": str(ROOT / row["ledger_md"]),
        "ledger_md_exists": (ROOT / row["ledger_md"]).is_file(),
    }
    return ledger


def validate_all() -> dict:
    issues: list[str] = []
    rows: list[dict] = []
    for entry in load_index().get("ledgers") or []:
        sid = entry.get("surface_id", "?")
        json_path = ROOT / entry.get("ledger_json", "")
        md_path = ROOT / entry.get("ledger_md", "")
        row_issues: list[str] = []
        if not json_path.is_file():
            row_issues.append(f"missing_json:{json_path.name}")
        if not md_path.is_file():
            row_issues.append(f"missing_md:{md_path.name}")
        if json_path.is_file():
            try:
                led = _read(json_path)
                if led.get("schema") != "ui-upgrade-ledger-v1":
                    row_issues.append("bad_schema")
                if not led.get("frozen_inventory"):
                    row_issues.append("empty_frozen_inventory")
                if not led.get("upgrades"):
                    row_issues.append("no_upgrade_history")
            except Exception as exc:
                row_issues.append(f"json_parse:{exc}")
        issues.extend(f"{sid}:{x}" for x in row_issues)
        rows.append({"surface_id": sid, "ok": not row_issues, "issues": row_issues})
    ok = not issues
    return {
        "ok": ok,
        "issues": issues,
        "ledgers": rows,
        "count": len(rows),
        "line": f"UI-LEDGER · {sum(1 for r in rows if r['ok'])}/{len(rows)} apps · ok={'YES' if ok else 'NO'}",
    }


def show(surface_id: str) -> dict:
    ledger = load_ledger(surface_id)
    upgrades = ledger.get("upgrades") or []
    last = upgrades[-1] if upgrades else None
    return {
        "ok": True,
        "surface_id": surface_id,
        "label": ledger.get("label"),
        "repo": ledger.get("repo"),
        "url": ledger.get("url"),
        "ledger_md": ledger["_paths"]["ledger_md"],
        "ledger_json": ledger["_paths"]["ledger_json"],
        "frozen_inventory_count": len(ledger.get("frozen_inventory") or []),
        "app_checklist_count": len(ledger.get("app_checklist") or []),
        "upgrade_count": len(upgrades),
        "last_upgrade": last,
        "app_checklist": ledger.get("app_checklist"),
        "frozen_inventory": ledger.get("frozen_inventory"),
    }


def append_upgrade(surface_id: str, entry: dict) -> dict:
    ledger = load_ledger(surface_id)
    upgrades = ledger.get("upgrades") or []
    prefix = surface_id.upper().replace("_", "-")[:12]
    if not entry.get("upgrade_id"):
        n = len(upgrades)
        entry["upgrade_id"] = f"UP-{prefix}-{n:03d}"
    if not entry.get("saved_at"):
        entry["saved_at"] = _now()
    upgrades.append(entry)
    ledger["upgrades"] = upgrades
    ledger["saved_at"] = _now()
    path = Path(ledger["_paths"]["ledger_json"])
    _write(path, {k: v for k, v in ledger.items() if not k.startswith("_")})
    return {"ok": True, "upgrade_id": entry["upgrade_id"], "path": str(path)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Per-app UI upgrade ledger")
    ap.add_argument("--surface")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--append", metavar="JSON", help="Append upgrade entry JSON string")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.validate:
        row = validate_all()
    elif args.list:
        idx = load_index()
        row = {"ok": True, "ledgers": idx.get("ledgers")}
    elif args.append:
        if not args.surface:
            print("FAIL: --surface required for --append", file=sys.stderr)
            return 1
        entry = json.loads(args.append)
        row = append_upgrade(args.surface, entry)
    elif args.show or args.surface:
        if not args.surface:
            print("FAIL: --surface required", file=sys.stderr)
            return 1
        row = show(args.surface)
    else:
        row = validate_all()

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or json.dumps(row, indent=2))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())

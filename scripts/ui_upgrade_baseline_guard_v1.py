#!/usr/bin/env python3
"""UI upgrade baseline guard — block downgrades on controlled landing surfaces.

Law: brain-os/law/enforcement/SOURCEA_UI_UPGRADE_NO_DOWNGRADE_LOCKED_v1.md
SSOT: SourceA-landing/green-unified/data/ui-upgrade-baseline-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "SourceA-landing" / "green-unified" / "data" / "ui-upgrade-baseline-v1.json"
GREEN = ROOT / "SourceA-landing" / "green-unified"


def load_baseline() -> dict:
    if not BASELINE_PATH.is_file():
        raise SystemExit(f"FAIL: baseline missing — {BASELINE_PATH}")
    row = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    if row.get("schema") != "sourcea-ui-upgrade-baseline-v1":
        raise SystemExit(f"FAIL: bad schema — {row.get('schema')}")
    return row


def _rel_green(path: Path) -> str | None:
    try:
        path = path.resolve()
        green = GREEN.resolve()
        if path == green:
            return ""
        rel = path.relative_to(green)
        return str(rel).replace("\\", "/")
    except ValueError:
        return None


def is_controlled_ui_path(path: str | Path) -> bool:
    rel = _rel_green(Path(path))
    if rel is None:
        return False
    if not rel:
        return False
    suffix = Path(rel).suffix.lower()
    return suffix in {".html", ".css", ".js"} and not rel.startswith("reference/")


def check_file(rel: str, rules: dict, *, green: Path = GREEN) -> list[str]:
    fails: list[str] = []
    target = green / rel
    if not target.is_file():
        return [f"{rel}: missing file"]
    text = target.read_text(encoding="utf-8", errors="replace")
    for needle in rules.get("must_contain") or []:
        if needle not in text:
            fails.append(f"{rel}: missing `{needle}`")
    for token, minimum in (rules.get("min_count") or {}).items():
        count = text.count(token)
        if count < int(minimum):
            fails.append(f"{rel}: `{token}` count {count} < {minimum}")
    return fails


def check_path(path: str, baseline: dict | None = None) -> dict:
    baseline = baseline or load_baseline()
    rel = _rel_green(Path(path))
    if rel is None or not is_controlled_ui_path(path):
        return {
            "ok": True,
            "skipped": True,
            "reason": "not_controlled_ui",
            "path": str(Path(path).resolve()),
        }
    files = baseline.get("files") or {}
    if rel not in files:
        return {
            "ok": True,
            "skipped": True,
            "reason": "not_in_baseline",
            "rel": rel,
        }
    fails = check_file(rel, files[rel])
    return {
        "ok": not fails,
        "rel": rel,
        "baseline_version": baseline.get("version"),
        "failures": fails,
        "law": "SOURCEA_UI_UPGRADE_NO_DOWNGRADE_LOCKED_v1.md",
    }


def verify_all(baseline: dict | None = None) -> dict:
    baseline = baseline or load_baseline()
    files = baseline.get("files") or {}
    all_fails: list[str] = []
    for rel in sorted(files):
        all_fails.extend(check_file(rel, files[rel]))
    return {
        "ok": not all_fails,
        "baseline_version": baseline.get("version"),
        "file_count": len(files),
        "failures": all_fails,
        "law": "SOURCEA_UI_UPGRADE_NO_DOWNGRADE_LOCKED_v1.md",
    }


def print_baseline(baseline: dict | None = None) -> dict:
    baseline = baseline or load_baseline()
    files = sorted((baseline.get("files") or {}).keys())
    return {
        "ok": True,
        "schema": baseline.get("schema"),
        "version": baseline.get("version"),
        "at": baseline.get("at"),
        "root": str(GREEN),
        "files": files,
        "check_cmd": "python3 scripts/ui_upgrade_baseline_guard_v1.py check --path <file>",
        "verify_cmd": "bash scripts/validate-ui-upgrade-no-downgrade-v1.sh",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="UI upgrade baseline guard")
    ap.add_argument("cmd", choices=("baseline", "check", "verify-all", "is-controlled"))
    ap.add_argument("--path", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.cmd == "baseline":
        row = print_baseline()
    elif args.cmd == "is-controlled":
        row = {"ok": True, "controlled": is_controlled_ui_path(args.path), "path": args.path}
    elif args.cmd == "check":
        if not args.path:
            print("FAIL: --path required", file=sys.stderr)
            return 2
        row = check_path(args.path)
    else:
        row = verify_all()

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        if row.get("skipped"):
            print(f"SKIP: {row.get('reason')} — {row.get('rel') or row.get('path')}")
        elif row.get("ok"):
            if args.cmd == "baseline":
                print(f"baseline v{row.get('version')} · {len(row.get('files') or [])} files")
            elif args.cmd == "verify-all":
                print(f"OK: ui baseline v{row.get('baseline_version')} · {row.get('file_count')} files")
            else:
                print(f"OK: {row.get('rel')} · baseline v{row.get('baseline_version')}")
        else:
            print(f"FAIL: ui baseline v{row.get('baseline_version', '?')}")
            for f in row.get("failures") or []:
                print(f"  - {f}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

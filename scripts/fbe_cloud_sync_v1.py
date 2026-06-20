#!/usr/bin/env python3
"""FBE cloud sync — bay receipts only; never_sync_as_authority enforced."""
from __future__ import annotations

import argparse
import fnmatch
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
MAP_PATH = DATA / "fbe_cloud_workspace_map_v1.json"
RECEIPT_PATH = SINA / "fbe-cloud-sync-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _expand(rel: str) -> Path:
    p = Path(rel.replace("~", str(Path.home())))
    return p if p.is_absolute() else ROOT / p


def _blocked(rel: str, patterns: list[str]) -> bool:
    for pat in patterns:
        p = pat.replace("~", str(Path.home())).replace("**", "*")
        if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(str(ROOT / rel), p):
            return True
        base = pat.replace("**", "").rstrip("/")
        if base and rel.startswith(base):
            return True
    return False


def assert_push_allowed(bundle_id: str) -> None:
    m = _read_json(MAP_PATH)
    bundle = next((b for b in m.get("bundles") or [] if b.get("id") == bundle_id), None)
    if not bundle:
        return
    if bundle.get("read_only_cloud"):
        raise PermissionError(f"bundle {bundle_id} is read_only_cloud — cloud cannot author")
    never = m.get("never_sync_as_authority") or []
    for rel in never:
        if _blocked(bundle_id, [rel]):
            raise PermissionError(f"never_sync_as_authority blocks {bundle_id}")


def pull_bay_receipts(*, bay_slug: str = "sample-bay") -> dict:
    src = ROOT / "receipts" / "bays" / bay_slug
    files = list(src.glob("*.json")) if src.is_dir() else []
    row = {
        "schema": "fbe-cloud-sync-receipt-v1",
        "ok": True,
        "at": _now(),
        "action": "pull_bay_receipts",
        "bay_slug": bay_slug,
        "files": [str(f.relative_to(ROOT)) for f in files],
        "count": len(files),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def pull_assembly_receipts(*, bay_slug: str = "sample-bay") -> dict:
    assert_push_allowed("fbe_assembly_receipts")
    src = ROOT / "receipts" / "bays" / bay_slug / "assembly"
    files = list(src.rglob("*.json")) if src.is_dir() else []
    ledger = src / "ledger.jsonl"
    if ledger.is_file():
        files.append(ledger)
    row = {
        "schema": "fbe-cloud-sync-receipt-v1",
        "ok": True,
        "at": _now(),
        "action": "pull_assembly_receipts",
        "bay_slug": bay_slug,
        "files": [str(f.relative_to(ROOT)) for f in files],
        "count": len(files),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="sample-bay")
    ap.add_argument("--assembly", action="store_true", help="Also pull assembly receipts")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        assert_push_allowed("fbe_bay_receipts")
        row = pull_bay_receipts(bay_slug=args.bay)
        if args.assembly:
            pull_assembly_receipts(bay_slug=args.bay)
            row["assembly_pulled"] = True
    except PermissionError as exc:
        row = {"ok": False, "error": str(exc)}
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

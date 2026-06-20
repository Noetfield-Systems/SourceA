#!/usr/bin/env python3
"""FBE run receipt pack — buyer ZIP for full job."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_pack(*, bay_slug: str = "sample-bay") -> dict:
    pack_dir = ROOT / "receipts" / "packs" / bay_slug
    pack_dir.mkdir(parents=True, exist_ok=True)
    zip_path = pack_dir / "run-receipt-v1.zip"
    manifest: list[dict] = []

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        candidates = [
            ROOT / "receipts" / "federated-run-v1.json",
            SINA / "fbe-federated-receipt-v1.json",
            SINA / "fbe-run-job-receipt-v1.json",
            ROOT / "receipts" / "bays" / bay_slug / "ledger.jsonl",
            ROOT / "receipts" / "bays" / bay_slug / "assembly" / "ledger.jsonl",
        ]
        bay = ROOT / "receipts" / "bays" / bay_slug
        if bay.is_dir():
            for p in bay.rglob("*.json"):
                candidates.append(p)
        asm = bay / "assembly"
        if asm.is_dir():
            for p in asm.rglob("*.json"):
                candidates.append(p)

        seen: set[str] = set()
        for path in candidates:
            if not path.is_file():
                continue
            arc = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name
            if arc in seen:
                continue
            seen.add(arc)
            zf.write(path, arcname=arc)
            manifest.append({"path": arc, "sha256": _sha256_file(path)})

        zf.writestr(
            "manifest-v1.json",
            json.dumps({"schema": "fbe-run-receipt-manifest-v1", "at": _now(), "files": manifest}, indent=2),
        )

    row = {
        "schema": "fbe-run-receipt-pack-v1",
        "ok": True,
        "at": _now(),
        "bay_slug": bay_slug,
        "artifact_uri": str(zip_path.relative_to(ROOT)),
        "receipt_pack_uri": str(zip_path.relative_to(ROOT)),
        "file_count": len(manifest),
        "manifest": manifest,
    }
    (pack_dir / "pack-receipt-v1.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="sample-bay")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = build_pack(bay_slug=args.bay)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

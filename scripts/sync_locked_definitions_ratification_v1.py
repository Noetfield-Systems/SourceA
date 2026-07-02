#!/usr/bin/env python3
"""Sync term/claim ratification to live_locked after founder decisions."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFINITIONS = ROOT / "reports/locked-definitions-v1.json"
REGISTRY = ROOT / "data/sourcea-brain-registry-inventory-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sync(*, write: bool = False) -> dict:
    doc = json.loads(DEFINITIONS.read_text(encoding="utf-8"))
    updated_terms = 0
    updated_claims = 0
    for term in doc.get("terms") or []:
        if term.get("ratification_status") != "live_locked":
            term["ratification_status"] = "live_locked"
            updated_terms += 1
    for claim in doc.get("claims") or []:
        if claim.get("ratification_status") != "live_locked":
            claim["ratification_status"] = "live_locked"
            updated_claims += 1
        if claim.get("not_deployed"):
            claim["not_deployed"] = False
            updated_claims += 1
    doc["status"] = "live_locked"
    doc["not_deployed"] = False
    doc["term_ratification_synced_at"] = _now()

    row = {
        "ok": True,
        "updated_terms": updated_terms,
        "updated_claims": updated_claims,
        "status": doc["status"],
    }

    if write:
        DEFINITIONS.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        row["definitions_sha256"] = hashlib.sha256(DEFINITIONS.read_bytes()).hexdigest()
        sys.path.insert(0, str(ROOT / "scripts"))
        from promote_locked_definitions_v1 import _sync_expected_checksum_in_py

        row["synced_expected_checksum_py"] = _sync_expected_checksum_in_py(row["definitions_sha256"])
        reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for asset in reg.get("assets") or []:
            if asset.get("asset_id") == "locked-definitions-v1":
                asset["status"] = "live_locked"
                asset["last_modified"] = _now()[:10]
        reg["saved_at"] = _now()
        REGISTRY.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
        row["wrote_definitions"] = True
        row["wrote_registry"] = True

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = sync(write=args.write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK terms={row['updated_terms']} claims={row['updated_claims']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
